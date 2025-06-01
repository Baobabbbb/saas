import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './HeroCreator.css';

const HeroCreator = ({ heroName, setHeroName, uploadedImage, setUploadedImage }) => {
  const [selectedAvatar, setSelectedAvatar] = useState(null);
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const fileInputRef = useRef(null);

  const handleAvatarSelect = (avatar) => {
    setSelectedAvatar(avatar);
    setUploadedPhoto(null);
    setUploadedImage(null); // 🔄 réinitialise l'image réelle
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedPhoto(event.target.result); // preview
        setUploadedImage(file);                // 🧠 envoi au backend
        setSelectedAvatar(null);               // désélectionne l’avatar
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
          <p>Choisissez un avatar ou ajoutez une photo</p>

          <div className="avatar-options">
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

          {uploadedPhoto && (
            <div className="uploaded-photo-container">
              <div className="uploaded-photo">
                <img src={uploadedPhoto} alt="Photo de l'enfant" />
              </div>
                <motion.button
                  className="remove-photo"
                  onClick={removePhoto}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  ✕
                </motion.button>
              <p className="photo-caption">Photo téléchargée</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HeroCreator;
