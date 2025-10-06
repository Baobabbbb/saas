import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './MusicalRhymeSelector.css';

const rhymeTypes = [
  { 
    id: 'lullaby', 
    title: 'Berceuse musicale', 
    description: 'Une douce berceuse avec mélodie apaisante pour endormir', 
    emoji: '🌙',
    musicStyle: 'gentle lullaby'
  },
  { 
    id: 'counting', 
    title: 'Comptine à compter', 
    description: 'Une comptine rythmée pour apprendre à compter en musique', 
    emoji: '🔢',
    musicStyle: 'upbeat educational'
  },
  { 
    id: 'animal', 
    title: 'Comptine animalière', 
    description: 'Une comptine avec des animaux et leurs sons sur fond musical', 
    emoji: '🐘',
    musicStyle: 'playful with animal sounds'
  },
  { 
    id: 'seasonal', 
    title: 'Comptine saisonnière', 
    description: 'Une comptine festive sur les saisons avec mélodie joyeuse', 
    emoji: '🍂',
    musicStyle: 'festive and warm'
  },
  { 
    id: 'educational', 
    title: 'Comptine éducative', 
    description: 'Une comptine pour apprendre avec musique mnémotechnique', 
    emoji: '🎨',
    musicStyle: 'educational and memorable'
  },
  { 
    id: 'movement', 
    title: 'Comptine de mouvement', 
    description: 'Une comptine énergique pour bouger et danser', 
    emoji: '💃',
    musicStyle: 'energetic dance rhythm'
  }
];

const musicStyles = [
  { id: 'auto', name: 'Style automatique', description: 'Laisse l\'IA choisir le meilleur style', icon: '🤖' },
  { id: 'gentle', name: 'Doux et apaisant', description: 'Mélodie calme et relaxante', icon: '🕊️' },
  { id: 'upbeat', name: 'Rythmé et joyeux', description: 'Tempo enjoué et dynamique', icon: '🎵' },
  { id: 'playful', name: 'Joueur et amusant', description: 'Sons rigolos et interactifs', icon: '🎪' },
  { id: 'educational', name: 'Éducatif', description: 'Mélodie simple et mémorable', icon: '📚' }
];

const MusicalRhymeSelector = ({ 
  selectedRhyme, 
  setSelectedRhyme, 
  customRhyme, 
  setCustomRhyme,
  generateMusic,
  setGenerateMusic,
  musicStyle,
  setMusicStyle,
  customMusicStyle,
  setCustomMusicStyle
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);

  const handleRhymeSelect = (rhymeId) => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (selectedRhyme === rhymeId) {
      setSelectedRhyme('');
      setShowCustomInput(false);
    } else {
      setSelectedRhyme(rhymeId);
      if (rhymeId !== 'custom') {
        setShowCustomInput(false);
      }
    }
  };

  const handleCustomSelect = () => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (selectedRhyme === 'custom') {
      setSelectedRhyme('');
      setShowCustomInput(false);
    } else {
      setSelectedRhyme('custom');
      setShowCustomInput(true);
    }
  };

  const handleMusicStyleSelect = (styleId) => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (musicStyle === styleId) {
      setMusicStyle('');
      setCustomMusicStyle('');
    } else {
      setMusicStyle(styleId);
      if (styleId !== 'custom') {
        setCustomMusicStyle('');
      }
    }
  };

  return (
    <div className="musical-rhyme-selector">
      <h3>2. Choisissez un type de comptine</h3>
      
      <div className="rhyme-grid">
        {/* Custom rhyme option first */}
        <motion.div
          className={`rhyme-card custom-rhyme ${selectedRhyme === 'custom' ? 'selected' : ''}`}
          onClick={handleCustomSelect}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="rhyme-emoji">✏️</div>
          <h4>Comptine personnalisée</h4>
          <p>Créez votre propre type de comptine unique, en y mettant par exemple le prénom de votre enfant</p>
        </motion.div>
        
        {/* Predefined rhymes */}
        {rhymeTypes.map((rhyme) => (
          <motion.div
            key={rhyme.id}
            className={`rhyme-card ${selectedRhyme === rhyme.id ? 'selected' : ''}`}
            onClick={() => handleRhymeSelect(rhyme.id)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="rhyme-emoji">{rhyme.emoji}</div>
            <h4>{rhyme.title}</h4>
            <p>{rhyme.description}</p>
          </motion.div>
        ))}
      </div>

      {/* Custom rhyme input */}
      <AnimatePresence>
        {showCustomInput && (
          <motion.div 
            className="custom-rhyme-input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <label htmlFor="customRhyme">Décrivez votre type de comptine</label>
            <motion.textarea
              id="customRhyme"
              value={customRhyme}
              onChange={(e) => setCustomRhyme(e.target.value)}
              placeholder="Ex: Une comptine sur les planètes du système solaire..."
              whileFocus={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 10 }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Musical style options - Always shown since all rhymes are musical */}
      <motion.div 
        className="music-style-section"
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        transition={{ duration: 0.4 }}
      >
        <h4>3. Choisissez un style musical</h4>
        <div className="music-style-grid">
          {/* Custom style option first */}
          <motion.div
            className={`music-style-card custom-style ${musicStyle === 'custom' ? 'selected' : ''}`}
            onClick={() => handleMusicStyleSelect('custom')}
            whileHover={{ y: -3 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="style-icon">✏️</div>
            <h4>Style personnalisé</h4>
            <p>Décrivez votre style musical</p>
          </motion.div>
          
          {/* Predefined styles */}
          {musicStyles.map((style) => (
            <motion.div
              key={style.id}
              className={`music-style-card ${musicStyle === style.id ? 'selected' : ''}`}
              onClick={() => handleMusicStyleSelect(style.id)}
              whileHover={{ y: -3 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="style-icon">{style.icon}</div>
              <h4>{style.name}</h4>
              <p>{style.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Custom music style input */}
        <AnimatePresence>
          {musicStyle === 'custom' && (
            <motion.div 
              className="custom-music-style-input"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <label htmlFor="customMusicStyle">Décrivez le style musical souhaité</label>
              <motion.textarea
                id="customMusicStyle"
                value={customMusicStyle}
                onChange={(e) => setCustomMusicStyle(e.target.value)}
                placeholder="Ex: Style jazz doux avec piano, tempo lent, ambiance chaleureuse..."
                whileFocus={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300, damping: 10 }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default MusicalRhymeSelector;