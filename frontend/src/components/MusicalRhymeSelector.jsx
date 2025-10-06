import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './MusicalRhymeSelector.css';

const rhymeTypes = [
  { 
    id: 'animal', 
    title: 'Comptine animalière', 
    description: 'Une comptine joyeuse avec des animaux et leurs sons', 
    emoji: '🐘',
    musicStyle: 'playful with animal sounds'
  },
  { 
    id: 'counting', 
    title: 'Comptine à compter', 
    description: 'Apprendre les chiffres en chanson', 
    emoji: '🔢',
    musicStyle: 'upbeat educational'
  },
  { 
    id: 'colors', 
    title: 'Comptine des couleurs', 
    description: 'Découvrir les couleurs en musique', 
    emoji: '🌈',
    musicStyle: 'cheerful and colorful'
  },
  { 
    id: 'alphabet', 
    title: 'Comptine de l\'alphabet', 
    description: 'Apprendre les lettres en chantant', 
    emoji: '🔤',
    musicStyle: 'educational and catchy'
  },
  { 
    id: 'family', 
    title: 'Comptine familiale', 
    description: 'Une chanson sur la famille et l\'amour', 
    emoji: '👨‍👩‍👧‍👦',
    musicStyle: 'warm and loving'
  },
  { 
    id: 'nature', 
    title: 'Comptine de la nature', 
    description: 'Explorer les plantes, arbres et fleurs', 
    emoji: '🌳',
    musicStyle: 'peaceful and natural'
  },
  { 
    id: 'seasonal', 
    title: 'Comptine saisonnière', 
    description: 'Célébrer les saisons et leurs merveilles', 
    emoji: '🍂',
    musicStyle: 'festive and warm'
  },
  { 
    id: 'movement', 
    title: 'Comptine de mouvement', 
    description: 'Bouger, sauter et danser en musique', 
    emoji: '💃',
    musicStyle: 'energetic dance rhythm'
  },
  { 
    id: 'emotions', 
    title: 'Comptine des émotions', 
    description: 'Comprendre et exprimer ses sentiments', 
    emoji: '😊',
    musicStyle: 'expressive and gentle'
  },
  { 
    id: 'lullaby', 
    title: 'Berceuse douce', 
    description: 'Une mélodie apaisante pour s\'endormir', 
    emoji: '🌙',
    musicStyle: 'gentle lullaby'
  }
];

const MusicalRhymeSelector = ({ 
  selectedRhyme, 
  setSelectedRhyme, 
  customRhyme, 
  setCustomRhyme
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
              placeholder="Ex: Une comptine sur les planètes du système solaire avec le prénom Lucas..."
              whileFocus={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 10 }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MusicalRhymeSelector;