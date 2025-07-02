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
  setCustomMusicStyle,
  fastMode,
  setFastMode
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [showMusicOptions, setShowMusicOptions] = useState(false);

  const handleRhymeSelect = (rhymeId) => {
    setSelectedRhyme(rhymeId);
    if (rhymeId !== 'custom') {
      setShowCustomInput(false);
    }
    // Montrer automatiquement les options musicales si activé
    if (generateMusic) {
      setShowMusicOptions(true);
    }
  };

  const handleCustomSelect = () => {
    setSelectedRhyme('custom');
    setShowCustomInput(true);
    if (generateMusic) {
      setShowMusicOptions(true);
    }
  };

  const handleMusicToggle = (enabled) => {
    setGenerateMusic(enabled);
    setShowMusicOptions(enabled);
    if (!enabled) {
      setMusicStyle('auto');
      setCustomMusicStyle('');
    }
  };

  const handleMusicStyleSelect = (styleId) => {
    setMusicStyle(styleId);
    if (styleId !== 'custom') {
      setCustomMusicStyle('');
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
            {generateMusic && (
              <div className="music-indicator">
                <span className="music-icon">🎵</span>
                <small>{rhyme.musicStyle}</small>
              </div>
            )}
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

      {/* Musical options toggle */}
      <div className="music-toggle-section">
        <h4>🎵 Options musicales</h4>
        <div className="music-toggle">
          <motion.button
            className={`toggle-button ${!generateMusic ? 'active' : ''}`}
            onClick={() => handleMusicToggle(false)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="toggle-icon">📝</span>
            <div className="toggle-content">
              <strong>Paroles seulement</strong>
              <small>Génération rapide, texte uniquement</small>
            </div>
          </motion.button>
          
          <motion.button
            className={`toggle-button ${generateMusic ? 'active' : ''}`}
            onClick={() => handleMusicToggle(true)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="toggle-icon">🎵</span>
            <div className="toggle-content">
              <strong>Comptine musicale</strong>
              <small>Paroles + mélodie avec IA DiffRhythm</small>
            </div>
          </motion.button>
        </div>
      </div>

      {/* Musical style options */}
      <AnimatePresence>
        {showMusicOptions && generateMusic && (
          <motion.div 
            className="music-style-section"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h4>🎨 Style musical</h4>
            <div className="music-style-grid">
              {musicStyles.map((style) => (
                <motion.div
                  key={style.id}
                  className={`music-style-card ${musicStyle === style.id ? 'selected' : ''}`}
                  onClick={() => handleMusicStyleSelect(style.id)}
                  whileHover={{ y: -3 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="style-icon">{style.icon}</div>
                  <h5>{style.name}</h5>
                  <p>{style.description}</p>
                </motion.div>
              ))}
              
              {/* Custom style option */}
              <motion.div
                className={`music-style-card custom-style ${musicStyle === 'custom' ? 'selected' : ''}`}
                onClick={() => handleMusicStyleSelect('custom')}
                whileHover={{ y: -3 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="style-icon">🎛️</div>
                <h5>Style personnalisé</h5>
                <p>Décrivez votre style musical</p>
              </motion.div>
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

            {/* Music generation info */}
            <motion.div 
              className="music-info"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="info-item">
                <span className="info-icon">🤖</span>
                <span>Powered by DiffRhythm AI</span>
              </div>
              <div className="info-item">
                <span className="info-icon">⏱️</span>
                <span>~30-60 secondes de génération</span>
              </div>
              <div className="info-item">
                <span className="info-icon">🎯</span>
                <span>Optimisé pour les enfants</span>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Fast Mode Option (visible quand generateMusic est actif) */}
      <AnimatePresence>
        {generateMusic && (
          <motion.div
            className="fast-mode-section"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            style={{
              marginTop: '1rem',
              padding: '0.75rem',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)',
              border: '1px solid #e1bee7'
            }}
          >
            <h5>⚡ Mode de génération</h5>
            <div className="fast-mode-toggle" style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
              <motion.button
                className={`mode-button ${fastMode ? 'active' : ''}`}
                onClick={() => setFastMode(true)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  flex: 1,
                  padding: '0.5rem',
                  borderRadius: '6px',
                  border: fastMode ? '2px solid #7b1fa2' : '1px solid #ddd',
                  background: fastMode ? '#f3e5f5' : '#fff',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                <div>⚡ <strong>Rapide</strong></div>
                <small>Comptine courte, génération plus rapide</small>
              </motion.button>
              
              <motion.button
                className={`mode-button ${!fastMode ? 'active' : ''}`}
                onClick={() => setFastMode(false)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  flex: 1,
                  padding: '0.5rem',
                  borderRadius: '6px',
                  border: !fastMode ? '2px solid #7b1fa2' : '1px solid #ddd',
                  background: !fastMode ? '#f3e5f5' : '#fff',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                <div>🎭 <strong>Complet</strong></div>
                <small>Comptine élaborée, plus longue</small>
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MusicalRhymeSelector;
