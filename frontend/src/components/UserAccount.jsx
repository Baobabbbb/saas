import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './UserAccount.css';
import { supabase } from '../supabaseClient';
import useSupabaseUser from '../hooks/useSupabaseUser';

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

  // Email de l'administrateur
  const ADMIN_EMAIL = 'fredagathe77@gmail.com';
  
  // Vérifier si l'utilisateur connecté est l'administrateur
  const isAdmin = () => {
    return user?.email === ADMIN_EMAIL;
  };

  // AUTHENTIFICATION SUPABASE RÉELLE - Plus de localStorage !
  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');
    setIsAuthenticating(true);
    
    try {
      console.log('🔐 HERBBIE: Tentative de connexion Supabase avec:', email);
      
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password: password.trim(),
      });

      if (error) {
        console.error('❌ HERBBIE: Erreur connexion Supabase:', error.message);
        setError(error.message === 'Invalid login credentials' 
          ? 'Email ou mot de passe incorrect' 
          : error.message);
        return;
      }

      if (data?.user) {
        console.log('✅ HERBBIE: Connexion Supabase réussie:', data.user.email);
        
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
      console.error('❌ HERBBIE: Erreur critique connexion:', error);
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
      console.log('📝 HERBBIE: Tentative d\'inscription Supabase avec:', email);
      
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
        console.error('❌ HERBBIE: Erreur inscription Supabase:', error.message);
        setError(error.message === 'User already registered' 
          ? 'Un compte existe déjà avec cet email' 
          : error.message);
        return;
      }

      if (data?.user) {
        console.log('✅ HERBBIE: Inscription Supabase réussie:', data.user.email);
        
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
      console.error('❌ HERBBIE: Erreur critique inscription:', error);
      setError('Erreur d\'inscription. Réessayez plus tard.');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleSignOut = async () => {
    try {
      console.log('🚪 HERBBIE: Déconnexion Supabase...');
      
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        console.error('❌ HERBBIE: Erreur déconnexion:', error.message);
        setError('Erreur lors de la déconnexion');
        return;
      }
      
      console.log('✅ HERBBIE: Déconnexion réussie');
      
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
      console.error('❌ HERBBIE: Erreur critique déconnexion:', error);
      setError('Erreur lors de la déconnexion');
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(resetEmail.trim(), {
        redirectTo: window.location.origin
      });

      if (error) {
        setError(error.message);
        return;
      }

      setResetEmailSent(true);
      setError('');
      
    } catch (error) {
      setError('Erreur lors de l\'envoi de l\'email de réinitialisation');
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
            <span>👤</span>
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
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={isAuthenticating}
                  />
                  <input
                    type="password"
                    placeholder="Mot de passe"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={isAuthenticating}
                  />
                  {error && <div className="error-message">{error}</div>}
                  <div className="form-buttons">
                    <button type="submit" disabled={isAuthenticating}>
                      {isAuthenticating ? 'Connexion...' : 'Se connecter'}
                    </button>
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
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={isAuthenticating}
                  />
                  <input
                    type="password"
                    placeholder="Mot de passe (min 6 caractères)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                    disabled={isAuthenticating}
                  />
                  {error && <div className="error-message">{error}</div>}
                  <div className="form-buttons">
                    <button type="submit" disabled={isAuthenticating}>
                      {isAuthenticating ? 'Création...' : 'Créer le compte'}
                    </button>
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
                    <input
                      type="email"
                      placeholder="Votre email"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      required
                    />
                    {error && <div className="error-message">{error}</div>}
                    <div className="form-buttons">
                      <button type="submit">Envoyer le lien</button>
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
            <span>{user?.firstName?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || '👤'}</span>
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
                    <button onClick={() => window.open('/admin', '_blank')}>
                      Administration
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
                    // Logique de mise à jour du profil ici
                    console.log('Mise à jour profil:', { profileFirstName, profileLastName });
                  }}>
                    <input
                      type="email"
                      value={profileEmail}
                      disabled
                      placeholder="Email"
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
                      <button type="submit">Mettre à jour</button>
                      <button type="button" onClick={() => setShowProfileForm(false)}>
                        Fermer
                      </button>
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