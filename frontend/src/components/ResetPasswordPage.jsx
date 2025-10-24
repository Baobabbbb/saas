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

  // Initialiser Feather Icons et les event listeners
  useEffect(() => {
    if (window.feather) {
      window.feather.replace();
    }

    // Gestionnaire pour le premier champ (nouveau mot de passe)
    const newPasswordEye = document.querySelector('.password-field .feather-eye');
    const newPasswordEyeOff = document.querySelector('.password-field .feather-eye-off');
    const newPasswordField = document.querySelector('.password-field input[id="newPassword"], .password-field input[id="newPassword"][type="text"]');

    if (newPasswordEye && newPasswordEyeOff && newPasswordField) {
      const handleNewPasswordEyeClick = () => {
        newPasswordEye.style.display = 'none';
        newPasswordEyeOff.style.display = 'block';
        newPasswordField.type = 'text';
        setShowNewPassword(true);
      };

      const handleNewPasswordEyeOffClick = () => {
        newPasswordEyeOff.style.display = 'none';
        newPasswordEye.style.display = 'block';
        newPasswordField.type = 'password';
        setShowNewPassword(false);
      };

      newPasswordEye.addEventListener('click', handleNewPasswordEyeClick);
      newPasswordEyeOff.addEventListener('click', handleNewPasswordEyeOffClick);

      return () => {
        newPasswordEye.removeEventListener('click', handleNewPasswordEyeClick);
        newPasswordEyeOff.removeEventListener('click', handleNewPasswordEyeOffClick);
      };
    }
  }, []);

  // Gestionnaire séparé pour le deuxième champ (confirmation)
  useEffect(() => {
    const confirmPasswordEye = document.querySelectorAll('.password-field .feather-eye')[1];
    const confirmPasswordEyeOff = document.querySelectorAll('.password-field .feather-eye-off')[1];
    const confirmPasswordField = document.querySelector('.password-field input[id="confirmPassword"], .password-field input[id="confirmPassword"][type="text"]');

    if (confirmPasswordEye && confirmPasswordEyeOff && confirmPasswordField) {
      const handleConfirmPasswordEyeClick = () => {
        confirmPasswordEye.style.display = 'none';
        confirmPasswordEyeOff.style.display = 'block';
        confirmPasswordField.type = 'text';
        setShowConfirmPassword(true);
      };

      const handleConfirmPasswordEyeOffClick = () => {
        confirmPasswordEyeOff.style.display = 'none';
        confirmPasswordEye.style.display = 'block';
        confirmPasswordField.type = 'password';
        setShowConfirmPassword(false);
      };

      confirmPasswordEye.addEventListener('click', handleConfirmPasswordEyeClick);
      confirmPasswordEyeOff.addEventListener('click', handleConfirmPasswordEyeOffClick);

      return () => {
        confirmPasswordEye.removeEventListener('click', handleConfirmPasswordEyeClick);
        confirmPasswordEyeOff.removeEventListener('click', handleConfirmPasswordEyeOffClick);
      };
    }
  }, []);

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
            <label className="password-field">
              <input
                type="password"
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Entrez votre nouveau mot de passe"
                required
                minLength="6"
              />
              <div className="password-icon">
                <i data-feather="eye"></i>
                <i data-feather="eye-off"></i>
              </div>
            </label>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
            <label className="password-field">
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirmez votre nouveau mot de passe"
                required
                minLength="6"
              />
              <div className="password-icon">
                <i data-feather="eye"></i>
                <i data-feather="eye-off"></i>
              </div>
            </label>
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

