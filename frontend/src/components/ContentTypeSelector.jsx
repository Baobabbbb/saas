import React from 'react';
import { motion } from 'framer-motion';
import './ContentTypeSelector.css';

const ContentTypeSelector = ({ contentType, setContentType }) => {
  return (
    <div className="content-type-selector">
      <h3>1. Choisissez le type de contenu</h3>
      
      <div className="content-type-options">
        <motion.div
          className={`content-type-option ${contentType === 'animation' ? 'selected' : ''}`}
          onClick={() => setContentType('animation')}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="content-type-icon">�</div>
          <div className="content-type-details">
            <h4>Dessin animé IA</h4>
            <p>Créez un véritable dessin animé fluide et cohérent avec l'IA</p>
          </div>
        </motion.div>

        <motion.div
          className={`content-type-option ${contentType === 'coloring' ? 'selected' : ''}`}
          onClick={() => setContentType('coloring')}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="content-type-icon">�</div>
          <div className="content-type-details">
            <h4>Coloriage</h4>
            <p>Créez des dessins à colorier personnalisés en noir et blanc</p>
          </div>
        </motion.div>
        
        {/*<motion.div
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
        </motion.div>*/}

        <motion.div
          className={`content-type-option ${contentType === 'audio' ? 'selected' : ''}`}
          onClick={() => setContentType('audio')}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="content-type-icon">📖</div>
          <div className="content-type-details">
            <h4>Histoire</h4>
            <p>Créez une courte histoire à lire ou à écouter pour votre enfant</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ContentTypeSelector;
