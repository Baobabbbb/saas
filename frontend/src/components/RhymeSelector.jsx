import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './RhymeSelector.css';

const rhymeTypes = [
  { id: 'lullaby', title: 'Berceuse', description: 'Une douce berceuse pour aider votre enfant à s\'endormir', emoji: '🌙' },
  { id: 'counting', title: 'Comptine à compter', description: 'Une comptine amusante pour apprendre à compter', emoji: '🔢' },
  { id: 'animal', title: 'Comptine animalière', description: 'Une comptine avec des animaux et leurs sons', emoji: '🐘' },
  { id: 'seasonal', title: 'Comptine saisonnière', description: 'Une comptine sur les saisons ou les fêtes', emoji: '🍂' },
  { id: 'educational', title: 'Comptine éducative', description: 'Une comptine pour apprendre les couleurs, formes, etc.', emoji: '🎨' },
  { id: 'movement', title: 'Comptine à gestes', description: 'Une comptine avec des mouvements et des gestes', emoji: '👐' }
];

const RhymeSelector = ({ selectedRhyme, setSelectedRhyme, customRhyme, setCustomRhyme }) => {
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

  const handleCustomRhymeChange = (e) => {
    setCustomRhyme(e.target.value);
  };

  return (
    <div className="rhyme-selector">
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
          <h4>Personnalisé</h4>
          <p>Créez votre propre type de comptine unique</p>
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
      
      {showCustomInput && (
        <motion.div 
          className="custom-rhyme-input"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <label htmlFor="customRhyme">Décrivez votre type de comptine</label>
          <motion.textarea
            id="customRhyme"
            value={customRhyme}
            onChange={handleCustomRhymeChange}
            placeholder="Ex: Une comptine sur les planètes du système solaire..."
            whileFocus={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          />
        </motion.div>
      )}
    </div>
  );
};

export default RhymeSelector;
