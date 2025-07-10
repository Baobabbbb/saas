import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './SeedanceViewer.css';

const SeedanceViewer = ({ seedanceResult, onClose }) => {
  const [activeTab, setActiveTab] = useState('video');
  const [selectedScene, setSelectedScene] = useState(null);

  if (!seedanceResult) return null;

  const {
    video_url,
    scenes = [],
    total_duration,
    generation_time,
    scenes_count,
    metadata = {}
  } = seedanceResult;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const getEducationalIcon = (theme) => {
    const icons = {
      nature: '🌿',
      science: '🔬',
      friendship: '👫',
      adventure: '🗺️',
      creativity: '🎨',
      emotion: '😊',
      family: '👨‍👩‍👧‍👦',
      ecology: '🌍'
    };
    return icons[theme] || '📚';
  };

  return (
    <motion.div
      className="seedance-viewer-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="seedance-viewer"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        transition={{ type: "spring", damping: 20, stiffness: 300 }}
      >
        {/* Header */}
        <div className="viewer-header">
          <h2>🚀 Votre animation SEEDANCE</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Stats rapides */}
        <div className="seedance-stats">
          <div className="stat-item">
            <span className="stat-icon">⏱️</span>
            <span>Durée: {formatTime(total_duration)}</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🎬</span>
            <span>{scenes_count} scènes</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🚀</span>
            <span>Généré en {Math.round(generation_time)}s</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">{getEducationalIcon(metadata.theme)}</span>
            <span>Thème: {metadata.theme}</span>
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
            className={`tab ${activeTab === 'educational' ? 'active' : ''}`}
            onClick={() => setActiveTab('educational')}
          >
            📚 Éducatif
          </button>
          <button
            className={`tab ${activeTab === 'technical' ? 'active' : ''}`}
            onClick={() => setActiveTab('technical')}
          >
            ⚙️ Technique
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
                {video_url ? (
                  <div className="video-player">
                    <div className="seedance-video-container">
                      <video 
                        src={`http://localhost:8000${video_url}`}
                        controls
                        autoPlay
                        muted
                        className="seedance-video"
                      >
                        Votre navigateur ne supporte pas la lecture vidéo.
                      </video>
                    </div>
                    
                    <div className="video-info">
                      <h3>🎉 Votre animation SEEDANCE est prête !</h3>
                      <p>
                        Animation éducative de {formatTime(total_duration)} générée automatiquement 
                        avec la technologie SEEDANCE avancée.
                      </p>
                      
                      <div className="video-actions">
                        <button className="download-btn">
                          📥 Télécharger
                        </button>
                        <button className="share-btn">
                          🔗 Partager
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="no-video">
                    <div className="no-video-icon">🎬</div>
                    <h3>Génération en cours...</h3>
                    <p>
                      Votre animation SEEDANCE est en cours de création.
                      Le processus peut prendre quelques minutes.
                    </p>
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
                  <h4>🎞️ Détail des scènes générées</h4>
                  {scenes.map((scene, index) => (
                    <motion.div
                      key={scene.scene_number}
                      className={`scene-card ${selectedScene === index ? 'selected' : ''}`}
                      onClick={() => setSelectedScene(selectedScene === index ? null : index)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="scene-header">
                        <span className="scene-number">Scène {scene.scene_number}</span>
                        <div className="scene-status">
                          <span className="status-icon success">✅</span>
                          <span className="status-text">{scene.status}</span>
                        </div>
                      </div>
                      <h5>{scene.description}</h5>
                      <div className="scene-duration">
                        Durée: {formatTime(scene.duration)}
                      </div>
                      
                      {selectedScene === index && (
                        <motion.div
                          className="scene-details"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                        >
                          {scene.video_url && (
                            <div className="scene-preview">
                              <video 
                                src={`http://localhost:8000${scene.video_url}`}
                                controls
                                className="scene-video"
                                muted
                              />
                            </div>
                          )}
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'educational' && (
              <motion.div
                key="educational"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="educational-tab"
              >
                <div className="educational-content">
                  <h4>📚 Valeur éducative</h4>
                  
                  <div className="educational-grid">
                    <div className="educational-item">
                      <h5>🎯 Thème principal</h5>
                      <p>{metadata.theme || 'Non spécifié'}</p>
                    </div>
                    
                    <div className="educational-item">
                      <h5>👶 Tranche d'âge</h5>
                      <p>{metadata.age_target || 'Non spécifié'}</p>
                    </div>
                    
                    <div className="educational-item">
                      <h5>🎨 Style pédagogique</h5>
                      <p>{metadata.style || 'Cartoon éducatif'}</p>
                    </div>
                    
                    <div className="educational-item">
                      <h5>💡 Objectifs d'apprentissage</h5>
                      <ul>
                        <li>Développement de l'imagination</li>
                        <li>Apprentissage par l'histoire</li>
                        <li>Sensibilisation au thème choisi</li>
                        <li>Stimulation visuelle et auditive</li>
                      </ul>
                    </div>
                  </div>
                  
                  {metadata.idea && (
                    <div className="story-concept">
                      <h5>📖 Concept de l'histoire</h5>
                      <p>{metadata.idea.Idea || metadata.idea}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {activeTab === 'technical' && (
              <motion.div
                key="technical"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="technical-tab"
              >
                <div className="technical-details">
                  <h4>⚙️ Détails techniques SEEDANCE</h4>
                  
                  <div className="tech-grid">
                    <div className="tech-item">
                      <strong>🧠 IA de génération:</strong>
                      <span>OpenAI GPT-4o-mini</span>
                    </div>
                    
                    <div className="tech-item">
                      <strong>🎬 Moteur vidéo:</strong>
                      <span>Wavespeed AI (ByteDance Seedance)</span>
                    </div>
                    
                    <div className="tech-item">
                      <strong>🔊 Génération audio:</strong>
                      <span>Fal AI (mmaudio-v2)</span>
                    </div>
                    
                    <div className="tech-item">
                      <strong>🎞️ Assemblage:</strong>
                      <span>FFmpeg API (Fal AI)</span>
                    </div>
                    
                    <div className="tech-item">
                      <strong>⏱️ Temps de génération:</strong>
                      <span>{Math.round(generation_time)}s</span>
                    </div>
                    
                    <div className="tech-item">
                      <strong>📊 Statut:</strong>
                      <span className="status success">✅ Succès</span>
                    </div>
                    
                    <div className="tech-item">
                      <strong>🎯 Pipeline:</strong>
                      <span>SEEDANCE Automatisé</span>
                    </div>
                    
                    <div className="tech-item">
                      <strong>📅 Généré le:</strong>
                      <span>{metadata.timestamp || new Date().toLocaleString()}</span>
                    </div>
                  </div>
                  
                  <div className="tech-note">
                    <h5>ℹ️ À propos de SEEDANCE</h5>
                    <p>
                      SEEDANCE est un système d'IA avancé qui automatise entièrement le processus 
                      de création d'animations éducatives. Il combine plusieurs technologies 
                      d'intelligence artificielle pour générer des contenus visuels et sonores 
                      cohérents et adaptés à l'âge des enfants.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default SeedanceViewer;
