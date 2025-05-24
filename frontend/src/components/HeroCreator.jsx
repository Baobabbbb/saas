import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './HeroCreator.css';

const HeroCreator = ({ heroName, setHeroName }) => {
  const [selectedAvatar, setSelectedAvatar] = useState(null);
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const fileInputRef = useRef(null);

  const handleAvatarSelect = (avatar) => {
    setSelectedAvatar(avatar);
    setUploadedPhoto(null); // Clear uploaded photo when selecting an avatar
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedPhoto(event.target.result);
        setSelectedAvatar(null); // Clear selected avatar when uploading a photo
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const removePhoto = () => {
    setUploadedPhoto(null);
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
            
            <motion.div 
              className="avatar-upload"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={triggerFileInput}
            >
              <span>+</span>
              <input 
                type="file" 
                ref={fileInputRef}
                onChange={handlePhotoUpload}
                accept="image/*"
                style={{ display: 'none' }}
              />
            </motion.div>
          </div>
          
          {uploadedPhoto && (
            <div className="uploaded-photo-container">
              <div className="uploaded-photo">
                <img src={uploadedPhoto} alt="Photo de l'enfant" />
                <motion.button 
                  className="remove-photo"
                  onClick={removePhoto}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  ✕
                </motion.button>
              </div>
              <p className="photo-caption">Photo téléchargée</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HeroCreator;
