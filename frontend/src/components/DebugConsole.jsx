import React from 'react';

const DebugConsole = () => {
  React.useEffect(() => {
    // Script de debug intégré

    // Vérifier React
    if (typeof React !== 'undefined') {
    } else {
      console.error('❌ React non chargé');
    }

    // Vérifier les hooks
    if (typeof React !== 'undefined' && React.useState) {
    } else {
      console.error('❌ React Hooks non disponibles');
    }

    // Vérifier localStorage
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
    } catch (e) {
      console.error('❌ localStorage erreur:', e);
    }

  }, []);

  return null; // Composant invisible
};

export default DebugConsole;


