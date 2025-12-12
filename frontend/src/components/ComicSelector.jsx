import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './ComicSelector.css';

const comicThemes = [
  { id: 'custom', name: 'Bande dessinée personnalisée', description: 'Créez votre propre thème', emoji: '✏️' },
  { id: 'space', name: 'Espace', description: 'Voyages spatiaux', emoji: '🚀' },
  { id: 'ocean', name: 'Océan', description: 'Aventures sous-marines', emoji: '🌊' },
  { id: 'adventure', name: 'Aventure', description: 'Exploration et découvertes', emoji: '🗺️' },
  { id: 'animals', name: 'Animaux', description: 'Animaux et leurs aventures', emoji: '🦁' },
  { id: 'magic', name: 'Magie', description: 'Monde magique et sortilèges', emoji: '✨' },
  { id: 'friendship', name: 'Amitié', description: 'Histoires d\'amitié', emoji: '👫' },
  { id: 'forest', name: 'Forêt', description: 'Mystères de la forêt', emoji: '🌲' },
  { id: 'pirates', name: 'Pirates', description: 'Aventures de pirates', emoji: '🏴‍☠️' },
  { id: 'dinosaurs', name: 'Dinosaures', description: 'L\'époque des dinosaures', emoji: '🦕' },
  { id: 'fairy_tale', name: 'Conte de fées', description: 'Contes classiques revisités', emoji: '🏰' },
  { id: 'superhero', name: 'Super-héros', description: 'Aventures héroïques', emoji: '🦸' },
  { id: 'robots', name: 'Robots', description: 'Robots et technologie', emoji: '🤖' },
  { id: 'knights', name: 'Chevaliers', description: 'Châteaux et chevaliers', emoji: '⚔️' },
  { id: 'sports', name: 'Sports', description: 'Aventures sportives', emoji: '⚽' },
  { id: 'music', name: 'Musique', description: 'Concerts et instruments', emoji: '🎵' },
  { id: 'circus', name: 'Cirque', description: 'Spectacles et acrobaties', emoji: '🎪' },
  { id: 'unicorns', name: 'Licornes', description: 'Licornes magiques', emoji: '🦄' },
  { id: 'vehicles', name: 'Véhicules', description: 'Voitures et transports', emoji: '🚗' },
  { id: 'cooking', name: 'Cuisine', description: 'Recettes et pâtisseries', emoji: '🍰' },
  { id: 'garden', name: 'Jardin', description: 'Plantes et fleurs', emoji: '🌻' },
  { id: 'ocean_fr', name: 'Océan', description: 'Aventures sous-marines', emoji: '🌊' },
  { id: 'zoo', name: 'Zoo', description: 'Aventures au zoo', emoji: '🦓' },
  { id: 'party', name: 'Fête', description: 'Anniversaires et célébrations', emoji: '🎉' }
];

const artStyles = [
  { id: 'cartoon', name: 'Cartoon', description: 'Style cartoon coloré et amusant', emoji: '🎨' },
  { id: 'realistic', name: 'Réaliste', description: 'Style réaliste et détaillé', emoji: '📸' },
  { id: 'manga', name: 'Manga', description: 'Style manga japonais', emoji: '🌸' },
  { id: 'comics', name: 'Comics', description: 'Style comics américain', emoji: '💥' },
  { id: 'watercolor', name: 'Aquarelle', description: 'Style aquarelle artistique', emoji: '🖌️' }
];

const characters = [
  { id: 'custom', name: 'Personnalisé', description: 'Décrivez votre personnage', emoji: '✏️', tooltip: 'Personnage personnalisé' },
  { id: 'boy', name: 'Garçon', description: 'Personnage principal garçon', emoji: '👦', tooltip: 'Personnage masculin' },
  { id: 'girl', name: 'Fille', description: 'Personnage principal fille', emoji: '👧', tooltip: 'Personnage féminin' }
];

