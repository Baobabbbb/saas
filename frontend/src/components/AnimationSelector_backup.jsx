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
  setCustomStory,
  // Nouveau: mode de génération
  generationMode,
  setGenerationMode
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
    { id: '30s', name: '30 secondes', description: 'Animation courte' },
    { id: '1min', name: '1 minute', description: 'Animation standard' },
    { id: '2min', name: '2 minutes', description: 'Animation longue' }
  ];

  const visualStyles = [
    { id: 'cartoon', name: 'Cartoon', description: 'Style dessin animé coloré' },
    { id: 'realistic', name: 'Réaliste', description: 'Style photo-réaliste' },
    { id: 'anime', name: 'Anime', description: 'Style manga japonais' },
    { id: 'disney', name: 'Disney', description: 'Style Disney classique' }
  ];

  const generationModes = [
    { id: 'simple', name: 'Simple', description: 'Génération rapide' },
    { id: 'advanced', name: 'Avancé', description: 'Plus de détails et d\'options' }
  ];

  return (
    <div className="animation-selector">
      {/* Section 2: Sélection du thème */}
      <div className="section">
        <h3>2. Choisissez un thème pour votre dessin animé</h3>
        <div className="theme-grid">
          {animationThemes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''} ${theme.id === 'custom' ? 'custom-animation' : ''}`}
              onClick={() => setSelectedTheme(theme.id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="theme-emoji">{theme.emoji}</div>
              <div className="theme-content">
                <h4>{theme.name}</h4>
                <p>{theme.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {selectedTheme === 'custom' && (
          <motion.div 
            className="custom-story-input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <label>Décrivez votre histoire personnalisée :</label>
            <textarea
              value={customStory}
              onChange={(e) => setCustomStory(e.target.value)}
              placeholder="Ex: Un petit robot qui découvre la magie dans un jardin secret..."
              rows={4}
            />
          </motion.div>
        )}
      </div>

      {/* Section 3: Durée */}
      <div className="section">
        <h3>3. Durée de l'animation</h3>
        <div className="duration-options">
          {durations.map((duration) => (
            <motion.div
              key={duration.id}
              className={`duration-card ${selectedDuration === duration.id ? 'selected' : ''}`}
              onClick={() => setSelectedDuration(duration.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <h4>{duration.name}</h4>
              <p>{duration.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Section 4: Style visuel */}
      <div className="section">
        <h3>4. Style visuel</h3>
        <div className="style-options">
          {visualStyles.map((style) => (
            <motion.div
              key={style.id}
              className={`style-card ${selectedStyle === style.id ? 'selected' : ''}`}
              onClick={() => setSelectedStyle(style.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <h4>{style.name}</h4>
              <p>{style.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Section 5: Mode de génération */}
      <div className="section">
        <h3>5. Mode de génération</h3>
        <div className="generation-options">
          {generationModes.map((mode) => (
            <motion.div
              key={mode.id}
              className={`generation-card ${generationMode === mode.id ? 'selected' : ''}`}
              onClick={() => setGenerationMode(mode.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <h4>{mode.name}</h4>
              <p>{mode.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnimationSelector;
