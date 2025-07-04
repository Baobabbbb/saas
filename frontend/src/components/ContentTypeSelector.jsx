import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './ContentTypeSelector.css';
import { getEnabledFeatures } from '../services/features';

const ContentTypeSelector = ({ contentType, setContentType }) => {
  const [enabledFeatures, setEnabledFeatures] = useState({});

  useEffect(() => {
    // Charger les fonctionnalités activées
    setEnabledFeatures(getEnabledFeatures());

    // Écouter les changements de fonctionnalités
    const handleFeaturesUpdate = (event) => {
      setEnabledFeatures(getEnabledFeatures());
      
      // Si la fonctionnalité actuellement sélectionnée est désactivée, 
      // basculer vers la première fonctionnalité disponible
      if (!event.detail[contentType]?.enabled) {
        const firstEnabled = Object.keys(event.detail).find(key => event.detail[key].enabled);
        if (firstEnabled) {
          setContentType(firstEnabled);
        }
      }
    };

    window.addEventListener('featuresUpdated', handleFeaturesUpdate);
    
    return () => {
      window.removeEventListener('featuresUpdated', handleFeaturesUpdate);
    };
  }, [contentType, setContentType]);

  const handleContentTypeSelect = (type) => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (contentType === type) {
      setContentType('');
    } else {
      setContentType(type);
    }
  };
  const hasEnabledFeatures = Object.keys(enabledFeatures).length > 0;
  
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
                <p>Créez une courte histoire à lire ou à écouter pour votre enfant</p>
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
                <p>Créez une comptine avec musique et mélodie personnalisées</p>
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};

export default ContentTypeSelector;
