import React from 'react';

const DebugConsole = () => {
  React.useEffect(() => {
    // Script de debug intégré
    console.log('🔍 Debug Frontend FRIDAY');

    // Vérifier React
    if (typeof React !== 'undefined') {
      console.log('✅ React chargé:', React.version);
    } else {
      console.error('❌ React non chargé');
    }

    // Vérifier les hooks
    if (typeof React !== 'undefined' && React.useState) {
      console.log('✅ React Hooks disponibles');
    } else {
      console.error('❌ React Hooks non disponibles');
    }

    // Vérifier localStorage
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      console.log('✅ localStorage fonctionne');
    } catch (e) {
      console.error('❌ localStorage erreur:', e);
    }

    console.log('🎯 Debug terminé');
  }, []);

  return null; // Composant invisible
};

export default DebugConsole;


