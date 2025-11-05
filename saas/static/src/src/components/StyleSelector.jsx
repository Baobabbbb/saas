import React from 'react';
import { motion } from 'framer-motion';
import './StyleSelector.css';

const styles = [
  {
    id: 'cartoon',
    name: 'Dessin animé',
    description: 'Style coloré et amusant',
    emoji: (
      <span className="w-6 h-6 flex items-center justify-center text-xl">
        🎨
      </span>
    )
  },
  {
    id: 'manga',
    name: 'Manga',
    description: 'Style inspiré des mangas japonais',
    emoji: (
      <img
        src="/assets/japan-flag.png"
        alt="Japon"
        className="w-6 h-6 object-contain inline-block align-middle relative top-[2px]"
        style={{ maxWidth: '20px', maxHeight: '20px' }}
      />
    )
  },
  {
    id: 'watercolor',
    name: 'Aquarelle',
    description: 'Style doux et artistique',
    emoji: (
      <span className="w-6 h-6 flex items-center justify-center text-xl">
        🖌️
      </span>
    )
  },
  {
    id: 'pixel',
    name: 'Pixel Art',
    description: 'Style rétro inspiré des jeux vidéo',
    emoji: (
      <span className="w-6 h-6 flex items-center justify-center text-xl">
        👾
      </span>
    )
  }
];

const StyleSelector = ({ selectedStyle, setSelectedStyle }) => {
  const handleStyleSelect = (styleId) => {
    // Toggle: déselectionne si déjà sélectionné, sinon sélectionne
    if (selectedStyle === styleId) {
      setSelectedStyle('');
    } else {
      setSelectedStyle(styleId);
    }
  };

  return (
    <div className="style-selector">
      <h3>2. Choisissez un style visuel</h3>

      <div className="style-options">
        {styles.map((style) => (
          <motion.div
            key={style.id}
            className={`style-option ${selectedStyle === style.id ? 'selected' : ''}`}
            onClick={() => handleStyleSelect(style.id)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="style-emoji">{style.emoji}</div>
            <h4 className="style-name">{style.name}</h4>
            <p className="style-description">{style.description}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default StyleSelector;
