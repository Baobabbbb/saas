import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './LegalPages.css';
import EmailInput from './EmailInput';

const LegalPages = ({ onClose, initialSection = 'mentions' }) => {
  const [activeSection, setActiveSection] = useState(initialSection);
  const [contactForm, setContactForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');

  const sections = [
    { id: 'mentions', title: 'Mentions Légales', icon: '📄' },
    { id: 'terms', title: 'Conditions d\'utilisation', icon: '📜' },
    { id: 'privacy', title: 'Confidentialité', icon: '🔒' },
    { id: 'cookies', title: 'Cookies', icon: '🍪' },
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
        <h3>1. Édition du site</h3>
        <div className="info-block">
          <p>En vertu de l'article 6 de la loi n° 2004-575 du 21 juin 2004 pour la confiance dans l'économie numérique, il est précisé aux utilisateurs du site internet https://herbbie.com l'identité des différents intervenants dans le cadre de sa réalisation et de son suivi :</p>
          <p><strong>Propriétaire et Éditeur du site :</strong> Monsieur Adrien Gaulin</p>
          <p><strong>Statut juridique :</strong> Entrepreneur Individuel (EI)</p>
          <p><strong>Adresse du siège :</strong> 10 B RUE Félix Arnaudin, 40100 Dax, FRANCE</p>
          <p><strong>SIREN :</strong> 992 909 051</p>
          <p><strong>SIRET :</strong> 992 909 051 00011</p>
          <p><strong>Code APE/NAF :</strong> 62.01Z (Programmation informatique)</p>
          <p><strong>Numéro de TVA Intracommunautaire :</strong> FR 46 992909051</p>
          <p><strong>Contact :</strong> Email : <span className="email-protected personal-data">contact@herbbie.com</span></p>
          <p><strong>Directeur de la publication :</strong> <span className="name-protected personal-data">Monsieur Adrien Gaulin</span></p>
        </div>
      </div>

      <div className="legal-section">
        <h3>2. Hébergement</h3>
        <div className="info-block">
          <p>Le site est hébergé par la société Vercel Inc. Siège social : 340 S Lemon Ave #4133, Walnut, CA 91789, États-Unis. Le stockage des données personnelles des utilisateurs est effectué conformément au RGPD, sur des serveurs sécurisés.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>3. Propriété intellectuelle</h3>
        <div className="info-block">
          <p>L'ensemble des éléments figurant sur le site Herbbie (textes, graphismes, logiciels, photographies, images, vidéos, sons, plans, noms, logos, marques, créations et œuvres protégeables diverses, bases de données, etc...) ainsi que le site lui-même, sont protégés par les dispositions du Code de la Propriété Intellectuelle. Monsieur Adrien Gaulin est titulaire exclusif de tous les droits de propriété intellectuelle sur la structure et le contenu du site, à l'exception des éléments générés par les utilisateurs via l'IA (voir CGU). Toute reproduction non autorisée est interdite.</p>
        </div>
      </div>
    </div>
  );

  const renderPrivacyPolicy = () => (
    <div className="legal-content">
      <h2>🔒 Politique de Confidentialité</h2>

      <div className="legal-section">
        <h3>1. Protection de l'Enfance et Photos "Héros"</h3>
        <div className="info-block">
          <p>Nous appliquons une politique de sécurité maximale concernant les photos d'enfants téléchargées pour la fonction "Héros" :</p>
          <ul>
            <li><strong>Usage unique :</strong> La photo sert exclusivement à créer l'avatar vectorisé.</li>
            <li><strong>Purge immédiate :</strong> La photo source originale est automatiquement et définitivement supprimée de nos serveurs dès que l'avatar est généré. Nous ne conservons aucune base de données de visages ("No Face Storage").</li>
            <li><strong>Pas d'entraînement d'IA :</strong> Nous garantissons que les photos des utilisateurs ne sont JAMAIS utilisées pour entraîner nos modèles d'intelligence artificielle ni vendues à des tiers.</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>2. Données collectées</h3>
        <div className="info-block">
          <p><strong>Commande :</strong> Email.</p>
          <p><strong>Paiement :</strong> Géré par Stripe. Herbbie n'a jamais accès à vos coordonnées bancaires complètes.</p>
          <p><strong>Navigation :</strong> Adresse IP et cookies techniques (panier).</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>3. Durée de conservation</h3>
        <div className="info-block">
          <p><strong>Données de facturation :</strong> 10 ans (obligation légale comptable, art. L123-22 du code de commerce).</p>
          <p><strong>Histoires générées :</strong> Conservées sur votre compte client jusqu'à votre demande de suppression, pour vous permettre de les retrouver.</p>
          <p><strong>Compte inactif :</strong> Suppression après 3 ans sans connexion.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>4. Vos Droits</h3>
        <div className="info-block">
          <p>Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et d'effacement de vos données. Pour exercer ce droit ou supprimer votre compte, écrivez à : <span className="email-protected personal-data">contact@herbbie.com</span></p>
        </div>
      </div>
    </div>
  );

  const renderCookiesPolicy = () => (
    <div className="legal-content">
      <h2>🍪 Politique des Cookies</h2>

      <div className="legal-section">
        <h3>Gestion des Cookies sur Herbbie</h3>
        <div className="info-block">
          <h4>1. Qu'est-ce qu'un cookie ?</h4>
          <p>Un cookie est un petit fichier texte déposé sur votre appareil lors de la visite du site.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>2. Les cookies que nous utilisons</h3>
        <div className="info-block">
          <p><strong>Cookies Indispensables (Techniques) :</strong> Ils sont nécessaires au fonctionnement du site (gestion du panier d'achat, maintien de la connexion sécurisée). Ils ne peuvent pas être désactivés.</p>
          <p><strong>Cookies de Mesure d'Audience (Analytiques) :</strong> Nous utilisons des outils anonymisés (comme Vercel Analytics) pour comprendre le trafic sur notre site.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>3. Vos Choix</h3>
        <div className="info-block">
          <p>Lors de votre arrivée sur le site, un bandeau vous permet d'accepter ou de refuser les cookies non essentiels. Vous pouvez modifier ce choix à tout moment. Conformément aux recommandations de la CNIL, le refus des cookies n'empêche pas l'accès au site (sauf fonctionnalités liées au panier d'achat).</p>
        </div>
      </div>
    </div>
  );

  const renderTermsOfService = () => (
    <div className="legal-content">
      <h2>📜 Conditions Générales de Vente et d'Utilisation (CGV/CGU)</h2>

      <div className="legal-section">
        <h3>Date de dernière mise à jour : 01 Décembre 2025</h3>
      </div>

      <div className="legal-section">
        <h3>PRÉAMBULE</h3>
        <div className="info-block">
          <p>Les présentes conditions régissent les ventes de contenus numériques (histoires, BD, coloriages) sur le site herbbie.com par Monsieur Adrien Gaulin (ci-après "l'Éditeur") à toute personne physique consommatrice (ci-après "le Client").</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>AVERTISSEMENT SUR L'INTELLIGENCE ARTIFICIELLE (IA)</h3>
        <div className="info-block">
          <p>Le service repose sur des technologies d'IA générative. Le Client reconnaît être informé que :</p>
          <ul>
            <li>Les résultats sont probabilistes et peuvent comporter des imperfections visuelles (artefacts) ou des incohérences narratives mineures.</li>
            <li>L'acceptation de cet aléa technologique est une condition substantielle du contrat.</li>
            <li>Ces imperfections ne constituent pas un défaut de conformité au sens légal, tant que le contenu respecte le thème global de la commande.</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>ARTICLE 1 : PRIX ET PAIEMENT</h3>
        <div className="info-block">
          <p>Les prix sont indiqués en euros (€) toutes taxes comprises (TTC). Le tarif unitaire par génération est indiqué clairement avant la validation de la commande (ex: 0,70 €). L'Éditeur se réserve le droit de modifier ses prix à tout moment. Le paiement est exigible immédiatement à la commande par carte bancaire via le prestataire sécurisé Stripe.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>ARTICLE 2 : RENONCIATION AU DROIT DE RÉTRACTATION</h3>
        <div className="info-block">
          <p>Le Client est informé que le droit de rétractation de 14 jours (article L.221-18 du Code de la consommation) ne s'applique pas aux contrats de fourniture d'un contenu numérique non fourni sur un support matériel, dont l'exécution a commencé après accord préalable exprès du consommateur et renoncement exprès à son droit de rétractation (Article L.221-28 13°).</p>
          <p>En validant sa commande et en cochant la case prévue à cet effet ("Je renonce à mon droit de rétractation pour un accès immédiat"), le Client :</p>
          <ul>
            <li>Demande expressément l'exécution immédiate du service (génération de l'histoire) avant la fin du délai légal de rétractation.</li>
            <li>Reconnaît expressément perdre son droit de rétractation une fois la commande validée. En conséquence, aucun remboursement ne sera effectué après la validation du paiement, sauf en cas de défaut technique avéré empêchant le téléchargement du fichier.</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>ARTICLE 3 : LICENCE D'UTILISATION DES CONTENUS</h3>
        <div className="info-block">
          <p>L'Éditeur concède au Client une licence d'utilisation personnelle, non exclusive, mondiale et perpétuelle sur les fichiers générés.</p>
          <p><strong>Autorisé :</strong> Usage privé, lecture, impression pour usage familial, partage sur les réseaux sociaux privés.</p>
          <p><strong>Interdit :</strong> Revente du fichier numérique brut, revendication d'un monopole de droit d'auteur empêchant des tiers de générer des contenus similaires. L'Éditeur ne garantit pas la protection par le droit d'auteur des œuvres générées exclusivement par IA, conformément à l'état actuel de la jurisprudence.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>ARTICLE 4 : RESPONSABILITÉ DE L'UTILISATEUR</h3>
        <div className="info-block">
          <p>Le Client est seul responsable des textes (prompts) et des photos qu'il soumet à l'IA. Il s'interdit de soumettre :</p>
          <ul>
            <li>Des contenus illicites, haineux, pornographiques ou diffamatoires.</li>
            <li>Des photos de tiers sans leur consentement.</li>
            <li>Des demandes violant le droit d'auteur de tiers (ex: personnages de marques protégées).</li>
          </ul>
          <p>Le Client garantit l'Éditeur contre toute action judiciaire résultant d'une utilisation illicite du service.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>ARTICLE 5 : MÉDIATION DE LA CONSOMMATION</h3>
        <div className="info-block">
          <p>Conformément aux articles L.616-1 et R.616-1 du code de la consommation, notre entreprise a mis en place un dispositif de médiation de la consommation. L'entité de médiation retenue est : CM2C. En cas de litige, vous pouvez déposer votre réclamation sur son site : <a href="https://www.cm2c.net" target="_blank" rel="noopener noreferrer">https://www.cm2c.net</a></p>
          <p>Ou par voie postale : CM2C, 14 rue Saint Jean, 75017 Paris.</p>
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
      // Envoyer les données à l'API backend
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          firstName: contactForm.firstName,
          lastName: contactForm.lastName,
          email: contactForm.email,
          subject: contactForm.subject,
          message: contactForm.message
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de l\'envoi du message');
      }

      const result = await response.json();

      // Afficher un message de succès
      setSubmitMessage('✅ Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.');

      // Réinitialiser le formulaire
      setContactForm({
        firstName: '',
        lastName: '',
        email: '',
        subject: '',
        message: ''
      });

    } catch (error) {
      setSubmitMessage(`❌ Erreur lors de l'envoi : ${error.message}`);
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
              <label htmlFor="contact-firstName">Prénom *</label>
              <input
                type="text"
                id="contact-firstName"
                value={contactForm.firstName}
                onChange={(e) => handleContactFormChange('firstName', e.target.value)}
                required
                placeholder="Votre prénom"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact-lastName">Nom *</label>
              <input
                type="text"
                id="contact-lastName"
                value={contactForm.lastName}
                onChange={(e) => handleContactFormChange('lastName', e.target.value)}
                required
                placeholder="Votre nom de famille"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact-email">Email *</label>
              <EmailInput
                value={contactForm.email}
                onChange={(e) => handleContactFormChange('email', e.target.value)}
                placeholder="votre.email@exemple.com"
                required
                user={null}
                onEmailSubmit={() => {}}
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
                  Envoi en cours...
                </>
              ) : (
                <>
                  📧 Envoyer l'email
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      <div className="legal-section">
        <h3>Informations de contact</h3>
        <div className="info-block personal-data">
          <p><strong>📧 Email :</strong> <a href="mailto:contact@herbbie.com" className="email-protected"><span className="personal-data">contact@herbbie.com</span></a></p>
          <p><strong>🏢 Nom de l'entreprise :</strong> <span className="protect-personal-info">HERBBIE</span></p>
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