import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL, ANIMATION_API_BASE_URL } from '../config/api';
import { motion, AnimatePresence } from 'framer-motion';
import './AnimationViewer.css';

// Composant pour afficher la vidéo finale assemblée
const SingleVideoPlayer = ({ videoUrl, duration, title }) => {
  const videoRef = useRef(null);

  if (!videoUrl) {
    return <div className="no-video">Aucune vidéo disponible</div>;
  }

  return (
    <div className="video-player-container" style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
      {/* Lecteur principal - Style cinématique */}
      <div className="main-video-container" style={{ 
        position: 'relative',
        backgroundColor: '#000',
        borderRadius: '16px',
        overflow: 'hidden',
        boxShadow: '0 20px 60px rgba(0,0,0,0.4)'
      }}>
        <video
          ref={videoRef}
          src={videoUrl}
          className="final-animation-video"
          controls
          autoPlay
          loop
          muted={false}
          preload="auto"
          style={{
            width: '100%',
            height: 'auto',
            aspectRatio: '16/9',
            display: 'block',
            objectFit: 'cover'
          }}
        />
        
        {/* Badge titre */}
        <div style={{
          position: 'absolute',
          top: '12px',
          left: '12px',
          background: 'rgba(0,0,0,0.7)',
          color: 'white',
          padding: '6px 12px',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: '600',
          backdropFilter: 'blur(10px)'
        }}>
          🎬 {title || 'Dessin animé'}
        </div>
      </div>

      {/* Informations */}
      <div style={{ 
        marginTop: '16px',
        padding: '0 8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span style={{ fontSize: '14px', color: '#666' }}>
          ⏱️ Durée: {duration ? `${Math.round(duration)}s` : 'N/A'}
        </span>
        <button 
          onClick={() => window.open(videoUrl, '_blank')}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          🔗 Ouvrir en plein écran
        </button>
      </div>

      {/* Message */}
      <p style={{
        textAlign: 'center',
        color: '#888',
        fontSize: '12px',
        marginTop: '12px'
      }}>
        ✨ Animation complète générée par IA et stockée dans le cloud
      </p>
    </div>
  );
};

const AnimationViewer = ({ animationResult, onClose }) => {
  const [activeTab, setActiveTab] = useState('video');
  const [selectedClip, setSelectedClip] = useState(null);

  if (!animationResult) return null;

  const {
    status,
    clips = [],
    video_urls = [],
    scenes = [],
    generation_time,
    total_duration,
    successful_clips = 0,
    fallback_clips = 0,
    pipeline_type,
    scenes_count = 0,
    video_count = 0
  } = animationResult;

  // Compatibilité : utiliser video_urls si clips est vide (nouveau format Veo 3.1 Fast)
  const actualClips = clips.length > 0 ? clips : video_urls.map((url, idx) => ({
    clip_url: url,
    status: 'success',
    prompt: `Scène ${idx + 1}`,
    duration: 8
  }));

  const hasVideo = actualClips.some(clip => clip.status === 'success') || (status === 'completed' && (animationResult.final_video_url || animationResult.result?.final_video_url));
  const scenesDetails = scenes || animationResult.scenes_details || [];
  const totalClips = actualClips.length || scenes_count || video_count;

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
            <span>{totalClips} scènes</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">✅</span>
            <span>{successful_clips || totalClips} réussies</span>
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
                {(() => {
                  // Déterminer l'URL vidéo finale (priorité: final_video_url > video_urls[0] > clips[0])
                  const finalVideoUrl = 
                    animationResult.final_video_url || 
                    animationResult.result?.final_video_url ||
                    (animationResult.video_urls && animationResult.video_urls[0]) ||
                    (actualClips[0]?.video_url || actualClips[0]?.clip_url);
                  
                  const videoDuration = total_duration || animationResult.duration || animationResult.duration_seconds;
                  
                  if (finalVideoUrl) {
                    return (
                      <div className="video-player">
                        <div className="final-animation">
                          <div className="video-icon">🎬</div>
                          <h3>🎉 {animationResult.title || 'Votre dessin animé est prêt !'}</h3>
                          <p>
                            Animation complète de {formatTime(videoDuration)}.
                            Générée par IA et sauvegardée dans le cloud.
                          </p>
                          
                          {/* LECTEUR VIDÉO UNIQUE */}
                          <SingleVideoPlayer 
                            videoUrl={finalVideoUrl}
                            duration={videoDuration}
                            title={animationResult.title}
                          />
                        </div>
                      </div>
                    );
                  } else if (status === 'completed') {
                    return (
                      <div className="no-video">
                        <div className="no-video-icon">✅</div>
                        <h3>Animation terminée !</h3>
                        <p>
                          Votre animation "{animationResult.theme || 'N/A'}" a été générée avec succès.
                        </p>
                      </div>
                    );
                  } else {
                    return (
                      <div className="no-video">
                        <div className="no-video-icon">⏳</div>
                        <h3>Génération en cours...</h3>
                        <p>La génération de votre dessin animé peut prendre quelques minutes.</p>
                      </div>
                    );
                  }
                })()}
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
                    const clip = actualClips.find(c => c.scene_number === scene.scene_number);
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
                      <span>{totalClips}</span>
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
