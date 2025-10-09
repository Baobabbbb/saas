import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CookieBanner.css';

const CookieBanner = ({ onLegalClick }) => {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Vérifier si l'utilisateur a déjà vu l'information sur les cookies essentiels
    const hasSeenEssentialCookies = localStorage.getItem('essentialCookiesInfo');
    if (!hasSeenEssentialCookies) {
      setShowBanner(true);
    }
  }, []);

  const handleAcceptInfo = () => {
    // Enregistrer que l'utilisateur a vu l'information sur les cookies essentiels
    localStorage.setItem('essentialCookiesInfo', JSON.stringify({
      shown: true,
      timestamp: new Date().toISOString()
    }));
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="cookie-banner"
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="cookie-content">
          <div className="cookie-info">
            <div className="cookie-icon">🍪</div>
            <div className="cookie-text">
              <h3>Cookies essentiels uniquement</h3>
              <p>
                Ce site utilise uniquement des cookies essentiels nécessaires à son fonctionnement
                (connexion, sécurité). Aucun cookie de suivi ou analytique n'est utilisé.
                {' '}
                <button
                  className="link-button"
                  onClick={() => onLegalClick?.('cookies')}
                >
                  En savoir plus
                </button>
              </p>
            </div>
          </div>

          <div className="cookie-actions">
            <button
              className="cookie-btn primary"
              onClick={handleAcceptInfo}
            >
              J'ai compris
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default CookieBanner;
