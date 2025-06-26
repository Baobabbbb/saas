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
      <div className="generator-header">
        <h2>🎬 Créateur d'Animation Narrative</h2>
        <p>Générez des dessins animés complets avec l'intelligence artificielle CrewAI</p>
      </div>

      <div className="generator-content">
        {/* Story Input Section */}
        <motion.div 
          className="story-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h3>📖 Votre Histoire</h3>
          
          {/* Example Stories */}
          <div className="example-stories">
            <p>💡 Exemples d'histoires :</p>
            <div className="examples-grid">
              {exampleStories.map((example, index) => (
                <motion.div
                  key={index}
                  className="example-card"
                  whileHover={{ scale: 1.02 }}
                  onClick={() => loadExampleStory(example)}
                >
                  <h4>{example.title}</h4>
                  <p>{example.story.substring(0, 100)}...</p>
                  <button className="load-example">Utiliser cet exemple</button>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Title Input */}
          <div className="input-group">
            <label>🏷️ Titre (optionnel)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Les Aventures de Luna"
              className="title-input"
            />
          </div>

          {/* Story Textarea */}
          <div className="input-group">
            <label>
              ✍️ Histoire complète 
              <span className="char-count">({story.length} caractères)</span>
            </label>
            <textarea
              value={story}
              onChange={(e) => setStory(e.target.value)}
              placeholder="Écrivez ici votre histoire pour enfants... 

Ex: Il était une fois un petit lapin qui découvrait un jardin magique. Les fleurs pouvaient chanter et les papillons racontaient des histoires merveilleuses. Un jour, une sombre malédiction menace le jardin et notre héros doit trouver le courage de sauver son monde enchanté..."
              className="story-textarea"
              rows={8}
            />
            {story.length < 20 && story.length > 0 && (
              <span className="validation-warning">⚠️ L'histoire doit contenir au moins 20 caractères</span>
            )}
          </div>
        </motion.div>

        {/* Style Selection */}
        <motion.div 
          className="style-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3>🎨 Style Visuel</h3>
          <div className="styles-grid">
            {storyStyles.map((style) => (
              <motion.div
                key={style.id}
                className={`style-card ${selectedStyle === style.id ? 'selected' : ''}`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedStyle(style.id)}
              >
                <div 
                  className="style-preview"
                  style={{ background: style.preview }}
                >
                  <span className="style-emoji">{style.emoji}</span>
                </div>
                <div className="style-info">
                  <h4>{style.name}</h4>
                  <p>{style.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Theme Selection */}
        <motion.div 
          className="theme-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3>🌟 Thème</h3>
          <div className="themes-grid">
            {storyThemes.map((theme) => (
              <motion.div
                key={theme.id}
                className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedTheme(theme.id)}
              >
                <span className="theme-emoji">{theme.emoji}</span>
                <div className="theme-info">
                  <h4>{theme.name}</h4>
                  <p>{theme.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Generation Mode */}
        <motion.div 
          className="mode-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3>🚀 Mode de Génération</h3>
          <div className="modes-grid">
            {generationModes.map((modeOption) => (
              <motion.div
                key={modeOption.id}
                className={`mode-card ${mode === modeOption.id ? 'selected' : ''}`}
                whileHover={{ scale: 1.05 }}
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

        {/* Advanced Settings */}
        <motion.div 
          className="settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3>⚙️ Paramètres Avancés</h3>
          
          <div className="settings-grid">
            <div className="setting-group">
              <label>⏱️ Durée cible</label>
              <input
                type="range"
                min="30"
                max="300"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="duration-slider"
              />
              <span className="duration-display">{duration} secondes ({Math.floor(duration/60)}min {duration%60}s)</span>
            </div>

            <div className="setting-group">
              <label>💎 Qualité</label>
              <select
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                className="quality-select"
              >
                <option value="fast">Rapide (moins de détails)</option>
                <option value="medium">Standard (équilibré)</option>
                <option value="high">Haute qualité (plus de temps)</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Generate Button */}
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
    </div>
  );
};

export default CrewAIAnimationGenerator;
