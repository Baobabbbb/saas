import React from 'react';
import { motion } from 'framer-motion';
import './ColoringSelector.css';

const ColoringSelector = ({ 
  selectedTheme, 
  setSelectedTheme
}) => {
  const themes = [
    { value: 'animals', label: 'Animaux', icon: '🐾', description: 'Chats, chiens, lions, éléphants...' },
    { value: 'space', label: 'Espace', icon: '🚀', description: 'Fusées, planètes, astronautes...' },
    { value: 'fairies', label: 'Fées', icon: '🧚', description: 'Fées, licornes, châteaux magiques...' },
    { value: 'superheroes', label: 'Super-héros', icon: '🦸', description: 'Héros masqués, super-pouvoirs...' },
    { value: 'nature', label: 'Nature', icon: '🌺', description: 'Fleurs, arbres, paysages...' },
    { value: 'vehicles', label: 'Véhicules', icon: '🚗', description: 'Voitures, avions, bateaux...' },
    { value: 'princess', label: 'Princesses', icon: '👸', description: 'Princesses, robes, diadèmes...' },
    { value: 'dinosaurs', label: 'Dinosaures', icon: '🦕', description: 'T-Rex, Triceratops, volcans...' }
  ];

  return (
    <div className="coloring-selector">
      <h3>2. Choisissez un thème pour vos coloriages</h3>
      
      <div className="theme-grid">        {themes.map((theme) => (
          <motion.div
            key={theme.value}
            className={`theme-option ${selectedTheme === theme.value ? 'selected' : ''}`}
            onClick={() => setSelectedTheme(theme.value)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="theme-icon">{theme.icon}</div>
            <div className="theme-info">
              <h4>{theme.label}</h4>
              <p>{theme.description}</p>            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ColoringSelector;
