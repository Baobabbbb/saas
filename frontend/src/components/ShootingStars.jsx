import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const ShootingStars = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    const createStar = () => {
      const star = {
        id: Date.now() + Math.random(),
        left: Math.random() * 100, // Position horizontale aléatoire (0-100%)
        top: Math.random() * 50, // Position verticale aléatoire (0-50% du haut)
        size: Math.random() * 3 + 1, // Taille aléatoire (1-4px)
        duration: Math.random() * 3 + 2, // Durée aléatoire (2-5s)
        delay: Math.random() * 10, // Délai avant apparition (0-10s)
      };

      setStars(prev => [...prev, star]);

      // Supprimer l'étoile après sa durée + délai
      setTimeout(() => {
        setStars(prev => prev.filter(s => s.id !== star.id));
      }, (star.duration + star.delay) * 1000);
    };

    // Créer une nouvelle étoile toutes les 3-8 secondes
    const interval = setInterval(createStar, Math.random() * 5000 + 3000);

    // Créer quelques étoiles au démarrage
    setTimeout(createStar, 1000);
    setTimeout(createStar, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="shooting-stars-container">
      {stars.map(star => (
        <div
          key={star.id}
          className="shooting-star"
          style={{
            left: `${star.left}%`,
            top: `${star.top}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            animationDuration: `${star.duration}s`,
            animationDelay: `${star.delay}s`,
          }}
        />
      ))}
    </div>
  );
};

export default ShootingStars;
