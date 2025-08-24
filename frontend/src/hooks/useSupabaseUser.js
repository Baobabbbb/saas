import { useEffect, useState } from "react";

export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fonction pour récupérer les données utilisateur depuis localStorage
    const getUserFromStorage = () => {
      try {
        const userEmail = localStorage.getItem('userEmail');
        const userName = localStorage.getItem('userName');
        const userFirstName = localStorage.getItem('userFirstName');
        
        if (userEmail) {
          return {
            id: 'local-user',
            email: userEmail,
            name: userName || userEmail.split('@')[0],
            firstName: userFirstName || userEmail.split('@')[0]
          };
        }
        return null;
      } catch (error) {
        console.warn('localStorage access error:', error);
        return null;
      }
    };

    // Initialisation avec timeout de sécurité
    const timeoutId = setTimeout(() => {
      console.warn('User initialization timeout - using guest mode');
      setUser(null);
      setLoading(false);
    }, 2000);

    try {
      const localUser = getUserFromStorage();
      clearTimeout(timeoutId);
      setUser(localUser);
      setLoading(false);
    } catch (error) {
      clearTimeout(timeoutId);
      console.warn('User initialization error:', error);
      setUser(null);
      setLoading(false);
    }
  }, []);

  return { user, loading };
}
