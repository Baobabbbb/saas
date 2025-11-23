import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getUserCreations, deleteCreation } from '../services/creations';
import './History.css';
import { jsPDF } from 'jspdf';
import { downloadColoringAsPDF } from '../utils/coloringPdfUtils';
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
  // Gère les URLs Supabase Storage complètes (https://) et les chemins relatifs
  const getAudioUrl = (creation) => {
    const audioPath = creation.audio_path || creation.data?.audio_path;
    if (!audioPath) return null;
    
    // Si c'est déjà une URL complète (Supabase Storage), l'utiliser directement
    if (audioPath.startsWith('http://') || audioPath.startsWith('https://')) {
      return audioPath;
    }
    
    // Sinon, construire l'URL avec API_BASE_URL (ancien format local)
    return `${API_BASE_URL}/${audioPath}`;
  };
  const getContentTypeIcon = (type) => {
    switch (type) {
      case 'story':
        return '📚';
      case 'rhyme':
        return '🎵';
      case 'audio':
        return '📖';
      case 'coloring':
        return '🎨';
      case 'crewai_animation':
        return '🎬';
      case 'animation':
        return '🎬';
      default:
        return '📄';
    }
  };

  const getContentTypeLabel = (type) => {
    switch (type) {
      case 'story':
        return 'Bande dessinée';
      case 'rhyme':
        return 'Comptine';
      case 'audio':
        return 'Histoire';
      case 'coloring':
        return 'Coloriage';
      case 'crewai_animation':
        return 'Dessin animé';
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
      link.download = `${safeTitle}.pdf`;
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
                  action: creation.type === 'coloring' ? 'showColoring' : 'showStory'
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
                            link.download = `${safeTitle}.mp3`;
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
                            className="btn-audio"
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
                                link.download = `${safeTitle}.mp3`;
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
                    
                    {/* Pour les autres types avec audio : bouton audio standard (sauf audio et rhyme qui ont leurs propres boutons) */}
                    {getAudioUrl(creation) && (creation.audio_generated || creation.data?.audio_generated) && creation.type !== 'rhyme' && creation.type !== 'audio' && (
                      <a
                        className="btn-audio"
                        href={getAudioUrl(creation)}
                        download
                        onClick={(e) => e.stopPropagation()}
                      >
                        🔊 Télécharger l'audio
                      </a>
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
