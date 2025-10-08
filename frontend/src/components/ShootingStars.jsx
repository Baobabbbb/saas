import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const ShootingStars = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    const createStar = () => {
      const star = {
        id: Date.now() + Math.random(),
        left: Math.random() * 120 - 20, // Position de départ (peut être hors écran à gauche)
        top: Math.random() * 60, // Position verticale aléatoire (haut de l'écran)
        size: Math.random() * 4 + 3, // Taille (3-7px)
        duration: Math.random() * 3 + 4, // Durée (4-7s)
        delay: Math.random() * 8, // Délai aléatoire (0-8s)
      };

      setStars(prev => [...prev, star]);

      // Supprimer l'étoile après sa durée + délai
      setTimeout(() => {
        setStars(prev => prev.filter(s => s.id !== star.id));
      }, (star.duration + star.delay) * 1000);
    };

    // Créer une nouvelle étoile filante toutes les 5-10 secondes
    const interval = setInterval(createStar, Math.random() * 5000 + 5000);

    // Créer quelques étoiles au démarrage
    setTimeout(createStar, 1000);
    setTimeout(createStar, 4000);

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
