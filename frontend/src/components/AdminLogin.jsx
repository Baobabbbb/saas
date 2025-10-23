import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import './AdminLogin.css';
import EmailInput, { saveEmailToHistory } from './EmailInput';

const AdminLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { signIn } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await signIn(email, password);
      // Sauvegarder l'email dans l'historique
      saveEmailToHistory(email.trim());
      // La redirection se fait automatiquement via le contexte d'authentification
    } catch (err) {
      setError(err.message || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <motion.div
        className="login-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="login-header">
          <div className="login-logo">
            <div className="login-logo-text">
              <h1>HERBBIE</h1>
              <span>Administration</span>
            </div>
          </div>
          <h2>Connexion Administrateur</h2>
          <p>Accès réservé aux administrateurs HERBBIE</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {error && (
            <motion.div
              className="login-error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2 }}
            >
              <span>⚠️</span> {error}
            </motion.div>
          )}

          <div className="login-field">
            <label htmlFor="email">Email administrateur</label>
            <EmailInput
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@herbbie.com"
              required
              disabled={loading}
              user={null}
              onEmailSubmit={() => {}}
            />
          </div>

          <div className="login-field">
            <label htmlFor="password">Mot de passe</label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={loading}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
                aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
              >
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading || !email || !password}
          >
            {loading ? (
              <>
                <div className="login-spinner"></div>
                Connexion en cours...
              </>
            ) : (
              'Se connecter'
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>
            🔒 Accès sécurisé - Seuls les administrateurs peuvent se connecter
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminLogin;

