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

  const renderMentionsLegales = () => (
    <div className="legal-content">
      <h2>📄 Mentions Légales</h2>
      
      <div className="legal-section">
        <h3>Éditeur du site</h3>
        <div className="info-block">
          <p><strong>Nom :</strong> FRIDAY</p>
          <p><strong>Adresse :</strong> [À compléter selon votre situation]</p>
          <p><strong>Email :</strong> contact@friday.com</p>
          <p><strong>Téléphone :</strong> [À compléter]</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Hébergement</h3>
        <div className="info-block">
          <p><strong>Hébergeur :</strong> [À compléter selon votre choix d'hébergement]</p>
          <p><strong>Adresse :</strong> [Adresse de l'hébergeur]</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Directeur de la publication</h3>
        <div className="info-block">
          <p>[Nom du responsable de la publication]</p>
        </div>
      </div>
    </div>
  );

  const renderPrivacyPolicy = () => (
    <div className="legal-content">
      <h2>🔒 Politique de Confidentialité</h2>
      
      <div className="legal-section">
        <h3>Collecte des données personnelles</h3>
        <div className="info-block">
          <p>Dans le cadre de l'utilisation de notre service, nous pouvons collecter :</p>
          <ul>
            <li><strong>Données de compte :</strong> email, nom d'utilisateur (si inscription)</li>
            <li><strong>Données de navigation :</strong> adresse IP, navigateur, pages visitées</li>
            <li><strong>Créations :</strong> contenus générés via notre service (comptines, histoires, coloriages)</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Finalités du traitement</h3>
        <div className="info-block">
          <p>Vos données sont utilisées pour :</p>
          <ul>
            <li>Fournir le service de génération de contenu pour enfants</li>
            <li>Conserver l'historique de vos créations</li>
            <li>Améliorer notre service</li>
            <li>Respecter nos obligations légales</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Base légale du traitement</h3>
        <div className="info-block">
          <p>Le traitement de vos données repose sur :</p>
          <ul>
            <li><strong>Votre consentement</strong> pour l'utilisation du service</li>
            <li><strong>L'intérêt légitime</strong> pour l'amélioration du service</li>
            <li><strong>L'exécution du contrat</strong> pour la fourniture du service</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Vos droits (RGPD)</h3>
        <div className="info-block">
          <p>Vous disposez des droits suivants :</p>
          <ul>
            <li><strong>Droit d'accès :</strong> consulter vos données</li>
            <li><strong>Droit de rectification :</strong> corriger vos données</li>
            <li><strong>Droit à l'effacement :</strong> supprimer vos données</li>
            <li><strong>Droit de portabilité :</strong> récupérer vos données</li>
            <li><strong>Droit d'opposition :</strong> vous opposer au traitement</li>
          </ul>
          <p><strong>Pour exercer vos droits :</strong> contactez-nous à l'adresse : privacy@friday.com</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Conservation des données</h3>
        <div className="info-block">
          <p>Vos données sont conservées :</p>
          <ul>
            <li><strong>Données de compte :</strong> jusqu'à suppression du compte</li>
            <li><strong>Historique des créations :</strong> jusqu'à suppression par l'utilisateur</li>
            <li><strong>Données de navigation :</strong> 13 mois maximum</li>
          </ul>
        </div>
      </div>
    </div>
  );

  const renderCookiesPolicy = () => (
    <div className="legal-content">
      <h2>🍪 Politique des Cookies</h2>
      
      <div className="legal-section">
        <h3>Qu'est-ce qu'un cookie ?</h3>
        <div className="info-block">
          <p>Un cookie est un petit fichier texte déposé sur votre ordinateur lors de la visite d'un site web. 
             Il permet de mémoriser des informations relatives à votre navigation.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Types de cookies utilisés</h3>
        <div className="info-block">
          <p><strong>🔧 Cookies techniques (obligatoires) :</strong></p>
          <ul>
            <li>Gestion de la session utilisateur</li>
            <li>Mémorisation de vos préférences</li>
            <li>Sécurité de l'application</li>
          </ul>
          
          <p><strong>📊 Cookies analytiques (optionnels) :</strong></p>
          <ul>
            <li>Mesure d'audience anonyme</li>
            <li>Amélioration de l'expérience utilisateur</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Gestion des cookies</h3>
        <div className="info-block">
          <p>Vous pouvez gérer vos préférences de cookies :</p>
          <ul>
            <li><strong>Via votre navigateur :</strong> paramètres de confidentialité</li>
            <li><strong>Via notre bandeau :</strong> accepter ou refuser les cookies optionnels</li>
          </ul>
          <p><em>⚠️ Note : La désactivation des cookies techniques peut affecter le fonctionnement du site.</em></p>
        </div>
      </div>
    </div>
  );

  const renderTermsOfService = () => (
    <div className="legal-content">
      <h2>📜 Conditions Générales d'Utilisation</h2>
      
      <div className="legal-section">
        <h3>Objet</h3>
        <div className="info-block">
          <p>Les présentes conditions générales régissent l'utilisation du service FRIDAY, 
             plateforme de génération de contenu ludique pour enfants (comptines, histoires, coloriages, animations).</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Utilisation du service</h3>
        <div className="info-block">
          <p><strong>✅ Utilisations autorisées :</strong></p>
          <ul>
            <li>Génération de contenu pour usage personnel et familial</li>
            <li>Partage des créations dans un cadre privé</li>
            <li>Utilisation pédagogique non commerciale</li>
          </ul>
          
          <p><strong>❌ Utilisations interdites :</strong></p>
          <ul>
            <li>Génération de contenu inapproprié ou dangereux</li>
            <li>Utilisation commerciale sans autorisation</li>
            <li>Tentative de contournement des limitations techniques</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Propriété intellectuelle</h3>
        <div className="info-block">
          <p><strong>Contenu généré :</strong></p>
          <ul>
            <li>Vous conservez la propriété de vos créations personnalisées</li>
            <li>FRIDAY se réserve le droit d'améliorer ses algorithmes via l'analyse anonyme</li>
            <li>Les modèles et templates restent propriété de FRIDAY</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Responsabilité</h3>
        <div className="info-block">
          <p>FRIDAY s'efforce de fournir un service de qualité mais :</p>
          <ul>
            <li>Ne garantit pas la perfection du contenu généré</li>
            <li>Recommande la supervision parentale pour les jeunes enfants</li>
            <li>N'est pas responsable de l'usage fait des créations</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Modifications</h3>
        <div className="info-block">
          <p>Ces conditions peuvent être modifiées à tout moment. 
             Les utilisateurs seront informés des changements importants.</p>
        </div>
      </div>
    </div>
  );

  const renderContact = () => (
    <div className="legal-content">
      <h2>📧 Contact & Support</h2>
      
      <div className="legal-section">
        <h3>Nous contacter</h3>
        <div className="info-block">
          <form className="contact-form" onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const subject = formData.get('subject');
            const message = formData.get('message');
            const firstName = formData.get('firstName');
            const lastName = formData.get('lastName');
            const email = formData.get('email');
            
            const mailtoLink = `mailto:contact@friday.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(
              `Prénom: ${firstName}\nNom: ${lastName}\nEmail: ${email}\n\nMessage:\n${message}`
            )}`;
            
            window.location.href = mailtoLink;
          }}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">Prénom *</label>
                <input type="text" id="firstName" name="firstName" required />
              </div>
              <div className="form-group">
                <label htmlFor="lastName">Nom *</label>
                <input type="text" id="lastName" name="lastName" required />
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input type="email" id="email" name="email" required />
            </div>
            
            <div className="form-group">
              <label htmlFor="subject">Sujet *</label>
              <select id="subject" name="subject" required>
                <option value="">Choisissez un sujet</option>
                <option value="Support technique">🔧 Support technique</option>
                <option value="Question de facturation">💰 Question de facturation</option>
                <option value="Suggestion d'amélioration">💡 Suggestion d'amélioration</option>
                <option value="Partenariat">🤝 Partenariat</option>
                <option value="Question générale">❓ Question générale</option>
                <option value="Autre">📋 Autre</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="message">Message *</label>
              <textarea 
                id="message" 
                name="message" 
                rows="5" 
                placeholder="Décrivez votre demande en détail..."
                required
              ></textarea>
            </div>
            
            <button type="submit" className="contact-submit-btn">
              📧 Envoyer le message
            </button>
          </form>
        </div>
      </div>
      
      <div className="legal-section">
        <h3>Besoin d'aide ?</h3>
        <div className="info-block">
          <p>Notre équipe de support est là pour vous aider avec toutes vos questions concernant FRIDAY.</p>
          <p><strong>📧 Email :</strong> <a href="mailto:contact@friday.com">contact@friday.com</a></p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Types de demandes</h3>
        <div className="info-block">
          <p><strong>🔧 Support technique :</strong></p>
          <ul>
            <li>Problèmes de génération de contenu</li>
            <li>Bugs ou erreurs techniques</li>
            <li>Questions sur les fonctionnalités</li>
          </ul>
          
          <p><strong>💰 Questions de facturation :</strong></p>
          <ul>
            <li>Gestion des crédits</li>
            <li>Problèmes de paiement</li>
            <li>Demandes de remboursement</li>
          </ul>
          
          <p><strong>📋 Demandes générales :</strong></p>
          <ul>
            <li>Suggestions d'amélioration</li>
            <li>Partenariats</li>
            <li>Questions commerciales</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Informations utiles</h3>
        <div className="info-block">
          <p>Pour nous aider à mieux vous assister, veuillez inclure dans votre message :</p>
          <ul>
            <li>Description détaillée du problème</li>
            <li>Captures d'écran si nécessaire</li>
            <li>Votre navigateur et système d'exploitation</li>
            <li>Étapes pour reproduire le problème</li>
          </ul>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'mentions': return renderMentionsLegales();
      case 'privacy': return renderPrivacyPolicy();
      case 'cookies': return renderCookiesPolicy();
      case 'terms': return renderTermsOfService();
      case 'contact': return renderContact();
      default: return renderMentionsLegales();
    }
  };

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

        <div className="legal-footer">
        </div>
      </motion.div>
    </motion.div>
  );
};

export default LegalPages;
