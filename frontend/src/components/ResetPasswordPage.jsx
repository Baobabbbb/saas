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

  useEffect(() => {
    // Vérifier si l'utilisateur est authentifié pour la récupération de mot de passe
    const checkAuthState = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setIsAuthenticated(!!session);

      // Écouter les changements d'authentification
      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        async (event, session) => {
          console.log('🔄 [RESET] État auth changé:', event, !!session);
          setIsAuthenticated(!!session);

          // Si l'utilisateur vient de se connecter via le lien de reset
          if (event === 'PASSWORD_RECOVERY' && session) {
            console.log('✅ [RESET] Session de récupération active');
          }
        }
      );

      return () => subscription.unsubscribe();
    };

    checkAuthState();
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
      console.log('🚀 [RESET] Tentative de mise à jour du mot de passe...');

      // Utiliser Supabase pour mettre à jour le mot de passe
      const { error } = await supabase.auth.updateUser({
        password: newPassword
      });

      if (error) {
        console.error('❌ [RESET] Erreur mise à jour:', error);
        setError(error.message);
      } else {
        console.log('✅ [RESET] Mot de passe mis à jour avec succès');
        setSuccess(true);
        // Rediriger vers la page d'accueil après 3 secondes
        setTimeout(() => {
          window.location.href = '/';
        }, 3000);
      }
    } catch (err) {
      console.error('❌ [RESET] Erreur inattendue:', err);
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
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Entrez votre nouveau mot de passe"
              required
              minLength="6"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirmez votre nouveau mot de passe"
              required
              minLength="6"
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

