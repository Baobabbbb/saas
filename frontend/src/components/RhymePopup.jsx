import React from 'react';
import { motion } from 'framer-motion';
import './RhymePopup.css';

const RhymePopup = ({ title, audioUrl, onClose }) => {
  return (
    <motion.div
      className="rhyme-popup-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="rhyme-popup-content"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="rhyme-popup-header">
          <h2 className="rhyme-title">{title}</h2>
          <button 
            className="close-button"
            onClick={onClose}
            aria-label="Fermer"
          >
            ✕
          </button>
        </div>
        
        <div className="rhyme-popup-body">
          <div className="audio-section">
            <div className="audio-icon">
              🎵
            </div>
            <h3>Votre comptine musicale est prête !</h3>
            <p>Cliquez sur le bouton play pour écouter votre comptine avec sa mélodie.</p>
            
            {audioUrl ? (
              <div className="audio-player-container">
                <audio
                  controls
                  autoPlay={false}
                  className="audio-player"
                  src={audioUrl}
                >
                  Votre navigateur ne supporte pas l'élément audio.
                </audio>
                
                <div className="audio-controls">
                  <a 
                    href={audioUrl} 
                    download={`${title.replace(/[^a-z0-9]/gi, '_')}.mp3`}
                    className="download-audio-btn"
                  >
                    💾 Télécharger l'audio
                  </a>
                </div>
              </div>
            ) : (
              <div className="no-audio">
                <p>🔄 L'audio est en cours de génération...</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default RhymePopup;
