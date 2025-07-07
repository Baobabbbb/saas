import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './ColoringSelector.css';

const ColoringSelector = ({ 
  selectedTheme, 
  setSelectedTheme,
  customColoringTheme,
  setCustomColoringTheme
}) => {
  const [showCustomTheme, setShowCustomTheme] = useState(false);

  const themes = [
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
    } else {
      setSelectedTheme(themeValue);
      setShowCustomTheme(themeValue === 'custom');
    }
  };

  return (
    <div className="coloring-selector">
      <h3>2. Choisissez un thème pour vos coloriages</h3>
      
      <div className="theme-grid">
        {themes.map((theme) => (
          <motion.div
            key={theme.value}
            className={`theme-option ${theme.value === 'custom' ? 'custom-coloring' : ''} ${selectedTheme === theme.value ? 'selected' : ''}`}
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
