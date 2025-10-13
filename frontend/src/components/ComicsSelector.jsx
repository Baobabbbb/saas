import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './ComicsSelector.css';

const ComicsSelector = ({
  selectedTheme,
  setSelectedTheme,
  selectedStyle,
  setSelectedStyle,
  numPages,
  setNumPages,
  customStory,
  setCustomStory,
  characterPhoto,
  setCharacterPhoto,
  onCharacterPhotoUpload
}) => {
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  // Thèmes disponibles
  const themes = [
    { id: 'custom', name: 'Personnalisé', icon: '✨', description: 'Votre propre histoire' },
    { id: 'espace', name: 'Espace', icon: '🚀', description: 'Aventures spatiales' },
    { id: 'pirates', name: 'Pirates', icon: '🏴‍☠️', description: 'Trésors et mers' },
    { id: 'princesses', name: 'Princesses', icon: '👸', description: 'Châteaux magiques' },
    { id: 'dinosaures', name: 'Dinosaures', icon: '🦕', description: 'Monde préhistorique' },
    { id: 'animaux', name: 'Animaux', icon: '🐾', description: 'Animaux mignons' },
    { id: 'superheros', name: 'Super-héros', icon: '🦸', description: 'Pouvoirs incroyables' },
    { id: 'foret', name: 'Forêt Magique', icon: '🌲', description: 'Forêt enchantée' },
    { id: 'ecole', name: 'École', icon: '🎒', description: 'Aventures scolaires' }
  ];

  // Styles artistiques disponibles
  const styles = [
    { id: '3d', name: '3D', icon: '🎭', description: 'Effets 3D modernes' },
    { id: 'cartoon', name: 'Cartoon', icon: '🎨', description: 'Coloré et enfantin' },
    { id: 'manga', name: 'Manga', icon: '🎌', description: 'Style japonais' },
    { id: 'comics', name: 'Comics Marvel', icon: '💥', description: 'Style américain' },
    { id: 'realistic', name: 'Réaliste', icon: '📸', description: 'Détaillé et réaliste' },
    { id: 'watercolor', name: 'Aquarelle', icon: '🖌️', description: 'Doux et artistique' }
  ];

  // Options nombre de pages (4 cases par page)
  const pageOptions = [1, 2, 3, 4, 5];

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingPhoto(true);
    try {
      await onCharacterPhotoUpload(file);
    } catch (error) {
      console.error('Erreur upload:', error);
      alert('Erreur lors de l\'upload de la photo');
    } finally {
      setUploadingPhoto(false);
    }
  };

  return (
    <div className="comics-selector">
      <div className="selector-section">
        <h3>2. Choisissez un thème pour votre bande dessinée</h3>
        <div className="theme-grid">
          {themes.map(theme => (
            <motion.div
              key={theme.id}
              className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''} ${
                theme.id === 'custom' ? 'custom-theme' : ''
              }`}
              onClick={() => setSelectedTheme(selectedTheme === theme.id ? null : theme.id)}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.2 }}
            >
              <div className="theme-icon">{theme.icon}</div>
              <div className="theme-name">{theme.name}</div>
              <div className="theme-description">{theme.description}</div>
            </motion.div>
          ))}
        </div>

          {selectedTheme === 'custom' && (
          <div className="custom-input-container">
            <textarea
              className="custom-story-input"
              placeholder="Décrivez votre histoire personnalisée... (ex: Une petite fille qui découvre un monde magique dans son jardin)"
              value={customStory}
              onChange={(e) => setCustomStory(e.target.value)}
              rows={3}
            />
          </div>
        )}
      </div>

      <div className="selector-section">
        <h3>3. Choisissez un style de dessin</h3>
        <div className="style-grid">
          {styles.map(style => (
            <motion.div
              key={style.id}
              className={`style-card ${selectedStyle === style.id ? 'selected' : ''}`}
              onClick={() => setSelectedStyle(selectedStyle === style.id ? null : style.id)}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.2 }}
            >
              <div className="style-icon">{style.icon}</div>
              <div className="style-name">{style.name}</div>
              <div className="style-description">{style.description}</div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="selector-section">
        <h3>4. Nombre de pages</h3>
        <div className="pages-selector">
          {pageOptions.map(num => (
            <motion.button
              key={num}
              className={`page-btn ${numPages === num ? 'selected' : ''}`}
              onClick={() => setNumPages(numPages === num ? null : num)}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.2 }}
            >
              {num} {num === 1 ? 'page' : 'pages'}
              <span className="cases-info">({num * 4} cases)</span>
            </motion.button>
          ))}
        </div>
      </div>

      <div className="selector-section">
        <h3>5. Personnage principal (optionnel)</h3>
        <div className="character-upload-section">
          <p className="character-description">
            Uploadez une photo pour créer un personnage ressemblant ! L'IA analysera la photo et créera un personnage de BD similaire.
          </p>
          
          <div className="upload-area">
            <input
              type="file"
              id="character-photo-upload"
              accept="image/*"
              onChange={handleFileUpload}
              className="file-input"
              disabled={uploadingPhoto}
            />
            {!characterPhoto && (
              <label htmlFor="character-photo-upload" className="upload-label">
                {uploadingPhoto ? (
                  <div className="uploading-state">
                    <div className="spinner"></div>
                    <span>Upload en cours...</span>
                  </div>
                ) : (
                  <div className="upload-prompt">
                    <span className="upload-icon">📸</span>
                    <span>Cliquez pour uploader une photo</span>
                    <span className="upload-hint">PNG, JPG, WEBP jusqu'à 10MB</span>
                  </div>
                )}
              </label>
            )}
          </div>

          {characterPhoto && (
            <div className="photo-preview">
              <img src={characterPhoto.url} alt="Personnage uploadé" />
              <div className="photo-actions">
                <button
                  className="change-photo-btn"
                  onClick={() => document.getElementById('character-photo-upload').click()}
                >
                  📷 Changer
                </button>
                <button
                  className="remove-photo-btn"
                  onClick={() => setCharacterPhoto(null)}
                >
                  ✕ Retirer
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComicsSelector;
