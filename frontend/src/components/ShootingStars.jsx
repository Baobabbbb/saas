import React, { useEffect, useState } from 'react';
import './ShootingStars.css';

const ShootingStars = () => {
  const [starDelays, setStarDelays] = useState([]);

  useEffect(() => {
    // Générer des délais aléatoires très espacés pour chaque étoile (une seule fois)
    const delays = [];
    let currentDelay = 0;

    for (let i = 0; i < 10; i++) {
      // Délai aléatoire entre 2 secondes et 20 minutes (1200 secondes)
      const randomDelay = Math.random() * (1200 - 2) + 2;
      currentDelay += randomDelay;
      delays.push(currentDelay);
    }

    setStarDelays(delays);
  }, []); // Le tableau vide [] garantit que useEffect ne s'exécute qu'une fois

  return (
    <section className="shooting-stars-container">
      {starDelays.map((delay, index) => (
        <span
          key={index}
          style={{
            animationDelay: `${delay}s`,
            animationDuration: `${Math.random() * 2 + 1}s` // Durée aléatoire 1-3s
          }}
        />
      ))}
    </section>
  );
};

export default ShootingStars;
