import { createClient } from '@supabase/supabase-js'
import { SUPABASE_CONFIG, diagnoseEnvironmentVariables } from './config/supabase-config'

// Diagnostic au chargement
console.log('🚀 INITIALISATION SUPABASE CLIENT FRIDAY');
const envDiagnostic = diagnoseEnvironmentVariables();

export const supabase = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
})

// Test de connexion immédiat
console.log('🔍 TEST CONNEXION SUPABASE...');
supabase.from('creations').select('count', { count: 'exact', head: true })
  .then(({ data, error, count }) => {
    if (error) {
      console.error('❌ ERREUR CONNEXION SUPABASE:', error);
    } else {
      console.log('✅ CONNEXION SUPABASE OK - Créations dans la base:', count);
    }
  })
  .catch(err => {
    console.error('❌ ERREUR CRITIQUE SUPABASE:', err);
  });

export function diagnoseSupabase() {
  console.log('🧪 DIAGNOSTIC COMPLET SUPABASE CLIENT');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  const config = {
    url: SUPABASE_CONFIG.url,
    keyPresent: !!SUPABASE_CONFIG.anonKey,
    keyPreview: SUPABASE_CONFIG.anonKey?.substring(0, 20) + '...',
    clientInitialized: !!supabase
  };
  
  console.log('📊 Configuration actuelle:', config);
  
  // Test de connexion
  return supabase.from('creations').select('count', { count: 'exact', head: true })
    .then(({ data, error, count }) => {
      const result = {
        ...config,
        connectionTest: error ? 'FAILED' : 'SUCCESS',
        error: error?.message,
        recordCount: count
      };
      
      console.log('🔍 Résultat test connexion:', result);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      
      return result;
    })
    .catch(err => {
      const result = {
        ...config,
        connectionTest: 'ERROR',
        error: err.message
      };
      
      console.error('❌ Erreur test connexion:', result);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      
      return result;
    });
}