import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './SeedanceSelector.css';

const SeedanceSelector = ({
  selectedTheme,
  setSelectedTheme,
  selectedDuration,
  setSelectedDuration,
  selectedAgeTarget,
  setSelectedAgeTarget,
  customStory,
  setCustomStory
}) => {
  const [storyLength, setStoryLength] = useState(0);

  // Thèmes éducatifs pour SEEDANCE
  const themes = [
    { id: 'nature', name: 'Nature & Animaux', description: 'Découverte de la nature', emoji: '🌿' },
    { id: 'science', name: 'Sciences', description: 'Expériences et découvertes', emoji: '🔬' },
    { id: 'friendship', name: 'Amitié', description: 'Valeurs sociales', emoji: '👫' },
    { id: 'adventure', name: 'Aventure', description: 'Exploration et courage', emoji: '🗺️' },
    { id: 'creativity', name: 'Créativité', description: 'Arts et imagination', emoji: '🎨' },
    { id: 'emotion', name: 'Émotions', description: 'Gestion des sentiments', emoji: '😊' },
    { id: 'family', name: 'Famille', description: 'Relations familiales', emoji: '👨‍👩‍👧‍👦' },
    { id: 'ecology', name: 'Écologie', description: 'Protection de l\'environnement', emoji: '🌍' }
  ];

  // Tranches d'âge
  const ageTargets = [
    { id: '2-4', name: '2-4 ans', description: 'Tout-petits', emoji: '👶' },
    { id: '3-6', name: '3-6 ans', description: 'Préscolaire', emoji: '🧒' },
    { id: '5-8', name: '5-8 ans', description: 'Primaire', emoji: '👦' },
    { id: '6-10', name: '6-10 ans', description: 'École élémentaire', emoji: '👧' }
  ];

  // Durées adaptées SEEDANCE
  const durations = [
    { id: 30, label: '30 secondes', description: 'Histoire courte', emoji: '⚡' },
    { id: 45, label: '45 secondes', description: 'Format standard', emoji: '⏱️' },
    { id: 60, label: '1 minute', description: 'Histoire développée', emoji: '🎬' },
    { id: 90, label: '1m30', description: 'Format étendu', emoji: '📽️' },
    { id: 120, label: '2 minutes', description: 'Histoire complète', emoji: '🎭' }
  ];

  const handleStoryChange = (e) => {
    const value = e.target.value;
    setCustomStory(value);
    setStoryLength(value.length);
  };

  const handleThemeSelect = (themeId) => {
    setSelectedTheme(themeId);
  };

  const handleAgeTargetSelect = (ageId) => {
    setSelectedAgeTarget(ageId);
  };

  const handleDurationSelect = (durationId) => {
    setSelectedDuration(durationId);
  };

  return (
    <div className="seedance-selector">
      {/* Section Histoire */}
      <div className="selector-section">
        <h4>1. 📖 Racontez votre histoire</h4>
        <motion.div
          className="story-input-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <textarea
            value={customStory}
            onChange={handleStoryChange}
            className="seedance-story-textarea"
            placeholder="Écrivez une histoire éducative pour enfants... 
            
Exemple: 'Un petit hérisson curieux découvre que les déchets dans la forêt font du mal à ses amis les animaux. Il décide d'organiser une grande journée de nettoyage avec tous les habitants de la forêt pour apprendre l'importance de protéger la nature.'"
            rows={5}
            maxLength={500}
          />
          <div className="character-count">
            <span className={storyLength < 50 ? 'count-warning' : storyLength > 450 ? 'count-danger' : 'count-ok'}>
              {storyLength}/500 caractères
            </span>
            {storyLength < 50 && (
              <span className="count-hint">📝 Histoire trop courte (minimum 50 caractères)</span>
            )}
          </div>
        </motion.div>
      </div>

      {/* Section Thème Éducatif */}
      <div className="selector-section">
        <h4>2. 🎯 Choisissez le thème éducatif</h4>
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
      </div>

      {/* Section Tranche d'Âge */}
      <div className="selector-section">
        <h4>3. 👶 Sélectionnez la tranche d'âge</h4>
        <div className="age-targets-grid">
          {ageTargets.map((age) => (
            <motion.div
              key={age.id}
              className={`age-card ${selectedAgeTarget === age.id ? 'selected' : ''}`}
              onClick={() => handleAgeTargetSelect(age.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="age-emoji">{age.emoji}</div>
              <h5>{age.name}</h5>
              <p>{age.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Section Durée */}
      <div className="selector-section">
        <h4>4. ⏱️ Choisissez la durée de l'animation</h4>
        <div className="durations-grid">
          {durations.map((duration) => (
            <motion.div
              key={duration.id}
              className={`duration-card ${selectedDuration === duration.id ? 'selected' : ''}`}
              onClick={() => handleDurationSelect(duration.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="duration-emoji">{duration.emoji}</div>
              <h5>{duration.label}</h5>
              <p>{duration.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Info SEEDANCE */}
      <motion.div 
        className="seedance-info"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="info-header">
          <h4>🚀 Technologie SEEDANCE</h4>
        </div>
        <div className="info-content">
          <p>
            SEEDANCE utilise une intelligence artificielle avancée pour créer automatiquement des dessins animés éducatifs personnalisés :
          </p>
          <ul>
            <li><strong>✨ Génération d'idées</strong> adaptées à l'âge et au thème</li>
            <li><strong>🎬 Création de 3 scènes</strong> visuellement cohérentes</li>
            <li><strong>🎵 Ajout de sons</strong> et effets sonores appropriés</li>
            <li><strong>🎞️ Assemblage automatique</strong> en vidéo finale</li>
          </ul>
          <div className="estimated-time">
            <span className="time-icon">⏰</span>
            <span>Temps de génération estimé: 3-5 minutes</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default SeedanceSelector;
