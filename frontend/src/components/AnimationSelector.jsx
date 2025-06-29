import React from 'react';
import { motion } from 'framer-motion';
import './AnimationSelector.css';

const AnimationSelector = ({ 
  selectedTheme, 
  setSelectedTheme, 
  selectedDuration, 
  setSelectedDuration,
  selectedStyle,
  setSelectedStyle,
  customStory,
  setCustomStory,
  // Nouveau: mode de génération
  generationMode,
  setGenerationMode
}) => {
  
  const animationThemes = [
    { id: 'aventure', name: 'Aventure', description: 'Voyages et explorations', emoji: '🗺️' },
    { id: 'animaux', name: 'Animaux', description: 'Histoires d\'animaux mignons', emoji: '🦁' },
    { id: 'magie', name: 'Magie', description: 'Monde magique et sortilèges', emoji: '✨' },
    { id: 'amitie', name: 'Amitié', description: 'Histoires d\'amitié', emoji: '👫' },
    { id: 'espace', name: 'Espace', description: 'Voyages spatiaux', emoji: '🚀' },
    { id: 'ocean', name: 'Océan', description: 'Aventures sous-marines', emoji: '🌊' },
    { id: 'foret', name: 'Forêt', description: 'Mystères de la forêt', emoji: '🌲' },
    { id: 'pirates', name: 'Pirates', description: 'Aventures de pirates', emoji: '🏴‍☠️' },
    { id: 'dinosaures', name: 'Dinosaures', description: 'L\'époque des dinosaures', emoji: '🦕' },
    { id: 'conte_fees', name: 'Conte de fées', description: 'Contes classiques revisités', emoji: '🏰' },
    { id: 'superheros', name: 'Super-héros', description: 'Aventures héroïques', emoji: '🦸' },
    { id: 'custom', name: 'Histoire personnalisée', description: 'Écrivez votre propre histoire', emoji: '✍️' }
  ];

  const durations = [
    { value: 30, label: '30 secondes', description: 'Court et dynamique' },
    { value: 60, label: '1 minute', description: 'Format idéal' },
    { value: 120, label: '2 minutes', description: 'Histoire développée' },
    { value: 180, label: '3 minutes', description: 'Récit complet' },
    { value: 300, label: '5 minutes', description: 'Long métrage' }
  ];

  const styles = [
    { id: 'cartoon', name: 'Cartoon', description: 'Style dessin animé coloré', emoji: '🎨' },
    { id: 'anime', name: 'Anime', description: 'Style manga japonais', emoji: '🇯🇵' },
    { id: 'realistic', name: 'Réaliste', description: 'Style cinématographique', emoji: '🎬' },
    { id: 'pastel', name: 'Pastel', description: 'Couleurs douces et tendres', emoji: '🌸' }
  ];

  return (
    <div className="animation-selector">
      <h3>🎬 Créer un dessin animé IA</h3>
      
      {/* Sélection du thème */}
      <div className="selector-section">
        <h4>Choisissez un thème d'histoire</h4>
        <div className="themes-grid">
          {animationThemes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
              onClick={() => setSelectedTheme(theme.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 300, damping: 10 }}
            >
              <div className="theme-emoji">{theme.emoji}</div>
              <div className="theme-content">
                <h5>{theme.name}</h5>
                <p>{theme.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Histoire personnalisée */}
      {selectedTheme === 'custom' && (
        <motion.div
          className="custom-story-section"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h4>Écrivez votre histoire</h4>
          <motion.textarea
            value={customStory}
            onChange={(e) => setCustomStory(e.target.value)}
            placeholder="Il était une fois... Racontez votre histoire ici. Plus elle est détaillée, plus l'animation sera riche et personnalisée !"
            rows={4}
            className="custom-story-textarea"
            whileFocus={{ scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          />
          <div className="character-count">
            {customStory.length}/500 caractères
          </div>
        </motion.div>
      )}

      {/* Sélection de la durée */}
      <div className="selector-section">
        <h4>Durée de l'animation</h4>
        <div className="duration-options">
          {durations.map((duration) => (
            <motion.div
              key={duration.value}
              className={`duration-option ${selectedDuration === duration.value ? 'selected' : ''}`}
              onClick={() => setSelectedDuration(duration.value)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 300, damping: 10 }}
            >
              <div className="duration-label">{duration.label}</div>
              <div className="duration-description">{duration.description}</div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Sélection du style visuel */}
      <div className="selector-section">
        <h4>Style visuel</h4>
        <div className="style-options">
          {styles.map((style) => (
            <motion.div
              key={style.id}
              className={`style-option ${selectedStyle === style.id ? 'selected' : ''}`}
              onClick={() => setSelectedStyle(style.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 300, damping: 10 }}
            >
              <div className="style-emoji">{style.emoji}</div>
              <div className="style-content">
                <h5>{style.name}</h5>
                <p>{style.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Sélection du mode de génération */}
      <div className="selector-section">
        <h4>🚀 Mode de génération</h4>
        <div className="mode-options">
          <motion.div
            className={`mode-option ${generationMode === 'demo' ? 'selected' : ''}`}
            onClick={() => setGenerationMode('demo')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          >
            <div className="mode-emoji">🎨</div>
            <div className="mode-content">
              <h5>Mode Démo</h5>
              <p>Génération rapide avec images SVG (gratuit)</p>
              <small>⚡ Idéal pour tester vos histoires</small>
            </div>
          </motion.div>
          
          <motion.div
            className={`mode-option ${generationMode === 'production' ? 'selected' : ''}`}
            onClick={() => setGenerationMode('production')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          >
            <div className="mode-emoji">🎬</div>
            <div className="mode-content">
              <h5>Mode Production</h5>
              <p>Vraies vidéos IA avec SD3-Turbo (crédits requis)</p>
              <small>🎥 Résultat final de qualité professionnelle</small>
            </div>
          </motion.div>
        </div>
        
        {generationMode === 'production' && (
          <motion.div
            className="production-warning"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="warning-content">
              <span className="warning-icon">⚠️</span>
              <div className="warning-text">
                <strong>Mode Production :</strong> Utilise vos crédits Stability AI.
                <br />
                <small>2-5 minutes par clip • Résultats de haute qualité</small>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Informations sur la génération */}
      <div className="generation-info">
        <h4>🤖 Technologie IA</h4>
        <div className="tech-info">
          <div className="tech-item">
            <span className="tech-icon">🧠</span>
            <span>GPT-4o-mini pour l'analyse narrative</span>
          </div>
          <div className="tech-item">
            <span className="tech-icon">🎬</span>
            <span>SD3-Turbo pour la génération vidéo</span>
          </div>
          <div className="tech-item">
            <span className="tech-icon">⚡</span>
            <span>Pipeline optimisée sans CrewAI</span>
          </div>
        </div>
        <p className="generation-note">
          ⏱️ Temps de génération estimé : {Math.ceil(selectedDuration / 30)} à {Math.ceil(selectedDuration / 15)} minutes
        </p>
      </div>
    </div>
  );
};

export default AnimationSelector;
