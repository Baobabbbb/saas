import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './ContentTypeSelector.css';
import { getEnabledFeatures, listenForFeatureChanges } from '../services/features';

const ContentTypeSelector = ({ contentType, setContentType }) => {
  const [enabledFeatures, setEnabledFeatures] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Charger les fonctionnalités activées
    loadEnabledFeatures();

    // Écouter les changements de fonctionnalités depuis le panneau
    const cleanup = listenForFeatureChanges(async (features) => {
      
      // Filtrer les fonctionnalités activées
      const enabled = Object.entries(features)
        .filter(([key, feature]) => feature.enabled)
        .reduce((enabled, [key, feature]) => {
          enabled[key] = feature;
          return enabled;
        }, {});
      
      setEnabledFeatures(enabled);
      
      // Si la fonctionnalité actuellement sélectionnée est désactivée, 
      // basculer vers la première fonctionnalité disponible
      if (!enabled[contentType]) {
        const firstEnabled = Object.keys(enabled).find(key => enabled[key].enabled);
        if (firstEnabled) {
          setContentType(firstEnabled);
        }
      }
    });
    
    return cleanup;
  }, [contentType, setContentType]);

  const loadEnabledFeatures = async () => {
    try {
      setLoading(true);
      const features = await getEnabledFeatures();
      setEnabledFeatures(features);
    } catch (error) {
      console.error('Erreur lors du chargement des fonctionnalités:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContentTypeSelect = (type) => {
    // Ne pas permettre la désélection - toujours sélectionner le type choisi
    setContentType(type);
  };
  
  const hasEnabledFeatures = Object.keys(enabledFeatures).length > 0;
  
  if (loading) {
    return (
      <div className="content-type-selector">
        <h3>1. Choisissez le type de contenu</h3>
        <div className="loading-message">
          <p>Chargement des fonctionnalités...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="content-type-selector">
      <h3>1. Choisissez le type de contenu</h3>
      
      {!hasEnabledFeatures ? (
        <div className="no-features-message">
          <p>Aucune fonctionnalité n'est actuellement disponible.</p>
        </div>
      ) : (
        <div className="content-type-options">
          {enabledFeatures.animation && (
            <motion.div
              className={`content-type-option ${contentType === 'animation' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('animation')}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="content-type-icon">🎬</div>
              <div className="content-type-details">
                <h4>Dessin animé</h4>
                <p>Créez un véritable dessin animé fluide et cohérent avec l'IA</p>
              </div>
            </motion.div>
          )}

          {enabledFeatures.comic && (
            <motion.div
              className={`content-type-option ${contentType === 'comic' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('comic')}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="content-type-icon">💬</div>
              <div className="content-type-details">
                <h4>Bande dessinée</h4>
                <p>Créez une vraie BD avec histoire cohérente et bulles de dialogue</p>
              </div>
            </motion.div>
          )}

          {enabledFeatures.coloring && (
            <motion.div
              className={`content-type-option ${contentType === 'coloring' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('coloring')}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="content-type-icon">🎨</div>
              <div className="content-type-details">
                <h4>Coloriage</h4>
                <p>Créez des dessins à colorier personnalisés en noir et blanc</p>
              </div>
            </motion.div>
          )}

          {enabledFeatures.audio && (
            <motion.div
              className={`content-type-option ${contentType === 'audio' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('audio')}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="content-type-icon">📖</div>
              <div className="content-type-details">
                <h4>Histoire</h4>
                <p>Créez une histoire audio avec narration et effets sonores</p>
              </div>
            </motion.div>
          )}

          {enabledFeatures.rhyme && (
            <motion.div
              className={`content-type-option ${contentType === 'rhyme' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('rhyme')}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="content-type-icon">🎵</div>
              <div className="content-type-details">
                <h4>Comptine</h4>
                <p>Créez une comptine musicale avec paroles et mélodie</p>
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};

export default ContentTypeSelector;