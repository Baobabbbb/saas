import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getUserCreations, deleteCreation } from '../services/creations';
import './History.css';
import { jsPDF } from 'jspdf';
import { downloadColoringAsPDF, addHerbbieSuffix } from '../utils/coloringPdfUtils';

// Fonction helper pour obtenir l'URL d'image correcte pour les BD
const getComicImageUrl = (imagePath, baseUrl) => {
  if (!imagePath) return null;
  
  // Si c'est déjà une URL complète (Supabase Storage), l'utiliser directement
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // Sinon, construire l'URL avec baseUrl (ancien format local)
  return `${baseUrl}${imagePath}`;
};

// Fonction pour télécharger une bande dessinée en PDF
const downloadComicAsPDF = async (comic, baseUrl) => {
  const pages = comic.pages || comic.data?.pages || comic.comic_data?.pages || [];
  
  if (!pages || pages.length === 0) {
    alert('Aucune page disponible pour cette bande dessinée.');
    return;
  }

  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'px',
    format: 'a4',
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 40;
  const imageWidth = pageWidth - 2 * margin;
  const imageHeight = pageHeight - 2 * margin;

  // Fonction pour charger une image et obtenir son dataURL
  const fetchImageInfo = (url) => {
    return new Promise((resolve, reject) => {
      const img = new window.Image();
      img.crossOrigin = "Anonymous";
      img.onload = function () {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const dataUrl = canvas.toDataURL('image/png');
        resolve({ width: img.width, height: img.height, dataUrl });
      };
      img.onerror = reject;
      img.src = url;
    });
  };

  // Précharger toutes les images
  const imgInfos = await Promise.all(
    pages.map(async (page) => {
      try {
        const imageUrl = getComicImageUrl(page.image_url || page, baseUrl);
        if (!imageUrl) return null;
        return await fetchImageInfo(imageUrl);
      } catch (e) {
        console.warn("Erreur chargement image BD pour le PDF :", page, e);
        return null;
      }
    })
  );

  let isFirstPage = true;
  
  for (let i = 0; i < imgInfos.length; i++) {
    if (!imgInfos[i]) continue;
    
    if (!isFirstPage) {
      pdf.addPage();
    }
    isFirstPage = false;

    const { dataUrl, width, height } = imgInfos[i];
    
    // Calcul des dimensions pour garder les proportions
    const aspectRatio = width / height;
    let finalWidth = imageWidth;
    let finalHeight = imageWidth / aspectRatio;
    
    if (finalHeight > imageHeight) {
      finalHeight = imageHeight;
      finalWidth = imageHeight * aspectRatio;
    }
    
    // Centrage de l'image
    const x = (pageWidth - finalWidth) / 2;
    const y = (pageHeight - finalHeight) / 2;

    pdf.addImage(dataUrl, 'PNG', x, y, finalWidth, finalHeight);
    
    // 🏷️ Watermark "Créé avec HERBBIE" en bas à gauche
    // Récupérer les dimensions de la page actuelle (en px)
    const currentPageWidth = pdf.internal.pageSize.getWidth();
    const currentPageHeight = pdf.internal.pageSize.getHeight();
    pdf.setFontSize(8);
    pdf.setTextColor(107, 78, 255); // #6B4EFF - Violet HERBBIE
    pdf.text("Créé avec HERBBIE", 15, currentPageHeight - 10, { align: "left" });
  }

  // Nom de fichier safe
  const safeTitle = (comic.title || 'bande_dessinee')
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");

  pdf.save(addHerbbieSuffix(safeTitle, 'pdf'));
};
import useSupabaseUser from '../hooks/useSupabaseUser';
import useUserCreations from '../hooks/useUserCreations';
import { API_BASE_URL } from '../config/api';

