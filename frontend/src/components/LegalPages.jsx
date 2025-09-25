import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './LegalPages.css';

const LegalPages = ({ onClose, initialSection = 'mentions' }) => {
  const [activeSection, setActiveSection] = useState(initialSection);

  const sections = [
    { id: 'mentions', title: 'Mentions Légales', icon: '📄' },
    { id: 'privacy', title: 'Confidentialité', icon: '🔒' },
    { id: 'cookies', title: 'Cookies', icon: '🍪' },
    { id: 'terms', title: 'Conditions d\'utilisation', icon: '📜' },
    { id: 'contact', title: 'Contact', icon: '📧' }
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'mentions':
        return renderMentionsLegales();
      case 'privacy':
        return renderPrivacyPolicy();
      case 'cookies':
        return renderCookiesPolicy();
      case 'terms':
        return renderTermsOfService();
      case 'contact':
        return renderContact();
      default:
        return renderMentionsLegales();
    }
  };

  const renderMentionsLegales = () => (
    <div className="legal-content">
      <h2>📄 Mentions Légales</h2>
      <div className="legal-section">
        <h3>Éditeur du site</h3>
        <div className="info-block">
          <p><strong>Nom :</strong> HERBBIE</p>
          <p><strong>Email :</strong> contact@herbbie.com</p>
        </div>
      </div>
    </div>
  );

  const renderPrivacyPolicy = () => (
    <div className="legal-content">
      <h2>🔒 Politique de Confidentialité</h2>
      <div className="legal-section">
        <h3>Collecte des données</h3>
        <div className="info-block">
          <p>HERBBIE collecte les informations nécessaires au fonctionnement du service.</p>
        </div>
      </div>
    </div>
  );

  const renderCookiesPolicy = () => (
    <div className="legal-content">
      <h2>🍪 Politique des Cookies</h2>
      <div className="legal-section">
        <h3>Utilisation des cookies</h3>
        <div className="info-block">
          <p>Ce site utilise des cookies techniques nécessaires au fonctionnement.</p>
        </div>
      </div>
    </div>
  );

  const renderTermsOfService = () => (
    <div className="legal-content">
      <h2>📜 Conditions d'utilisation</h2>
      <div className="legal-section">
        <h3>Utilisation du service</h3>
        <div className="info-block">
          <p>HERBBIE est un service de génération de contenu créatif pour enfants.</p>
        </div>
      </div>
    </div>
  );

  const renderContact = () => (
    <div className="legal-content">
      <h2>📧 Contact</h2>
      <div className="legal-section">
        <h3>Informations de contact</h3>
        <div className="info-block">
          <p><strong>📧 Email :</strong> <a href="mailto:contact@herbbie.com">contact@herbbie.com</a></p>
          <p><strong>🏢 Nom de l'entreprise :</strong> HERBBIE</p>
        </div>
      </div>
    </div>
  );

  return (
    <motion.div
      className="legal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      onClick={onClose}
    >
      <motion.div
        className="legal-modal"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ duration: 0.3 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="legal-header">
          <h1>⚖️ Informations Légales</h1>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="legal-body">
          <nav className="legal-nav">
            {sections.map((section) => (
              <button
                key={section.id}
                className={`nav-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => setActiveSection(section.id)}
              >
                <span className="nav-icon">{section.icon}</span>
                <span className="nav-title">{section.title}</span>
              </button>
            ))}
          </nav>

          <div className="legal-main">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeSection}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              >
                {renderContent()}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default LegalPages;