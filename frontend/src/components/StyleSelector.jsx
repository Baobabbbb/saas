import React from 'react';
import { motion } from 'framer-motion';
import './StyleSelector.css';

const styles = [
  { id: 'cartoon', name: 'Dessin animé', description: 'Style coloré et amusant', emoji: '🎨' },
  { id: 'manga', name: 'Manga', description: 'Style inspiré des mangas japonais', emoji: '🇯🇵' },
  { id: 'watercolor', name: 'Aquarelle', description: 'Style doux et artistique', emoji: '🖌️' },
  { id: 'pixel', name: 'Pixel Art', description: 'Style rétro inspiré des jeux vidéo', emoji: '👾' }
];

const StyleSelector = ({ selectedStyle, setSelectedStyle }) => {
  /*return (
    <div className="style-selector">
      <h3>2. Choisissez un style visuel</h3>
      
      <div className="style-options">
        {styles.map((style) => (
          <motion.div
            key={style.id}
            className={`style-option ${selectedStyle === style.id ? 'selected' : ''}`}
            onClick={() => setSelectedStyle(style.id)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="style-emoji">{style.emoji}</div>
            <h4>{style.name}</h4>
            <p>{style.description}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );*/
};

export default StyleSelector;
