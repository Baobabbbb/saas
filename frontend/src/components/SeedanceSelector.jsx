import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './SeedanceSelector.css';

const SeedanceSelector = ({
  selectedTheme,
  setSelectedTheme,
  selectedDuration,
  setSelectedDuration
}) => {
  // Thèmes simplifiés pour génération automatique d'histoires
  const themes = [
    { id: 'space', name: 'Aventure Spatiale', description: 'Explorations dans l\'espace', emoji: '🚀' },
    { id: 'ocean', name: 'Aventures Sous-Marines', description: 'Découvertes océaniques', emoji: '🐠' },
    { id: 'nature', name: 'Merveilles de la Nature', description: 'Écologie et environnement', emoji: '🌿' },
    { id: 'animals', name: 'Royaume des Animaux', description: 'Histoires d\'animaux', emoji: '🦁' },
    { id: 'friendship', name: 'Histoires d\'Amitié', description: 'Relations et entraide', emoji: '👫' },
    { id: 'adventure', name: 'Grande Aventure', description: 'Voyages et explorations', emoji: '🗺️' },
    { id: 'magic', name: 'Monde Magique', description: 'Magie et fantaisie', emoji: '✨' },
    { id: 'learning', name: 'Apprentissage', description: 'Découvertes éducatives', emoji: '📚' }
  ];

  // Durées SEEDANCE selon les spécifications
  const durations = [
    { id: 30, name: '30 secondes', emoji: '⏱️' },
    { id: 60, name: '1 minute', emoji: '📽️' },
    { id: 120, name: '2 minutes', emoji: '🎬' },
    { id: 180, name: '3 minutes', emoji: '🎭' },
    { id: 240, name: '4 minutes', emoji: '�' },
    { id: 300, name: '5 minutes', emoji: '�' }
  ];

  const handleThemeSelect = (themeId) => {
    // Permettre la désélection si on clique sur le thème déjà sélectionné
    if (selectedTheme === themeId) {
      setSelectedTheme(null);
    } else {
      setSelectedTheme(themeId);
    }
  };

  const handleDurationSelect = (durationId) => {
    // Permettre la désélection si on clique sur la durée déjà sélectionnée
    if (selectedDuration === durationId) {
      setSelectedDuration(null);
    } else {
      setSelectedDuration(durationId);
    }
  };

  return (
    <div className="seedance-selector">
      {/* Section Thème */}
      <motion.div 
        className="selector-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h4>2. Choisissez un thème pour votre animation</h4>
        <div className="themes-grid">
          {themes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
              onClick={() => handleThemeSelect(theme.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="theme-emoji">{theme.emoji}</div>
              <h5>{theme.name}</h5>
              <p>{theme.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Section Durée */}
      <motion.div 
        className="selector-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h4>3. Choisissez la durée de l'animation</h4>
        <div className="durations-grid">
          {durations.map((duration) => (
            <motion.div
              key={duration.id}
              className={`duration-card ${selectedDuration === duration.id ? 'selected' : ''}`}
              onClick={() => handleDurationSelect(duration.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <h5>{duration.name}</h5>
            </motion.div>
          ))}
        </div>
      </motion.div>

    </div>
  );
};

export default SeedanceSelector;
