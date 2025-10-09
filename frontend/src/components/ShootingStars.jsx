import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const ShootingStars = () => {
  const [activeStars, setActiveStars] = useState([]);

  useEffect(() => {
    const scheduleStar = (starIndex) => {
      // Délai aléatoire entre 2 secondes et 1 minute (60 secondes) pour le test
      const randomDelay = Math.random() * (60 - 2) + 2; // 2s → 60s (1min)

      setTimeout(() => {
        // Ajouter l'étoile active
        const newStar = {
          id: Date.now() + starIndex,
          index: starIndex,
          duration: Math.random() * 2 + 1, // Durée 1-3s
        };

        setActiveStars(prev => [...prev, newStar]);

        // Programmer la suppression après la durée de l'animation
        setTimeout(() => {
          setActiveStars(prev => prev.filter(star => star.id !== newStar.id));
        }, newStar.duration * 1000);

        // Programmer la prochaine apparition de cette étoile
        scheduleStar(starIndex);
      }, randomDelay * 1000);
    };

    // Lancer le cycle pour chaque étoile
    for (let i = 0; i < 10; i++) {
      // Délai initial aléatoire pour éviter qu'elles partent toutes en même temps
      setTimeout(() => scheduleStar(i), Math.random() * 5000);
    }

    return () => {
      // Nettoyer les timeouts si le composant se démonte
      setActiveStars([]);
    };
  }, []);

  return (
    <section className="shooting-stars-container">
      {activeStars.map(star => (
        <span
          key={star.id}
          className={`shooting-star star-${star.index + 1}`}
          style={{
            animationDuration: `${star.duration}s`,
          }}
        />
      ))}
    </section>
  );
};

export default ShootingStars;
