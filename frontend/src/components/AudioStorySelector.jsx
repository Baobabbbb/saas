import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './AudioStorySelector.css';

const audioStories = [
  { id: 'magic', title: 'Monde magique', description: 'Fées, sorciers, créatures enchantées', emoji: '🧚‍♀️' },
  { id: 'dinosaurs', title: 'Temps des dinosaures', description: 'Dinosaures gentils, voyages dans le temps', emoji: '🦕' },
  { id: 'space', title: 'Voyage spatial', description: 'Planètes, fusées, aliens sympathiques', emoji: '🚀' },
  { id: 'adventure', title: 'Aventure fantastique', description: 'Rebondissements, magie, découvertes', emoji: '✨' },
  { id: 'animals', title: 'Amis animaux', description: 'Animaux qui parlent, aventures sauvages', emoji: '🦊' },
  { id: 'underwater', title: 'Monde sous-marin', description: 'Océans, créatures marines, trésors', emoji: '🐠' },
  { id: 'forest', title: 'Forêt enchantée', description: 'Forêt mystérieuse, surprises magiques', emoji: '🌲' },
  { id: 'funny', title: 'Histoire drôle', description: 'Contes amusants, rires garantis', emoji: '😄' },
  { id: 'mystery', title: 'Petit mystère', description: 'Énigmes pour enfants, investigations', emoji: '🔍' },
  { id: 'friendship', title: 'Belle amitié', description: 'Histoire sur l\'amitié, entraide', emoji: '👫' },
  { id: 'learning', title: 'Conte éducatif', description: 'Leçons importantes, apprentissage', emoji: '📚' },
  { id: 'bedtime', title: 'Histoire du soir', description: 'Contes apaisants, sommeil doux', emoji: '🌙' },
  { id: 'robots', title: 'Robots amis', description: 'Robots gentils, inventions magiques', emoji: '🤖' },
  { id: 'pirates', title: 'Pirates courageux', description: 'Bateaux pirates, trésors cachés', emoji: '🏴‍☠️' }
];

const voices = [
  { id: 'female', name: 'Voix féminine' },
  { id: 'male', name: 'Voix masculine' }
];

const AudioStorySelector = ({
  selectedAudioStory,
  setSelectedAudioStory,
  customAudioStory,
  setCustomAudioStory,
  selectedVoice,
  setSelectedVoice
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const handleAudioStorySelect = (storyId) => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (selectedAudioStory === storyId) {
      setSelectedAudioStory('');
      setShowCustomInput(false);
    } else {
      setSelectedAudioStory(storyId);
      if (storyId !== 'custom') {
        setShowCustomInput(false);
      }
    }
  };

  const handleCustomSelect = () => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (selectedAudioStory === 'custom') {
      setSelectedAudioStory('');
      setShowCustomInput(false);
    } else {
      setSelectedAudioStory('custom');
      setShowCustomInput(true);
    }
  };

  // Liste combinée pour la grille avec slots
  const allStories = [
    { id: 'custom', title: 'Histoire personnalisée', description: 'Créez votre propre type d\'histoire unique', emoji: '✏️', isCustom: true },
    ...audioStories
  ];

  const handleCustomAudioStoryChange = (e) => {
    setCustomAudioStory(e.target.value);
  };

  const handleVoiceSelect = (voiceId) => {
    setSelectedVoice(selectedVoice === voiceId ? null : voiceId);
  };

  return (
    <div className="audio-story-selector">
      <h3>2. Choisissez un type d'histoire</h3>

      <div className="audio-story-grid">
        {allStories.map((story) => (
          <div key={story.id} className="audio-story-slot">
            <motion.div
              className={`audio-story-card ${story.isCustom ? 'custom-audio-story' : ''} ${selectedAudioStory === story.id ? 'selected' : ''}`}
              onClick={() => story.isCustom ? handleCustomSelect() : handleAudioStorySelect(story.id)}
              whileHover={{ y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="audio-story-emoji">{story.emoji}</div>
              <h4>{story.title}</h4>
              <p>{story.description}</p>
            </motion.div>

            {/* Encart de personnalisation juste en dessous du bouton custom */}
            {story.isCustom && showCustomInput && selectedAudioStory === 'custom' && (
              <motion.div
                className="custom-theme-input inline-input"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                transition={{ duration: 0.3 }}
              >
                <motion.textarea
                  id="customAudioStory"
                  value={customAudioStory}
                  onChange={handleCustomAudioStoryChange}
                  placeholder="Ex: Un conte qui se déroule dans un monde sous-marin avec des créatures magiques..."
                  className="custom-input"
                  whileFocus={{ scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 300, damping: 10 }}
                />
              </motion.div>
            )}
          </div>
        ))}
      </div>

      <div className="voice-selector-section">
        <h3>3. Choisissez une narration (optionnel)</h3>
        
        <div className="voice-options">
          {voices.map((voice) => (
            <motion.div
              key={voice.id}
              className={`voice-option ${selectedVoice === voice.id ? 'selected' : ''}`}
              onClick={() => handleVoiceSelect(voice.id)}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="voice-icon">
                {voice.id === 'female' ? '👩' : '👨'}
              </div>
              <div className="voice-details">
                <h4>{voice.name}</h4>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AudioStorySelector;
