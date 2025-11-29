import React from 'react';
import { motion } from 'framer-motion';
import './RhymePopup.css';

const RhymePopup = ({ title, audioUrls, onClose }) => {
  // Gérer le cas où audioUrls est un tableau (Suno retourne 2 chansons) ou une seule URL
  const songs = Array.isArray(audioUrls) ? audioUrls : (audioUrls ? [{ audio_url: audioUrls, title: title }] : []);
  
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
            <h3>Vos comptines musicales sont prêtes !</h3>
            <p className="suno-info">
              ✨ Généré avec Suno AI - {songs.length} version{songs.length > 1 ? 's' : ''} disponible{songs.length > 1 ? 's' : ''}
            </p>
            
            {songs.length > 0 ? (
              <div className="songs-container">
                {songs.map((song, index) => (
                  <div key={song.id || index} className="song-item">
                    <h4 className="song-title">
                      🎼 Version {index + 1}
                      {song.title && song.title !== title && ` - ${song.title}`}
                    </h4>
                    
                    <div className="audio-player-container">
                      <audio
                        controls
                        autoPlay={false}
                        className="audio-player"
                        src={song.audio_url}
                      >
                        Votre navigateur ne supporte pas l'élément audio.
                      </audio>
                      
                      <div className="audio-controls">
                        <button 
                          onClick={async (e) => {
                            e.stopPropagation();
                            try {
                              const response = await fetch(song.audio_url);
                              if (!response.ok) throw new Error('Erreur lors du téléchargement');
                              
                              const blob = await response.blob();
                              const blobUrl = URL.createObjectURL(blob);
                              
                              const safeTitle = `${title.replace(/[^a-z0-9]/gi, '_')}_v${index + 1}.mp3`;
                              const link = document.createElement('a');
                              link.href = blobUrl;
                              link.download = safeTitle;
                              link.style.display = 'none';
                              
                              document.body.appendChild(link);
                              link.click();
                              document.body.removeChild(link);
                              
                              URL.revokeObjectURL(blobUrl);
                            } catch (error) {
                              console.error('Erreur lors du téléchargement:', error);
                              alert('Erreur lors du téléchargement. Veuillez réessayer.');
                            }
                          }}
                          className="download-audio-btn"
                        >
                          💾 Télécharger
                        </button>
                        {song.video_url && (
                          <a 
                            href={song.video_url} 
                            target="_blank"
                            rel="noopener noreferrer"
                            className="view-video-btn"
                          >
                            🎬 Voir la vidéo
                          </a>
                        )}
                      </div>
                    </div>
                    
                    {song.duration && (
                      <p className="song-duration">⏱️ Durée: {Math.floor(song.duration)}s</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-audio">
                <p>🔄 L'audio est en cours de génération avec Suno AI...</p>
                <p className="suno-wait">Cela prend généralement 2-3 minutes</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default RhymePopup;
