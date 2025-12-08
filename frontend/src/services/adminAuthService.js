// Service d'authentification pour le panneau administrateur HERBBIE
// Utilise Supabase pour la vérification des identifiants

import { supabase } from '../supabaseClient';

// Configuration des administrateurs autorisés
const ADMIN_EMAILS = [
  'fredagathe77@gmail.com',
  'admin@herbbie.com'
];

// Clé de session dans localStorage
const SESSION_KEY = 'herbbie_admin_session';

export const authService = {
  // Initialisation de l'écouteur d'état d'authentification
  initAuthListener(callback) {
    // Vérifier la session stockée localement
    const checkAuth = () => {
      const session = this.getStoredSession();
      if (session && session.user) {
        callback({ user: session.user, isAdmin: session.isAdmin, session });
      } else {
        callback(null);
      }
    };

    // Vérifier immédiatement
    checkAuth();

    // Écouter les changements de localStorage
    const handleStorageChange = (event) => {
      if (event.key === SESSION_KEY) {
        checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Retourner un objet avec une méthode unsubscribe
    return {
      unsubscribe: () => {
        window.removeEventListener('storage', handleStorageChange);
      }
    };
  },

  // Connexion avec email et mot de passe - VÉRIFICATION RÉELLE VIA SUPABASE
  async signIn(email, password) {
    try {
      // Vérifier d'abord si l'email est dans la liste des admins autorisés
      if (!ADMIN_EMAILS.includes(email)) {
        throw new Error('Accès refusé. Seuls les administrateurs peuvent accéder à ce panneau.');
      }

      // IMPORTANT: Authentification via Supabase pour vérifier le mot de passe
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password,
      });

      if (error) {
        console.error('Erreur Supabase de connexion:', error);
        // Traduire les erreurs Supabase en français
        if (error.message.includes('Invalid login credentials')) {
          throw new Error('Email ou mot de passe incorrect.');
        }
        if (error.message.includes('Email not confirmed')) {
          throw new Error('Veuillez confirmer votre email avant de vous connecter.');
        }
        throw new Error(error.message || 'Erreur de connexion');
      }

      if (data.user) {
        // Vérifier une dernière fois que l'utilisateur est bien admin
        const isAdminUser = await this.checkUserIsAdmin(data.user);
        
        if (!isAdminUser) {
          // Déconnecter l'utilisateur s'il n'est pas admin
          await supabase.auth.signOut();
          throw new Error('Accès refusé. Seuls les administrateurs peuvent accéder à ce panneau.');
        }

        // Créer et stocker la session admin
        const sessionData = { 
          user: data.user, 
          isAdmin: isAdminUser, 
          session: data.session 
        };
        this.storeSession(sessionData);
        
        return sessionData;
      }

      throw new Error('Aucun utilisateur retourné par Supabase.');
    } catch (error) {
      console.error('Erreur de connexion:', error);
      throw error;
    }
  },

  // Déconnexion
  async signOut() {
    try {
      // Déconnecter de Supabase
      await supabase.auth.signOut();
      // Supprimer la session stockée localement
      localStorage.removeItem(SESSION_KEY);
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
      // Supprimer quand même la session locale
      localStorage.removeItem(SESSION_KEY);
      throw error;
    }
  },

  // Obtenir l'utilisateur actuel
  async getCurrentUser() {
    try {
      const session = this.getStoredSession();
      if (session && session.user) {
        return { user: session.user, isAdmin: session.isAdmin };
      }
      return null;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'utilisateur:', error);
      return null;
    }
  },

  // Vérifier si l'utilisateur est administrateur
  async checkUserIsAdmin(user) {
    try {
      if (!user || !user.email) {
        return false;
      }

      // Vérifier si l'email est dans la liste des admins
      const isInAdminList = ADMIN_EMAILS.includes(user.email);
      
      if (!isInAdminList) {
        return false;
      }

      // Optionnel: Vérifier aussi le rôle dans la base de données
      try {
        const { data: profile, error } = await supabase
          .from('profiles')
          .select('role')
          .eq('id', user.id)
          .single();

        if (!error && profile && profile.role === 'admin') {
          return true;
        }
      } catch (dbError) {
        // Si la vérification en base échoue, se fier à la liste des emails
        console.warn('Vérification du rôle en base échouée, utilisation de la liste des emails');
      }
      
      // Si l'email est dans la liste, c'est un admin
      return isInAdminList;
    } catch (error) {
      console.error('Erreur lors de la vérification du rôle admin:', error);
      return false;
    }
  },

  // Authentification automatique via token URL (désactivée pour des raisons de sécurité)
  async authenticateWithToken(token) {
    try {
      // Cette méthode est désactivée pour des raisons de sécurité
      // L'authentification doit passer par signIn avec vérification du mot de passe
      console.warn('authenticateWithToken désactivé - utilisez signIn');
      return false;
    } catch (error) {
      console.error('Erreur authentification automatique:', error);
      return false;
    }
  },

  // Obtenir la session actuelle
  async getCurrentSession() {
    try {
      return this.getStoredSession();
    } catch (error) {
      console.error('Erreur lors de la récupération de la session:', error);
      return null;
    }
  },

  // Méthodes utilitaires pour le stockage local
  storeSession(sessionData) {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    } catch (error) {
      console.error('Erreur lors du stockage de la session:', error);
    }
  },

  getStoredSession() {
    try {
      const stored = localStorage.getItem(SESSION_KEY);
      if (stored) {
        const session = JSON.parse(stored);
        // Vérifier si la session n'est pas expirée
        if (session.session && session.session.expires_at) {
          const expiresAt = typeof session.session.expires_at === 'number' 
            ? session.session.expires_at * 1000 // Si c'est un timestamp en secondes
            : new Date(session.session.expires_at).getTime();
          
          if (expiresAt > Date.now()) {
            return session;
          } else {
            // Session expirée, la supprimer
            localStorage.removeItem(SESSION_KEY);
          }
        } else if (session.user) {
          // Session sans expiration explicite (ancienne session)
          return session;
        }
      }
    } catch (error) {
      console.error('Erreur lors de la récupération de la session:', error);
    }
    return null;
  }
};

export default authService;
