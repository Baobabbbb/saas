import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './UserAccount.css';

import useSupabaseUser from '../hooks/useSupabaseUser';

const UserAccount = ({ isLoggedIn, onLogin, onLogout, onRegister }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [showProfileForm, setShowProfileForm] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  
  // Utiliser le hook useSupabaseUser simplifié
  const { user, loading } = useSupabaseUser();
  
  // Utiliser la prop isLoggedIn du parent pour déterminer l'état de connexion
  const isUserLoggedIn = isLoggedIn || !!user;
  
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
    return user?.email === ADMIN_EMAIL;
  };

  // Fonctions d'authentification simplifiées avec localStorage
  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      // Simulation d'authentification simple
      if (email && password) {
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userName', email.split('@')[0]);
        localStorage.setItem('userFirstName', email.split('@')[0]);
        
        // Recharger la page pour mettre à jour l'état
        window.location.reload();
      } else {
        setError('Veuillez remplir tous les champs');
      }
    } catch (error) {
      setError('Erreur de connexion');
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      if (email && password && firstName && lastName) {
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userName', `${firstName} ${lastName}`);
        localStorage.setItem('userFirstName', firstName);
        localStorage.setItem('userLastName', lastName);
        
        // Recharger la page pour mettre à jour l'état
        window.location.reload();
      } else {
        setError('Veuillez remplir tous les champs');
      }
    } catch (error) {
      setError('Erreur d\'inscription');
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    localStorage.removeItem('userFirstName');
    localStorage.removeItem('userLastName');
    
    // Recharger la page pour mettre à jour l'état
    window.location.reload();
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      if (profileFirstName && profileLastName) {
        localStorage.setItem('userName', `${profileFirstName} ${profileLastName}`);
        localStorage.setItem('userFirstName', profileFirstName);
        localStorage.setItem('userLastName', profileLastName);
        
        setProfileUpdateSuccess(true);
        setTimeout(() => {
          setProfileUpdateSuccess(false);
          setShowProfileForm(false);
        }, 2000);
        
        // Recharger la page pour mettre à jour l'état
        window.location.reload();
      } else {
        setError('Veuillez remplir tous les champs');
      }
    } catch (error) {
      setError('Erreur de mise à jour du profil');
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText === 'SUPPRIMER') {
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      localStorage.removeItem('userFirstName');
      localStorage.removeItem('userLastName');
      
      // Recharger la page pour mettre à jour l'état
      window.location.reload();
    } else {
      setError('Veuillez taper SUPPRIMER pour confirmer');
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      if (resetEmail) {
        setResetEmailSent(true);
        setTimeout(() => {
          setResetEmailSent(false);
          setShowForgotPassword(false);
        }, 3000);
      } else {
        setError('Veuillez entrer votre email');
      }
    } catch (error) {
      setError('Erreur d\'envoi d\'email');
    }
  };

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
    setShowDeleteConfirm(false);
  };

  // Charger les données du profil quand l'utilisateur est connecté
  useEffect(() => {
    if (user) {
      setProfileFirstName(user.firstName || '');
      setProfileLastName(user.lastName || '');
      setProfileEmail(user.email || '');
    }
  }, [user]);

  // Afficher un indicateur de chargement si nécessaire
  if (loading) {
    return (
      <div className="user-account">
        <div className="user-avatar loading">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-account" ref={userAccountRef}>
      <motion.div 
        className="user-icon"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={toggleDropdown}
      >
        {isUserLoggedIn ? (
          <div className="avatar">
            {/* Première lettre du prénom de l'utilisateur ou icône par défaut */}
            {user?.name?.charAt(0).toUpperCase() || 'U'}
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
            {isUserLoggedIn ? (
              <>
                <div className="user-info">
                  <p>Bonjour {user?.firstName || user?.name?.split(' ')[0] || 'Visiteur'}</p>
                </div>
                <ul>
                  {isAdmin() && (
                    <motion.li 
                      className="admin-option" 
                      onClick={() => { setShowDropdown(false); window.open('http://192.168.1.19:5174', '_blank'); }}
                      whileHover={{ x: 2, transition: { type: "spring", stiffness: 300, damping: 20 } }}
                      whileTap={{ scale: 0.98 }}
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
                    onClick={() => { setShowDropdown(false); window.location.hash = 'historique'; }}
                    whileHover={{ x: 2, transition: { type: "spring", stiffness: 300, damping: 20 } }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Mon historique
                  </motion.li>
                  <motion.li 
                    onClick={handleSignOut}
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
                  <li onClick={() => { setShowDropdown(false); setShowLoginForm(true); }}>Se connecter</li>
                  <li onClick={() => { setShowDropdown(false); setShowRegisterForm(true); }}>S'inscrire</li>
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
              <form onSubmit={handleSignIn}>
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
                    autoComplete="new-password"
                    required 
                  />
                  <div className="forgot-password-section">
                    <button 
                      type="button" 
                      className="link-button register-link"
                      onClick={() => { setShowLoginForm(false); setShowRegisterForm(true); }}
                    >
                      S'inscrire
                    </button>
                    <button 
                      type="button" 
                      className="link-button"
                      onClick={() => { setShowLoginForm(false); setShowForgotPassword(true); }}
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
              <form onSubmit={handleSignUp}>
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
                    autoComplete="new-password"
                    required 
                  />
                  <div className="login-section">
                    <button 
                      type="button" 
                      className="link-button login-link"
                      onClick={() => { setShowRegisterForm(false); setShowLoginForm(true); }}
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
                    onClick={() => { setShowProfileForm(false); setShowDeleteConfirm(true); }}
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
                  onClick={() => { setShowDeleteConfirm(false); setDeleteConfirmText(''); }}
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
                  onClick={handleDeleteAccount}
                >
                  Confirmer
                </button>
                <button 
                  className="confirm-popup-btn confirm-popup-btn-secondary"
                  onClick={() => { setShowDeleteConfirm(false); setDeleteConfirmText(''); }}
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
                  onClick={() => { setShowDeleteConfirm(false); setDeleteConfirmText(''); }}
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
                  onClick={() => { setShowDeleteConfirm(false); setDeleteConfirmText(''); }}
                >
                  Annuler
                </button>
                <button 
                  className="error-popup-btn"
                  onClick={handleDeleteAccount}
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
                <form onSubmit={handleResetPassword}>
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
                    <button type="button" onClick={() => { setShowForgotPassword(false); setShowLoginForm(true); }}>Retour</button>
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
                      onClick={() => { setShowForgotPassword(false); setShowLoginForm(true); }}
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
