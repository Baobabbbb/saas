import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './UserAccount.css';
import { signUpWithProfile, signIn, signOut, updateUserProfile, getCurrentUserProfile, deleteUserAccount, resetPassword } from '../services/auth';
import AdminPanel from './AdminPanel';

const UserAccount = ({ isLoggedIn, onLogin, onLogout, onRegister }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  const [userFirstName, setUserFirstName] = useState('');
  
  // Référence pour le composant user-account afin de détecter les clics en dehors
  const userAccountRef = useRef(null);
  
  // États pour le profil utilisateur
  const [profileFirstName, setProfileFirstName] = useState('');
  const [profileLastName, setProfileLastName] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [profileUpdateSuccess, setProfileUpdateSuccess] = useState(false);

  // États pour la réinitialisation du mot de passe
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetEmailSent, setResetEmailSent] = useState(false);

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
      if (isLoggedIn) {
        const storedFirstName = localStorage.getItem('userFirstName');
        setUserFirstName(storedFirstName || '');
      } else {
        // Si pas connecté, vider le firstName
        setUserFirstName('');
      }
    };

    // Mise à jour initiale
    updateUserFirstName();

    // Surveiller les changements seulement si connecté
    let interval;
    if (isLoggedIn) {
      interval = setInterval(updateUserFirstName, 1000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLoggedIn]);

  // useEffect pour fermer le dropdown quand on clique en dehors
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Pour le dropdown du profil, on vérifie si le clic est en dehors du composant principal
      if (userAccountRef.current && !userAccountRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
      
      // Pour les popups (modales), on vérifie si le clic est sur l'overlay ou en dehors du formulaire
      const clickedElement = event.target;
      
      // Si on clique sur l'overlay (auth-form-container) mais pas sur le formulaire (auth-form)
      if (clickedElement.classList.contains('auth-form-container') || 
          clickedElement.classList.contains('error-popup-overlay')) {
        setShowLoginForm(false);
        setShowRegisterForm(false);
        setShowProfileForm(false);
        setShowForgotPassword(false);
        setShowDeleteConfirm(false);
      }
      
      // Si on clique complètement en dehors de toute popup
      const isOutsideAllPopups = !clickedElement.closest('.auth-form-container') && 
                                 !clickedElement.closest('.error-popup-overlay') &&
                                 !clickedElement.closest('.user-account');
      
      if (isOutsideAllPopups) {
        setShowLoginForm(false);
        setShowRegisterForm(false);
        setShowProfileForm(false);
        setShowForgotPassword(false);
        setShowDeleteConfirm(false);
        setShowDropdown(false);
      }
    };

    // Ajouter l'event listener si n'importe quelle popup est ouverte
    if (showDropdown || showLoginForm || showRegisterForm || showProfileForm || showForgotPassword || showDeleteConfirm) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    // Nettoyer l'event listener
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showDropdown, showLoginForm, showRegisterForm, showProfileForm, showForgotPassword, showDeleteConfirm]);
  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
    setShowLoginForm(false);
    setShowRegisterForm(false);
    setShowProfileForm(false);
    setShowForgotPassword(false);
    setError('');
    setResetEmailSent(false);
  };

  const handleProfileClick = async () => {
    setError('');
    setProfileUpdateSuccess(false);
    
    // Charger les données utilisateur depuis Supabase
    const { data, error } = await getCurrentUserProfile();
    
    if (error) {
      // Fallback vers localStorage si erreur
      setProfileFirstName(localStorage.getItem('userFirstName') || '');
      setProfileLastName(localStorage.getItem('userLastName') || '');
      setProfileEmail(localStorage.getItem('userEmail') || '');
      setError('Impossible de charger le profil depuis la base de données');
    } else {
      setProfileFirstName(data.firstName || '');
      setProfileLastName(data.lastName || '');
      setProfileEmail(data.email || '');
    }
    
    setShowProfileForm(true);
    setShowDropdown(false);
  };

  const handleLoginClick = () => {
    setShowLoginForm(true);
    setShowRegisterForm(false);
    setError('');
  };

  const handleRegisterClick = () => {
    setShowRegisterForm(true);
    setShowLoginForm(false);
    setShowProfileForm(false);
    setError('');
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setProfileUpdateSuccess(false);
    
    if (!profileFirstName.trim() || !profileLastName.trim()) {
      setError('Le prénom et le nom sont obligatoires');
      return;
    }
    
    try {
      // Mise à jour du profil dans Supabase
      const { data, error } = await updateUserProfile({
        firstName: profileFirstName.trim(),
        lastName: profileLastName.trim()
      });
      
      if (error) {
        setError('Erreur lors de la mise à jour du profil: ' + error.message);
        return;
      }
      
      // Mettre à jour l'état local
      setUserFirstName(profileFirstName.trim());
      
      // Afficher le message de succès
      setProfileUpdateSuccess(true);
      
      // Masquer le message de succès après 3 secondes
      setTimeout(() => {
        setProfileUpdateSuccess(false);
      }, 3000);
      
    } catch (error) {
      setError('Erreur lors de la mise à jour du profil');
      console.error('Erreur mise à jour profil:', error);
    }
  };  const handleLogin = async (e) => {
    e.preventDefault();
    const { error } = await signIn({ email, password });
    
    if (error) {
      // Afficher l'erreur directement dans le formulaire
      if (error.message === 'WRONG_PASSWORD') {
        setError('Les identifiants saisis sont incorrects. Vérifiez votre email et mot de passe.');
      } else {
        setError(error.originalMessage || error.message);
      }
      setPassword(''); // Vider le mot de passe
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

  // Fonction de validation d'email
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

  // Fonction de validation de mot de passe
  const validatePassword = (password) => {
    // Au moins 6 caractères
    if (password.length < 6) {
      return "Le mot de passe doit contenir au moins 6 caractères";
    }
    
    // Au moins une majuscule
    if (!/[A-Z]/.test(password)) {
      return "Le mot de passe doit contenir au moins une majuscule";
    }
    
    // Au moins un chiffre
    if (!/[0-9]/.test(password)) {
      return "Le mot de passe doit contenir au moins un chiffre";
    }
    
    // Au moins un caractère spécial
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      return "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*...)";
    }
    
    return null; // Pas d'erreur
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    // Validation du format de l'email
    if (!validateEmail(email)) {
      setError('Veuillez saisir une adresse email valide (ex: nom@domaine.com)');
      return;
    }
    
    // Validation des champs requis
    if (!firstName.trim() || !lastName.trim()) {
      setError('Le prénom et le nom sont obligatoires');
      return;
    }
    
    // Validation du mot de passe
    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }
    
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
  };  const handleLogout = () => {
    localStorage.clear();
    window.location.reload();
  };
  const handleAdminPanelClick = () => {
    setShowAdminPanel(true);
    setShowDropdown(false);
  };

  const closeAdminPanel = () => {
    setShowAdminPanel(false);
  };

  const handleDeleteAccount = () => {
    setShowDeleteConfirm(true);
    setDeleteConfirmText('');
    setError('');
  };

  const handleConfirmDelete = async () => {
    if (deleteConfirmText !== 'SUPPRIMER') {
      setError('Veuillez saisir "SUPPRIMER" pour confirmer');
      return;
    }

    try {
      const { data, error } = await deleteUserAccount();
      
      if (error) {
        let errorMessage = 'Erreur lors de la suppression: ' + error.message;
        
        // Gestion spéciale si la fonction RPC n'est pas disponible
        if (error.requiresAdminCleanup) {
          errorMessage = `Suppression partielle effectuée. L'utilisateur ${error.userEmail} (ID: ${error.userId}) doit être supprimé manuellement par l'administrateur dans Supabase.`;
          
          // Fermer les formulaires même en cas d'erreur partielle
          setShowDeleteConfirm(false);
          setShowProfileForm(false);
          setShowDropdown(false);
          
          // Informer le parent de la déconnexion
          if (onLogout) {
            onLogout();
          }
          
          // Afficher l'erreur mais procéder au rechargement
          alert(errorMessage);
          window.location.reload();
          return;
        }
        
        setError(errorMessage);
        return;
      }

      // Fermer tous les formulaires
      setShowDeleteConfirm(false);
      setShowProfileForm(false);
      setShowDropdown(false);

      // Afficher un message de confirmation
      alert(data.message || 'Votre compte a été supprimé avec succès');

      // Informer le composant parent de la déconnexion
      if (onLogout) {
        onLogout();
      }

      // Recharger la page pour nettoyer l'état
      window.location.reload();

    } catch (error) {
      setError('Erreur lors de la suppression du compte');
      console.error('Erreur suppression compte:', error);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
    setDeleteConfirmText('');
    setError('');
  };

  // Fonctions pour la réinitialisation du mot de passe
  const handleForgotPassword = () => {
    setShowForgotPassword(true);
    setShowLoginForm(false);
    setError('');
    setResetEmailSent(false);
    setResetEmail(email); // Pré-remplir avec l'email de connexion si disponible
  };

  const handleSendResetEmail = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!resetEmail.trim()) {
      setError('Veuillez saisir votre adresse email');
      return;
    }

    try {
      const { error } = await resetPassword({ email: resetEmail });
      
      if (error) {
        setError('Erreur lors de l\'envoi de l\'email: ' + error.message);
        return;
      }

      setResetEmailSent(true);
    } catch (error) {
      setError('Erreur lors de l\'envoi de l\'email de réinitialisation');
      console.error('Erreur reset password:', error);
    }
  };

  const handleBackToLogin = () => {
    setShowForgotPassword(false);
    setShowLoginForm(true);
    setResetEmailSent(false);
    setResetEmail('');
    setError('');
  };

  return (
    <div className="user-account" ref={userAccountRef}>
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
                  <p>Bonjour, {userFirstName || 'Visiteur'}</p>
                </div>
                <ul>
                  {isAdmin() && (
                    <motion.li 
                      className="admin-option" 
                      onClick={handleAdminPanelClick}
                      whileHover={{ 
                        scale: 1.02,
                        x: 3,
                        transition: { 
                          type: "spring", 
                          stiffness: 400, 
                          damping: 17 
                        }
                      }}
                      whileTap={{ 
                        scale: 0.98,
                        x: 1,
                        transition: { 
                          type: "spring", 
                          stiffness: 600, 
                          damping: 20 
                        }
                      }}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ 
                        duration: 0.3,
                        ease: "easeOut"
                      }}
                    >
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.1 }}
                      >
                        Panneau administrateur
                      </motion.span>
                    </motion.li>
                  )}
                  <motion.li 
                    onClick={handleProfileClick}
                    whileHover={{ x: 2, transition: { type: "spring", stiffness: 300, damping: 20 } }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Mon compte
                  </motion.li>
                  <motion.li 
                    onClick={() => { setShowDropdown(false); window.location.hash = 'historique'; }}
                    whileHover={{ x: 2, transition: { type: "spring", stiffness: 300, damping: 20 } }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Mon historique
                  </motion.li>
                  <motion.li 
                    onClick={handleLogout}
                    whileHover={{ x: 2, transition: { type: "spring", stiffness: 300, damping: 20 } }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Se déconnecter
                  </motion.li>
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
            onClick={(e) => {
              // Fermer la popup si on clique sur l'overlay (pas sur le formulaire)
              if (e.target === e.currentTarget) {
                setShowLoginForm(false);
              }
            }}
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
                  <div className="forgot-password-section">
                    <button 
                      type="button" 
                      className="link-button register-link"
                      onClick={handleRegisterClick}
                    >
                      S'inscrire
                    </button>
                    <button 
                      type="button" 
                      className="link-button"
                      onClick={handleForgotPassword}
                    >
                      Mot de passe oublié ?
                    </button>
                  </div>
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
            onClick={(e) => {
              // Fermer la popup si on clique sur l'overlay (pas sur le formulaire)
              if (e.target === e.currentTarget) {
                setShowRegisterForm(false);
              }
            }}
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
                  <div className="login-section">
                    <button 
                      type="button" 
                      className="link-button login-link"
                      onClick={handleLoginClick}
                    >
                      Connexion
                    </button>
                  </div>
                </div>
                <div className="form-actions">
                  <button type="button" onClick={() => setShowRegisterForm(false)}>Annuler</button>
                  <button type="submit">S'inscrire</button>
                </div>
              </form>
            </div>          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showProfileForm && (
          <motion.div 
            className="auth-form-container"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => {
              // Fermer la popup si on clique sur l'overlay (pas sur le formulaire)
              if (e.target === e.currentTarget) {
                setShowProfileForm(false);
              }
            }}
          >
            <div className="auth-form">
              <h3>Mon compte</h3>
              {/* Affichage de l'erreur ou du succès */}
              {error && <div className="error" style={{ color: "red", marginBottom: 10 }}>{error}</div>}
              {profileUpdateSuccess && (
                <div className="success" style={{ color: "green", marginBottom: 10 }}>
                  Profil mis à jour avec succès !
                </div>
              )}
              <form onSubmit={handleUpdateProfile}>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="profile-firstName">Prénom</label>
                    <input 
                      type="text" 
                      id="profile-firstName" 
                      value={profileFirstName} 
                      onChange={(e) => setProfileFirstName(e.target.value)} 
                      required 
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="profile-lastName">Nom</label>
                    <input 
                      type="text" 
                      id="profile-lastName" 
                      value={profileLastName} 
                      onChange={(e) => setProfileLastName(e.target.value)} 
                      required 
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="profile-email">Email</label>
                  <input 
                    type="email" 
                    id="profile-email" 
                    value={profileEmail} 
                    disabled
                    style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
                    title="L'email ne peut pas être modifié"
                  />
                  <small style={{ color: '#666', fontSize: '0.8rem' }}>
                    L'email ne peut pas être modifié
                  </small>
                </div>
                <div className="form-actions">
                  <button type="button" onClick={() => setShowProfileForm(false)}>Annuler</button>
                  <button type="submit">Mettre à jour</button>
                </div>
                
                {/* Bouton de suppression de compte */}
                <div className="delete-account-section">
                  <button 
                    type="button" 
                    className="delete-account-btn"
                    onClick={handleDeleteAccount}
                  >
                    Supprimer mon compte
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Popup de confirmation de suppression de compte */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div 
            className="confirm-popup-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div 
              className="confirm-popup"
              initial={{ opacity: 0, scale: 0.8, y: -50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: -50 }}
              transition={{ duration: 0.3 }}
            >
              <div className="confirm-popup-header">
                <h4>⚠️ Confirmation de suppression</h4>
                <button 
                  className="confirm-popup-close"
                  onClick={handleCancelDelete}
                >
                  ✕
                </button>
              </div>
              <div className="confirm-popup-content">
                <p>Pour confirmer la suppression de votre compte, veuillez saisir le mot "SUPPRIMER" ci-dessous :</p>
                <input 
                  type="text" 
                  value={deleteConfirmText} 
                  onChange={(e) => setDeleteConfirmText(e.target.value)} 
                  className="confirm-input"
                />
                {/* Affichage de l'erreur si présente */}
                {error && <div className="error" style={{ color: "red", marginTop: 10 }}>{error}</div>}
              </div>
              <div className="confirm-popup-actions">
                <button 
                  className="confirm-popup-btn"
                  onClick={handleConfirmDelete}
                >
                  Confirmer
                </button>
                <button 
                  className="confirm-popup-btn confirm-popup-btn-secondary"
                  onClick={handleCancelDelete}
                >
                  Annuler
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Popup d'erreur supprimée - erreurs affichées directement dans le formulaire */}

      {/* Modal de confirmation de suppression de compte */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div 
            className="error-popup-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => {
              // Fermer la popup si on clique sur l'overlay (pas sur le formulaire)
              if (e.target === e.currentTarget) {
                setShowDeleteConfirm(false);
              }
            }}
          >
            <motion.div 
              className="error-popup"
              initial={{ opacity: 0, scale: 0.8, y: -50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: -50 }}
              transition={{ duration: 0.3 }}
              style={{ maxWidth: '500px' }}
            >
              <div className="error-popup-header">
                <h4>🗑️ Supprimer mon compte</h4>
                <button 
                  className="error-popup-close"
                  onClick={handleCancelDelete}
                >
                  ✕
                </button>
              </div>
              <div className="error-popup-content">
                <p style={{ marginBottom: '15px' }}>
                  ⚠️ <strong>Cette action est irréversible !</strong>
                </p>
                <p style={{ marginBottom: '15px' }}>
                  En supprimant votre compte, vous perdrez définitivement :
                </p>
                <ul style={{ textAlign: 'left', marginBottom: '20px', paddingLeft: '20px' }}>
                  <li>Vos informations personnelles</li>
                  <li>Toutes vos histoires générées</li>
                  <li>Toutes vos animations créées</li>
                  <li>Votre historique de génération</li>
                  <li>Tous vos contenus sauvegardés</li>
                </ul>
                <p style={{ marginBottom: '15px' }}>
                  Pour confirmer, saisissez <strong>SUPPRIMER</strong> ci-dessous :
                </p>
                <input
                  type="text"
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="Saisissez SUPPRIMER"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    marginBottom: '15px'
                  }}
                />
                {error && <div className="error" style={{ color: "red", marginBottom: 10 }}>{error}</div>}
              </div>
              <div className="error-popup-actions">
                <button 
                  className="error-popup-btn error-popup-btn-secondary"
                  onClick={handleCancelDelete}
                >
                  Annuler
                </button>
                <button 
                  className="error-popup-btn"
                  onClick={handleConfirmDelete}
                  style={{
                    backgroundColor: deleteConfirmText === 'SUPPRIMER' ? '#d73a49' : '#ccc',
                    cursor: deleteConfirmText === 'SUPPRIMER' ? 'pointer' : 'not-allowed'
                  }}
                  disabled={deleteConfirmText !== 'SUPPRIMER'}
                >
                  Supprimer définitivement
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

      {/* Formulaire de réinitialisation du mot de passe */}
      <AnimatePresence>
        {showForgotPassword && (
          <motion.div 
            className="auth-form-container"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => {
              // Fermer la popup si on clique sur l'overlay (pas sur le formulaire)
              if (e.target === e.currentTarget) {
                setShowForgotPassword(false);
              }
            }}
          >
            <div className="auth-form">
              <h3>Réinitialiser le mot de passe</h3>
              {error && <div className="error" style={{ color: "red", marginBottom: 10 }}>{error}</div>}
              
              {!resetEmailSent ? (
                <form onSubmit={handleSendResetEmail}>
                  <p style={{ marginBottom: 16, color: '#666' }}>
                    Saisissez votre adresse email pour recevoir un lien de réinitialisation.
                  </p>
                  <div className="form-group">
                    <label htmlFor="reset-email">Email</label>
                    <input 
                      type="email" 
                      id="reset-email" 
                      value={resetEmail} 
                      onChange={(e) => setResetEmail(e.target.value)} 
                      required 
                    />
                  </div>
                  <div className="form-actions">
                    <button type="button" onClick={handleBackToLogin}>Retour</button>
                    <button type="submit">Envoyer</button>
                  </div>
                </form>
              ) : (
                <div className="reset-success">
                  <div style={{ textAlign: 'center', padding: '20px 0' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
                    <h4 style={{ color: 'green', marginBottom: '16px' }}>Email envoyé !</h4>
                    <p style={{ marginBottom: '16px', color: '#666' }}>
                      Un lien de réinitialisation a été envoyé à <strong>{resetEmail}</strong>
                    </p>
                    <p style={{ marginBottom: '20px', color: '#666', fontSize: '0.9rem' }}>
                      Vérifiez votre boîte mail et cliquez sur le lien pour réinitialiser votre mot de passe.
                    </p>
                    <button 
                      type="button" 
                      onClick={handleBackToLogin}
                      style={{ 
                        background: 'var(--primary)', 
                        color: 'white', 
                        border: 'none', 
                        padding: '10px 20px', 
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      Retour à la connexion
                    </button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserAccount;
