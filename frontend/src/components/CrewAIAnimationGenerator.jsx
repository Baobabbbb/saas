import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CrewAIAnimationGenerator.css';

const CrewAIAnimationGenerator = ({ onGenerate, isGenerating }) => {
  const [story, setStory] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('cartoon');
  const [selectedTheme, setSelectedTheme] = useState('adventure');
  const [duration, setDuration] = useState(60); // en secondes
  const [quality, setQuality] = useState('medium');
  const [title, setTitle] = useState('');
  const [mode, setMode] = useState('complete'); // complete, fast, cohesive
  
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
      id: 'educational', 
      name: 'Éducatif', 
      description: 'Apprentissage ludique',
      emoji: '📚'
    }
  ];

  const generationModes = [
    {
      id: 'complete',
      name: 'Complet',
      description: 'Analyse narrative complète avec 5 agents CrewAI',
      time: '5-10 min',
      emoji: '🎬'
    },
    {
      id: 'fast',
      name: 'Rapide',
      description: 'Génération optimisée (3-4 scènes)',
      time: '2-5 min',
      emoji: '⚡'
    },
    {
      id: 'cohesive',
      name: 'Cohérent',
      description: 'Focus sur la continuité visuelle',
      time: '7-12 min',
      emoji: '🎭'
    }
  ];

  const handleGenerate = () => {
    if (!story.trim()) {
      alert('Veuillez entrer une histoire');
      return;
    }

    if (story.length < 20) {
      alert('L\'histoire doit contenir au moins 20 caractères');
      return;
    }

    const generationData = {
      story: story.trim(),
      style_preferences: {
        style: selectedStyle,
        theme: selectedTheme,
        quality: quality,
        target_age: '3-8 ans',
        mode: mode
      },
      duration: duration,
      title: title.trim() || undefined,
      generation_mode: mode
    };

    onGenerate(generationData);
  };

  const exampleStories = [
    {
      title: "Le Petit Dragon Courageux",
      story: "Il était une fois un petit dragon qui avait peur de voler. Un jour, il découvre qu'un village est en danger et qu'il est le seul à pouvoir aider. Grâce à l'encouragement de ses amis, il trouve le courage de déployer ses ailes et devient le héros du village."
    },
    {
      title: "Luna et l'Étoile Perdue",
      story: "Luna, une petite fille curieuse, remarque qu'une étoile a disparu du ciel. Elle entreprend un voyage magique à travers les nuages pour la retrouver. En chemin, elle rencontre des créatures fantastiques qui l'aident dans sa quête et apprend l'importance de l'entraide."
    },
    {
      title: "Le Jardin Secret de Grand-mère",
      story: "Maxime découvre le jardin secret de sa grand-mère où les fleurs peuvent parler et les papillons racontent des histoires. Quand les plantes commencent à faner, Maxime doit résoudre le mystère et sauver ce monde merveilleux avec l'aide de ses nouveaux amis magiques."
    }
  ];

  const loadExampleStory = (example) => {
    setStory(example.story);
    setTitle(example.title);
  };

  return (
    <div className="crewai-animation-generator">
      {/* Section Histoire */}
      <motion.div 
        className="story-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h3>📖 1. Écrivez votre histoire</h3>
        
        {/* Titre */}
        <div className="title-section">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Titre de votre animation (optionnel)"
            className="title-input"
          />
        </div>

        {/* Histoire */}
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
      </motion.div>

      {/* Section Style */}
      <motion.div 
        className="style-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3>🎨 2. Choisissez le style visuel</h3>
        <div className="style-grid">
          {storyStyles.map((style) => (
            <motion.div
              key={style.id}
              className={`style-option ${selectedStyle === style.id ? 'selected' : ''}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedStyle(style.id)}
            >
              <div className="style-icon">{style.emoji}</div>
              <div className="style-info">
                <h4>{style.name}</h4>
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
        <h3>🌟 3. Choisissez le thème</h3>
        <div className="theme-grid">
          {storyThemes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`theme-option ${selectedTheme === theme.id ? 'selected' : ''}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedTheme(theme.id)}
            >
              <div className="theme-icon">{theme.emoji}</div>
              <div className="theme-info">
                <h4>{theme.name}</h4>
                <p>{theme.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Section Mode de génération */}
      <motion.div 
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
      </motion.div>

      {/* Section Options */}
      <motion.div 
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
      </motion.div>

      {/* Bouton de génération */}
      <motion.div 
        className="generate-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <motion.button
          className={`generate-btn ${isGenerating ? 'generating' : ''}`}
          onClick={handleGenerate}
          disabled={isGenerating || !story.trim() || story.length < 20}
          whileHover={{ scale: isGenerating ? 1 : 1.05 }}
          whileTap={{ scale: isGenerating ? 1 : 0.98 }}
        >
          {isGenerating ? (
            <>
              <div className="loading-spinner"></div>
              Génération en cours...
            </>
          ) : (
            <>
              🎬 Créer l'Animation
            </>
          )}
        </motion.button>

        {mode === 'complete' && (
          <div className="generation-info">
            <p>🤖 <strong>Pipeline CrewAI complet :</strong></p>
            <ul>
              <li>🧩 Scénariste : Découpage en scènes</li>
              <li>🎨 Directeur Artistique : Style et cohérence</li>
              <li>🧠 Prompt Engineer : Optimisation IA</li>
              <li>📡 Opérateur Technique : Génération vidéo</li>
              <li>🎬 Monteur : Assemblage final</li>
            </ul>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default CrewAIAnimationGenerator;
