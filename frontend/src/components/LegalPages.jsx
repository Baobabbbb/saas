import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './LegalPages.css';

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
        <h3>Hébergement</h3>
        <div className="info-block">
          <p><strong>Hébergeur :</strong> Railway</p>
          <p><strong>Adresse :</strong> Railway, 1 Sentry Way, San Francisco, CA 94103, États-Unis</p>
          <p><strong>Site web :</strong> <a href="https://railway.app" target="_blank" rel="noopener noreferrer">railway.app</a></p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Propriété intellectuelle</h3>
        <div className="info-block">
          <p>L'ensemble du contenu de ce site (textes, images, vidéos, éléments graphiques, logos, icônes, sons, logiciels) est la propriété exclusive de HERBBIE ou de ses partenaires, sauf mention contraire.</p>
          <p>Toute reproduction, distribution, modification ou exploitation commerciale, même partielle, sans autorisation préalable écrite de HERBBIE est strictement interdite et constituerait une contrefaçon sanctionnée par les articles L.335-2 et suivants du Code de la propriété intellectuelle.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Responsabilité</h3>
        <div className="info-block">
          <p>HERBBIE s'efforce d'assurer l'exactitude et la mise à jour des informations diffusées sur ce site, dont elle se réserve le droit de corriger, à tout moment et sans préavis, le contenu.</p>
          <p>Toutefois, HERBBIE ne peut garantir l'exactitude, la précision ou l'exhaustivité des informations mises à disposition sur ce site. En conséquence, HERBBIE décline toute responsabilité :</p>
          <ul>
            <li>Pour toute imprécision, inexactitude ou omission portant sur des informations disponibles sur le site</li>
            <li>Pour tous dommages résultant d'une intrusion frauduleuse d'un tiers ayant entraîné une modification des informations mises à disposition sur le site</li>
            <li>Et plus généralement pour tous dommages, directs ou indirects, quelles qu'en soient les causes, origines, natures ou conséquences, provoqués à raison de l'accès de quiconque au site ou de l'impossibilité d'y accéder</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>Données personnelles</h3>
        <div className="info-block">
          <p>Conformément à la loi n°78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés, vous disposez d'un droit d'accès, de rectification et de suppression des données vous concernant.</p>
          <p>Pour exercer ce droit, vous pouvez nous contacter par email à l'adresse : contact@herbbie.com</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Cookies</h3>
        <div className="info-block">
          <p>Le site HERBBIE utilise des cookies pour améliorer votre expérience utilisateur et réaliser des statistiques de visite.</p>
          <p>Conformément à la réglementation, vous pouvez refuser le dépôt de cookies en configurant votre navigateur.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>Éditeur du site</h3>
        <div className="info-block">
          <p><strong>Dénomination sociale :</strong> HERBBIE</p>
          <p><strong>Forme juridique :</strong> Auto-entreprise (en cours d'immatriculation)</p>
          <p><strong>Adresse du siège social :</strong> 10 bis rue Félix Arnaudin, 40100 Dax</p>
          <p><strong>Numéro SIRET :</strong> En cours d'attribution</p>
          <p><strong>Directeur de la publication :</strong> Adrien Gaulin</p>
        </div>
      </div>
    </div>
  );

  const renderPrivacyPolicy = () => (
    <div className="legal-content">
      <h2>🔒 Politique de Confidentialité</h2>

      <div className="legal-section">
        <h3>1. Collecte des données personnelles</h3>
        <div className="info-block">
          <p>Lors de votre utilisation du service HERBBIE, nous pouvons collecter les informations suivantes :</p>
          <ul>
            <li><strong>Données de compte :</strong> adresse email, nom d'utilisateur (si inscription)</li>
            <li><strong>Données d'utilisation :</strong> historique des créations, préférences, statistiques d'usage</li>
            <li><strong>Données techniques :</strong> adresse IP, type de navigateur, système d'exploitation</li>
            <li><strong>Contenu généré :</strong> les créations réalisées via notre service (histoires, coloriages, etc.)</li>
          </ul>
          <p>La collecte de ces données est nécessaire pour :</p>
          <ul>
            <li>Fournir nos services de génération de contenu créatif</li>
            <li>Améliorer la qualité de nos services</li>
            <li>Assurer la sécurité de la plateforme</li>
            <li>Respecter nos obligations légales</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>2. Utilisation des données</h3>
        <div className="info-block">
          <p>Les données collectées sont utilisées pour :</p>
          <ul>
            <li><strong>Fournir le service :</strong> génération de contenu personnalisé, sauvegarde des créations</li>
            <li><strong>Amélioration :</strong> analyse des usages pour optimiser l'expérience utilisateur</li>
            <li><strong>Communication :</strong> envoi d'informations relatives au service, support client</li>
            <li><strong>Sécurité :</strong> détection et prévention des fraudes et activités malveillantes</li>
            <li><strong>Obligations légales :</strong> conservation des données requises par la loi</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>3. Partage des données</h3>
        <div className="info-block">
          <p>HERBBIE s'engage à ne pas vendre, louer ou commercialiser vos données personnelles.</p>
          <p>Les données peuvent être partagées uniquement dans les cas suivants :</p>
          <ul>
            <li><strong>Fournisseurs de services :</strong> hébergeurs, prestataires techniques (sous contrat de confidentialité)</li>
            <li><strong>Obligations légales :</strong> sur demande des autorités compétentes</li>
            <li><strong>Protection des droits :</strong> en cas de litige ou contentieux</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>4. Conservation des données</h3>
        <div className="info-block">
          <p>Les données sont conservées pendant la durée nécessaire aux finalités pour lesquelles elles ont été collectées :</p>
          <ul>
            <li><strong>Données de compte :</strong> tant que le compte est actif + 3 ans après inactivation</li>
            <li><strong>Données d'utilisation :</strong> 2 ans à compter de la collecte</li>
            <li><strong>Contenu généré :</strong> tant que le compte est actif</li>
            <li><strong>Données de facturation :</strong> 10 ans (obligation légale)</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>5. Sécurité des données</h3>
        <div className="info-block">
          <p>HERBBIE met en œuvre des mesures techniques et organisationnelles appropriées pour protéger vos données personnelles contre :</p>
          <ul>
            <li>L'accès non autorisé</li>
            <li>L'utilisation illégitime</li>
            <li>La perte ou destruction accidentelle</li>
            <li>Toute forme de traitement illicite</li>
          </ul>
          <p>Ces mesures incluent le chiffrement des données, des contrôles d'accès stricts et des audits réguliers de sécurité.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>6. Vos droits</h3>
        <div className="info-block">
          <p>Conformément au RGPD, vous disposez des droits suivants :</p>
          <ul>
            <li><strong>Droit d'accès :</strong> demander l'accès à vos données personnelles</li>
            <li><strong>Droit de rectification :</strong> demander la correction de données inexactes</li>
            <li><strong>Droit à l'effacement :</strong> demander la suppression de vos données</li>
            <li><strong>Droit à la limitation :</strong> demander la limitation du traitement</li>
            <li><strong>Droit à la portabilité :</strong> demander la récupération de vos données</li>
            <li><strong>Droit d'opposition :</strong> vous opposer au traitement de vos données</li>
          </ul>
          <p>Pour exercer ces droits, contactez-nous à : contact@herbbie.com</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>7. Cookies et technologies similaires</h3>
        <div className="info-block">
          <p>HERBBIE utilise des cookies et technologies similaires pour :</p>
          <ul>
            <li>Assurer le fonctionnement technique du site</li>
            <li>Mémoriser vos préférences</li>
            <li>Réaliser des statistiques d'utilisation</li>
            <li>Améliorer la sécurité</li>
          </ul>
          <p>Vous pouvez gérer vos préférences cookies via les paramètres de votre navigateur.</p>
        </div>
      </div>
    </div>
  );

  const renderCookiesPolicy = () => (
    <div className="legal-content">
      <h2>🍪 Politique des Cookies</h2>

      <div className="legal-section">
        <h3>1. Qu'est-ce qu'un cookie ?</h3>
        <div className="info-block">
          <p>Un cookie est un petit fichier texte déposé sur votre terminal (ordinateur, tablette, smartphone) lors de la visite d'un site internet. Il permet de stocker des informations relatives à votre navigation et d'améliorer votre expérience utilisateur.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>2. Cookies utilisés par HERBBIE</h3>
        <div className="info-block">
          <h4>Cookies essentiels (obligatoires) :</h4>
          <ul>
            <li><strong>Session :</strong> Maintien de votre connexion et sécurité</li>
            <li><strong>Authentification :</strong> Mémorisation de votre identité</li>
            <li><strong>Sécurité :</strong> Protection contre les attaques CSRF</li>
            <li><strong>Préférences :</strong> Mémorisation de vos choix (langue, paramètres)</li>
          </ul>

          <h4>Cookies de fonctionnalité :</h4>
          <ul>
            <li><strong>Historique :</strong> Sauvegarde de vos créations récentes</li>
            <li><strong>Paramètres :</strong> Conservation de vos préférences utilisateur</li>
            <li><strong>Interface :</strong> Adaptation de l'affichage selon vos préférences</li>
          </ul>

          <h4>Cookies analytiques :</h4>
          <ul>
            <li><strong>Statistiques :</strong> Mesure de l'audience et analyse des usages</li>
            <li><strong>Performance :</strong> Analyse des temps de chargement</li>
            <li><strong>Amélioration :</strong> Collecte d'informations pour optimiser le service</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>3. Gestion des cookies</h3>
        <div className="info-block">
          <p>Vous avez plusieurs options pour gérer les cookies :</p>

          <h4>Via votre navigateur :</h4>
          <ul>
            <li><strong>Chrome :</strong> Paramètres → Confidentialité et sécurité → Cookies</li>
            <li><strong>Firefox :</strong> Préférences → Vie privée et sécurité → Cookies</li>
            <li><strong>Safari :</strong> Préférences → Confidentialité → Gérer les cookies</li>
            <li><strong>Edge :</strong> Paramètres → Cookies et autorisations de site</li>
          </ul>

          <h4>Via notre site :</h4>
          <p>Vous pouvez refuser ou accepter les cookies non essentiels en modifiant vos préférences dans les paramètres de votre compte HERBBIE.</p>

          <h4>Durée de conservation :</h4>
          <ul>
            <li><strong>Cookies de session :</strong> Supprimés à la fermeture du navigateur</li>
            <li><strong>Cookies persistants :</strong> Jusqu'à 13 mois maximum</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>4. Finalités des cookies</h3>
        <div className="info-block">
          <h4>Fonctionnement du service :</h4>
          <ul>
            <li>Maintien de la session utilisateur</li>
            <li>Sécurisation des transactions</li>
            <li>Mémorisation des préférences</li>
            <li>Optimisation des performances</li>
          </ul>

          <h4>Amélioration de l'expérience :</h4>
          <ul>
            <li>Personnalisation du contenu</li>
            <li>Sauvegarde des créations en cours</li>
            <li>Adaptation de l'interface utilisateur</li>
          </ul>

          <h4>Analyse et statistiques :</h4>
          <ul>
            <li>Mesure de l'audience</li>
            <li>Analyse des parcours utilisateur</li>
            <li>Détection des problèmes techniques</li>
            <li>Amélioration continue du service</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>5. Cookies tiers</h3>
        <div className="info-block">
          <p>HERBBIE peut faire appel à des services tiers qui déposent leurs propres cookies :</p>
          <ul>
            <li><strong>Services d'analyse :</strong> Google Analytics, Matomo (statistiques)</li>
            <li><strong>Réseaux sociaux :</strong> Boutons de partage (si implémentés)</li>
            <li><strong>Services de paiement :</strong> Stripe, PayPal (si applicable)</li>
            <li><strong>Services d'IA :</strong> OpenAI, Stability AI (pour la génération de contenu)</li>
          </ul>
          <p>Ces tiers sont responsables de leurs propres cookies et de leur politique de confidentialité.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>6. Consentement</h3>
        <div className="info-block">
          <p>En continuant à utiliser le site HERBBIE, vous consentez à l'utilisation des cookies conformément à la présente politique.</p>
          <p>Vous pouvez retirer votre consentement à tout moment en modifiant vos paramètres de cookies ou en nous contactant.</p>
          <p>Note : La désactivation de certains cookies peut affecter le bon fonctionnement du service.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>7. Mise à jour</h3>
        <div className="info-block">
          <p>Cette politique des cookies peut être mise à jour régulièrement pour refléter les évolutions de nos services ou de la réglementation.</p>
          <p>La date de dernière modification est indiquée en bas de cette page.</p>
          <p>En cas de modification substantielle, nous vous en informerons via une notification sur le site.</p>
        </div>
      </div>
    </div>
  );

  const renderTermsOfService = () => (
    <div className="legal-content">
      <h2>📜 Conditions d'utilisation</h2>

      <div className="legal-section">
        <h3>1. Objet du service</h3>
        <div className="info-block">
          <p>HERBBIE est une plateforme de génération de contenu créatif destinée aux enfants, utilisant l'intelligence artificielle pour créer :</p>
          <ul>
            <li>Des histoires personnalisées et éducatives</li>
            <li>Des coloriages et activités créatives</li>
            <li>Du contenu pédagogique adapté à chaque âge</li>
            <li>Des expériences d'apprentissage ludiques</li>
          </ul>
          <p>Le service est conçu pour stimuler l'imagination et la créativité des enfants de manière sécurisée et éducative.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>2. Conditions d'accès</h3>
        <div className="info-block">
          <h4>Âge minimum :</h4>
          <p>Le service HERBBIE est accessible aux enfants de tous âges. Pour les enfants de moins de 13 ans, l'utilisation doit se faire sous la supervision d'un adulte responsable.</p>

          <h4>Inscription :</h4>
          <ul>
            <li>Les utilisateurs peuvent créer un compte gratuit</li>
            <li>L'inscription nécessite une adresse email valide</li>
            <li>Les mots de passe doivent être sécurisés</li>
            <li>Une seule inscription par personne est autorisée</li>
          </ul>

          <h4>Utilisation acceptable :</h4>
          <ul>
            <li>Respect des autres utilisateurs</li>
            <li>Utilisation dans un cadre éducatif et ludique</li>
            <li>Interdiction de générer du contenu inapproprié</li>
            <li>Respect des droits d'auteur et propriété intellectuelle</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>3. Services et fonctionnalités</h3>
        <div className="info-block">
          <h4>Services gratuits :</h4>
          <ul>
            <li>Accès à un nombre limité de génération par jour</li>
            <li>Fonctionnalités de base de création de contenu</li>
            <li>Sauvegarde des créations pendant 30 jours</li>
            <li>Support communautaire</li>
          </ul>

          <h4>Services premium (optionnels) :</h4>
          <ul>
            <li>Générations illimitées</li>
            <li>Sauvegarde permanente des créations</li>
            <li>Fonctionnalités avancées</li>
            <li>Support prioritaire</li>
            <li>Contenu personnalisé avancé</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>4. Règles de conduite</h3>
        <div className="info-block">
          <h4>Interdictions :</h4>
          <ul>
            <li>Générer du contenu violent, haineux ou inapproprié</li>
            <li>Utiliser le service pour harceler ou intimider</li>
            <li>Tenter de contourner les limitations techniques</li>
            <li>Partager des informations personnelles d'autrui</li>
            <li>Utiliser le service à des fins commerciales sans autorisation</li>
            <li>Copier ou reproduire le contenu généré par d'autres utilisateurs</li>
          </ul>

          <h4>Obligations des utilisateurs :</h4>
          <ul>
            <li>Fournir des informations exactes lors de l'inscription</li>
            <li>Respecter les droits d'auteur et la propriété intellectuelle</li>
            <li>Signaler tout contenu inapproprié</li>
            <li>Maintenir la confidentialité de leurs identifiants</li>
            <li>Utiliser le service de manière responsable</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>5. Propriété intellectuelle</h3>
        <div className="info-block">
          <h4>Contenu généré :</h4>
          <p>Le contenu créé via HERBBIE appartient à l'utilisateur qui l'a généré. L'utilisateur peut :</p>
          <ul>
            <li>Télécharger et utiliser ses créations à des fins personnelles</li>
            <li>Partager ses créations dans un cadre familial ou éducatif</li>
            <li>Modifier ses propres créations</li>
          </ul>

          <h4>Plateforme HERBBIE :</h4>
          <p>Tous les éléments de la plateforme (interface, algorithmes, design, etc.) restent la propriété exclusive de HERBBIE.</p>

          <h4>Contenu tiers :</h4>
          <p>Certains éléments peuvent être soumis à des licences tierces (polices, images, sons). L'utilisation doit respecter ces licences.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>6. Limitation de responsabilité</h3>
        <div className="info-block">
          <p>HERBBIE s'efforce de fournir un service de qualité, mais ne peut garantir :</p>
          <ul>
            <li>La disponibilité permanente du service (maintenance, pannes)</li>
            <li>L'absence totale de bugs ou erreurs</li>
            <li>L'adéquation du contenu généré à tous les besoins</li>
            <li>La sécurité absolue contre les cyberattaques</li>
          </ul>

          <p>En aucun cas HERBBIE ne pourra être tenu responsable :</p>
          <ul>
            <li>Des dommages indirects ou consécutifs à l'utilisation du service</li>
            <li>De la perte de données ou de créations</li>
            <li>Des interruptions de service non planifiées</li>
            <li>Des actes de tiers (piratage, virus, etc.)</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>7. Résiliation</h3>
        <div className="info-block">
          <h4>Par l'utilisateur :</h4>
          <p>L'utilisateur peut résilier son compte à tout moment via les paramètres de son profil.</p>

          <h4>Par HERBBIE :</h4>
          <p>HERBBIE peut suspendre ou résilier un compte en cas de :</p>
          <ul>
            <li>Violation grave des conditions d'utilisation</li>
            <li>Utilisation abusive du service</li>
            <li>Non-paiement des services premium</li>
            <li>Inactivité prolongée (plus de 2 ans)</li>
          </ul>

          <h4>Conséquences de la résiliation :</h4>
          <ul>
            <li>Accès immédiat au service suspendu</li>
            <li>Conservation des données pendant 30 jours</li>
            <li>Suppression définitive après ce délai</li>
            <li>Possibilité de réactivation sous conditions</li>
          </ul>
        </div>
      </div>

      <div className="legal-section">
        <h3>8. Modification des conditions</h3>
        <div className="info-block">
          <p>HERBBIE se réserve le droit de modifier ces conditions d'utilisation à tout moment.</p>
          <p>Les modifications seront notifiées aux utilisateurs par email ou notification sur le site.</p>
          <p>La poursuite de l'utilisation du service après notification vaut acceptation des nouvelles conditions.</p>
          <p>En cas de désaccord avec les modifications, l'utilisateur peut résilier son compte.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>9. Droit applicable</h3>
        <div className="info-block">
          <p>Ces conditions d'utilisation sont régies par le droit français.</p>
          <p>Tout litige relatif à l'interprétation ou l'exécution de ces conditions sera soumis aux tribunaux compétents du ressort de Paris.</p>
          <p>En cas de traduction de ces conditions, seule la version française fait foi.</p>
        </div>
      </div>

      <div className="legal-section">
        <h3>10. Contact</h3>
        <div className="info-block">
          <p>Pour toute question relative à ces conditions d'utilisation :</p>
          <ul>
            <li><strong>Email :</strong> contact@herbbie.com</li>
            <li><strong>Objet :</strong> "Question CGU"</li>
            <li><strong>Délai de réponse :</strong> 48-72 heures</li>
          </ul>
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
      console.error('Erreur lors de l\'envoi du message:', error);
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