import { createClient } from '@supabase/supabase-js'

// Fonction pour récupérer la configuration depuis le backend
async function getSupabaseConfig() {
  try {
    const response = await fetch('/api/config');
    if (response.ok) {
      const config = await response.json();
      return config;
    }
  } catch (error) {
    console.warn('Impossible de récupérer la configuration depuis /api/config:', error);
  }

  // Fallback vers les variables d'environnement ou valeurs par défaut
  return {
    supabase_url: import.meta.env.VITE_SUPABASE_URL || 'https://xfbmdeuzuyixpmouhqcv.supabase.co',
    supabase_anon_key: import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw'
  };
}

// Créer le client Supabase de manière asynchrone
let supabaseClient = null;

export async function initializeSupabase() {
  if (!supabaseClient) {
    const config = await getSupabaseConfig();
    supabaseClient = createClient(config.supabase_url, config.supabase_anon_key, {

      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: false,
        storage: window.localStorage,  // Stockage explicite des sessions
        storageKey: 'herbbie-auth',    // Clé personnalisée pour les sessions
        // Gestion des erreurs de refresh token
        onAuthStateChange: (event, session) => {
          if (event === 'TOKEN_REFRESHED') {
            // Token rafraîchi avec succès
            console.log('✅ Token Supabase rafraîchi');
          } else if (event === 'SIGNED_OUT') {
            // Nettoyer toutes les sessions en cas de déconnexion
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
              if (key.startsWith('sb-') || key.startsWith('supabase.') || key.startsWith('herbbie-auth')) {
                localStorage.removeItem(key);
              }
            });
          }
        }
      },
      global: {
        headers: {
          'x-client-info': 'herbbie-web'
        },
        fetch: (url, options = {}) => {
          // Wrapper personnalisé pour gérer les erreurs de fetch
          return fetch(url, options).catch(error => {
            console.error('Erreur Supabase:', error);
            // Si c'est une erreur de réseau, ne pas propager l'erreur pour éviter de casser l'app
            if (error.message.includes('Failed to fetch') || error.message.includes('ERR_NAME_NOT_RESOLVED')) {
              return Promise.resolve(new Response(JSON.stringify({ error: 'Network error' }), {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
              }));
            }
            throw error;
          });
        }
      }
    });
  }

  return supabaseClient;
}

// Exporter une fonction qui initialise et retourne le client
export async function getSupabaseClient() {
  return await initializeSupabase();
}

// Pour la compatibilité, exporter aussi une instance par défaut
let defaultSupabase = null;

export const supabase = new Proxy({}, {
  get(target, prop) {
    if (!defaultSupabase) {
      throw new Error('Supabase client not initialized. Call getSupabaseClient() first.');
    }
    return defaultSupabase[prop];
  }
});

// Initialiser automatiquement au chargement
initializeSupabase().then(client => {
  defaultSupabase = client;
}).catch(error => {
  console.error('Erreur initialisation Supabase:', error);
});