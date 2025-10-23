// Configuration centralisée Supabase - Valeurs hardcodées pour le frontend statique
export const SUPABASE_CONFIG = {
  url: 'https://jjqruvvqkqjsxzjcxwai.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqcXJ1dnZxa3Fqc3h6amN4d2FpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ2MzE0NzcsImV4cCI6MjA1MDIwNzQ3N30.rKqHwGxGBFVxwHlpwAaGq2yjNPEFVWMdZKrQQdvRHqM'
};

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

