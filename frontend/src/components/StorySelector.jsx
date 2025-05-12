import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './StorySelector.css';

const stories = [
  { id: 'space', title: 'Aventure spatiale', description: 'Une exploration de l\'espace et des planètes lointaines', emoji: '🚀' },
  { id: 'ocean', title: 'Sous l\'océan', description: 'Une aventure sous-marine avec des créatures fantastiques', emoji: '🐠' },
  { id: 'dinosaur', title: 'Monde des dinosaures', description: 'Un voyage dans le temps à l\'époque des dinosaures', emoji: '🦕' },
  { id: 'fairy', title: 'Conte de fées', description: 'Une histoire magique avec des fées et des créatures enchantées', emoji: '🧚' },
  { id: 'superhero', title: 'Super-héros', description: 'Une aventure où votre enfant devient un super-héros', emoji: '🦸' },
  { id: 'jungle', title: 'Aventure dans la jungle', description: 'Une exploration de la jungle et ses animaux sauvages', emoji: '🌴' }
];

const StorySelector = ({ selectedStory, setSelectedStory, customStory, setCustomStory }) => {
  const [showCustomInput, setShowCustomInput] = useState(false);

  const handleStorySelect = (storyId) => {
    setSelectedStory(storyId);
    if (storyId !== 'custom') {
      setShowCustomInput(false);
    }
  };

  const handleCustomSelect = () => {
    setSelectedStory('custom');
    setShowCustomInput(true);
  };

  const handleCustomStoryChange = (e) => {
    setCustomStory(e.target.value);
  };

  /*return (
    <div className="story-selector">
      <h3>4. Choisissez un type d'histoire</h3>
      
      <div className="story-grid">
        {/* Custom story option first *RAJOUTER UN SLASH APRES L'ETOILE}
        <motion.div
          className={`story-card custom-story ${selectedStory === 'custom' ? 'selected' : ''}`}
          onClick={handleCustomSelect}
          whileHover={{ y: -5 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="story-emoji">✏️</div>
          <h4>Histoire personnalisée</h4>
          <p>Créez votre propre type d'histoire unique</p>
        </motion.div>
        
        {/* Predefined stories *RAJOUTER UN SLASH APRES L'ETOILE}
        {stories.map((story) => (
          <motion.div
            key={story.id}
            className={`story-card ${selectedStory === story.id ? 'selected' : ''}`}
            onClick={() => handleStorySelect(story.id)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="story-emoji">{story.emoji}</div>
            <h4>{story.title}</h4>
            <p>{story.description}</p>
          </motion.div>
        ))}
      </div>
      
      {showCustomInput && (
        <motion.div 
          className="custom-story-input"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <label htmlFor="customStory">Décrivez votre type d'histoire</label>
          <motion.textarea
            id="customStory"
            value={customStory}
            onChange={handleCustomStoryChange}
            placeholder="Ex: Une aventure dans un monde de bonbons où les arbres sont en chocolat..."
            whileFocus={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 300, damping: 10 }}
          />
        </motion.div>
      )}
    </div>
  );*/
};

export default StorySelector;
