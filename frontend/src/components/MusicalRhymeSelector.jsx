import React from 'react';
import { motion } from 'framer-motion';
import './MusicalRhymeSelector.css';

const rhymeTypes = [
  {
    id: 'lullaby',
    title: 'Berceuse douce',
    description: 'Une mélodie apaisante pour s\'endormir',
    emoji: '🌙',
    musicStyle: 'gentle lullaby'
  },
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
  }
];

const MusicalRhymeSelector = ({ 
  selectedRhyme, 
  setSelectedRhyme, 
  customRhyme, 
  setCustomRhyme
}) => {
  const handleRhymeSelect = (rhymeId) => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (selectedRhyme === rhymeId) {
      setSelectedRhyme('');
    } else {
      setSelectedRhyme(rhymeId);
    }
  };

  return (
    <div className="musical-rhyme-selector">
      <h3>2. Choisissez un type de comptine</h3>
      
      <div className="rhyme-grid">
        {/* Custom rhyme option first */}
        <div className="rhyme-slot">
          <motion.div
            className={`rhyme-card custom-rhyme ${selectedRhyme === 'custom' ? 'selected' : ''}`}
            onClick={() => handleRhymeSelect('custom')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="rhyme-emoji">✏️</div>
            <h4>Comptine personnalisée</h4>
            <p>Créez votre propre type de comptine unique, en y mettant par exemple le prénom de votre enfant</p>
          </motion.div>

          {/* Zone de saisie pour "Comptine personnalisée" - juste en dessous */}
          {selectedRhyme === 'custom' && (
            <motion.div
              className="custom-rhyme-input inline-input"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
            >
              <textarea
                id="customRhyme"
                value={customRhyme}
                onChange={(e) => setCustomRhyme(e.target.value)}
                placeholder="Décrivez votre type de comptine personnalisée..."
                className="custom-textarea"
              />
            </motion.div>
          )}
        </div>

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
    </div>
  );
};

export default MusicalRhymeSelector;