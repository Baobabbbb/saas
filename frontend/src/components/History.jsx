import React from 'react';
import { motion } from 'framer-motion';
import './History.css';
import jsPDF from 'jspdf';

const History = ({ creations, onClose, onSelect, onDelete }) => {
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
        return '🎧';
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
        return 'Conte audio';
      default:
        return 'Création';
    }
  };

  const handleDownloadPDF = (creation) => {
    if (!creation?.content) return;

    const doc = new jsPDF();
    const lines = doc.splitTextToSize(creation.content, 180);
    doc.setFontSize(12);
    doc.text(lines, 15, 20);

    const rawTitle = creation.title || creation.type;
    const safeTitle = rawTitle.toLowerCase().replace(/\s+/g, '_').replace(/[^\w\-]/g, '');
    doc.save(`${safeTitle}.pdf`);
  };

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
          <div className="creations-list">
            {creations.map((creation) => (
              <motion.div 
                key={creation.id}
                className="creation-item"
                onClick={() => onSelect(creation)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="creation-icon">
                  {getContentTypeIcon(creation.type)}
                </div>
                <div className="creation-details">
                  <h3>{creation.title}</h3>
                  <div className="creation-meta">
                    <span className="creation-type">{getContentTypeLabel(creation.type)}</span>
                    <span className="creation-date">{formatDate(creation.createdAt)}</span>
                  </div>

                  {creation.content && creation.type !== 'rhyme' && (
                    <div className="creation-text">
                      {creation.content}
                    </div>
                  )}

                  {creation.audio_path && (
                    <audio
                      controls
                      className="creation-audio"
                      src={`http://localhost:8000/${creation.audio_path}`}
                    />
                  )}

                  <div className="creation-actions">
                    {(creation.type === 'audio' || creation.type === 'rhyme') && creation.content && (
                      <button
                        className="btn-pdf"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownloadPDF(creation);
                        }}
                      >
                        📄 Télécharger le PDF
                      </button>
                    )}

                    {creation.audio_path && (
                      <a
                        className="btn-audio"
                        href={`http://localhost:8000/${creation.audio_path}`}
                        download
                        onClick={(e) => e.stopPropagation()}
                      >
                        🔊 Télécharger l'audio
                      </a>
                    )}

                    <button
                      className="btn-delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        const confirmDelete = window.confirm(`Supprimer « ${creation.title} » ?`);
                        if (confirmDelete) {
                          onDelete(creation.id);
                        }
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
