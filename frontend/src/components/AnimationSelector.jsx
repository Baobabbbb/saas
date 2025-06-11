import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './AnimationSelector.css';

const animationStyles = [
  { 
    id: 'cartoon', 
    name: 'Cartoon', 
    description: 'Style coloré et amusant',
    emoji: '🎨'
  },
  { 
    id: 'fairy_tale', 
    name: 'Conte de fées', 
    description: 'Style féerique et magique',
    emoji: '🏰'
  },
  { 
    id: 'anime', 
    name: 'Anime', 
    description: 'Style anime japonais',
    emoji: '🌸'
  },
  { 
    id: 'realistic', 
    name: 'Réaliste', 
    description: 'Style semi-réaliste',
    emoji: '🎭'
  },
  { 
    id: 'paper_craft', 
    name: 'Papier découpé', 
    description: 'Style papier découpé en relief',
    emoji: '✂️'
  },
  { 
    id: 'watercolor', 
    name: 'Aquarelle', 
    description: 'Style aquarelle artistique',
    emoji: '🖌️'
  }
];

const animationThemes = [
  { 
    id: 'custom', 
    name: 'Thème personnalisé', 
    description: 'Décrivez votre propre thème',
    emoji: '✏️'
  },
  { 
    id: 'adventure', 
    name: 'Aventure', 
    description: 'Explorations et découvertes',
    emoji: '🗺️'
  },
  { 
    id: 'magic', 
    name: 'Magie', 
    description: 'Monde magique et sortilèges',
    emoji: '✨'
  },
  { 
    id: 'animals', 
    name: 'Animaux', 
    description: 'Animaux mignons et leurs aventures',
    emoji: '🦁'
  },
  { 
    id: 'friendship', 
    name: 'Amitié', 
    description: 'Histoires d\'amitié et de solidarité',
    emoji: '👫'
  },
  { 
    id: 'space', 
    name: 'Espace', 
    description: 'Voyages spatiaux et planètes',
    emoji: '🚀'
  },
  { 
    id: 'underwater', 
    name: 'Sous-marin', 
    description: 'Aventures sous l\'océan',
    emoji: '🐠'
  },
  { 
    id: 'forest', 
    name: 'Forêt', 
    description: 'Créatures et mystères de la forêt',
    emoji: '🌲'
  },
  { 
    id: 'superhero', 
    name: 'Super-héros', 
    description: 'Aventures de super-héros enfants',
    emoji: '🦸'
  }
];

const AnimationSelector = ({ 
  selectedAnimationStyle, 
  setSelectedAnimationStyle,
  selectedAnimationTheme,
  setSelectedAnimationTheme,
  customPrompt,
  setCustomPrompt,
  orientation,
  setOrientation,
  uploadedAnimationImage,
  setUploadedAnimationImage
}) => {
  const [showCustomThemeInput, setShowCustomThemeInput] = useState(false);
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const fileInputRef = useRef(null);

  const handleStyleSelect = (styleId) => {
    setSelectedAnimationStyle(styleId);
  };

  const handleThemeSelect = (themeId) => {
    setSelectedAnimationTheme(themeId);
    if (themeId === 'custom') {
      setShowCustomThemeInput(true);
    } else {
      setShowCustomThemeInput(false);
    }
  };
  const handleCustomPromptChange = (e) => {
    setCustomPrompt(e.target.value);
  };
  const handleOrientationSelect = (orientationValue) => {
    setOrientation(orientationValue);
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedPhoto(event.target.result);
        setUploadedAnimationImage(file);
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const removePhoto = () => {
    setUploadedPhoto(null);
    setUploadedAnimationImage(null);
    fileInputRef.current.value = '';
  };

  return (
    <div className="animation-selector">
      {/* Style visuel */}
      <div className="style-selector">
        <h3>2. Choisissez le style visuel</h3>
        <div className="style-options">
          {animationStyles.map((style) => (
            <motion.div
              key={style.id}
              className={`style-option ${selectedAnimationStyle === style.id ? 'selected' : ''}`}
              onClick={() => handleStyleSelect(style.id)}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="style-emoji">{style.emoji}</div>
              <h4 className="style-name">{style.name}</h4>
              <p className="style-description">{style.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Orientation */}
      <div className="orientation-selector">
        <h3>3. Choisissez l'orientation</h3>
        <div className="orientation-options">
          <motion.div
            className={`orientation-option ${orientation === 'landscape' ? 'selected' : ''}`}
            onClick={() => handleOrientationSelect('landscape')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="orientation-icon">📱</div>
            <h4 className="orientation-name">Paysage</h4>
            <p className="orientation-description">Format horizontal (16:9)</p>
          </motion.div>
          
          <motion.div
            className={`orientation-option ${orientation === 'portrait' ? 'selected' : ''}`}
            onClick={() => handleOrientationSelect('portrait')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="orientation-icon">📱</div>
            <h4 className="orientation-name">Portrait</h4>
            <p className="orientation-description">Format vertical (9:16)</p>
          </motion.div>
        </div>
      </div>

      {/* Thème */}
      <div className="theme-selector">
        <h3>4. Choisissez le thème</h3>
        <div className="theme-grid">
          {animationThemes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`theme-card ${theme.id === 'custom' ? 'custom-theme' : ''} ${selectedAnimationTheme === theme.id ? 'selected' : ''}`}
              onClick={() => handleThemeSelect(theme.id)}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="theme-emoji">{theme.emoji}</div>
              <h4>{theme.name}</h4>
              <p>{theme.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Custom theme input */}
        {showCustomThemeInput && (          <motion.div
            className="custom-theme-input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <label htmlFor="customTheme">Décrivez le thème de votre animation</label>
            <motion.textarea
              id="customTheme"
              value={customPrompt}
              onChange={handleCustomPromptChange}
              placeholder="Ex: Un petit chat orange qui découvre un jardin magique plein de papillons colorés..."
              whileFocus={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 10 }}
            />
          </motion.div>
        )}
      </div>

      {/* Personnage principal (optionnel) */}
      <div className="character-selector">
        <h3>5. Personnage principal (optionnel)</h3>
        <p className="character-description">
          Ajoutez une photo pour créer un personnage à votre image dans l'animation
        </p>        <div className="character-upload-section">
          {!uploadedPhoto ? (
            <motion.button
              className="character-upload-button"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={triggerFileInput}
            >
              <span className="upload-icon">📷</span>
              <span>Ajouter une photo</span>
            </motion.button>          ) : (
            <div className="character-preview">
              <div className="preview-image">
                <img src={uploadedPhoto} alt="Personnage principal" />
              </div>
              <p className="preview-text">Votre personnage principal</p>
              <div className="photo-actions">
                <motion.button
                  className="change-photo-btn"
                  onClick={triggerFileInput}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Changer la photo
                </motion.button>
                <motion.button
                  className="remove-photo-btn"
                  onClick={removePhoto}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Supprimer la photo
                </motion.button>
              </div>
            </div>
          )}

          <input
            type="file"
            ref={fileInputRef}
            onChange={handlePhotoUpload}
            accept="image/*"
            style={{ display: 'none' }}
          />
        </div>
      </div>
    </div>
  );
};

export default AnimationSelector;
