import React from 'react';
import { motion } from 'framer-motion';
import './ContentTypeSelector.css';

const ContentTypeSelector = ({ contentType, setContentType }) => {
  return (
    <div className="content-type-selector">
      <h3>1. Choisissez le type de contenu</h3>
      
      <div className="content-type-options">
        <motion.div
          className={`content-type-option ${contentType === 'story' ? 'selected' : ''}`}
          onClick={() => setContentType('story')}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="content-type-icon">📚</div>
          <div className="content-type-details">
            <h4>Histoire</h4>
            <p>Créez une bande dessinée avec des personnages et une aventure</p>
          </div>
        </motion.div>
        
        <motion.div
          className={`content-type-option ${contentType === 'rhyme' ? 'selected' : ''}`}
          onClick={() => setContentType('rhyme')}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="content-type-icon">🎵</div>
          <div className="content-type-details">
            <h4>Comptine</h4>
            <p>Créez une comptine ou berceuse personnalisée pour votre enfant</p>
          </div>
        </motion.div>

        <motion.div
          className={`content-type-option ${contentType === 'audio' ? 'selected' : ''}`}
          onClick={() => setContentType('audio')}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="content-type-icon">🎧</div>
          <div className="content-type-details">
            <h4>Conte Audio</h4>
            <p>Créez un court conte audio narré pour votre enfant</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ContentTypeSelector;
