import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './ColoringSelector.css';

const ColoringSelector = ({ 
  selectedTheme, 
  setSelectedTheme,
  customColoringTheme,
  setCustomColoringTheme,
  uploadedPhoto,
  setUploadedPhoto,
  withColoredModel,
  setWithColoredModel
}) => {
  const [showCustomTheme, setShowCustomTheme] = useState(false);
  const [showPhotoUpload, setShowPhotoUpload] = useState(false);
  const [uploadPreview, setUploadPreview] = useState(null);

  const themes = [
    { value: 'upload_photo', label: 'Ma Photo', icon: '📸', description: 'Transformez votre photo en coloriage !', special: true },
    { value: 'custom', label: 'Coloriage personnalisé', icon: '✏️', description: 'Créez votre propre thème de coloriage' },
    { value: 'animals', label: 'Animaux', icon: '🐾', description: 'Chats, chiens, lions, éléphants...' },
    { value: 'space', label: 'Espace', icon: '🚀', description: 'Fusées, planètes, astronautes...' },
    { value: 'fairies', label: 'Fées', icon: '🧚', description: 'Fées, licornes, châteaux magiques...' },
    { value: 'superheroes', label: 'Super-héros', icon: '🦸', description: 'Héros masqués, super-pouvoirs...' },
    { value: 'nature', label: 'Nature', icon: '🌺', description: 'Fleurs, arbres, paysages...' },
    { value: 'vehicles', label: 'Véhicules', icon: '🚗', description: 'Voitures, avions, bateaux...' },
    { value: 'robots', label: 'Robots', icon: '🤖', description: 'Robots futuristes, androïdes, mécaniques...' },
    { value: 'princess', label: 'Princesses', icon: '👸', description: 'Princesses, robes, diadèmes...' },
    { value: 'dinosaurs', label: 'Dinosaures', icon: '🦕', description: 'T-Rex, Triceratops, volcans...' }
  ];

  const handleThemeSelect = (themeValue) => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (selectedTheme === themeValue) {
      setSelectedTheme('');
      setShowCustomTheme(false);
      setShowPhotoUpload(false);
    } else {
      setSelectedTheme(themeValue);
      setShowCustomTheme(themeValue === 'custom');
      setShowPhotoUpload(themeValue === 'upload_photo');
    }
  };

  const handlePhotoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Vérifier le type de fichier
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        alert('Format de fichier non supporté. Utilisez JPG, PNG, GIF ou WebP.');
        return;
      }

      // Vérifier la taille (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('La photo est trop grande. Taille maximale : 5 MB');
        return;
      }

      // Créer une preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadPreview(reader.result);
      };
      reader.readAsDataURL(file);

      // Stocker le fichier
      setUploadedPhoto(file);
    }
  };

  const handleModelSelect = (modelValue) => {
    // Toggle: désélectionne si déjà sélectionné, sinon sélectionne
    if (withColoredModel === modelValue) {
      setWithColoredModel(null);
    } else {
      setWithColoredModel(modelValue);
    }
  };

  const removePhoto = () => {
    setUploadedPhoto(null);
    setUploadPreview(null);
    // Réinitialiser l'input file
    const fileInput = document.getElementById('photo-upload-input');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  return (
    <div className="coloring-selector">
      <h3>2. Choisissez un thème pour vos coloriages</h3>
      
      <div className="theme-grid">
        {/* Boutons de thème normaux (sauf upload_photo et custom) */}
        {themes.filter(theme => !theme.special && theme.value !== 'custom').map((theme) => (
          <motion.div
            key={theme.value}
            className={`theme-option ${selectedTheme === theme.value ? 'selected' : ''}`}
            onClick={() => handleThemeSelect(theme.value)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="theme-icon">{theme.icon}</div>
            <div className="theme-info">
              <h4>{theme.label}</h4>
              <p>{theme.description}</p>
            </div>
          </motion.div>
        ))}

        {/* Bouton Ma photo avec sa zone d'upload juste en dessous */}
        <div className="theme-with-input">
          <motion.div
            className={`theme-option photo-upload-option ${selectedTheme === 'upload_photo' ? 'selected' : ''}`}
            onClick={() => handleThemeSelect('upload_photo')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="theme-icon">📸</div>
            <div className="theme-info">
              <h4>Ma Photo</h4>
              <p>Transformez votre photo en coloriage !</p>
            </div>
          </motion.div>

          {/* Upload de photo personnalisée - juste en dessous */}
          {showPhotoUpload && (
            <motion.div
              className="photo-upload-container inline-upload"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
            >
              <div className="upload-section">
                <p className="upload-hint">Formats acceptés : JPG, PNG, GIF, WebP (max 5 MB)</p>

                <input
                  type="file"
                  id="photo-upload-input"
                  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                  onChange={handlePhotoUpload}
                  style={{ display: 'none' }}
                />

                {!uploadPreview ? (
                  <label htmlFor="photo-upload-input" className="upload-button">
                    <span className="upload-icon">📁</span>
                    <span>Choisir une photo</span>
                  </label>
                ) : (
                  <div className="photo-preview-container">
                    <img src={uploadPreview} alt="Aperçu" className="photo-preview" />
                    <button onClick={removePhoto} className="remove-photo-btn">
                      ✕ Supprimer
                    </button>
                  </div>
                )}
              </div>

              {/* Message de confirmation */}
              {uploadPreview && (
                <motion.div
                  className="style-selector"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="conversion-info">
                    <span className="info-icon">✨</span>
                    <p>Votre photo sera automatiquement convertie en coloriage avec des contours nets et propres</p>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </div>

        {/* Bouton Coloriage personnalisé avec sa zone de saisie juste en dessous */}
        <div className="theme-with-input">
          <motion.div
            className={`theme-option custom-coloring ${selectedTheme === 'custom' ? 'selected' : ''}`}
            onClick={() => handleThemeSelect('custom')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="theme-icon">✏️</div>
            <div className="theme-info">
              <h4>Coloriage personnalisé</h4>
              <p>Créez votre propre thème de coloriage</p>
            </div>
          </motion.div>

          {/* Champ personnalisé pour thème custom - juste en dessous */}
          {showCustomTheme && (
            <motion.div
              className="custom-theme-input inline-input"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
            >
              <input
                type="text"
                placeholder="Décrivez votre thème de coloriage personnalisé..."
                value={customColoringTheme}
                onChange={(e) => setCustomColoringTheme(e.target.value)}
                className="custom-input"
              />
            </motion.div>
          )}
        </div>
      </div>

      {/* Section 3 : Choix du modèle coloré */}
      <div className="model-choice-section">
        <h3>3. Voulez-vous un modèle ?</h3>
        <div className="model-buttons">
          <motion.button
            className={`model-btn ${withColoredModel === true ? 'active' : ''}`}
            onClick={() => handleModelSelect(true)}
            whileHover={{ y: -3 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="model-icon">🎨</span>
            <span className="model-label">Avec modèle</span>
            <span className="model-desc">Inclut un exemple coloré en coin</span>
          </motion.button>
          <motion.button
            className={`model-btn ${withColoredModel === false ? 'active' : ''}`}
            onClick={() => handleModelSelect(false)}
            whileHover={{ y: -3 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="model-icon">✏️</span>
            <span className="model-label">Sans modèle</span>
            <span className="model-desc">Coloriage pur, liberté créative</span>
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default ColoringSelector;
