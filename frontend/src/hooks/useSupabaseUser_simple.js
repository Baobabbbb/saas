import { useEffect, useState } from "react";

// Hook simplifié : localStorage pour l'interface
export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeUser = () => {
      try {
        const userEmail = localStorage.getItem('userEmail');
        const userName = localStorage.getItem('userName');
        const userFirstName = localStorage.getItem('userFirstName');
        
        if (userEmail) {
          setUser({
            email: userEmail,
            name: userName || userEmail.split('@')[0],
            firstName: userFirstName || userName?.split(' ')[0] || userEmail.split('@')[0]
          });
        } else {
          setUser(null);
        }
      } catch (error) {
        console.warn('User initialization error:', error);
        setUser(null);
      }
      setLoading(false);
    };

    // Initialiser immédiatement
    initializeUser();

    // Écouter les changements dans localStorage
    const handleStorageChange = (e) => {
      if (e.key === 'userEmail' || e.key === 'userName') {
        initializeUser();
      }
    };

    // Écouter les événements de stockage
    window.addEventListener('storage', handleStorageChange);

    // Écouter les changements personnalisés (pour les changements dans le même onglet)
    const handleCustomStorageChange = () => {
      initializeUser();
    };

    window.addEventListener('localStorageChanged', handleCustomStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('localStorageChanged', handleCustomStorageChange);
    };
  }, []);

  return { user, loading };
} 