import React, { useState } from 'react';
import { API_BASE_URL, ANIMATION_API_BASE_URL } from '../config/api';
import { motion, AnimatePresence } from 'framer-motion';
import './AnimationViewer.css';

const AnimationViewer = ({ animationResult, onClose }) => {
  const [activeTab, setActiveTab] = useState('video');
  const [selectedClip, setSelectedClip] = useState(null);

  if (!animationResult) return null;

  const {
    status,
    clips = [],
    scenes = [],
    generation_time,
    total_duration,
    successful_clips = 0,
    fallback_clips = 0,
    pipeline_type
  } = animationResult;

  const hasVideo = clips.some(clip => clip.status === 'success') || (status === 'completed' && (animationResult.final_video_url || animationResult.result?.final_video_url));
  const scenesDetails = scenes || animationResult.scenes_details || [];

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '---';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return '#4CAF50';
      case 'fallback': return '#FF9800';
      case 'error': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return '✅';
      case 'fallback': return '⚠️';
      case 'error': return '❌';
      default: return '🔄';
    }
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
      >
        {/* Header */}
        <div className="viewer-header">
          <h2>🎬 Votre dessin animé IA</h2>
          {status && (
            <div className="status-badge" style={{backgroundColor: getStatusColor(status)}}>
              {getStatusIcon(status)} {status === 'generating_idea' ? 'Création de l\'idée...' :
                                      status === 'creating_scenes' ? 'Création des scènes...' :
                                      status === 'generating_clips' ? 'Génération vidéo...' :
                                      status === 'completed' ? 'Terminé !' :
                                      status === 'failed' ? 'Échoué' : status}
            </div>
          )}
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Stats rapides */}
        <div className="animation-stats">
          <div className="stat-item">
            <span className="stat-icon">⏱️</span>
            <span>Durée: {formatTime(total_duration || animationResult.duration)}</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🎞️</span>
            <span>{clips.length} scènes</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">✅</span>
            <span>{successful_clips} réussies</span>
          </div>
          {fallback_clips > 0 && (
            <div className="stat-item">
              <span className="stat-icon">⚠️</span>
              <span>{fallback_clips} fallback</span>
            </div>
          )}
          <div className="stat-item">
            <span className="stat-icon">🚀</span>
            <span>Généré en {generation_time ? Math.round(generation_time) + 's' : 'En cours...'}</span>
          </div>
        </div>

        {/* Onglets */}
        <div className="viewer-tabs">
          <button
            className={`tab ${activeTab === 'video' ? 'active' : ''}`}
            onClick={() => setActiveTab('video')}
          >
            🎬 Vidéo
          </button>
          <button
            className={`tab ${activeTab === 'scenes' ? 'active' : ''}`}
            onClick={() => setActiveTab('scenes')}
          >
            🎞️ Scènes
          </button>
          <button
            className={`tab ${activeTab === 'details' ? 'active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            📊 Détails
          </button>
        </div>

        {/* Contenu des onglets */}
        <div className="viewer-content">
          <AnimatePresence mode="wait">
            {activeTab === 'video' && (
              <motion.div
                key="video"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="video-tab"
              >
                {hasVideo ? (
                  <div className="video-player">
                    {/* VIDÉO FINALE ASSEMBLÉE EN PREMIER */}
                    {(animationResult.final_video_url || animationResult.result?.final_video_url) ? (
                      <div className="final-animation">
                        <div className="video-icon">🎬</div>
                        <h3>🎉 {animationResult.title || 'Votre dessin animé est prêt !'}</h3>
                        <p>
                          Animation complète de {formatTime(total_duration || animationResult.duration)} avec {successful_clips || clips.length} scènes.
                        </p>
                        
                        {/* LECTEUR VIDÉO PRINCIPAL */}
                        <div className="main-video-container">
                          <video 
                            src={animationResult.final_video_url || animationResult.result?.final_video_url}
                            className="final-animation-video"
                            controls
                            autoPlay
                            loop
                            muted
                            preload="metadata"
                            style={{
                              width: '100%',
                              maxWidth: '600px',
                              height: 'auto',
                              borderRadius: '12px',
                              boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                              margin: '1rem 0'
                            }}
                            onLoadedData={() => {/* console.log('✅ Animation finale chargée!') */}}
                            onError={(e) => {
                              // console.log('❌ Erreur vidéo finale:', e.target.src);
                              e.target.style.display = 'none';
                            }}
                          />
                        </div>
                        
                        <div className="video-controls">
                          <button 
                            className="play-btn" 
                            onClick={() => window.open(animationResult.final_video_url || animationResult.result?.final_video_url, '_blank')}
                            style={{
                              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                              color: 'white',
                              border: 'none',
                              padding: '12px 24px',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              margin: '0 auto'
                            }}
                          >
                            🎬 Ouvrir en plein écran
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="animation-gallery">
                        <div className="video-icon">🎬</div>
                        <h3>🎉 Votre dessin animé est prêt !</h3>
                        <p>
                          Animation de {formatTime(total_duration)} générée avec succès.
                          {successful_clips > 0 && ` ${successful_clips} scènes créées avec l'IA.`}
                        </p>
                        
                        {/* Galerie d'images des scènes - FALLBACK SI PAS DE VIDÉO FINALE */}
                        <div className="scenes-gallery">
                          <h4>🎨 Votre dessin animé en images :</h4>
                        <div className="gallery-grid">
                          {clips.map((clip, index) => {
                            // Gestion des médias : vidéo réelle ou image
                            let mediaUrl = null;
                            let isVideo = false;
                            
                            // Priorité: video_url pour vraies vidéos > demo_image_url > image_url
                            if (clip.video_url && clip.type === 'real_video') {
                              // Si l'URL est déjà absolue, on la garde telle quelle ; sinon, on préfixe avec le domaine de l'API animation
                              mediaUrl = /^https?:\/\//i.test(clip.video_url)
                                ? clip.video_url
                                : `${ANIMATION_API_BASE_URL}${clip.video_url}`;
                              isVideo = true;
                            } else if (clip.demo_image_url) {
                              mediaUrl = /^https?:\/\//i.test(clip.demo_image_url)
                                ? clip.demo_image_url
                                : `${ANIMATION_API_BASE_URL}${clip.demo_image_url}`;
                            } else if (clip.image_url) {
                              mediaUrl = /^https?:\/\//i.test(clip.image_url)
                                ? clip.image_url
                                : `${ANIMATION_API_BASE_URL}${clip.image_url}`;
                            } else if (clip.video_url) {
                              mediaUrl = /^https?:\/\//i.test(clip.video_url)
                                ? clip.video_url
                                : `${ANIMATION_API_BASE_URL}${clip.video_url}`;
                            }
                            
                            // console.log(`Clip ${index + 1}:`, { clip, mediaUrl, isVideo });
                            
                            return (
                              <div key={index} className="scene-media-card">
                                {isVideo ? (
                                  <video 
                                    src={mediaUrl}
                                    className="scene-video"
                                    controls
                                    loop
                                    muted
                                    preload="metadata"
                                    onLoadedData={() => {/* console.log(`✅ Vidéo ${index + 1} chargée:`, mediaUrl) */}}
                                    onError={(e) => {
                                      // console.log('❌ Erreur vidéo:', mediaUrl);
                                      e.target.style.display = 'none';
                                      e.target.nextSibling.style.display = 'flex';
                                    }}
                                  />
                                ) : (
                                  <img 
                                    src={mediaUrl}
                                    alt={`Scène ${clip.scene_number}`}
                                    className="scene-image"
                                    onLoad={() => {/* console.log(`✅ Image ${index + 1} chargée:`, mediaUrl) */}}
                                    onError={(e) => {
                                      // console.log('❌ Erreur image:', mediaUrl);
                                      e.target.style.display = 'none';
                                      e.target.nextSibling.style.display = 'flex';
                                    }}
                                  />
                                )}
                                <div className="scene-placeholder" style={{display: 'none'}}>
                                  <span>🎬</span>
                                  <p>Scène {clip.scene_number}</p>
                                  <small>{clip.type || 'En cours...'}</small>
                                </div>
                                <div className="scene-info">
                                  <span>Scène {clip.scene_number}</span>
                                  <span>{formatTime(clip.duration)}</span>
                                  {clip.type === 'real_video' && <span className="clip-type real">🎥 Vidéo</span>}
                                  {clip.type === 'demo' && <span className="clip-type demo">🎨 Démo</span>}
                                  {clip.status === 'success' && <span className="clip-status success">✅</span>}
                                  {clip.status === 'fallback' && <span className="clip-status fallback">⚠️</span>}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        
                        <div className="gallery-summary">
                          <p>
                            <strong>🎬 Votre animation complète :</strong> 
                            {clips.length} scènes illustrées représentant votre histoire.
                            Chaque image correspond à un moment clé de votre récit généré par l'IA.
                          </p>
                        </div>
                      </div>
                      
                      {/* Liste des clips pour les scènes sans image */}
                      {clips.filter(clip => clip.status === 'success').length > 0 && (
                        <div className="video-clips-list">
                          <h4>📝 Toutes les scènes générées :</h4>
                          {clips.filter(clip => clip.status === 'success').map((clip, index) => (
                            <div key={index} className="clip-item">
                              <span>🎬 Scène {clip.scene_number}</span>
                              <span>{formatTime(clip.duration)}</span>
                              {clip.type === 'image' && <span className="clip-type">🎨 Image</span>}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <div className="video-actions">
                        <button className="download-btn">
                          📥 Télécharger
                        </button>
                        <button className="share-btn">
                          🔗 Partager
                        </button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="no-video">
                    <div className="no-video-icon">{status === 'completed' ? '✅' : '⚠️'}</div>
                    <h3>{status === 'completed' ? 'Animation terminée !' : 'Génération en cours...'}</h3>
                    {/* <p style={{fontSize: '12px', color: '#666'}}>Debug: status={status}, hasVideo={hasVideo}</p> */}
                    <p>
                      {status === 'completed' 
                        ? 'Votre animation a été générée avec succès ! Thème: ' + (animationResult.theme || 'N/A')
                        : 'La génération vidéo peut prendre quelques minutes. Certaines scènes utilisent des modes de fallback.'}
                    </p>
                    {status === 'completed' && (animationResult.final_video_url || animationResult.result?.final_video_url) && (
                      <div className="video-controls">
                        <button className="play-btn" onClick={() => window.open(animationResult.final_video_url || animationResult.result?.final_video_url, '_blank')}>
                          🎬 Voir l'animation
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            )}

            {activeTab === 'scenes' && (
              <motion.div
                key="scenes"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="scenes-tab"
              >
                <div className="scenes-list">
                  {scenesDetails.map((scene, index) => {
                    const clip = clips.find(c => c.scene_number === scene.scene_number);
                    return (
                      <motion.div
                        key={scene.scene_number}
                        className={`scene-card ${selectedClip === index ? 'selected' : ''}`}
                        onClick={() => setSelectedClip(selectedClip === index ? null : index)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <div className="scene-header">
                          <span className="scene-number">Scène {scene.scene_number}</span>
                          <div className="scene-status">
                            <span 
                              className="status-icon"
                              style={{ color: getStatusColor(clip?.status || 'pending') }}
                            >
                              {getStatusIcon(clip?.status || 'pending')}
                            </span>
                            <span className="status-text">{clip?.status || 'pending'}</span>
                          </div>
                        </div>
                        <h4>{scene.description}</h4>
                        <p><strong>Action:</strong> {scene.action}</p>
                        <p><strong>Décor:</strong> {scene.setting}</p>
                        <div className="scene-duration">
                          Durée: {formatTime(scene.duration)}
                        </div>
                        
                        {selectedClip === index && clip && (
                          <motion.div
                            className="scene-details"
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                          >
                            {clip.video_url && (
                              <div className="clip-preview">
                                <span>📁 Fichier: {clip.video_url}</span>
                              </div>
                            )}
                          </motion.div>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {activeTab === 'details' && (
              <motion.div
                key="details"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="details-tab"
              >
                <div className="technical-details">
                  <h4>🤖 Détails techniques</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <strong>Pipeline:</strong>
                      <span>{pipeline_type || 'custom_animation_ai'}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Statut:</strong>
                      <span className={`status ${status}`}>{status}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Temps de génération:</strong>
                      <span>{Math.round(generation_time)}s</span>
                    </div>
                    <div className="detail-item">
                      <strong>Scènes totales:</strong>
                      <span>{clips.length}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Scènes réussies:</strong>
                      <span>{successful_clips}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Durée totale:</strong>
                      <span>{formatTime(total_duration)}</span>
                    </div>
                  </div>

                  {animationResult.note && (
                    <div className="generation-note">
                      <h5>📝 Note de génération</h5>
                      <p>{animationResult.note}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AnimationViewer;
