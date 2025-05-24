import React from 'react';
import './ComicImageSelector.css';

const ComicImageSelector = ({ numImages, setNumImages }) => {
  const options = [4, 8, 12, 16, 20];

  // Calcule la largeur (%) de la barre de progression
  const progressWidth = ((options.indexOf(numImages)) / (options.length - 1)) * 100;

  return (
    <div className="image-selector">
      <label className="label">5. Choisissez le nombre d'images</label>
      <div className="slider-container">
        <div className="progress-line-background">
          <div
            className="progress-line-fill"
            style={{ width: `${progressWidth}%` }}
          />
        </div>
        {options.map((n) => (
          <div
            key={n}
            className={`slider-step ${numImages === n ? 'active' : ''}`}
            onClick={() => setNumImages(n)}
          >
            <div className="dot" />
            <span className="step-label">{n}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComicImageSelector;
