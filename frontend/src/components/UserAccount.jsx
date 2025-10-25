import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './UserAccount.css';
import { supabase } from '../supabaseClient';
import useSupabaseUser from '../hooks/useSupabaseUser';
import { updateUserProfile } from '../services/profileService';
import { resetPassword as resetPasswordService } from '../services/auth';
import EmailInput, { saveEmailToHistory } from './EmailInput';

const UserAccount = ({ isLoggedIn, onLogin, onLogout, onRegister, onOpenHistory }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [showProfileForm, setShowProfileForm] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  
  // Utiliser le hook useSupabaseUser
  const { user, loading } = useSupabaseUser();
  
  // L'utilisateur est connecté si nous avons un objet user
  const isUserLoggedIn = !!user && !loading;
  
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
  const [isAdminUser, setIsAdminUser] = useState(false);

  // États pour la visibilité des mots de passe
  const [showPassword, setShowPassword] = useState(false);
  const [showSignupPassword, setShowSignupPassword] = useState(false);


  // Vérifier si l'utilisateur connecté est administrateur (en vérifiant le rôle dans la base)
  useEffect(() => {
    const checkAdminRole = async () => {
      if (!user || !user.id) {
        setIsAdminUser(false);
        return;
      }

      try {
        // Vérifier le rôle dans la table profiles
        const { data: profile, error } = await supabase
          .from('profiles')
          .select('role')
          .eq('id', user.id)
          .single();

        if (error) {
          setIsAdminUser(false);
          return;
        }

        const isAdmin = profile?.role === 'admin' || profile?.role === 'super_admin';
        setIsAdminUser(isAdmin);
      } catch (error) {
        setIsAdminUser(false);
      }
    };

    checkAdminRole();
  }, [user]);

  // Fonction helper pour vérifier si admin (synchrone)
  const isAdmin = () => {
    return isAdminUser;
  };

  // AUTHENTIFICATION SUPABASE RÉELLE - Plus de localStorage !
  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');
    setIsAuthenticating(true);
    
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password: password.trim(),
      });

      if (error) {
        setError(error.message === 'Invalid login credentials' 
          ? 'Email ou mot de passe incorrect' 
          : error.message);
        return;
      }

      if (data?.user) {

        // Sauvegarder l'email dans l'historique
        saveEmailToHistory(email.trim());

        // Fermer les formulaires
        setShowLoginForm(false);
        setShowDropdown(false);

        // Réinitialiser les champs
        setEmail('');
        setPassword('');

        // Informer le parent si nécessaire
        if (onLogin) onLogin(data.user);
        
      }
    } catch (error) {
      setError('Erreur de connexion. Vérifiez vos identifiants.');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    setIsAuthenticating(true);
    
    try {
      
      const { data, error } = await supabase.auth.signUp({
        email: email.trim(),
        password: password.trim(),
        options: {
          data: {
            firstName: firstName.trim(),
            lastName: lastName.trim(),
            name: `${firstName.trim()} ${lastName.trim()}`
          }
        }
      });

      if (error) {
        setError(error.message === 'User already registered'
          ? 'Un compte existe déjà avec cet email'
          : error.message);
        return;
      }

      if (data?.user) {

        // Sauvegarder l'email dans l'historique
        saveEmailToHistory(email.trim());

        // Vérifier si l'email nécessite une confirmation
        if (!data.session) {
          setError('Un email de confirmation a été envoyé. Vérifiez votre boîte mail.');
        } else {
          // Connexion immédiate réussie
          setShowRegisterForm(false);
          setShowDropdown(false);

          // Réinitialiser les champs
          setEmail('');
          setPassword('');
          setFirstName('');
          setLastName('');

          // Informer le parent si nécessaire
          if (onRegister) onRegister(data.user);
        }
      }
    } catch (error) {
      setError('Erreur d\'inscription. Réessayez plus tard.');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        setError('Erreur lors de la déconnexion');
        return;
      }
      
      // Nettoyer les états locaux
      setShowDropdown(false);
      setShowProfileForm(false);
      
      // Nettoyer localStorage (au cas où)
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      localStorage.removeItem('userFirstName');
      localStorage.removeItem('userLastName');
      localStorage.removeItem('friday_supabase_user');
      
      // Informer le parent si nécessaire
      if (onLogout) onLogout();
      
      // Recharger la page pour reset complet
      window.location.reload();
      
    } catch (error) {
      setError('Erreur lors de la déconnexion');
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');

    // Afficher immédiatement la popup de succès
    setResetEmailSent(true);
    setError('');

    // Sauvegarder l'email dans l'historique immédiatement
    saveEmailToHistory(resetEmail.trim());

    try {
      const { data, error } = await resetPasswordService({ email: resetEmail.trim() });

      if (error) {
        setResetEmailSent(false);
        setError(error.message || 'Erreur lors de l\'envoi de l\'email');
        return;
      }

    } catch (error) {
      setResetEmailSent(false);
      setError('Erreur lors de l\'envoi de l\'email de réinitialisation');
    }
  };

  // Fonction pour recharger les données utilisateur depuis la base
  const reloadUserData = async () => {
    if (!user || !user.id) return;

    try {
      // Récupérer le profil mis à jour depuis la base
      const { data: profile, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();

      if (!error && profile) {
        // Mettre à jour les champs du formulaire avec les données fraîchement récupérées
        setProfileEmail(profile.email || user.email || '');
        setProfileFirstName(profile.prenom || '');
        setProfileLastName(profile.nom || '');
      }
      } catch (error) {
        // Erreur silencieuse - pas critique
      }
  };

  // Charger les données du profil depuis Supabase
  useEffect(() => {
    if (user) {
      setProfileEmail(user.email || '');
      setProfileFirstName(user.firstName || user.user_metadata?.firstName || '');
      setProfileLastName(user.lastName || user.user_metadata?.lastName || '');
    }
  }, [user]);

  // Détecter les clics en dehors du composant
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userAccountRef.current && !userAccountRef.current.contains(event.target)) {
        setShowDropdown(false);
        setShowLoginForm(false);
        setShowRegisterForm(false);
        setShowProfileForm(false);
        setShowForgotPassword(false);
        setError('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Affichage conditionnel basé sur l'état de chargement et d'authentification
  if (loading) {
    return (
      <div className="user-account" ref={userAccountRef}>
        <div className="user-avatar">
          <span>⏳</span>
        </div>
      </div>
    );
  }

  return (
    <div className="user-account" ref={userAccountRef}>
      {!isUserLoggedIn ? (
        <>
          <div className="user-avatar" onClick={() => setShowDropdown(!showDropdown)}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </div>

          <AnimatePresence>
            {showDropdown && (
              <motion.div
                className="user-dropdown"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="dropdown-actions">
                  <button onClick={() => {
                    setShowDropdown(false);
                    setShowLoginForm(true);
                    setError('');
                  }}>
                    Se connecter
                  </button>
                  <button onClick={() => {
                    setShowDropdown(false);
                    setShowRegisterForm(true);
                    setError('');
                  }}>
                    Créer un compte
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence>
            {showLoginForm && (
              <motion.div
                className="auth-form-container"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                onClick={() => setShowLoginForm(false)}
              >
                <motion.div
                  className="auth-form"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  onClick={(e) => e.stopPropagation()}
                >
                <h3>Connexion</h3>
                <form onSubmit={handleSignIn}>
                  <EmailInput
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                    disabled={isAuthenticating}
                    user={null}
                    onEmailSubmit={() => {}}
                  />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Mot de passe"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={isAuthenticating}
                    className={`password-input ${showPassword ? 'password-visible' : ''}`}
                    onClick={(e) => {
                      // Toggle visibility when clicking on the right side of the input
                      const rect = e.currentTarget.getBoundingClientRect();
                      const clickX = e.clientX - rect.left;
                      if (clickX > rect.width - 40) { // Last 40px of input
                        e.preventDefault();
                        setShowPassword(!showPassword);
                      }
                    }}
                  />
                  {error && <div className="error-message">{error}</div>}
                  <div className="form-buttons">
                    <button
                      type="button"
                      onClick={() => {
                        setShowLoginForm(false);
                        setShowRegisterForm(true);
                        setError('');
                      }}
                      disabled={isAuthenticating}
                    >
                      Créer un compte
                    </button>
                    <button type="submit" disabled={isAuthenticating}>
                      {isAuthenticating ? 'Connexion...' : 'Se connecter'}
                    </button>
                  </div>
                  <button
                    type="button"
                    className="forgot-password-link"
                    onClick={() => {
                      setShowLoginForm(false);
                      setShowForgotPassword(true);
                      setError('');
                    }}
                    disabled={isAuthenticating}
                  >
                    Mot de passe oublié ?
                  </button>
                </form>
                </motion.div>
              </motion.div>
            )}

            {showRegisterForm && (
              <motion.div
                className="auth-form-container"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                onClick={() => setShowRegisterForm(false)}
              >
                <motion.div
                  className="auth-form"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  onClick={(e) => e.stopPropagation()}
                >
                <h3>Créer un compte</h3>
                <form onSubmit={handleSignUp}>
                  <input
                    type="text"
                    placeholder="Prénom"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                    disabled={isAuthenticating}
                  />
                  <input
                    type="text"
                    placeholder="Nom"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                    disabled={isAuthenticating}
                  />
                  <EmailInput
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                    disabled={isAuthenticating}
                    user={null}
                    onEmailSubmit={() => {}}
                  />
                  <div className="password-input-container">
                    <input
                      type={showSignupPassword ? "text" : "password"}
                      placeholder="Mot de passe (min 6 caractères)"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      minLength={6}
                      disabled={isAuthenticating}
                      className="password-input"
                    />
                    <button
                      type="button"
                      className="password-toggle-btn"
                      onClick={() => setShowSignupPassword(!showSignupPassword)}
                      disabled={isAuthenticating}
                      aria-label={showSignupPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                    >
                      {showSignupPassword ? (
                        <svg className="password-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                          <line x1="1" y1="1" x2="23" y2="23"></line>
                        </svg>
                      ) : (
                        <svg className="password-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                          <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                      )}
                    </button>
                  </div>
                  {error && <div className="error-message">{error}</div>}
                  <div className="form-buttons">
                    <button
                      type="button"
                      onClick={() => {
                        setShowRegisterForm(false);
                        setShowLoginForm(true);
                        setError('');
                      }}
                      disabled={isAuthenticating}
                    >
                      Déjà un compte ?
                    </button>
                    <button type="submit" disabled={isAuthenticating}>
                      {isAuthenticating ? 'Création...' : 'Créer le compte'}
                    </button>
                  </div>
                </form>
                </motion.div>
              </motion.div>
            )}

            {showForgotPassword && (
              <motion.div
                className="auth-form-container"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                onClick={() => setShowForgotPassword(false)}
              >
                <motion.div
                  className="auth-form"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  onClick={(e) => e.stopPropagation()}
                >
                <h3>Réinitialiser le mot de passe</h3>
                {!resetEmailSent ? (
                  <form onSubmit={handleResetPassword}>
                    <EmailInput
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      placeholder="Votre email"
                      required
                      user={null}
                      onEmailSubmit={() => {}}
                    />
                    {error && <div className="error-message">{error}</div>}
                    <div className="form-buttons">
                      <button
                        type="button"
                        onClick={() => {
                          setShowForgotPassword(false);
                          setShowLoginForm(true);
                          setError('');
                        }}
                      >
                        Retour à la connexion
                      </button>
                      <button type="submit">Envoyer le lien</button>
                    </div>
                  </form>
                ) : (
                  <div className="success-message">
                    <p>Un email de réinitialisation a été envoyé à {resetEmail}</p>
                    <button
                      onClick={() => {
                        setShowForgotPassword(false);
                        setShowLoginForm(true);
                        setResetEmailSent(false);
                        setResetEmail('');
                      }}
                    >
                      Retour à la connexion
                    </button>
                  </div>
                )}
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </>
      ) : (
        <>
          <div className="user-avatar" onClick={() => setShowDropdown(!showDropdown)}>
            <span className="user-initial">{user?.firstName?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || '👤'}</span>
          </div>

          <AnimatePresence>
            {showDropdown && (
              <motion.div
                className="user-dropdown"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="user-info">
                  <div className="user-name">{user?.firstName || user?.name || user?.email?.split('@')[0]}</div>
                  <div className="user-email">{user?.email}</div>
                </div>
                
                <div className="dropdown-actions">
                  {isAdmin() && (
                    <button onClick={() => {
                      // Accès direct au panneau d'administration intégré avec auto-auth dans un nouvel onglet
                      window.open('/ilmysv6iepwepoa4tj2k?auth=auto', '_blank');
                    }}>
                      ⚙️ Administration
                    </button>
                  )}
                  
                  <button onClick={() => {
                    setShowDropdown(false);
                    setShowProfileForm(true);
                  }}>
                    Mon profil
                  </button>
                  
                  <button onClick={() => {
                    setShowDropdown(false);
                    if (onOpenHistory) onOpenHistory();
                  }}>
                    Mon historique
                  </button>
                  
                  <button onClick={handleSignOut} className="logout-button">
                    Se déconnecter
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Formulaire de profil utilisateur */}
          <AnimatePresence>
            {showProfileForm && (
              <motion.div
                className="auth-form-container"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                onClick={() => setShowProfileForm(false)}
              >
                <motion.div
                  className="auth-form profile-form"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <h3>Mon profil</h3>
                  <form onSubmit={async (e) => {
                    e.preventDefault();
                    setError('');

                    try {
                      await updateUserProfile(user.id, {
                        firstName: profileFirstName.trim(),
                        lastName: profileLastName.trim()
                      });

                      // Recharger immédiatement les données pour refléter les changements dans le formulaire
                      await reloadUserData();

                      setProfileUpdateSuccess(true);
                      setTimeout(() => setProfileUpdateSuccess(false), 3000);

                    } catch (error) {
                      console.error('Erreur mise à jour profil:', error);
                      setError('Erreur lors de la mise à jour du profil');
                    }
                  }}>
                    <EmailInput
                      value={profileEmail}
                      onChange={(e) => setProfileEmail(e.target.value)}
                      placeholder="Email"
                      disabled
                      user={user}
                      onEmailSubmit={() => {}}
                    />
                    <input
                      type="text"
                      placeholder="Prénom"
                      value={profileFirstName}
                      onChange={(e) => setProfileFirstName(e.target.value)}
                    />
                    <input
                      type="text"
                      placeholder="Nom"
                      value={profileLastName}
                      onChange={(e) => setProfileLastName(e.target.value)}
                    />
                    
                    {error && <div className="error-message">{error}</div>}
                    {profileUpdateSuccess && <div className="success-message">Profil mis à jour avec succès !</div>}
                    
                    <div className="form-buttons">
                      <button type="button" onClick={() => setShowProfileForm(false)}>
                        Fermer
                      </button>
                      <button type="submit">Mettre à jour</button>
                    </div>
                  </form>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}
    </div>
  );
};

export default UserAccount;