import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const ShootingStars = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    const createStar = () => {
      const star = {
        id: Date.now() + Math.random(),
        left: Math.random() * 120 - 20, // Position de départ (peut être hors écran à gauche)
        top: Math.random() * 30 + 10, // Position verticale aléatoire (10-40% du haut)
        size: Math.random() * 3 + 2, // Taille (2-5px)
        duration: Math.random() * 4 + 6, // Durée (6-10s) - plus long pour la traînée
        delay: Math.random() * 12, // Délai aléatoire (0-12s)
      };

      setStars(prev => [...prev, star]);

      // Supprimer l'étoile après sa durée + délai
      setTimeout(() => {
        setStars(prev => prev.filter(s => s.id !== star.id));
      }, (star.duration + star.delay) * 1000);
    };

    // Créer plus d'étoiles - toutes les 3-6 secondes
    const interval = setInterval(createStar, Math.random() * 3000 + 3000);

    // Créer plusieurs étoiles au démarrage pour plus d'activité
    setTimeout(createStar, 500);
    setTimeout(createStar, 1500);
    setTimeout(createStar, 2500);
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
