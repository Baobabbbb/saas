import { createClient } from '@supabase/supabase-js'

// Configuration Supabase - Valeurs hardcodées pour le frontend statique
const supabaseUrl = 'https://xfbmdeuzuyixpmouhqcv.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw'

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