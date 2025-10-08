import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const ShootingStars = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    const createStar = () => {
      const star = {
        id: Date.now() + Math.random(),
        left: Math.random() * 100, // Position horizontale aléatoire (0-100%)
        top: Math.random() * 40, // Position verticale aléatoire (0-40% du haut)
        size: Math.random() * 6 + 4, // Taille plus grande (4-10px)
        duration: Math.random() * 2 + 3, // Durée plus longue (3-5s)
        delay: 0, // Pas de délai pour visibilité immédiate
      };

      console.log('🌟 Création d\'une étoile filante:', star);
      setStars(prev => [...prev, star]);

      // Supprimer l'étoile après sa durée
      setTimeout(() => {
        setStars(prev => prev.filter(s => s.id !== star.id));
      }, star.duration * 1000);
    };

    // Créer une nouvelle étoile toutes les 2-4 secondes
    const interval = setInterval(createStar, Math.random() * 2000 + 2000);

    // Créer une étoile immédiatement pour test
    createStar();

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
