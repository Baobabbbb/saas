// Configuration centralisée Supabase - DOIT être définie dans Railway
export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL,
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY
};

// Vérification obligatoire
if (!SUPABASE_CONFIG.url || !SUPABASE_CONFIG.anonKey) {
  console.error('❌ ERREUR CRITIQUE: Variables Supabase manquantes dans Railway!');
  console.error('Configurez VITE_SUPABASE_URL et VITE_SUPABASE_ANON_KEY dans Railway > Variables');
  throw new Error('Configuration Supabase manquante');
}

// Diagnostic des variables d'environnement
export function diagnoseEnvironmentVariables() {
  console.log('🔍 DIAGNOSTIC VARIABLES ENVIRONNEMENT HERBBIE');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  // Vérifier toutes les variables d'environnement Vite
  const allEnvVars = import.meta.env;
  console.log('📋 Toutes les variables import.meta.env:', allEnvVars);
  
  // Variables Supabase spécifiques
  console.log('🗃️ Variables Supabase:');
  console.log('  VITE_SUPABASE_URL:', import.meta.env.VITE_SUPABASE_URL);
  console.log('  VITE_SUPABASE_ANON_KEY présente:', !!import.meta.env.VITE_SUPABASE_ANON_KEY);
  console.log('  VITE_SUPABASE_ANON_KEY (10 premiers chars):', import.meta.env.VITE_SUPABASE_ANON_KEY?.substring(0, 10) + '...');
  
  // Configuration finale utilisée
  console.log('⚙️ Configuration finale utilisée:');
  console.log('  URL:', SUPABASE_CONFIG.url);
  console.log('  Key présente:', !!SUPABASE_CONFIG.anonKey);
  console.log('  Key (10 premiers chars):', SUPABASE_CONFIG.anonKey?.substring(0, 10) + '...');
  
  // Variables d'environnement brutes
  console.log('🌍 Environnement de build:');
  console.log('  NODE_ENV:', import.meta.env.NODE_ENV);
  console.log('  MODE:', import.meta.env.MODE);
  console.log('  DEV:', import.meta.env.DEV);
  console.log('  PROD:', import.meta.env.PROD);
  
  // Test de validité
  const isValid = SUPABASE_CONFIG.url && SUPABASE_CONFIG.anonKey;
  console.log('✅ Configuration valide:', isValid);
  
  if (!isValid) {
    console.error('❌ ERREUR: Configuration Supabase invalide!');
    console.error('Variables manquantes:');
    if (!SUPABASE_CONFIG.url) console.error('  - VITE_SUPABASE_URL');
    if (!SUPABASE_CONFIG.anonKey) console.error('  - VITE_SUPABASE_ANON_KEY');
  }
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  return {
    isValid,
    url: SUPABASE_CONFIG.url,
    hasKey: !!SUPABASE_CONFIG.anonKey,
    envVars: allEnvVars
  };
}

// Auto-diagnostic au chargement du module
console.log('🚀 CHARGEMENT MODULE SUPABASE CONFIG');
diagnoseEnvironmentVariables();

