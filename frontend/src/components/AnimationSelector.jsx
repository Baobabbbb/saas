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
  const [loading, setLoading] = useState(true);

  // Charger les thèmes et durées depuis Animation Studio
  useEffect(() => {
    const loadThemesAndDurations = async () => {
      try {
        setLoading(true);
        const response = await fetch(API_ENDPOINTS.animationThemes);
        const data = await response.json();
        
        if (data.themes) {
          // Convertir les thèmes reçus au format attendu
          const formattedThemes = Object.entries(data.themes).map(([key, theme]) => ({
            id: key,
            name: theme.name,
            description: theme.description,
            emoji: theme.icon
          }));
          
          // Ajouter l'option personnalisée en premier
          setAnimationThemes([
            { id: 'custom', name: 'Dessin animé personnalisé', description: 'Écrivez votre propre histoire', emoji: '✏️' },
            ...formattedThemes
          ]);
        }
        
        if (data.durations) {
          // Convertir les durées au format attendu
          const formattedDurations = data.durations.map(duration => ({
            value: duration,
            label: duration >= 60 ? `${duration / 60} minute${duration > 60 ? 's' : ''}` : `${duration} secondes`
          }));
          setDurations(formattedDurations);
        }
        
      } catch (error) {
        console.error('Erreur lors du chargement des thèmes:', error);
        // Fallback avec thèmes par défaut
        setAnimationThemes([
          { id: 'custom', name: 'Dessin animé personnalisé', description: 'Écrivez votre propre histoire', emoji: '✏️' },
          { id: 'space', name: 'Espace', description: 'Voyages spatiaux', emoji: '🚀' },
          { id: 'nature', name: 'Nature', description: 'Monde naturel', emoji: '🌳' },
          { id: 'adventure', name: 'Aventure', description: 'Voyages et explorations', emoji: '🏰' },
          { id: 'animals', name: 'Animaux', description: 'Histoires d\'animaux mignons', emoji: '🐾' },
          { id: 'magic', name: 'Magie', description: 'Monde magique et sortilèges', emoji: '✨' },
          { id: 'friendship', name: 'Amitié', description: 'Histoires d\'amitié', emoji: '🤝' }
        ]);
        setDurations([
          { value: 30, label: '30 secondes' },
          { value: 60, label: '1 minute' },
          { value: 120, label: '2 minutes' },
          { value: 180, label: '3 minutes' },
          { value: 240, label: '4 minutes' },
          { value: 300, label: '5 minutes' }
        ]);
      } finally {
        setLoading(false);
      }
      
      // Toujours définir les durées par défaut même si l'API fonctionne
      // Au cas où l'API ne retourne pas les durées
      if (durations.length === 0) {
        setDurations([
          { value: 30, label: '30 secondes' },
          { value: 60, label: '1 minute' },
          { value: 120, label: '2 minutes' },
          { value: 180, label: '3 minutes' },
          { value: 240, label: '4 minutes' },
          { value: 300, label: '5 minutes' }
        ]);
      }
    };

    loadThemesAndDurations();
  }, []);

  const visualStyles = [
    { id: '3d', name: '3D', description: 'Animation 3D moderne', emoji: '🎮' },
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


  if (loading) {
    return (
      <div className="animation-selector loading">
        <div className="loading-message">
          <div className="spinner">🎬</div>
          <p>Chargement des thèmes d'animation...</p>
        </div>
      </div>
    );
  }

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

      {/* Section 4: Personnage principal (optionnel) */}
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
    </div>
  );
};

export default AnimationSelector;
