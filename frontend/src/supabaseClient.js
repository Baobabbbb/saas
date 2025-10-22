import { createClient } from '@supabase/supabase-js'

// Configuration Supabase - DOIT être définie dans Railway
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Vérification obligatoire des variables d'environnement
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ ERREUR CRITIQUE: Variables Supabase manquantes!');
  console.error('VITE_SUPABASE_URL:', supabaseUrl);
  console.error('VITE_SUPABASE_ANON_KEY présente:', !!supabaseAnonKey);
  throw new Error('Variables d\'environnement Supabase non configurées. Configurez VITE_SUPABASE_URL et VITE_SUPABASE_ANON_KEY dans Railway.');
}

// Créer le client Supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    storage: window.localStorage,
    storageKey: 'herbbie-auth',
    flowType: 'pkce',
    onAuthStateChange: (event, session) => {
      if (event === 'SIGNED_OUT') {
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
      return fetch(url, options).catch(error => {
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
})