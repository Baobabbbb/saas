import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './AudioStorySelector.css';

const audioStories = [
  { id: 'bedtime', title: 'Histoire du soir', description: 'Un conte apaisant pour aider votre enfant à s\'endormir', emoji: '🌙' },
  { id: 'adventure', title: 'Aventure fantastique', description: 'Une aventure pleine de rebondissements et de magie', emoji: '✨' },
  { id: 'animals', title: 'Amis animaux', description: 'Une histoire avec des animaux qui parlent et vivent des aventures', emoji: '🦊' },
  { id: 'learning', title: 'Conte éducatif', description: 'Une histoire qui enseigne une leçon importante', emoji: '📚' },
  { id: 'funny', title: 'Histoire drôle', description: 'Un conte amusant qui fera rire votre enfant', emoji: '😄' },
  { id: 'mystery', title: 'Petit mystère', description: 'Une énigme adaptée aux enfants à résoudre', emoji: '🔍' }
];

const voices = [
  { id: 'female', name: 'Voix féminine douce', description: 'Une voix apaisante et chaleureuse' },
  { id: 'male', name: 'Voix masculine calme', description: 'Une voix posée et rassurante' },
  { id: 'child', name: 'Voix d\'enfant', description: 'Une voix enjouée et espiègle' },
  { id: 'grandma', name: 'Voix de grand-mère', description: 'Une voix chaleureuse et bienveillante' },
  { id: 'grandpa', name: 'Voix de grand-père', description: 'Une voix sage et posée' }
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
    console.log('🎵 Sélection histoire audio:', storyId);
    setSelectedAudioStory(storyId);
    if (storyId !== 'custom') {
      setShowCustomInput(false);
    }
  };

  const handleCustomSelect = () => {
    setSelectedAudioStory('custom');
    setShowCustomInput(true);
  };

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
        <motion.div
          className={`audio-story-card custom-audio-story ${selectedAudioStory === 'custom' ? 'selected' : ''}`}
          onClick={handleCustomSelect}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="audio-story-emoji">✏️</div>
          <h4>Histoire personnalisée</h4>
          <p>Créez votre propre type d'histoire unique</p>
        </motion.div>
        
        {audioStories.map((story) => (
          <motion.div
            key={story.id}
            className={`audio-story-card ${selectedAudioStory === story.id ? 'selected' : ''}`}
            onClick={() => handleAudioStorySelect(story.id)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="audio-story-emoji">{story.emoji}</div>
            <h4>{story.title}</h4>
            <p>{story.description}</p>
          </motion.div>
        ))}
      </div>
      
      {showCustomInput && (
        <motion.div 
          className="custom-audio-story-input"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <label htmlFor="customAudioStory">Décrivez votre type d'histoire</label>
          <motion.textarea
            id="customAudioStory"
            value={customAudioStory}
            onChange={handleCustomAudioStoryChange}
            placeholder="Ex: Un conte qui se déroule dans un monde sous-marin avec des créatures magiques..."
            whileFocus={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          />
        </motion.div>
      )}

      <div className="voice-selector-section">
        <h3>2.1. Choisissez une voix pour la narration (optionnel)</h3>
        
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
                {voice.id === 'female' ? '👩' : 
                 voice.id === 'male' ? '👨' : 
                 voice.id === 'child' ? '👧' : 
                 voice.id === 'grandma' ? '👵' : '👴'}
              </div>
              <div className="voice-details">
                <h4>{voice.name}</h4>
                <p>{voice.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AudioStorySelector;
