import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './UserAccount.css';
import { signUpWithProfile, signIn, signOut } from '../services/auth';
import AdminPanel from './AdminPanel';

const UserAccount = ({ isLoggedIn, onLogin, onLogout, onRegister }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [showErrorPopup, setShowErrorPopup] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  const [errorPopupMessage, setErrorPopupMessage] = useState('');
  const [userFirstName, setUserFirstName] = useState('');

  // Email de l'administrateur
  const ADMIN_EMAIL = 'fredagathe77@gmail.com';
  
  // Vérifier si l'utilisateur connecté est l'administrateur
  const isAdmin = () => {
    const userEmail = localStorage.getItem('userEmail');
    return userEmail === ADMIN_EMAIL;
  };

  // Effet pour surveiller les changements de firstName dans localStorage
  useEffect(() => {
    const updateUserFirstName = () => {
      const storedFirstName = localStorage.getItem('userFirstName');
      setUserFirstName(storedFirstName || '');
    };

    // Mise à jour initiale
    updateUserFirstName();

    // Surveiller les changements (optionnel si on veut être plus réactif)
    const interval = setInterval(updateUserFirstName, 1000);
    
    return () => clearInterval(interval);
  }, [isLoggedIn]);
  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
    setShowLoginForm(false);
    setShowRegisterForm(false);
    setError('');
    setShowErrorPopup(false);
  };

  const handleLoginClick = () => {
    setShowLoginForm(true);
    setShowRegisterForm(false);
    setError('');
    setShowErrorPopup(false);
  };

  const handleRegisterClick = () => {
    setShowRegisterForm(true);
    setShowLoginForm(false);
    setError('');
    setShowErrorPopup(false);
  };  const handleLogin = async (e) => {
    e.preventDefault();
    const { error } = await signIn({ email, password });
    
    if (error) {
      // Vérifier le type d'erreur selon nos codes personnalisés
      if (error.message === 'WRONG_PASSWORD') {
        // Mauvais mot de passe ou email inexistant - afficher popup d'erreur avec option d'inscription
        setErrorPopupMessage('Les identifiants saisis sont incorrects. Vérifiez votre email et mot de passe, ou inscrivez-vous si vous n\'avez pas encore de compte.');
        setShowErrorPopup(true);
        setError('');
        setPassword(''); // Vider le mot de passe
      } else {
        // Autres erreurs - afficher dans le formulaire
        setError(error.originalMessage || error.message);
      }
    } else {
      setError('');
      // Succès de connexion
      setEmail('');
      setPassword('');
      setShowLoginForm(false);
      setShowDropdown(false);
      
      // Mettre à jour le prénom depuis localStorage
      setTimeout(() => {
        const storedFirstName = localStorage.getItem('userFirstName');
        setUserFirstName(storedFirstName || '');
      }, 100);
      
      // Appeler le callback de connexion pour mettre à jour l'état global
      if (onLogin) {
        onLogin();
      }
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const { error } = await signUpWithProfile({ email, password, firstName, lastName });
    if (error) {
      setError(error.message);    } else {
      setError('');
      // Succès de l'inscription
      setFirstName('');
      setLastName('');
      setEmail('');
      setPassword('');
      setShowRegisterForm(false);
      setShowDropdown(false);
      
      // Mettre à jour le prénom depuis localStorage
      setTimeout(() => {
        const storedFirstName = localStorage.getItem('userFirstName');
        setUserFirstName(storedFirstName || '');
      }, 100);
      
      // Appeler le callback d'inscription pour mettre à jour l'état global
      if (onRegister) {
        onRegister();
      }
    }
  };  const handleLogout = async () => {
    await signOut();
    setShowDropdown(false);
    setShowAdminPanel(false);
    setError('');
    setShowErrorPopup(false);
    setUserFirstName(''); // Réinitialiser le prénom
    // Appeler le callback de déconnexion pour mettre à jour l'état global
    if (onLogout) {
      onLogout();
    }
  };
  const closeErrorPopup = () => {
    setShowErrorPopup(false);
    setErrorPopupMessage('');
  };

  const switchToRegisterFromPopup = () => {
    setShowErrorPopup(false);
    setErrorPopupMessage('');
    setShowLoginForm(false);
    setShowRegisterForm(true);
    setPassword(''); // Vider le mot de passe mais garder l'email
  };

  const handleAdminPanelClick = () => {
    setShowAdminPanel(true);
    setShowDropdown(false);
  };

  const closeAdminPanel = () => {
    setShowAdminPanel(false);
  };

  return (
    <div className="user-account">
      <motion.div 
        className="user-icon"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={toggleDropdown}
      >
        {isLoggedIn ? (
          <div className="avatar">
            {/* Première lettre du prénom de l'utilisateur ou icône par défaut */}
            {userFirstName?.charAt(0).toUpperCase() || localStorage.getItem('userFirstName')?.charAt(0).toUpperCase() || 'U'}
          </div>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
          </svg>
        )}
      </motion.div>

      <AnimatePresence>
        {showDropdown && (
          <motion.div 
            className="dropdown-menu"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {isLoggedIn ? (
              <>
                <div className="user-info">
                  <p>Bonjour, {userFirstName || localStorage.getItem('userFirstName') || 'Utilisateur'}</p>
                </div>
                <ul>
                  {isAdmin() && (
                    <li className="admin-option" onClick={handleAdminPanelClick}>
                      Panneau administrateur
                    </li>
                  )}
                  <li onClick={() => { setShowDropdown(false); window.location.hash = 'historique'; }}>
                    Mon historique
                  </li>
                  <li onClick={handleLogout}>Se déconnecter</li>
                </ul>
              </>
            ) : (
              <>
                <ul>
                  <li onClick={handleLoginClick}>Se connecter</li>
                  <li onClick={handleRegisterClick}>S'inscrire</li>
                </ul>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showLoginForm && (
          <motion.div 
            className="auth-form-container"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            <div className="auth-form">
              <h3>Connexion</h3>
              {/* Affichage de l'erreur ici */}
              {error && <div className="error" style={{ color: "red", marginBottom: 10 }}>{error}</div>}
              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input 
                    type="email" 
                    id="email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    required 
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="password">Mot de passe</label>
                  <input 
                    type="password" 
                    id="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    required 
                  />
                </div>
                <div className="form-actions">
                  <button type="button" onClick={() => setShowLoginForm(false)}>Annuler</button>
                  <button type="submit">Se connecter</button>
                </div>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showRegisterForm && (
          <motion.div 
            className="auth-form-container"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            <div className="auth-form">
              <h3>Inscription</h3>
              {/* Affichage de l'erreur ici */}
              {error && <div className="error" style={{ color: "red", marginBottom: 10 }}>{error}</div>}
              <form onSubmit={handleRegister}>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="firstName">Prénom</label>
                    <input 
                      type="text" 
                      id="firstName" 
                      value={firstName} 
                      onChange={(e) => setFirstName(e.target.value)} 
                      required 
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="lastName">Nom</label>
                    <input 
                      type="text" 
                      id="lastName" 
                      value={lastName} 
                      onChange={(e) => setLastName(e.target.value)} 
                      required 
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="register-email">Email</label>
                  <input 
                    type="email" 
                    id="register-email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    required 
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="register-password">Mot de passe</label>
                  <input 
                    type="password" 
                    id="register-password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    required 
                  />
                </div>
                <div className="form-actions">
                  <button type="button" onClick={() => setShowRegisterForm(false)}>Annuler</button>
                  <button type="submit">S'inscrire</button>
                </div>
              </form>
            </div>          </motion.div>
        )}
      </AnimatePresence>

      {/* Popup d'erreur pour les mots de passe incorrects */}
      <AnimatePresence>
        {showErrorPopup && (
          <motion.div 
            className="error-popup-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div 
              className="error-popup"
              initial={{ opacity: 0, scale: 0.8, y: -50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: -50 }}
              transition={{ duration: 0.3 }}
            >
              <div className="error-popup-header">
                <h4>⚠️ Erreur de connexion</h4>
                <button 
                  className="error-popup-close"
                  onClick={closeErrorPopup}
                >
                  ✕
                </button>
              </div>
              <div className="error-popup-content">
                <p>{errorPopupMessage}</p>
              </div>              <div className="error-popup-actions">
                <button 
                  className="error-popup-btn"
                  onClick={closeErrorPopup}
                >
                  Réessayer
                </button>
                <button 
                  className="error-popup-btn error-popup-btn-secondary"
                  onClick={switchToRegisterFromPopup}
                >
                  S'inscrire
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Panneau Administrateur */}
      <AnimatePresence>
        {showAdminPanel && (
          <AdminPanel onClose={closeAdminPanel} />
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserAccount;
