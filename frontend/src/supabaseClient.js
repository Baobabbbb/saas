import { createClient } from '@supabase/supabase-js'

// Configuration Supabase - Valeurs hardcodées pour le frontend statique
const supabaseUrl = 'https://jjqruvvqkqjsxzjcxwai.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqcXJ1dnZxa3Fqc3h6amN4d2FpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ2MzE0NzcsImV4cCI6MjA1MDIwNzQ3N30.rKqHwGxGBFVxwHlpwAaGq2yjNPEFVWMdZKrQQdvRHqM'

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