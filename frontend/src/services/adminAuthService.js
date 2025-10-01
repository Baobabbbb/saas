// Service d'authentification simplifié pour le panneau administrateur HERBBIE
// Version locale sans dépendance Supabase

// Configuration des administrateurs autorisés
const ADMIN_EMAILS = [
  'fredagathe77@gmail.com',
  'admin@herbbie.com'
];

// Clé de session dans localStorage
const SESSION_KEY = 'herbbie_admin_session';

export const authService = {
  // Initialisation de l'écouteur d'état d'authentification (simulé)
  initAuthListener(callback) {
    // Simuler l'écoute d'état d'authentification
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

  // Connexion avec email et mot de passe (version simplifiée)
  async signIn(email, password) {
    try {
      // Vérifier si l'email est autorisé
      if (!ADMIN_EMAILS.includes(email)) {
        throw new Error('Accès refusé. Seuls les administrateurs peuvent accéder à ce panneau.');
      }

      // Simuler une authentification (en production, vous pourriez utiliser un vrai système)
      const user = {
        id: 'admin-' + Date.now(),
        email: email,
        user_metadata: {
          full_name: email === 'fredagathe77@gmail.com' ? 'Admin Principal' : 'Administrateur'
        }
      };

      const session = {
        user,
        access_token: 'admin-token-' + Date.now(),
        token_type: 'bearer',
        expires_at: Date.now() + (24 * 60 * 60 * 1000) // 24 heures
      };

      // Stocker la session
      this.storeSession({ user, isAdmin: true, session });

      console.log('✅ Connexion admin réussie:', email);
      return { user, session, isAdmin: true };
    } catch (error) {
      console.error('Erreur de connexion:', error);
      throw error;
    }
  },

  // Déconnexion
  async signOut() {
    try {
      // Supprimer la session stockée
      localStorage.removeItem(SESSION_KEY);
      console.log('✅ Déconnexion réussie');
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
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

  // Vérifier si l'utilisateur est administrateur (version simplifiée)
  async checkUserIsAdmin(user) {
    try {
      if (!user || !user.email) {
        return false;
      }

      // Vérifier si l'email est dans la liste des admins
      const isAdmin = ADMIN_EMAILS.includes(user.email);
      
      if (isAdmin) {
        console.log(`👑 Utilisateur ${user.email} - Rôle: admin - Admin: true`);
      } else {
        console.log(`👤 Utilisateur ${user.email} - Rôle: user - Admin: false`);
      }
      
      return isAdmin;
    } catch (error) {
      console.error('Erreur lors de la vérification du rôle admin:', error);
      return false;
    }
  },

  // Authentification automatique via token URL (version simplifiée)
  async authenticateWithToken(token) {
    try {
      console.log('🔑 Authentification automatique avec token');
      
      // Vérifier si le token est valide (version simplifiée)
      if (!token || !token.includes('admin')) {
        console.warn('Token invalide');
        return false;
      }

      // Créer un utilisateur admin par défaut
      const user = {
        id: 'admin-auto-' + Date.now(),
        email: 'admin@herbbie.com',
        user_metadata: {
          full_name: 'Administrateur Auto'
        }
      };

      const session = {
        user,
        access_token: token,
        token_type: 'bearer',
        expires_at: Date.now() + (24 * 60 * 60 * 1000) // 24 heures
      };

      // Stocker la session
      this.storeSession({ user, isAdmin: true, session });

      console.log('✅ Authentification automatique réussie:', user.email);
      return { user, isAdmin: true, session };
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
        if (session.session && session.session.expires_at > Date.now()) {
          return session;
        } else {
          // Session expirée, la supprimer
          localStorage.removeItem(SESSION_KEY);
        }
      }
    } catch (error) {
      console.error('Erreur lors de la récupération de la session:', error);
    }
    return null;
  }
};

export default authService;

