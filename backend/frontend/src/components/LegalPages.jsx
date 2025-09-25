import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './LegalPages.css';

const LegalPages = ({ onClose, initialSection = 'mentions' }) => {
  const [activeSection, setActiveSection] = useState(initialSection);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');

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

  const handleContactFormChange = (field, value) => {
    setContactForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleContactFormSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitMessage('');

    try {
      // Créer le lien mailto avec les données du formulaire
      const subject = encodeURIComponent(contactForm.subject);
      const body = encodeURIComponent(
        `Nom: ${contactForm.name}\n` +
        `Email: ${contactForm.email}\n\n` +
        `Message:\n${contactForm.message}`
      );

      const mailtoLink = `mailto:contact@herbbie.com?subject=${subject}&body=${body}`;

      // Ouvrir le client email
      window.location.href = mailtoLink;

      // Afficher un message de succès
      setSubmitMessage('✅ Votre email a été préparé ! Vérifiez votre client email et envoyez le message.');

      // Réinitialiser le formulaire après 3 secondes
      setTimeout(() => {
        setContactForm({
          name: '',
          email: '',
          subject: '',
          message: ''
        });
        setSubmitMessage('');
      }, 3000);

    } catch (error) {
      console.error('Erreur lors de l\'envoi du formulaire:', error);
      setSubmitMessage('❌ Une erreur s\'est produite. Veuillez réessayer.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderContact = () => (
    <div className="legal-content">
      <h2>📧 Contact</h2>

      <div className="legal-section">
        <h3>📝 Formulaire de contact</h3>
        <div className="info-block">
          <p>Vous pouvez nous contacter directement en remplissant le formulaire ci-dessous :</p>

          <form className="contact-form" onSubmit={handleContactFormSubmit}>
            <div className="form-group">
              <label htmlFor="contact-name">Nom *</label>
              <input
                type="text"
                id="contact-name"
                value={contactForm.name}
                onChange={(e) => handleContactFormChange('name', e.target.value)}
                required
                placeholder="Votre nom complet"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact-email">Email *</label>
              <input
                type="email"
                id="contact-email"
                value={contactForm.email}
                onChange={(e) => handleContactFormChange('email', e.target.value)}
                required
                placeholder="votre.email@exemple.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact-subject">Sujet *</label>
              <select
                id="contact-subject"
                value={contactForm.subject}
                onChange={(e) => handleContactFormChange('subject', e.target.value)}
                required
              >
                <option value="">Choisissez un sujet</option>
                <option value="Support technique">🔧 Support technique</option>
                <option value="Question générale">💬 Question générale</option>
                <option value="Partenariat">🤝 Partenariat</option>
                <option value="Signaler un bug">🐛 Signaler un bug</option>
                <option value="Suggestion">💡 Suggestion</option>
                <option value="Autre">📋 Autre</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="contact-message">Message *</label>
              <textarea
                id="contact-message"
                value={contactForm.message}
                onChange={(e) => handleContactFormChange('message', e.target.value)}
                required
                placeholder="Décrivez votre demande en détail..."
                rows="5"
              />
            </div>

            {submitMessage && (
              <div className={`submit-message ${submitMessage.includes('✅') ? 'success' : 'error'}`}>
                {submitMessage}
              </div>
            )}

            <button
              type="submit"
              className="contact-submit-btn"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="spinner"></span>
                  Préparation de l'email...
                </>
              ) : (
                <>
                  📧 Préparer l'email
                </>
              )}
            </button>
          </form>

          <div className="contact-info">
            <p><strong>💡 Astuce :</strong> Ce formulaire ouvrira votre client email avec un message pré-rempli. Il vous suffira de cliquer sur "Envoyer".</p>
          </div>
        </div>
      </div>

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