import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/adminAuthService';

// Créer le contexte d'authentification
const AuthContext = createContext();

// Hook personnalisé pour utiliser le contexte d'authentification
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};

// Provider du contexte d'authentification
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  // Initialiser l'écouteur d'authentification au montage
  useEffect(() => {
    let subscription;

    const initAuth = async () => {
      try {
        // Vérifier s'il y a une session existante
        const currentSession = await authService.getCurrentSession();
        if (currentSession?.user) {
          const isAdminUser = await authService.checkUserIsAdmin(currentSession.user);
          setUser(currentSession.user);
          setIsAdmin(isAdminUser);
          setSession(currentSession);
        }
      } catch (error) {
        console.error('Erreur lors de l\'initialisation de l\'authentification:', error);
      } finally {
        setLoading(false);
      }

      // Configurer l'écouteur d'état d'authentification
      subscription = authService.initAuthListener(async (authData) => {
        if (authData) {
          setUser(authData.user);
          setIsAdmin(authData.isAdmin);
          setSession(authData.session);
        } else {
          setUser(null);
          setIsAdmin(false);
          setSession(null);
        }
        setLoading(false);
      });
    };

    initAuth();

    // Nettoyer l'écouteur au démontage
    return () => {
      if (subscription) {
        subscription.unsubscribe();
      }
    };
  }, []);

  // Fonction de connexion
  const signIn = async (email, password) => {
    setLoading(true);
    try {
      const result = await authService.signIn(email, password);
      if (result) {
        setUser(result.user);
        setIsAdmin(result.isAdmin);
        setSession(result.session);
      }
      return result;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Fonction de déconnexion
  const signOut = async () => {
    setLoading(true);
    try {
      await authService.signOut();
      setUser(null);
      setIsAdmin(false);
      setSession(null);
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Valeur du contexte
  const value = {
    user,
    isAdmin,
    loading,
    session,
    signIn,
    signOut,
    authenticateWithToken: authService.authenticateWithToken.bind(authService),
    isAuthenticated: !!user && isAdmin
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

