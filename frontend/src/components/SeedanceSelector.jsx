import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './SeedanceSelector.css';

const SeedanceSelector = ({
  selectedTheme,
  setSelectedTheme,
  selectedDuration,
  setSelectedDuration,
  selectedAgeTarget,
  setSelectedAgeTarget,
  selectedStoryTitle,
  setSelectedStoryTitle
}) => {
  const [availableStories, setAvailableStories] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Charger les histoires depuis l'API
  useEffect(() => {
    const fetchStories = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/seedance/stories');
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des histoires');
        }
        const data = await response.json();
        if (data.status === 'success') {
          setAvailableStories(data.stories);
        } else {
          throw new Error(data.error || 'Erreur lors du chargement des histoires');
        }
      } catch (err) {
        console.error('Erreur chargement histoires:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStories();
  }, []);

  // Thèmes éducatifs pour SEEDANCE (mis à jour selon les histoires disponibles)
  const themes = Object.keys(availableStories).map(themeKey => ({
    id: themeKey,
    name: availableStories[themeKey]?.title || themeKey,
    description: `Histoires sur ${availableStories[themeKey]?.title || themeKey}`,
    emoji: availableStories[themeKey]?.icon || '📚'
  }));

  // Tranches d'âge
  const ageTargets = [
    { id: '2-3 ans', name: '2-3 ans', description: 'Tout-petits', emoji: '👶' },
    { id: '3-5 ans', name: '3-5 ans', description: 'Préscolaire', emoji: '🧒' },
    { id: '5-7 ans', name: '5-7 ans', description: 'Primaire', emoji: '👦' },
    { id: '7-10 ans', name: '7-10 ans', description: 'École élémentaire', emoji: '👧' }
  ];

  // Durées adaptées SEEDANCE
  const durations = [
    { id: 30, label: '30 secondes', description: 'Histoire courte', emoji: '⚡' },
    { id: 45, label: '45 secondes', description: 'Format standard', emoji: '⏱️' },
    { id: 60, label: '1 minute', description: 'Histoire développée', emoji: '🎬' },
    { id: 90, label: '1m30', description: 'Format étendu', emoji: '📽️' },
    { id: 120, label: '2 minutes', description: 'Histoire complète', emoji: '🎭' }
  ];

  const handleThemeSelect = (themeId) => {
    setSelectedTheme(themeId);
    // Reset la sélection d'histoire quand le thème change
    setSelectedStoryTitle(null);
  };

  const handleAgeTargetSelect = (ageId) => {
    setSelectedAgeTarget(ageId);
  };

  const handleDurationSelect = (durationId) => {
    setSelectedDuration(durationId);
  };

  const handleStorySelect = (storyTitle) => {
    setSelectedStoryTitle(storyTitle);
  };

  // Obtenir les histoires du thème sélectionné
  const getStoriesForTheme = () => {
    if (!selectedTheme || !availableStories[selectedTheme]) {
      return [];
    }
    return availableStories[selectedTheme].stories || [];
  };

  if (loading) {
    return (
      <div className="seedance-selector">
        <div className="loading-stories">
          <div className="loading-spinner"></div>
          <p>Chargement des histoires...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="seedance-selector">
        <div className="error-stories">
          <h4>❌ Erreur</h4>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="seedance-selector">
      {/* Section Thème Éducatif */}
      <div className="selector-section">
        <h4>1. 🎯 Choisissez le thème de l'histoire</h4>
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

      {/* Section Sélection d'Histoire */}
      {selectedTheme && (
        <motion.div 
          className="selector-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h4>2. 📖 Sélectionnez une histoire</h4>
          <div className="stories-grid">
            {getStoriesForTheme().map((story, index) => (
              <motion.div
                key={index}
                className={`story-card ${selectedStoryTitle === story.title ? 'selected' : ''}`}
                onClick={() => handleStorySelect(story.title)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <div className="story-header">
                  <h5>{story.title}</h5>
                  <span className="age-badge">{story.age_target}</span>
                </div>
                <p className="story-description">{story.description}</p>
                <div className="story-preview">
                  <em>"{story.story.substring(0, 120)}..."</em>
                </div>
              </motion.div>
            ))}
          </div>
          {getStoriesForTheme().length === 0 && (
            <div className="no-stories">
              <p>Aucune histoire disponible pour ce thème.</p>
            </div>
          )}
        </motion.div>
      )}

      {/* Section Tranche d'Âge */}
      {selectedStoryTitle && (
        <motion.div 
          className="selector-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
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
        </motion.div>
      )}

      {/* Section Durée */}
      {selectedAgeTarget && (
        <motion.div 
          className="selector-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
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
        </motion.div>
      )}

      {/* Info SEEDANCE */}
      {selectedDuration && (
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
              <li><strong>✨ Histoire prédéfinie</strong> adaptée à l'âge et au thème</li>
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
      )}
    </div>
  );
};

export default SeedanceSelector;
