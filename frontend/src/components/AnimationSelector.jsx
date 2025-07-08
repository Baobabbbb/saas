import React from 'react';
import { motion } from 'framer-motion';
import './AnimationSelector.css';

const AnimationSelector = ({ 
  selectedTheme, 
  setSelectedTheme, 
  selectedDuration, 
  setSelectedDuration,
  selectedStyle,
  setSelectedStyle,
  customStory,
  setCustomStory
}) => {
  
  const animationThemes = [
    { id: 'custom', name: 'Dessin animé personnalisé', description: 'Écrivez votre propre histoire', emoji: '✏️' },
    { id: 'espace', name: 'Espace', description: 'Voyages spatiaux', emoji: '🚀' },
    { id: 'ocean', name: 'Océan', description: 'Aventures sous-marines', emoji: '🌊' },
    { id: 'aventure', name: 'Aventure', description: 'Voyages et explorations', emoji: '🗺️' },
    { id: 'animaux', name: 'Animaux', description: 'Histoires d\'animaux mignons', emoji: '🦁' },
    { id: 'magie', name: 'Magie', description: 'Monde magique et sortilèges', emoji: '✨' },
    { id: 'amitie', name: 'Amitié', description: 'Histoires d\'amitié', emoji: '👫' },
    { id: 'foret', name: 'Forêt', description: 'Mystères de la forêt', emoji: '🌲' },
    { id: 'pirates', name: 'Pirates', description: 'Aventures de pirates', emoji: '🏴‍☠️' },
    { id: 'dinosaures', name: 'Dinosaures', description: 'L\'époque des dinosaures', emoji: '🦕' },
    { id: 'conte_fees', name: 'Conte de fées', description: 'Contes classiques revisités', emoji: '🏰' },
    { id: 'superheros', name: 'Super-héros', description: 'Aventures héroïques', emoji: '🦸' }
  ];

  const durations = [
    { value: 10, label: '10 secondes' },
    { value: 30, label: '30 secondes' },
    { value: 60, label: '1 minute' },
    { value: 120, label: '2 minutes' },
    { value: 180, label: '3 minutes' },
    { value: 300, label: '5 minutes' }
  ];

  const visualStyles = [
    { id: 'cartoon', name: 'Cartoon', description: 'Style dessin animé coloré', emoji: '🎨' },
    { id: 'anime', name: 'Anime', description: 'Style manga japonais', emoji: '🇯🇵', useImage: true, imagePath: '/assets/japan-flag.png' },
    { id: 'realistic', name: 'Réaliste', description: 'Style cinématographique', emoji: '🎬' },
    { id: 'pastel', name: 'Pastel', description: 'Couleurs douces et tendres', emoji: '🌸' }
  ];

  // Fonctions de toggle pour désélectionner en recliquant
  const handleThemeSelect = (themeId) => {
    if (selectedTheme === themeId) {
      setSelectedTheme(null); // Désélectionner si déjà sélectionné
    } else {
      setSelectedTheme(themeId); // Sélectionner si pas encore sélectionné
    }
  };

  const handleDurationSelect = (durationValue) => {
    if (selectedDuration === durationValue) {
      setSelectedDuration(null); // Désélectionner si déjà sélectionné
    } else {
      setSelectedDuration(durationValue); // Sélectionner si pas encore sélectionné
    }
  };

  const handleStyleSelect = (styleId) => {
    if (selectedStyle === styleId) {
      setSelectedStyle(null); // Désélectionner si déjà sélectionné
    } else {
      setSelectedStyle(styleId); // Sélectionner si pas encore sélectionné
    }
  };

  return (
    <div className="animation-selector">
      {/* Section 2: Sélection du thème */}
      <div className="selector-section">
        <h4>2. Choisissez un thème pour votre dessin animé</h4>
        <div className="themes-grid">
          {animationThemes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''} ${theme.id === 'custom' ? 'custom-animation' : ''}`}
              onClick={() => handleThemeSelect(theme.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="theme-emoji">{theme.emoji}</div>
              <div className="theme-content">
                <h5>{theme.name}</h5>
                <p>{theme.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {selectedTheme === 'custom' && (
          <motion.div 
            className="custom-story-section"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <h4>Écrivez votre histoire</h4>
            <textarea
              className="custom-story-textarea"
              value={customStory}
              onChange={(e) => setCustomStory(e.target.value)}
              placeholder="Il était une fois... Racontez votre histoire ici. Plus elle est détaillée, plus l'animation sera riche et personnalisée !"
              rows={4}
            />
            <div className="character-count">
              {customStory.length}/500 caractères
            </div>
          </motion.div>
        )}
      </div>

      {/* Section 3: Durée */}
      <div className="selector-section">
        <h4>3. Choisissez la durée de l'animation</h4>
        <div className="duration-options">
          {durations.map((duration) => (
            <motion.div
              key={duration.value}
              className={`duration-option ${selectedDuration === duration.value ? 'selected' : ''}`}
              onClick={() => handleDurationSelect(duration.value)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="duration-label">{duration.label}</div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Section 4: Style visuel */}
      <div className="selector-section">
        <h4>4. Choisissez un style visuel</h4>
        <div className="style-options">
          {visualStyles.map((style) => (
            <motion.div
              key={style.id}
              className={`style-option ${selectedStyle === style.id ? 'selected' : ''}`}
              onClick={() => handleStyleSelect(style.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="style-emoji">
                {style.useImage ? (
                  <img 
                    src={style.imagePath} 
                    alt={style.name} 
                    className="style-flag-image"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                ) : null}
                <span style={{ display: style.useImage ? 'none' : 'block' }}>
                  {style.emoji}
                </span>
              </div>
              <div className="style-content">
                <h5>{style.name}</h5>
                <p>{style.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnimationSelector;
