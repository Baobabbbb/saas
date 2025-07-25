import React from 'react';
import { motion } from 'framer-motion';
import './GenerateButton.css';

const GenerateButton = ({ onGenerate, isGenerating, isDisabled, contentType }) => {  const getButtonText = () => {
    if (isGenerating) {
      return contentType === 'story' 
        ? 'Création de la BD en cours...' 
        : contentType === 'rhyme'
        ? 'Création de la comptine en cours...'
        : contentType === 'coloring'
        ? 'Création du coloriage en cours...'
        : contentType === 'comic'
        ? 'Création de la BD en cours...'
        : contentType === 'animation'
        ? 'Création du dessin animé en cours...'
        : 'Création du contenu en cours...';
    }
    
    return contentType === 'story' 
      ? 'Créer ma bande dessinée' 
      : contentType === 'rhyme'
      ? 'Créer ma comptine'
      : contentType === 'coloring'
      ? 'Créer mon coloriage'
      : contentType === 'comic'
      ? 'Créer ma bande dessinée'
      : contentType === 'animation'
      ? 'Créer mon dessin animé'
      : contentType === 'audio'
      ? 'Créer mon histoire'
      : 'Créer mon contenu';
  };

  return (
    <div className="generate-button-container">
      <motion.button
        className="generate-button"
        onClick={onGenerate}
        disabled={isDisabled || isGenerating}
        whileHover={!isDisabled && !isGenerating ? { scale: 1.03 } : {}}
        whileTap={!isDisabled && !isGenerating ? { scale: 0.98 } : {}}
        initial={{ opacity: 0.9 }}
        animate={{ 
          opacity: isDisabled ? 0.6 : 1,
          y: [0, isGenerating ? -5 : 0, isGenerating ? 0 : 0]
        }}
        transition={{ 
          duration: isGenerating ? 0.5 : 0.2,
          repeat: isGenerating ? Infinity : 0
        }}
      >
        {isGenerating && (
          <div className="button-loading-dots">
            <div className="button-dot"></div>
            <div className="button-dot"></div>
            <div className="button-dot"></div>
          </div>
        )}
        <span>{getButtonText()}</span>
      </motion.button>
      
      {isDisabled && !isGenerating && (        <p className="generate-button-hint">
          {contentType === 'story' 
            ? 'Veuillez remplir tous les champs requis pour créer votre BD' 
            : contentType === 'rhyme'
            ? 'Veuillez sélectionner un type de comptine pour continuer'
            : contentType === 'coloring'
            ? 'Veuillez sélectionner un thème de coloriage pour continuer'
            : contentType === 'comic'
            ? 'Veuillez sélectionner un thème, style et longueur pour votre BD'
            : contentType === 'animation'
            ? 'Veuillez sélectionner un thème et configurer votre animation'
            : 'Veuillez sélectionner un type d\'histoire (et une voix) pour continuer'}
        </p>
      )}
    </div>
  );
};

export default GenerateButton;
