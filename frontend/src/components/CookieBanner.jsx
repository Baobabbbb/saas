import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CookieBanner.css';

const CookieBanner = ({ onLegalClick }) => {
  const [showBanner, setShowBanner] = useState(false);
  const [preferences, setPreferences] = useState(null);

  useEffect(() => {
    // Vérifier si l'utilisateur a déjà donné son consentement
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      setShowBanner(true);
    } else {
      setPreferences(JSON.parse(consent));
    }
  }, []);

  const handleAcceptAll = () => {
    const consent = {
      necessary: true,
      analytics: true,
      preferences: true,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('cookieConsent', JSON.stringify(consent));
    setPreferences(consent);
    setShowBanner(false);
    
    // Activer les cookies optionnels
    enableOptionalCookies(consent);
  };

  const handleAcceptNecessary = () => {
    const consent = {
      necessary: true,
      analytics: false,
      preferences: false,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('cookieConsent', JSON.stringify(consent));
    setPreferences(consent);
    setShowBanner(false);
    
    // Désactiver les cookies optionnels
    disableOptionalCookies();
  };

  const enableOptionalCookies = (consent) => {
    // Ici vous pouvez activer Google Analytics, etc. selon les préférences
    if (consent.analytics) {
      console.log('✅ Cookies analytiques activés');
      // Exemple : gtag('consent', 'update', { analytics_storage: 'granted' });
    }
    
    if (consent.preferences) {
      console.log('✅ Cookies de préférences activés');
      // Activer les cookies de personnalisation
    }
  };

  const disableOptionalCookies = () => {
    console.log('❌ Cookies optionnels désactivés');
    // Exemple : gtag('consent', 'update', { analytics_storage: 'denied' });
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
              <h3>Nous utilisons des cookies</h3>
              <p>
                Ce site utilise des cookies pour améliorer votre expérience et analyser notre trafic. 
                Les cookies nécessaires sont toujours activés.{' '}
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
              className="cookie-btn secondary"
              onClick={handleAcceptNecessary}
            >
              Nécessaires uniquement
            </button>
            <button 
              className="cookie-btn primary"
              onClick={handleAcceptAll}
            >
              Accepter tous
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default CookieBanner;
