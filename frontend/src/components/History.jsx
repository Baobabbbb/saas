import React from 'react';
import { motion } from 'framer-motion';
import './History.css';

const History = ({ creations, onClose, onSelect }) => {
  // Function to format date
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

  // Function to get icon based on content type
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

  // Function to get content type label
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
            <div className="empty-icon">📭</div>
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
