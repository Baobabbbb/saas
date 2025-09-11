import { useState, useEffect } from "react";

export default function useSupabaseUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fonction pour charger l'utilisateur de manière sécurisée
    const loadUser = () => {
      try {
        const userEmail = localStorage.getItem('userEmail');
        if (userEmail && userEmail.trim()) {
          const userData = {
            id: 'local-user',
            email: userEmail.trim(),
            name: (localStorage.getItem('userName') || userEmail.split('@')[0] || 'User').trim(),
            firstName: (localStorage.getItem('userFirstName') || userEmail.split('@')[0] || 'User').trim()
          };
          setUser(userData);
        } else {
          setUser(null);
        }
      } catch (error) {
        console.warn('Erreur chargement user:', error.message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    // Délai minimal pour s'assurer que React est prêt
    setTimeout(loadUser, 50);
  }, []);

  return { user, loading };
}
