import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getUserCreations, deleteCreation } from '../services/creations';
import './History.css';
import jsPDF from 'jspdf';

const History = ({ onClose, onSelect }) => {
  const [creations, setCreations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCreations();
  }, []);

  const fetchCreations = async () => {
    setLoading(true);
    const data = await getUserCreations();
    setCreations(data || []);
    setLoading(false);
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
    if (!content) return;

    const doc = new jsPDF();
    const lines = doc.splitTextToSize(content, 180);
    doc.setFontSize(12);
    doc.text(lines, 15, 20);

    const rawTitle = creation.title || creation.type;
    const safeTitle = rawTitle.toLowerCase().replace(/\s+/g, '_').replace(/[^\w\-]/g, '');
    doc.save(`${safeTitle}.pdf`);
  };

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm("Supprimer cette création ?");
    if (!confirmDelete) return;
    const { error } = await deleteCreation(id);
    if (error) {
      alert("Erreur lors de la suppression !");
      return;
    }
    fetchCreations(); // Rafraîchir la liste après suppression
  };

  if (loading) return <div>Chargement...</div>;

  return (
    <motion.div 
      className="history-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="history-header">
        <h2>Historique de vos créations</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
      
      <div className="history-content">
        {creations.length === 0 ? (
          <div className="empty-history">
            <p>Vous n'avez pas encore de créations</p>
            <p className="empty-subtext">Vos créations apparaîtront ici une fois générées</p>
          </div>
        ) : (
          <div className="creations-list">            {creations.map((creation) => (              <motion.div 
                key={creation.id}
                className="creation-item"
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
                  </div>                  {creation.audio_path && (
                    <audio
                      controls
                      className="creation-audio"
                      src={`http://localhost:8000/${creation.audio_path}`}
                    />
                  )}

                  {creation.type === 'coloring' && creation.images && creation.images.length > 0 && (
                    <div className="coloring-preview">
                      {creation.images.map((image, index) => (
                        <img 
                          key={index}
                          src={image.image_url} 
                          alt={`Coloriage ${creation.theme}`}
                          className="coloring-thumbnail"
                          style={{
                            width: '100px',
                            height: '100px',
                            objectFit: 'cover',
                            border: '2px solid #ddd',
                            borderRadius: '8px',
                            margin: '5px'
                          }}
                        />
                      ))}
                    </div>
                  )}<div className="creation-actions">
                    {(creation.type === 'audio' || creation.type === 'rhyme') && (creation.content || creation.data?.content) && (
                      <button
                        className="btn-pdf"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownloadPDF(creation);
                        }}
                      >
                        📄 Télécharger le PDF
                      </button>
                    )}                    {creation.audio_path && (
                      <a
                        className="btn-audio"
                        href={`http://localhost:8000/${creation.audio_path}`}
                        download
                        onClick={(e) => e.stopPropagation()}
                      >
                        🔊 Télécharger l'audio
                      </a>
                    )}

                    {creation.type === 'coloring' && creation.images && creation.images.length > 0 && (
                      creation.images.map((image, index) => (
                        <a
                          key={index}
                          className="btn-coloring"
                          href={image.image_url}
                          download={`coloriage_${creation.theme}_${index + 1}.png`}
                          onClick={(e) => e.stopPropagation()}
                        >
                          🎨 Télécharger coloriage {index + 1}
                        </a>
                      ))
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
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default History;
