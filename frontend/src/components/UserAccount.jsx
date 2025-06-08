import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './UserAccount.css';

const UserAccount = ({ isLoggedIn, onLogin, onLogout, onRegister }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
    setShowLoginForm(false);
    setShowRegisterForm(false);
  };

  const handleLoginClick = () => {
    setShowLoginForm(true);
    setShowRegisterForm(false);
  };

  const handleRegisterClick = () => {
    setShowRegisterForm(true);
    setShowLoginForm(false);
  };

  const handleLogin = (e) => {
    e.preventDefault();
    onLogin({ email, password });
    setEmail('');
    setPassword('');
    setShowLoginForm(false);
    setShowDropdown(false);
  };

  const handleRegister = (e) => {
    e.preventDefault();
    onRegister({ firstName, lastName, email, password });
    setFirstName('');
    setLastName('');
    setEmail('');
    setPassword('');
    setShowRegisterForm(false);
    setShowDropdown(false);
  };

  const handleLogout = () => {
    onLogout();
    setShowDropdown(false);
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
            {/* Première lettre du nom de l'utilisateur ou icône par défaut */}
            {localStorage.getItem('userName')?.charAt(0).toUpperCase() || 'U'}
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
                  <p>Bonjour, {localStorage.getItem('userName')}</p>
                </div>
                <ul>
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
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserAccount;
