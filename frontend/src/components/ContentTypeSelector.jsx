import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import './ContentTypeSelector.css';
import { getEnabledFeatures, listenForFeatureChanges } from '../services/features';

const ContentTypeSelector = ({ contentType, setContentType }) => {
  const [enabledFeatures, setEnabledFeatures] = useState({});
  const [loading, setLoading] = useState(true);
  const previousAnimationEnabled = useRef(null);

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

      const animationEnabled = !!features.animation?.enabled;

      if (!animationEnabled) {
        const fallbackKey = features.comic?.enabled
          ? 'comic'
          : Object.keys(enabled).find(key => enabled[key].enabled);

        if (fallbackKey) {
          const normalizedFallback = fallbackKey === 'audio' ? 'histoire' : fallbackKey;
          if (contentType !== normalizedFallback) {
            setContentType(normalizedFallback);
          }
        }
      } else if (previousAnimationEnabled.current === false && contentType !== 'animation') {
        setContentType('animation');
      } else if (!enabled[contentType]) {
        const firstEnabled = Object.keys(enabled).find(key => enabled[key].enabled);
        if (firstEnabled) {
          // Toujours utiliser 'histoire' au lieu de 'audio' pour la compatibilité
          const normalizedType = firstEnabled === 'audio' ? 'histoire' : firstEnabled;
          setContentType(normalizedType);
        }
      }

      previousAnimationEnabled.current = animationEnabled;
    });
    
    return cleanup;
  }, [contentType, setContentType]);

  const loadEnabledFeatures = async () => {
    try {
      setLoading(true);
      const features = await getEnabledFeatures();
      
      // Normaliser: si contentType est 'audio', le changer en 'histoire'
      if (contentType === 'audio') {
        setContentType('histoire');
      }
      
      setEnabledFeatures(features);

      const animationEnabled = !!features.animation?.enabled;

      if (!animationEnabled) {
        const fallbackKey = features.comic?.enabled
          ? 'comic'
          : Object.keys(features)[0];

        if (fallbackKey) {
          const normalizedFallback = fallbackKey === 'audio' ? 'histoire' : fallbackKey;
          if (contentType !== normalizedFallback) {
            setContentType(normalizedFallback);
          }
        }
      } else if (contentType !== 'animation') {
        setContentType('animation');
      }

      previousAnimationEnabled.current = animationEnabled;

      if (Object.keys(features).length > 0 && !features[contentType]) {
        const [firstEnabledKey] = Object.keys(features);
        if (firstEnabledKey) {
          const normalizedType = firstEnabledKey === 'audio' ? 'histoire' : firstEnabledKey;
          setContentType(normalizedType);
        }
      }
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
              className={`content-type-option animation-full-width ${contentType === 'animation' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('animation')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
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
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
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
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
            >
              <div className="content-type-icon">🎨</div>
              <div className="content-type-details">
                <h4>Coloriage</h4>
                <p>Créez des dessins à colorier personnalisés en noir et blanc</p>
              </div>
            </motion.div>
          )}

          {(enabledFeatures.histoire || enabledFeatures.audio) && (
            <motion.div
              className={`content-type-option ${contentType === 'histoire' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('histoire')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
            >
              <div className="content-type-icon">📖</div>
              <div className="content-type-details">
                <h4>Histoire</h4>
                <p>Créez une histoire avec possibilité d'ajouter une narration audio</p>
              </div>
            </motion.div>
          )}

          {enabledFeatures.rhyme && (
            <motion.div
              className={`content-type-option ${contentType === 'rhyme' ? 'selected' : ''}`}
              onClick={() => handleContentTypeSelect('rhyme')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
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