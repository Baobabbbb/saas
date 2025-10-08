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
        size: Math.random() * 8 + 6, // Taille encore plus grande (6-14px)
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

    // Créer énormément d'étoiles - toutes les 0.5-2 secondes
    const interval = setInterval(createStar, Math.random() * 1500 + 500);

    // Créer beaucoup d'étoiles au démarrage pour activité immédiate
    setTimeout(createStar, 100);
    setTimeout(createStar, 300);
    setTimeout(createStar, 500);
    setTimeout(createStar, 700);
    setTimeout(createStar, 900);
    setTimeout(createStar, 1100);
    setTimeout(createStar, 1300);
    setTimeout(createStar, 1500);

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
