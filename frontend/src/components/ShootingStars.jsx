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
        duration: Math.random() * 2 + 1, // Durée (1-3s) - plus court pour l'effet naturel
        delay: 0, // Pas de délai individuel, géré par l'intervalle
      };

      setStars(prev => [...prev, star]);

      // Supprimer l'étoile après sa durée
      setTimeout(() => {
        setStars(prev => prev.filter(s => s.id !== star.id));
      }, star.duration * 1000);
    };

    const scheduleNextStar = () => {
      // Délai aléatoire entre 2 secondes et 20 minutes (1200 secondes)
      const randomDelay = Math.random() * (1200 - 2) + 2; // Entre 2s et 1200s (20min)
      setTimeout(() => {
        createStar();
        scheduleNextStar(); // Programmer la suivante
      }, randomDelay * 1000);
    };

    // Démarrer le cycle
    scheduleNextStar();

    return () => {
      // Nettoyer les timeouts si le composant se démonte
    };
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
