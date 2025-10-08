import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const TwinklingStars = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    // Créer 50 étoiles scintillantes
    const initialStars = [];
    for (let i = 0; i < 50; i++) {
      initialStars.push({
        id: i,
        left: Math.random() * 100, // Position horizontale aléatoire (0-100%)
        top: Math.random() * 100, // Position verticale aléatoire (0-100%)
        size: Math.random() * 2 + 1, // Taille petite (1-3px)
        delay: Math.random() * 3, // Délai aléatoire pour le scintillement
        brightness: Math.random() * 0.5 + 0.5, // Luminosité de base (0.5-1.0)
      });
    }
    setStars(initialStars);
  }, []);

  return (
    <div className="twinkling-stars-container">
      {stars.map(star => (
        <div
          key={star.id}
          className="twinkling-star"
          style={{
            left: `${star.left}%`,
            top: `${star.top}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            animationDelay: `${star.delay}s`,
            opacity: star.brightness,
          }}
        />
      ))}
    </div>
  );
};

export default TwinklingStars;