const History = ({ onClose, onSelect }) => {
  // Utiliser les hooks optimisés pour Supabase
  const { user } = useSupabaseUser();
  const { creations, loading: creationsLoading, refreshCreations } = useUserCreations(user?.id);
  

  // Fonction de suppression mise à jour pour utiliser le hook
  const handleDelete = async (id) => {
    const confirmDelete = window.confirm("Supprimer cette création ?");
    if (!confirmDelete) return;
    
    try {
      const { error } = await deleteCreation(id);
      if (error) {
        alert("Erreur lors de la suppression !");
        return;
      }
      // Rafraîchir les créations après suppression
      refreshCreations();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      alert("Erreur lors de la suppression !");
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  // Fonction helper pour obtenir l'URL audio correcte
  // Gère les URLs Supabase Storage complètes (https://) et ignore les chemins locaux obsolètes
  const getAudioUrl = (creation) => {
    const audioPath = creation.audio_path || creation.data?.audio_path;
    
    // Pour les comptines, utiliser suno_url comme fallback si audio_path n'est pas disponible
    if (!audioPath && (creation.type === 'rhyme' || creation.type === 'comptine')) {
      const sunoUrl = creation.suno_url || creation.data?.suno_url;
      if (sunoUrl) {
        return sunoUrl; // URL Suno directe
      }
    }
    
    if (!audioPath) return null;
    
    // Si c'est déjà une URL complète (Supabase Storage), l'utiliser directement
    if (audioPath.startsWith('http://') || audioPath.startsWith('https://')) {
      return audioPath;
    }
    
    // Si c'est un chemin local (commence par static/), ignorer car les fichiers locaux ont été supprimés
    // Les fichiers sont maintenant uniquement dans Supabase Storage
    if (audioPath.startsWith('static/')) {
      // Ne pas logger de warning - les anciens chemins locaux sont normaux pour les anciennes créations
      return null; // Ne pas essayer de charger les anciens fichiers locaux
    }
    
    // Pour les autres chemins relatifs (non-static), construire l'URL avec API_BASE_URL
    // (au cas où il y aurait d'autres formats)
    return `${API_BASE_URL}/${audioPath}`;
  };
  const getContentTypeIcon = (type) => {
    switch (type) {
      case 'comic':
      case 'bd':
      case 'story':
        return '💬';
      case 'rhyme':
      case 'comptine':
        return '🎵';
      case 'audio':
      case 'histoire':
        return '📖';
      case 'coloring':
      case 'coloriage':
        return '🎨';
      case 'crewai_animation':
      case 'animation':
        return '🎬';
      default:
        return '📄';
    }
  };

  const getContentTypeLabel = (type) => {
    switch (type) {
      case 'comic':
      case 'bd':
      case 'story':
        return 'Bande dessinée';
      case 'rhyme':
      case 'comptine':
        return 'Comptine';
      case 'audio':
      case 'histoire':
        return 'Histoire';
      case 'coloring':
      case 'coloriage':
        return 'Coloriage';
      case 'crewai_animation':
      case 'animation':
        return 'Dessin animé';
      default:
        return 'Création';
    }
  };

  const handleDownloadPDF = (creation) => {
    const content = creation.content || creation.data?.content || '';
    if (!content || typeof content !== "string") {
      console.error("❌ Contenu invalide ou manquant pour le PDF.");
      return;
    }

    const doc = new jsPDF({
      orientation: "p",
      unit: "mm",
      format: "a4"
    });

    const marginTop = 40;
    const pageWidth = 210;
    const pageHeight = 297;
    const lineHeight = 12;
    const maxLinesPerPage = Math.floor((pageHeight - marginTop * 2) / lineHeight);
    const fontSize = 13;

    // 🏷️ Titre réel (extrait du markdown **titre**)
    let finalTitle = creation.title;
    let processedContent = content;
    if (content.startsWith("**") && content.includes("**", 2)) {
      finalTitle = content.split("**")[1].trim();
      processedContent = content.replace(`**${finalTitle}**`, "").trim();
    }

    // 🌠 Chargement de l'image de fond
    const loadImage = (url) =>
      new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        // Note: crossOrigin est toujours nécessaire pour les images externes
        img.src = url;
        img.onload = () => resolve(img);
      });

    // 📄 Génération du PDF avec mise en page
    const generatePDF = async () => {
      try {
        // 🎨 Charger l'image de fond
        const bgImageUrl = '/assets/fond.png?v=1';
        let bgImage = null;
        try {
          bgImage = await loadImage(bgImageUrl);
        } catch (error) {
          console.log('⚠️ Image de fond non disponible, PDF sans fond');
        }

        // ✂️ Texte découpé (exactement comme la fonction originale)
        const lines = doc.splitTextToSize(processedContent, 150); // max 150mm
        let currentLine = 0;

        for (let page = 0; currentLine < lines.length; page++) {
          if (page > 0) doc.addPage();

          // Ajouter l'image de fond si disponible
          if (bgImage) {
            doc.addImage(bgImage, "PNG", 0, 0, pageWidth, pageHeight, undefined, "FAST");
          }

          // 🎨 Titre (uniquement page 1)
          if (page === 0) {
            doc.setFont("courier", "bold");
            doc.setFontSize(22);
            doc.setTextColor(110, 50, 230); // Violet
            doc.text(finalTitle, pageWidth / 2, marginTop - 20, { align: "center" });
          }

          // ✍️ Texte principal (gras et bleu nuit)
          doc.setFont("courier", "bold");
          doc.setFontSize(fontSize);
          doc.setTextColor(25, 25, 112); // Bleu nuit

          for (let i = 0; i < maxLinesPerPage && currentLine < lines.length; i++, currentLine++) {
            const y = marginTop + i * lineHeight;
            doc.text(lines[currentLine], pageWidth / 2, y, { align: "center" });
          }

          // 📄 Pagination
          doc.setFontSize(11);
          doc.setTextColor(106, 90, 205); // Violet doux
          doc.text(`Page ${page + 1}`, pageWidth - 15, 290, { align: "right" });
          
          // 🏷️ Watermark "Créé avec HERBBIE" en bas à gauche
          doc.setFontSize(8);
          doc.setTextColor(106, 90, 205); // Violet doux (même couleur que la pagination)
          doc.text("Créé avec HERBBIE", 15, 290, { align: "left" });
        }
      } catch (error) {
        console.error('❌ Erreur lors de la génération du PDF:', error);
        // Fallback : PDF simple sans image de fond
        doc.setFontSize(22);
        doc.setTextColor(110, 50, 230);
        doc.setFont("courier", "bold");
        doc.text(finalTitle, pageWidth / 2, marginTop - 20, { align: "center" });
        
        doc.setFontSize(fontSize);
        doc.setTextColor(25, 25, 112);
        doc.setFont("courier", "bold");
        const lines = doc.splitTextToSize(processedContent, 150);
        for (let i = 0; i < lines.length; i++) {
          const y = marginTop + i * lineHeight;
          doc.text(lines[i], pageWidth / 2, y, { align: "center" });
        }
      }
    };

    // 🚀 Lancer la génération
    generatePDF().then(() => {
      // 📁 Nom de fichier propre
      const safeTitle = finalTitle
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");

      // Générer le PDF comme blob et déclencher le téléchargement direct
      const pdfBlob = doc.output('blob');
      const pdfUrl = URL.createObjectURL(pdfBlob);

      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = addHerbbieSuffix(safeTitle, 'pdf');
      link.style.display = 'none';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Nettoyer l'URL du blob après utilisation
      setTimeout(() => {
        URL.revokeObjectURL(pdfUrl);
      }, 100);
    });
  };

  return (
    <motion.div 
      className="history-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="history-header">
        <h2>Historique de vos créations</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
        
        <div className="history-content">
          {!user ? (
            <div className="empty-history">
              <p>Connexion en cours...</p>
            </div>
          ) : creations.length === 0 && !creationsLoading ? (
            <div className="empty-history">
              <p>Vous n'avez pas encore de créations</p>
              <p className="empty-subtext">Vos créations apparaîtront ici une fois générées</p>
            </div>
          ) : (
            <div className="creations-list">{creations.map((creation) => {
              // Déterminer les classes CSS selon le contenu
              const hasAudio = !!getAudioUrl(creation);
              const hasText = !!(creation.content || creation.data?.content);
              const itemClasses = [
                'creation-item',
                hasAudio ? 'has-audio' : '',
                hasText ? 'has-text' : ''
              ].filter(Boolean).join(' ');

              return (
                <motion.div 
                key={creation.id}
                className={itemClasses}
                onClick={() => onSelect({
                  ...creation,
                  action: creation.type === 'coloring' ? 'showColoring' : 
                          (creation.type === 'comic' || creation.type === 'bd') ? 'showComic' : 'showStory'
                })}
                whileHover={{ scale: 1.01 }}
                transition={{ duration: 0.2 }}
              >
                <div className="creation-icon">
                  {getContentTypeIcon(creation.type)}
                </div>                  <div className="creation-details">
                  <h3>{creation.title}</h3>
                  <div className="creation-meta">
                    <span className="creation-type">{getContentTypeLabel(creation.type)}</span>
                    <span className="creation-date">{formatDate(creation.created_at)}</span>
                  </div>                  {getAudioUrl(creation) && (
                    <audio
                      controls
                      className="creation-audio"
                      src={getAudioUrl(creation)}
                    />
                  )}

                  <div className="creation-actions">
                    {/* Pour les comptines : bouton spécial qui télécharge le MP3 */}
                    {creation.type === 'rhyme' && getAudioUrl(creation) && (
                      <button
                        className="btn-pdf"
                        onClick={async (e) => {
                          e.stopPropagation();
                          try {
                            const audioUrl = getAudioUrl(creation);
                            const response = await fetch(audioUrl);
                            const blob = await response.blob();
                            const blobUrl = URL.createObjectURL(blob);
                            
                            // Utiliser le même titre que le PDF
                            let finalTitle = creation.title || 'Comptine';
                            const content = creation.content || creation.data?.content || '';
                            if (content && content.startsWith("**") && content.includes("**", 2)) {
                              finalTitle = content.split("**")[1].trim();
                            }
                            
                            // Appliquer la même transformation que le PDF
                            const safeTitle = finalTitle
                              .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                              .toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
                            
                            const link = document.createElement('a');
                            link.href = blobUrl;
                            link.download = addHerbbieSuffix(safeTitle, 'mp3');
                            link.style.display = 'none';
                            
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            
                            URL.revokeObjectURL(blobUrl);
                          } catch (error) {
                            console.error('Erreur lors du téléchargement de la comptine:', error);
                            alert('Erreur lors du téléchargement. Veuillez réessayer.');
                          }
                        }}
                      >
                        🎵 Télécharger la comptine
                      </button>
                    )}
                    
                    {/* Pour les histoires audio : boutons PDF et audio */}
                    {(creation.type === 'audio' || creation.type === 'histoire') && (creation.content || creation.data?.content) && (
                      <>
                        <button
                          className="btn-pdf"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDownloadPDF(creation);
                          }}
                        >
                          📄 Télécharger le PDF
                        </button>

                        {getAudioUrl(creation) && (creation.audio_generated || creation.data?.audio_generated) && (
                          <button
                            className="btn-pdf"
                            onClick={async (e) => {
                              e.stopPropagation();
                              try {
                                const audioUrl = getAudioUrl(creation);
                                const response = await fetch(audioUrl);
                                const blob = await response.blob();
                                const blobUrl = URL.createObjectURL(blob);
                                
                                // Utiliser le même titre que le PDF
                                let finalTitle = creation.title || 'Histoire';
                                const content = creation.content || creation.data?.content || '';
                                if (content && content.startsWith("**") && content.includes("**", 2)) {
                                  finalTitle = content.split("**")[1].trim();
                                }
                                
                                // Appliquer la même transformation que le PDF
                                const safeTitle = finalTitle
                                  .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                                  .toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
                                
                                const link = document.createElement('a');
                                link.href = blobUrl;
                                link.download = addHerbbieSuffix(safeTitle, 'mp3');
                                link.style.display = 'none';
                                
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                                
                                URL.revokeObjectURL(blobUrl);
                              } catch (error) {
                                console.error('Erreur lors du téléchargement audio:', error);
                                alert('Erreur lors du téléchargement. Veuillez réessayer.');
                              }
                            }}
                          >
                            🎵 Télécharger l'audio
                          </button>
                        )}
                      </>
                    )}
                    
                    {/* Pour les autres types avec audio : bouton audio standard (sauf audio, histoire et rhyme qui ont leurs propres boutons) */}
                    {getAudioUrl(creation) && (creation.audio_generated || creation.data?.audio_generated) && creation.type !== 'rhyme' && creation.type !== 'audio' && creation.type !== 'histoire' && (
                      <button
                        className="btn-audio"
                        onClick={async (e) => {
                          e.stopPropagation();
                          try {
                            const audioUrl = getAudioUrl(creation);
                            const response = await fetch(audioUrl);
                            if (!response.ok) throw new Error('Erreur lors du téléchargement');
                            
                            const blob = await response.blob();
                            const blobUrl = URL.createObjectURL(blob);
                            
                            const safeTitle = (creation.title || 'audio').replace(/[^a-z0-9]/gi, '_').toLowerCase();
                            const link = document.createElement('a');
                            link.href = blobUrl;
                            link.download = addHerbbieSuffix(safeTitle, 'mp3');
                            link.style.display = 'none';
                            
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            
                            URL.revokeObjectURL(blobUrl);
                          } catch (error) {
                            console.error('Erreur lors du téléchargement audio:', error);
                            alert('Erreur lors du téléchargement. Veuillez réessayer.');
                          }
                        }}
                      >
                        🔊 Télécharger l'audio
                      </button>
                    )}

                    {creation.type === 'coloring' && (creation.images || creation.data?.images) && (creation.images?.length > 0 || creation.data?.images?.length > 0) && (
                      <button
                        className="btn-pdf"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Utiliser le même titre que la page principale
                          const titleForDownload = creation.title || (creation.theme ? `coloriages_${creation.theme}` : 'coloriages');
                          const images = creation.images || creation.data?.images || [];
                          downloadColoringAsPDF(images, titleForDownload);
                        }}
                      >
                        📄 Télécharger le coloriage
                      </button>
                    )}

                    {/* Pour les bandes dessinées : bouton PDF */}
                    {(creation.type === 'comic' || creation.type === 'bd' || creation.type === 'story') && (creation.pages || creation.data?.pages || creation.comic_data?.pages) && (
                      <button
                        className="btn-pdf"
                        onClick={async (e) => {
                          e.stopPropagation();
                          try {
                            await downloadComicAsPDF(creation, API_BASE_URL);
                          } catch (error) {
                            console.error('Erreur lors du téléchargement de la BD:', error);
                            alert('Erreur lors du téléchargement. Veuillez réessayer.');
                          }
                        }}
                      >
                        📄 Télécharger le PDF
                      </button>
                    )}

                    <button
                      className="btn-delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(creation.id);
                      }}
                    >
                      🗑️ Supprimer
                    </button>
                  </div>
                </div>
              </motion.div>
              );
            })}
            </div>
          )}
        </div>
    </motion.div>
  );
};

export default History;
