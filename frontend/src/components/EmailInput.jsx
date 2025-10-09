import React, { useState, useEffect, useRef } from 'react';
import './EmailInput.css';

// Fonction utilitaire pour sauvegarder un email dans localStorage
export const saveEmailToHistory = (email, userId = null) => {
  if (!email || !email.trim()) return;

  const userKey = userId ? `email_history_${userId}` : 'email_history_guest';
  const stored = localStorage.getItem(userKey);
  let emailHistory = [];

  if (stored) {
    try {
      emailHistory = JSON.parse(stored);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique email:', error);
    }
  }

  const updatedHistory = [email, ...emailHistory.filter(e => e !== email)].slice(0, 5); // Max 5 emails
  localStorage.setItem(userKey, JSON.stringify(updatedHistory));
};

// Hook pour gérer l'auto-complétion des emails
export const useEmailAutocomplete = (user) => {
  const [emailHistory, setEmailHistory] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredEmails, setFilteredEmails] = useState([]);

  // Charger l'historique des emails depuis localStorage
  useEffect(() => {
    const userKey = user?.id ? `email_history_${user.id}` : 'email_history_guest';
    const stored = localStorage.getItem(userKey);
    if (stored) {
      try {
        const emails = JSON.parse(stored);
        setEmailHistory(emails);
      } catch (error) {
        console.error('Erreur lors du chargement de l\'historique email:', error);
      }
    }
  }, [user]);

  // Sauvegarder un email dans l'historique
  const saveEmail = (email) => {
    if (!email || !email.trim()) return;

    const userKey = user?.id ? `email_history_${user.id}` : 'email_history_guest';
    const updatedHistory = [email, ...emailHistory.filter(e => e !== email)].slice(0, 5); // Max 5 emails

    setEmailHistory(updatedHistory);
    localStorage.setItem(userKey, JSON.stringify(updatedHistory));
  };

  // Filtrer les emails selon la saisie
  const filterEmails = (input) => {
    if (!input || input.length < 1) {
      setFilteredEmails([]);
      setShowSuggestions(false);
      return;
    }

    const filtered = emailHistory.filter(email =>
      email.toLowerCase().includes(input.toLowerCase())
    );
    setFilteredEmails(filtered);
    setShowSuggestions(filtered.length > 0);
  };

  return {
    showSuggestions,
    filteredEmails,
    saveEmail,
    filterEmails,
    hideSuggestions: () => setShowSuggestions(false)
  };
};

// Composant EmailInput avec auto-complétion
const EmailInput = ({ value, onChange, placeholder, required, disabled, user, onEmailSubmit }) => {
  const { showSuggestions, filteredEmails, saveEmail, filterEmails, hideSuggestions } = useEmailAutocomplete(user);
  const [inputValue, setInputValue] = useState(value || '');
  const inputRef = useRef(null);

  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange(e);
    filterEmails(newValue);
  };

  const handleEmailSelect = (email) => {
    setInputValue(email);
    onChange({ target: { value: email } });
    hideSuggestions();
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && onEmailSubmit) {
      saveEmail(inputValue);
      onEmailSubmit();
    }
  };

  const handleBlur = () => {
    // Délai pour permettre la sélection d'un email
    setTimeout(() => {
      hideSuggestions();
    }, 200);
  };

  return (
    <div className="email-input-container">
      <input
        ref={inputRef}
        type="email"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        autoComplete="email"
      />
      {showSuggestions && (
        <div className="email-suggestions">
          {filteredEmails.map((email, index) => (
            <div
              key={index}
              className="email-suggestion-item"
              onClick={() => handleEmailSelect(email)}
            >
              {email}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmailInput;
