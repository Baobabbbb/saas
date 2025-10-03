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
  photoStyle,
  setPhotoStyle
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
        {themes.map((theme) => (
          <motion.div
            key={theme.value}
            className={`theme-option ${theme.special ? 'photo-upload-option' : ''} ${theme.value === 'custom' ? 'custom-coloring' : ''} ${selectedTheme === theme.value ? 'selected' : ''}`}
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
      </div>

      {/* Upload de photo personnalisée */}
      {showPhotoUpload && (
        <motion.div
          className="photo-upload-container"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <div className="upload-section">
            <h4>📸 Uploadez votre photo</h4>
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

          {/* Sélection du mode ControlNet */}
          {uploadPreview && (
            <motion.div
              className="style-selector"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <h4>🎨 Mode de conversion</h4>
              <div className="style-options">
                {['canny', 'scribble'].map((mode) => (
                  <button
                    key={mode}
                    className={`style-btn ${photoStyle === mode ? 'selected' : ''}`}
                    onClick={() => setPhotoStyle && setPhotoStyle(mode)}
                  >
                    {mode === 'canny' && '🔍 Canny (Contours nets)'}
                    {mode === 'scribble' && '✏️ Scribble (Croquis)'}
                  </button>
                ))}
              </div>
              <p className="style-description">
                {photoStyle === 'canny' && 'Détection de contours précise - Idéal pour photos détaillées'}
                {photoStyle === 'scribble' && 'Style croquis simplifié - Idéal pour un rendu dessin enfant'}
              </p>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* Champ personnalisé pour thème custom */}
      {showCustomTheme && (
        <motion.div
          className="custom-theme-input"
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
  );
};

export default ColoringSelector;
