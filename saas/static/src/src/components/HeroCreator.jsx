import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './HeroCreator.css';

const HeroCreator = ({
  heroName,
  setHeroName,
  uploadedImage,
  setUploadedImage,
  customPrompt,
  setCustomPrompt
}) => {
  const [selectedAvatar, setSelectedAvatar] = useState(null);
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [showPromptInput, setShowPromptInput] = useState(false);
  const fileInputRef = useRef(null);

  const handleAvatarSelect = (avatar) => {
    setSelectedAvatar(avatar);
    setUploadedPhoto(null);
    setUploadedImage(null);
    // Si on sélectionne un avatar emoji, on masque le prompt input
    setShowPromptInput(false);
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedPhoto(event.target.result);
        setUploadedImage(file);
        setSelectedAvatar(null);
        setShowPromptInput(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const removePhoto = () => {
    setUploadedPhoto(null);
    setUploadedImage(null);
    fileInputRef.current.value = '';
  };

  return (
    <div className="hero-creator">
      <h3>3. Créez votre héros</h3>

      <div className="hero-form">
        <div className="input-group">
          <label htmlFor="heroName">Nom de l'enfant</label>
          <motion.input
            type="text"
            id="heroName"
            value={heroName}
            onChange={(e) => setHeroName(e.target.value)}
            placeholder="Entrez le prénom de votre enfant"
            whileFocus={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          />
        </div>

        <div className="avatar-selector">
          <p>Personnalisez votre héros ou choisissez un avatar</p>

          <div className="avatar-options">
            {/* 1. Bouton upload photo */}
            <motion.div
              className="avatar-upload"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={triggerFileInput}
            >
              <span>+</span>
              <span className="tooltip">Crée un héros à ton image !</span>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handlePhotoUpload}
                accept="image/*"
                style={{ display: 'none' }}
              />
            </motion.div>

            {/* 2. Bouton prompt personnalisé */}
            <motion.div
              className="avatar-prompt"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => {
                setShowPromptInput(true);
                setSelectedAvatar(null);
                setUploadedPhoto(null);
                setUploadedImage(null);
              }}
            >
              <span role="img" aria-label="Créer via prompt">📝</span>
              <span className="tooltip">Décris ton héros !</span>
            </motion.div>

            {/* 3+. Avatars prédéfinis */}
            {['👦', '👧', '👶'].map((avatar, index) => (
              <motion.div
                key={index}
                className={`avatar-option ${selectedAvatar === avatar ? 'selected' : ''}`}
                whileHover={{ scale: 1.2, rotate: 10 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => handleAvatarSelect(avatar)}
              >
                {avatar}
              </motion.div>
            ))}
          </div>

          {/* === Champ de saisie du prompt juste en dessous des boutons === */}
          {showPromptInput && (
            <div className="prompt-encart">
              <input
                type="text"
                className="prompt-input"
                value={customPrompt}
                onChange={e => setCustomPrompt(e.target.value)}
                placeholder="Décris le héros de ton histoire..."
                autoFocus
              />
            </div>
          )}          {/* Affichage de la photo uploadée */}
          {uploadedPhoto && (
            <div className="uploaded-photo-container">
              <div className="uploaded-photo">
                <img src={uploadedPhoto} alt="Photo de l'enfant" />
              </div>
              <p className="photo-caption">Photo téléchargée</p>
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
        </div>
      </div>
    </div>
  );
};

export default HeroCreator;
