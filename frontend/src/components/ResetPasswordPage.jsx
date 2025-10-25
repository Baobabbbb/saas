import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { supabase } from '../supabaseClient';
import './ResetPasswordPage.css';

const ResetPasswordPage = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isInvalidLink, setIsInvalidLink] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);


  useEffect(() => {
    let timeoutId;
    let subscription;

    const checkAuthState = async () => {
      await new Promise(resolve => setTimeout(resolve, 500));

      const { data: { session } } = await supabase.auth.getSession();
      
      if (session) {
        setIsAuthenticated(true);
        return;
      }

      timeoutId = setTimeout(async () => {
        const { data: { session: currentSession } } = await supabase.auth.getSession();
        if (!currentSession) {
          setIsInvalidLink(true);
        }
      }, 15000);

      const { data: { subscription: sub } } = supabase.auth.onAuthStateChange(
        async (event, session) => {
          if ((event === 'PASSWORD_RECOVERY' || event === 'SIGNED_IN' || event === 'INITIAL_SESSION') && session) {
            setIsAuthenticated(true);
            setIsInvalidLink(false);
            if (timeoutId) clearTimeout(timeoutId);
          }
        }
      );

      subscription = sub;
    };

    checkAuthState();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      if (subscription) subscription.unsubscribe();
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation des mots de passe
    if (newPassword.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      setLoading(false);
      return;
    }

    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword
      });

      if (error) {
        setError(error.message);
      } else {
        setSuccess(true);
        setTimeout(() => {
          window.location.href = '/';
        }, 3000);
      }
    } catch (err) {
      setError('Une erreur est survenue lors de la mise à jour du mot de passe');
    }

    setLoading(false);
  };

  if (success) {
    return (
      <div className="reset-password-page">
        <motion.div
          className="reset-password-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="success-message">
            <div className="success-icon">✅</div>
            <h2>Mot de passe mis à jour !</h2>
            <p>Votre mot de passe a été changé avec succès.</p>
            <p>Vous serez redirigé vers la page d'accueil dans quelques secondes...</p>
          </div>
        </motion.div>
      </div>
    );
  }

  // Si le lien est invalide, afficher un message d'erreur
  if (isInvalidLink) {
    return (
      <div className="reset-password-page">
        <motion.div
          className="reset-password-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="reset-password-header">
            <h1>HERBBIE</h1>
            <h2>Erreur de lien</h2>
          </div>

          <div className="error-message">
            <div className="error-icon">❌</div>
            <h3>Lien de réinitialisation invalide</h3>
            <p>Ce lien de réinitialisation de mot de passe n'est pas valide ou a expiré.</p>
            <p>Veuillez demander un nouveau lien de réinitialisation.</p>
          </div>

          <div className="reset-password-footer">
            <a href="/">Retour à l'accueil</a>
          </div>
        </motion.div>
      </div>
    );
  }

  // Si l'utilisateur n'est pas authentifié, afficher un message d'attente
  if (!isAuthenticated) {
    return (
      <div className="reset-password-page">
        <motion.div
          className="reset-password-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="reset-password-header">
            <h1>HERBBIE</h1>
            <h2>Réinitialiser votre mot de passe</h2>
          </div>

          <div className="waiting-message">
            <div className="loading-spinner"></div>
            <p>Vérification de votre lien de réinitialisation...</p>
            <p className="waiting-subtitle">
              Si cette page ne se met pas à jour automatiquement, assurez-vous d'avoir cliqué sur le lien complet dans votre email.
            </p>
          </div>

          <div className="reset-password-footer">
            <a href="/">Retour à l'accueil</a>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="reset-password-page">
      <motion.div
        className="reset-password-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="reset-password-header">
          <h1>HERBBIE</h1>
          <h2>Réinitialiser votre mot de passe</h2>
        </div>

        <form onSubmit={handleSubmit} className="reset-password-form">
          <div className="form-group">
            <label htmlFor="newPassword">Nouveau mot de passe</label>
            <input
              type={showNewPassword ? "text" : "password"}
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Entrez votre nouveau mot de passe"
              required
              minLength="6"
              className={`password-input ${showNewPassword ? 'password-visible' : ''}`}
              onClick={(e) => {
                // Toggle visibility when clicking on the right side of the input
                const rect = e.currentTarget.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                if (clickX > rect.width - 40) { // Last 40px of input
                  e.preventDefault();
                  setShowNewPassword(!showNewPassword);
                }
              }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
            <input
              type={showConfirmPassword ? "text" : "password"}
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirmez votre nouveau mot de passe"
              required
              minLength="6"
              className={`password-input ${showConfirmPassword ? 'password-visible' : ''}`}
              onClick={(e) => {
                // Toggle visibility when clicking on the right side of the input
                const rect = e.currentTarget.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                if (clickX > rect.width - 40) { // Last 40px of input
                  e.preventDefault();
                  setShowConfirmPassword(!showConfirmPassword);
                }
              }}
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="reset-button"
            disabled={loading}
          >
            {loading ? 'Mise à jour...' : 'Mettre à jour le mot de passe'}
          </button>
        </form>

        <div className="reset-password-footer">
          <a href="/">Retour à l'accueil</a>
        </div>
      </motion.div>
    </div>
  );
};

export default ResetPasswordPage;

