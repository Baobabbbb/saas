import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { API_ENDPOINTS } from '../config/api';
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
  characterImage,
  setCharacterImage
}) => {
  
  const [animationThemes, setAnimationThemes] = useState([]);
  const [durations, setDurations] = useState([]);

  // Initialiser directement avec les thèmes (évite les appels API pour garantir l'affichage des nouveaux thèmes) - Build: 2024
  useEffect(() => {
          setAnimationThemes([
      { id: 'custom', name: 'Personnalisé', description: 'Écrivez votre propre histoire', emoji: '✏️' },
          { id: 'space', name: 'Espace', description: 'Voyages spatiaux', emoji: '🚀' },
      { id: 'ocean', name: 'Sous-marin', description: 'Exploration sous-marine', emoji: '🐠' },
          { id: 'nature', name: 'Nature', description: 'Monde naturel', emoji: '🌳' },
          { id: 'adventure', name: 'Aventure', description: 'Voyages et explorations', emoji: '🏰' },
          { id: 'animals', name: 'Animaux', description: 'Histoires d\'animaux mignons', emoji: '🐾' },
          { id: 'magic', name: 'Magie', description: 'Monde magique et sortilèges', emoji: '✨' },
      { id: 'friendship', name: 'Amitié', description: 'Histoires d\'amitié', emoji: '🤝' },
      { id: 'circus', name: 'Cirque', description: 'Spectacle de cirque magique', emoji: '🎪' },
      { id: 'sport', name: 'Sport', description: 'Matchs et compétitions sportives', emoji: '⚽' },
      { id: 'pirate', name: 'Pirates', description: 'Aventures sur les mers', emoji: '🏴‍☠️' },
      { id: 'superhero', name: 'Super-héros', description: 'Sauver le monde', emoji: '🦸' },
      { id: 'dinosaur', name: 'Dinosaures', description: 'Monde préhistorique', emoji: '🦖' },
      { id: 'fairy', name: 'Fées & Princesses', description: 'Contes de fées enchantés', emoji: '🧚' },
      { id: 'robot', name: 'Robots', description: 'Technologie et robots futuristes', emoji: '🤖' }
        ]);
        setDurations([
          { value: 30, label: '30 secondes' },
          { value: 60, label: '1 minute' },
          { value: 120, label: '2 minutes' },
          { value: 180, label: '3 minutes' },
          { value: 240, label: '4 minutes' },
          { value: 300, label: '5 minutes' }
        ]);
  }, []);

  const visualStyles = [
    { id: '3d', name: '3D', description: 'Animation 3D moderne', emoji: '🎭' },
    { id: 'realistic', name: 'Réaliste', description: 'Style cinématographique', emoji: '🎬' },
    { id: 'cartoon', name: 'Cartoon', description: 'Style dessin animé coloré', emoji: '🎨' },
    { id: 'anime', name: 'Anime', description: 'Style manga japonais', emoji: '🇯🇵', useImage: true, imagePath: '/assets/japan-flag.png' }
  ];

  // Fonctions de toggle pour désélectionner en recliquant
  const handleThemeSelect = (themeId) => {
    if (selectedTheme === themeId) {
      setSelectedTheme(null); // Désélectionner si déjà sélectionné
    } else {
      setSelectedTheme(themeId);
    }
  };


  const handleDurationSelect = (duration) => {
    if (selectedDuration === duration) {
      setSelectedDuration(null); // Désélectionner si déjà sélectionné
    } else {
      setSelectedDuration(duration);
    }
  };

  const handleStyleSelect = (styleId) => {
    if (selectedStyle === styleId) {
      setSelectedStyle(null); // Désélectionner si déjà sélectionné
    } else {
      setSelectedStyle(styleId);
    }
  };



  return (
    <div className="animation-selector">
      {/* Section 2: Sélection du thème */}
      <div className="selector-section">
        <h4>2. Choisissez un thème pour votre dessin animé</h4>
        <div className="themes-grid">
          {animationThemes.map((theme) => (
            <div key={theme.id}>
            <motion.div
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

              {/* Encart personnalisé juste en dessous du bouton Personnalisé */}
              {theme.id === 'custom' && selectedTheme === 'custom' && (
          <motion.div 
                  className="custom-theme-input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3 }}
          >
            <textarea
              className="custom-story-textarea"
              value={customStory}
              onChange={(e) => setCustomStory(e.target.value)}
              placeholder="Il était une fois... Racontez votre histoire ici. Plus elle est détaillée, plus l'animation sera riche et personnalisée !"
              rows={4}
            />
          </motion.div>
        )}
      </div>
          ))}
        </div>

      </div>


      {/* Section 2: Durée */}
      <div className="selector-section">
        <h4>2. Choisissez la durée de l'animation</h4>
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

      {/* Section 3: Style visuel */}
      <div className="selector-section">
        <h4>3. Choisissez un style visuel</h4>
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

      {/*
      // Section 4: Personnage principal (optionnel)
      // Conservé en commentaire pour réactivation future
      <div className="selector-section">
        <h4>4. Personnage principal (optionnel)</h4>
        <p className="section-description">
          Uploadez une photo pour créer un personnage personnalisé dans votre dessin animé
        </p>
        
        <div className="character-upload-container">
          {!characterImage ? (
            <motion.label 
              className="character-upload-zone"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                      setCharacterImage(reader.result);
                    };
                    reader.readAsDataURL(file);
                  }
                }}
                style={{ display: 'none' }}
              />
              <div className="upload-icon">📸</div>
              <div className="upload-text">
                <strong>Cliquez pour uploader une photo</strong>
                <span>ou glissez-déposez une image ici</span>
              </div>
            </motion.label>
          ) : (
            <div className="character-preview">
              <img src={characterImage} alt="Personnage" className="character-image" />
              <motion.button
                className="remove-character-btn"
                onClick={() => setCharacterImage(null)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                ✕ Supprimer
              </motion.button>
            </div>
          )}
        </div>
      </div>
      */}
    </div>
  );
};

export default AnimationSelector;
