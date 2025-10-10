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

  // Supprimer un email de l'historique
  const removeEmail = (emailToRemove) => {
    const userKey = user?.id ? `email_history_${user.id}` : 'email_history_guest';
    const updatedHistory = emailHistory.filter(email => email !== emailToRemove);

    setEmailHistory(updatedHistory);
    localStorage.setItem(userKey, JSON.stringify(updatedHistory));

    // Mettre à jour les suggestions filtrées
    setFilteredEmails(prev => prev.filter(email => email !== emailToRemove));
  };

  // Filtrer les emails selon la saisie
  const filterEmails = (input) => {
    if (!input || input.length < 1) {
      setFilteredEmails([]);
      setShowSuggestions(false);
      return;
    }

    const filtered = emailHistory.filter(email =>
      email.toLowerCase().startsWith(input.toLowerCase())
    );
    setFilteredEmails(filtered);
    setShowSuggestions(filtered.length > 0);
  };

  return {
    showSuggestions,
    filteredEmails,
    saveEmail,
    removeEmail,
    filterEmails,
    hideSuggestions: () => setShowSuggestions(false)
  };
};

// Composant EmailInput avec auto-complétion
const EmailInput = ({ value, onChange, placeholder, required, disabled, user, onEmailSubmit }) => {
  const { showSuggestions, filteredEmails, saveEmail, removeEmail, filterEmails, hideSuggestions } = useEmailAutocomplete(user);
  const [inputValue, setInputValue] = useState(value || '');
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        hideSuggestions();
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [hideSuggestions]);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange(e);
    filterEmails(newValue);
    setSelectedIndex(-1);
  };

  const handleEmailSelect = (email) => {
    setInputValue(email);
    onChange({ target: { value: email } });
    hideSuggestions();
    setSelectedIndex(-1);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || filteredEmails.length === 0) {
      if (e.key === 'Enter' && onEmailSubmit) {
        saveEmail(inputValue);
        onEmailSubmit();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev =>
          prev < filteredEmails.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredEmails.length) {
          handleEmailSelect(filteredEmails[selectedIndex]);
        } else if (onEmailSubmit) {
          saveEmail(inputValue);
          onEmailSubmit();
        }
        break;
      case 'Escape':
        hideSuggestions();
        setSelectedIndex(-1);
        break;
    }
  };

  return (
    <div className="email-input-container" ref={containerRef}>
      <input
        ref={inputRef}
        type="email"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        autoComplete="off"
      />
      {showSuggestions && filteredEmails.length > 0 && (
        <div className="email-suggestions google-style">
          {filteredEmails.map((email, index) => (
            <div
              key={index}
              className={`email-suggestion-item ${index === selectedIndex ? 'selected' : ''}`}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div
                className="email-suggestion-content"
                onClick={() => handleEmailSelect(email)}
              >
                {email}
              </div>
              <button
                type="button"
                className="email-suggestion-remove"
                onClick={(e) => {
                  e.stopPropagation();
                  removeEmail(email);
                }}
                onMouseEnter={(e) => e.stopPropagation()}
                title="Supprimer cet email"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmailInput;
