import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const ShootingStars = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    const createStar = () => {
      const star = {
        id: Date.now() + Math.random(),
        left: Math.random() * 120 - 20, // Position de départ (peut être hors écran à gauche)
        top: Math.random() * 60 + 5, // Position verticale aléatoire (5-65% du haut)
        size: Math.random() * 6 + 4, // Taille plus grande (4-10px)
        duration: Math.random() * 5 + 5, // Durée (5-10s)
        delay: Math.random() * 8, // Délai aléatoire (0-8s)
        angle: Math.random() * 60 - 30, // Angle aléatoire (-30° à +30°)
      };

      setStars(prev => [...prev, star]);

      // Supprimer l'étoile après sa durée + délai
      setTimeout(() => {
        setStars(prev => prev.filter(s => s.id !== star.id));
      }, (star.duration + star.delay) * 1000);
    };

    // Créer beaucoup plus d'étoiles - toutes les 1-3 secondes
    const interval = setInterval(createStar, Math.random() * 2000 + 1000);

    // Créer plusieurs étoiles au démarrage pour plus d'activité
    setTimeout(createStar, 200);
    setTimeout(createStar, 600);
    setTimeout(createStar, 1000);
    setTimeout(createStar, 1400);
    setTimeout(createStar, 1800);

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
            '--star-angle': `${star.angle}deg`,
          }}
        />
      ))}
    </div>
  );
};

export default ShootingStars;