const ComicSelector = ({
  selectedTheme,
  setSelectedTheme,
  selectedArtStyle,
  setSelectedArtStyle,
  selectedCharacter,
  setSelectedCharacter,
  selectedStoryLength,
  setSelectedStoryLength,
  customRequest,
  setCustomRequest,
  customCharacter,
  setCustomCharacter,
  customComicTheme,
  setCustomComicTheme
}) => {
  const [showCustomTheme, setShowCustomTheme] = useState(false);
  const [showCustomCharacter, setShowCustomCharacter] = useState(false);

  const handleThemeSelect = (themeId) => {
    if (selectedTheme === themeId) {
      // Déselectionner si déjà sélectionné
      setSelectedTheme(null);
      setShowCustomTheme(false);
    } else {
      setSelectedTheme(themeId);
      setShowCustomTheme(themeId === 'custom');
    }
  };

  const handleCharacterSelect = (characterId) => {
    if (selectedCharacter === characterId) {
      // Déselectionner si déjà sélectionné
      setSelectedCharacter(null);
      setShowCustomCharacter(false);
    } else {
      setSelectedCharacter(characterId);
      setShowCustomCharacter(characterId === 'custom');
    }
  };

  const handleArtStyleSelect = (styleId) => {
    if (selectedArtStyle === styleId) {
      // Déselectionner si déjà sélectionné
      setSelectedArtStyle(null);
    } else {
      setSelectedArtStyle(styleId);
    }
  };

  const handleStoryLengthSelect = (lengthId) => {
    if (selectedStoryLength === lengthId) {
      // Déselectionner si déjà sélectionné
      setSelectedStoryLength(null);
    } else {
      setSelectedStoryLength(lengthId);
    }
  };

  return (
    <div className="comic-selector">
      {/* Section Thème */}
      <motion.div 
        className="selector-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h3>2. Choisissez un thème pour votre BD</h3>
        <div className="options-grid">
          {comicThemes.map((theme) => (
            <motion.div
              key={theme.id}
              className={`option-card ${theme.id === 'custom' ? 'custom-comic' : ''} ${selectedTheme === theme.id ? 'selected' : ''}`}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleThemeSelect(theme.id)}
            >
              <div className="option-emoji">{theme.emoji}</div>
              <div className="option-content">
                <h4>{theme.name}</h4>
                <p>{theme.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Champ personnalisé pour thème custom */}
        {showCustomTheme && (
          <motion.div
            className="custom-theme-input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <input
              type="text"
              placeholder="Décrivez votre thème personnalisé..."
              value={customComicTheme}
              onChange={(e) => setCustomComicTheme(e.target.value)}
              className="custom-input"
            />
          </motion.div>
        )}
      </motion.div>

      {/* Section Style Artistique */}
      <motion.div 
        className="selector-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3>3. Choisissez un style artistique</h3>
        <div className="options-grid">
          {artStyles.map((style) => (
            <motion.div
              key={style.id}
              className={`option-card ${selectedArtStyle === style.id ? 'selected' : ''}`}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleArtStyleSelect(style.id)}
            >
              <div className="option-emoji">{style.emoji}</div>
              <div className="option-content">
                <h4>{style.name}</h4>
                <p>{style.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Section Personnage Principal */}
      <motion.div 
        className="selector-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3>4. Choisissez un personnage principal</h3>
        <div className="length-buttons-container">
          {characters.map((character) => (
            <motion.button
              key={character.id}
              className={`length-button-character ${selectedCharacter === character.id ? 'selected' : ''}`}
              data-tooltip={character.tooltip}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleCharacterSelect(character.id)}
            >
              <span className="length-number-character">
                {character.emoji}
              </span>
            </motion.button>
          ))}
        </div>

        {/* Champ personnalisé pour personnage custom */}
        {showCustomCharacter && (
          <motion.div
            className="custom-theme-input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <input
              type="text"
              placeholder="Décrivez votre personnage (âge, apparence, traits)..."
              value={customCharacter}
              onChange={(e) => setCustomCharacter(e.target.value)}
              className="custom-input"
            />
          </motion.div>
        )}
      </motion.div>

      {/* Section Longueur d'Histoire */}
      <motion.div 
        className="selector-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h3>5. Choisissez le nombre d'images</h3>
        <div className="length-buttons-container">
          {[
            { id: '4', number: '4' },
            { id: '8', number: '8' },
            { id: '12', number: '12' },
            { id: '16', number: '16' },
            { id: '20', number: '20' },
            { id: '22', number: '22' }
          ].map((length) => (
            <motion.button
              key={length.id}
              className={`length-button-small ${selectedStoryLength === length.id ? 'selected' : ''}`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleStoryLengthSelect(length.id)}
            >
              <span className="length-number-small">{length.number}</span>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default ComicSelector;
