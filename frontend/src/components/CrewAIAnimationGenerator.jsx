import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CrewAIAnimationGenerator.css';

const CrewAIAnimationGenerator = ({ onSelectionChange }) => {
  const [selectedStyle, setSelectedStyle] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('');
  const [selectedDuration, setSelectedDuration] = useState('');

  // Notifier le parent quand les sélections changent
  const handleStyleChange = (style) => {
    // Déselectionner si on clique sur le même style
    const newStyle = selectedStyle === style ? '' : style;
    setSelectedStyle(newStyle);
    if (onSelectionChange) {
      onSelectionChange({ style: newStyle, theme: selectedTheme, duration: selectedDuration });
    }
  };

  const handleThemeChange = (theme) => {
    // Déselectionner si on clique sur le même thème
    const newTheme = selectedTheme === theme ? '' : theme;
    setSelectedTheme(newTheme);
    if (onSelectionChange) {
      onSelectionChange({ style: selectedStyle, theme: newTheme, duration: selectedDuration });
    }
  };

  const handleDurationChange = (duration) => {
    // Déselectionner si on clique sur la même durée
    const newDuration = selectedDuration === duration ? '' : duration;
    setSelectedDuration(newDuration);
    if (onSelectionChange) {
      onSelectionChange({ style: selectedStyle, theme: selectedTheme, duration: newDuration });
    }
  };
  
  const storyStyles = [
    { 
      id: 'cartoon', 
      name: 'Cartoon 3D', 
      description: 'Style coloré et amusant en 3D',
      emoji: '🎨',
      preview: 'linear-gradient(135deg, #ff6b6b, #4ecdc4)'
    },
    { 
      id: 'watercolor', 
      name: 'Aquarelle', 
      description: 'Style artistique aquarelle',
      emoji: '🖌️',
      preview: 'linear-gradient(135deg, #74b9ff, #0984e3)'
    },
    { 
      id: 'anime', 
      name: 'Anime', 
      description: 'Style anime japonais',
      emoji: '🌸',
      preview: 'linear-gradient(135deg, #fd79a8, #e84393)'
    },
    { 
      id: 'fairy_tale', 
      name: 'Conte Magique', 
      description: 'Style féerique et enchanteur',
      emoji: '✨',
      preview: 'linear-gradient(135deg, #a29bfe, #6c5ce7)'
    }
  ];

  const storyThemes = [
    { 
      id: 'adventure', 
      name: 'Aventure', 
      description: 'Explorations et découvertes',
      emoji: '🗺️'
    },
    { 
      id: 'magic', 
      name: 'Magie', 
      description: 'Monde magique et sortilèges',
      emoji: '✨'
    },
    { 
      id: 'animals', 
      name: 'Animaux', 
      description: 'Animaux et leurs aventures',
      emoji: '🦁'
    },
    { 
      id: 'friendship', 
      name: 'Amitié', 
      description: 'Histoires d\'amitié',
      emoji: '👫'
    },
    { 
      id: 'space', 
      name: 'Espace', 
      description: 'Voyages spatiaux',
      emoji: '🚀'
    },
    { 
      id: 'ocean', 
      name: 'Océan', 
      description: 'Aventures sous-marines',
      emoji: '🌊'
    },
    { 
      id: 'forest', 
      name: 'Forêt', 
      description: 'Mystères de la forêt',
      emoji: '🌲'
    },
    { 
      id: 'pirates', 
      name: 'Pirates', 
      description: 'Aventures de pirates',
      emoji: '🏴‍☠️'
    },
    { 
      id: 'dinosaurs', 
      name: 'Dinosaures', 
      description: 'L\'époque des dinosaures',
      emoji: '🦕'
    },
    { 
      id: 'fairy_tale', 
      name: 'Conte de fées', 
      description: 'Contes classiques revisités',
      emoji: '🏰'
    },
    { 
      id: 'superhero', 
      name: 'Super-héros', 
      description: 'Aventures héroïques',
      emoji: '🦸'
    },
    { 
      id: 'winter', 
      name: 'Hiver', 
      description: 'Magie de l\'hiver',
      emoji: '❄️'
    },
    { 
      id: 'educational', 
      name: 'Éducatif', 
      description: 'Apprentissage ludique',
      emoji: '📚'
    }
  ];

  return (
    <div className="crewai-animation-generator">
      {/* Section Histoire - SUPPRIMÉE */}
      {/* <motion.div 
        className="story-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h3>📖 1. Écrivez votre histoire</h3>
        
        <div className="title-section">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Titre de votre animation (optionnel)"
            className="title-input"
          />
        </div>

        <textarea
          value={story}
          onChange={(e) => setStory(e.target.value)}
          placeholder="Écrivez ici votre histoire pour enfants... 

Ex: Il était une fois un petit lapin qui découvrait un jardin magique. Les fleurs pouvaient chanter et les papillons racontaient des histoires merveilleuses. Un jour, une sombre malédiction menace le jardin et notre héros doit trouver le courage de sauver son monde enchanté..."
          className="story-textarea"
          rows={6}
        />
        {story.length < 20 && story.length > 0 && (
          <span style={{ color: '#ff6b6b', fontSize: '0.8rem' }}>⚠️ L'histoire doit contenir au moins 20 caractères</span>
        )}
      </motion.div> */}

      {/* Section Style */}
      <motion.div 
        className="style-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3>2. Choisissez le style visuel</h3>
        <div className="style-grid">
          {storyStyles.map((style) => (
            <motion.div
              key={style.id}
              className={`style-option ${selectedStyle === style.id ? 'selected' : ''}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleStyleChange(style.id)}
            >
              <div className="style-icon">{style.emoji}</div>
              <div className="style-info">
                <h4 className="section-subtitle">{style.name}</h4>
                <p>{style.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Section Thème */}
      <motion.div 
        className="theme-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3>3. Choisissez le thème</h3>
        <div className="theme-grid">
          {storyThemes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleThemeChange(theme.id)}
            >
              <div className="theme-emoji">{theme.emoji}</div>
              <h4>{theme.name}</h4>
              <p>{theme.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Section Durée */}
      <motion.div 
        className="duration-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h3>4. Choisissez la durée</h3>
        <div className="duration-grid">
          {[
            { id: '10', label: '10 secondes', description: 'Animation courte et rythmée', emoji: '⚡' },
            { id: '30', label: '30 secondes', description: 'Animation équilibrée', emoji: '⏱️' },
            { id: '60', label: '1 minute', description: 'Animation développée', emoji: '🎬' },
            { id: '120', label: '2 minutes', description: 'Histoire complète', emoji: '📽️' },
            { id: '180', label: '3 minutes', description: 'Animation riche', emoji: '🎭' },
            { id: '240', label: '4 minutes', description: 'Récit détaillé', emoji: '📚' },
            { id: '300', label: '5 minutes', description: 'Animation complète', emoji: '🎪' }
          ].map((duration) => (
            <motion.div
              key={duration.id}
              className={`duration-card ${selectedDuration === duration.id ? 'selected' : ''}`}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleDurationChange(duration.id)}
            >
              <div className="duration-emoji">{duration.emoji}</div>
              <h4>{duration.label}</h4>
              <p>{duration.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Section Mode de génération - SUPPRIMÉE */}
      {/* <motion.div 
        className="mode-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h3>🚀 4. Mode de génération</h3>
        <div className="mode-grid">
          {generationModes.map((modeOption) => (
            <motion.div
              key={modeOption.id}
              className={`mode-option ${mode === modeOption.id ? 'selected' : ''}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode(modeOption.id)}
            >
              <span className="mode-emoji">{modeOption.emoji}</span>
              <div className="mode-info">
                <h4>{modeOption.name}</h4>
                <p>{modeOption.description}</p>
                <span className="mode-time">⏱️ {modeOption.time}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div> */}

      {/* Section Options - SUPPRIMÉE */}
      {/* <motion.div 
        className="options-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3>⚙️ 5. Options avancées</h3>
        <div className="options-grid">
          <div className="option-group">
            <label>⏱️ Durée de l'animation</label>
            <select
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
            >
              <option value={30}>30 secondes (3-4 scènes)</option>
              <option value={60}>1 minute (5-6 scènes)</option>
              <option value={120}>2 minutes (8-10 scènes)</option>
              <option value={180}>3 minutes (12-15 scènes)</option>
            </select>
          </div>
          
          <div className="option-group">
            <label>💎 Qualité de génération</label>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
            >
              <option value="fast">Rapide (moins de détails)</option>
              <option value="medium">Standard (équilibré)</option>
              <option value="high">Haute qualité (plus de temps)</option>
            </select>
          </div>
        </div>
      </motion.div> */}
    </div>
  );
};

export default CrewAIAnimationGenerator;
