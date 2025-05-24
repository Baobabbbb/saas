import React, { useState } from 'react';
import './ComicImageSelector.css';

const ComicImageSelector = ({ numImages, setNumImages }) => {
  const steps = [4, 8, 12, 16, 20];
  const [hoverIndex, setHoverIndex] = useState(null);

  return (
    <div className="image-selector">
      <h2>5. Choisissez le nombre d'images</h2>

      <div className="dock-buttons">
        {steps.map((value, index) => {
          const isActive = value === numImages;
          const isHovered = hoverIndex === index;
          const isNeighbor =
            hoverIndex === index - 1 || hoverIndex === index + 1;

          return (
            <button
              key={value}
              className={`dock-button ${isActive ? 'active' : ''} ${
                isHovered ? 'hovered' : ''
              } ${isNeighbor ? 'neighbor' : ''}`}
              onMouseEnter={() => setHoverIndex(index)}
              onMouseLeave={() => setHoverIndex(null)}
              onClick={() => setNumImages(value)}
            >
              {value}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ComicImageSelector;
