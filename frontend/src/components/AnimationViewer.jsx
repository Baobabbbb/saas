import React from 'react';
import { motion } from 'framer-motion';
import './AnimationViewer.css';

const AnimationViewer = ({ animationResult, onClose }) => {
  if (!animationResult) return null;

  // Déterminer l'URL vidéo finale
  const finalVideoUrl = 
    animationResult.final_video_url || 
    animationResult.result?.final_video_url ||
    animationResult.video_url ||
    animationResult.data?.final_video_url ||
    animationResult.data?.video_url ||
    (animationResult.video_urls && animationResult.video_urls[0]);
  
  const videoDuration = animationResult.duration || 
                        animationResult.duration_seconds || 
                        animationResult.total_duration ||
                        animationResult.data?.duration;
  
  const videoTitle = animationResult.title || animationResult.data?.title || 'Dessin animé';

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '';
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  return (
    <motion.div
      className="animation-viewer-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="animation-viewer"
        initial={{ opacity: 0, scale: 0.8, y: 50 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.8, y: 50 }}
        onClick={(e) => e.stopPropagation()}
        transition={{ type: "spring", damping: 20, stiffness: 300 }}
        style={{ maxWidth: '900px', width: '95%' }}
      >
        {/* Header simplifié */}
        <div className="viewer-header" style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: '16px 20px',
          borderBottom: '1px solid #eee'
        }}>
          <h2 style={{ margin: 0, fontSize: '1.3rem' }}>🎬 {videoTitle}</h2>
          <button 
            className="close-button" 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              padding: '4px 8px',
              borderRadius: '4px',
              color: '#666'
            }}
          >
            ✕
          </button>
        </div>

        {/* Contenu : juste la vidéo */}
        <div style={{ padding: '20px' }}>
          {finalVideoUrl ? (
            <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
              {/* Lecteur vidéo */}
              <div style={{ 
                position: 'relative',
                backgroundColor: '#000',
                borderRadius: '12px',
                overflow: 'hidden',
                boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
              }}>
                <video
                  src={finalVideoUrl}
                  controls
                  autoPlay
                  loop
                  style={{
                    width: '100%',
                    height: 'auto',
                    aspectRatio: '16/9',
                    display: 'block',
                    objectFit: 'cover'
                  }}
                />
              </div>

              {/* Barre d'actions sous la vidéo */}
              <div style={{ 
                marginTop: '16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '12px'
              }}>
                {videoDuration && (
                  <span style={{ fontSize: '14px', color: '#666' }}>
                    ⏱️ Durée : {formatTime(videoDuration)}
                  </span>
                )}
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    onClick={() => window.open(finalVideoUrl, '_blank')}
                    style={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: 'white',
                      border: 'none',
                      padding: '10px 18px',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    🔗 Plein écran
                  </button>
                  <button 
                    onClick={async () => {
                      try {
                        const response = await fetch(finalVideoUrl);
                        const blob = await response.blob();
                        const blobUrl = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = blobUrl;
                        link.download = `${videoTitle.replace(/[^a-z0-9]/gi, '_')}_herbbie.mp4`;
                        link.click();
                        URL.revokeObjectURL(blobUrl);
                      } catch (e) {
                        window.open(finalVideoUrl, '_blank');
                      }
                    }}
                    style={{
                      background: '#f0f0f0',
                      color: '#333',
                      border: 'none',
                      padding: '10px 18px',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    📥 Télécharger
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '60px 20px',
              color: '#666'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎬</div>
              <h3>Vidéo non disponible</h3>
              <p>Cette animation n'a pas de vidéo associée.</p>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AnimationViewer;
