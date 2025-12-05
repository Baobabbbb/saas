import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL, ANIMATION_API_BASE_URL } from '../config/api';
import { motion, AnimatePresence } from 'framer-motion';
import './AnimationViewer.css';

// Composant pour jouer les clips en séquence fluide (comme un vrai film)
const VideoPlaylist = ({ clips }) => {
  const [currentClipIndex, setCurrentClipIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const videoRef = useRef(null);
  const nextVideoRef = useRef(null);

  const currentClip = clips[currentClipIndex];
  const nextClip = clips[currentClipIndex + 1];
  const videoUrl = currentClip?.video_url || currentClip?.clip_url;
  const nextVideoUrl = nextClip?.video_url || nextClip?.clip_url;

  // Précharger le prochain clip pour transition fluide
  useEffect(() => {
    if (nextVideoUrl && nextVideoRef.current) {
      nextVideoRef.current.src = nextVideoUrl;
      nextVideoRef.current.load();
    }
  }, [currentClipIndex, nextVideoUrl]);

  // Passer au clip suivant automatiquement (transition fluide)
  const handleVideoEnded = () => {
    if (currentClipIndex < clips.length - 1) {
      setIsLoading(true);
      setCurrentClipIndex(prev => prev + 1);
      // Transition rapide
      setTimeout(() => setIsLoading(false), 100);
    } else {
      // Boucle vers le début
      setCurrentClipIndex(0);
    }
  };

  // Jouer le clip quand il change
  useEffect(() => {
    if (videoRef.current && isPlaying) {
      videoRef.current.play().catch(() => {});
    }
  }, [currentClipIndex, isPlaying]);

  // Calculer la durée totale
  const totalDuration = clips.length * 5; // 5 secondes par clip
  const currentTime = currentClipIndex * 5;
  const progressPercent = ((currentClipIndex + 1) / clips.length) * 100;

  if (!videoUrl) {
    return <div className="no-video">Aucune vidéo disponible</div>;
  }

  return (
    <div className="video-playlist" style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
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
          muted={false}
          preload="auto"
          onEnded={handleVideoEnded}
          onCanPlay={() => setIsLoading(false)}
          style={{
            width: '100%',
            height: 'auto',
            aspectRatio: '16/9',
            display: 'block',
            opacity: isLoading ? 0.7 : 1,
            transition: 'opacity 0.2s ease'
          }}
        />
        
        {/* Préchargement du prochain clip (invisible) */}
        <video
          ref={nextVideoRef}
          style={{ display: 'none' }}
          preload="auto"
        />

        {/* Badge de scène */}
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
          🎬 Scène {currentClipIndex + 1}/{clips.length}
        </div>
      </div>

      {/* Barre de progression globale */}
      <div style={{ 
        marginTop: '16px',
        padding: '0 8px'
      }}>
        <div style={{
          height: '6px',
          background: '#e0e0e0',
          borderRadius: '3px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: `${progressPercent}%`,
            background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '3px',
            transition: 'width 0.3s ease'
          }} />
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '8px',
          fontSize: '12px',
          color: '#666'
        }}>
          <span>Durée: ~{totalDuration}s</span>
          <span>Lecture automatique</span>
        </div>
      </div>

      {/* Timeline des scènes */}
      <div style={{ 
        display: 'flex', 
        gap: '4px', 
        marginTop: '16px',
        padding: '8px',
        overflowX: 'auto',
        justifyContent: 'center'
      }}>
        {clips.map((clip, index) => (
          <button
            key={index}
            onClick={() => {
              setCurrentClipIndex(index);
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                videoRef.current.play();
              }
            }}
            style={{
              minWidth: '50px',
              height: '36px',
              borderRadius: '8px',
              border: 'none',
              background: currentClipIndex === index 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                : index < currentClipIndex 
                  ? '#c0c0c0' 
                  : '#e8e8e8',
              color: currentClipIndex === index ? 'white' : '#666',
              cursor: 'pointer',
              fontSize: '11px',
              fontWeight: currentClipIndex === index ? '700' : '500',
              transition: 'all 0.2s ease',
              transform: currentClipIndex === index ? 'scale(1.1)' : 'scale(1)',
              boxShadow: currentClipIndex === index ? '0 4px 12px rgba(102,126,234,0.4)' : 'none'
            }}
          >
            {index + 1}
          </button>
        ))}
      </div>

      {/* Message d'information */}
      <p style={{
        textAlign: 'center',
        color: '#888',
        fontSize: '12px',
        marginTop: '12px'
      }}>
        ▶️ Les scènes se jouent automatiquement en séquence
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
                {hasVideo ? (
                  <div className="video-player">
                    {/* TOUJOURS AFFICHER LES CLIPS EN PLAYLIST */}
                    {actualClips.length > 0 ? (
                      <div className="final-animation">
                        <div className="video-icon">🎬</div>
                        <h3>🎉 {animationResult.title || 'Votre dessin animé est prêt !'}</h3>
                        <p>
                          Animation de {formatTime(total_duration || animationResult.duration)} avec {actualClips.length} scènes.
                          {actualClips.length > 1 && ' Cliquez sur une scène pour la voir.'}
                        </p>
                        
                        {/* LECTEUR VIDÉO AVEC PLAYLIST */}
                        <VideoPlaylist clips={actualClips} />
                      </div>
                    ) : (animationResult.final_video_url || animationResult.result?.final_video_url) ? (
                      <div className="final-animation">
                        <div className="video-icon">🎬</div>
                        <h3>🎉 {animationResult.title || 'Votre dessin animé est prêt !'}</h3>
                        <p>
                          Animation complète de {formatTime(total_duration || animationResult.duration)}.
                        </p>
                        
                        {/* LECTEUR VIDÉO PRINCIPAL (fallback) */}
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
                            onLoadedData={() => {}}
                            onError={(e) => {
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
                          {actualClips.map((clip, index) => {
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
                            {totalClips} scènes illustrées représentant votre histoire.
                            Chaque image correspond à un moment clé de votre récit généré par l'IA.
                          </p>
                        </div>
                      </div>
                      
                      {/* Liste des clips pour les scènes sans image */}
                      {actualClips.filter(clip => clip.status === 'success').length > 0 && (
                        <div className="video-clips-list">
                          <h4>📝 Toutes les scènes générées :</h4>
                          {actualClips.filter(clip => clip.status === 'success').map((clip, index) => (
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
