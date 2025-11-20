// Configuration centralisée Supabase - Variables d'environnement Vite (prioritaires) ou valeurs par défaut
export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL || 'https://xfbmdeuzuyixpmouhqcv.supabase.co',
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw'
};

// Diagnostic des variables d'environnement
export function diagnoseEnvironmentVariables() {
  
  // Vérifier toutes les variables d'environnement Vite
  const allEnvVars = import.meta.env;
  
  // Variables Supabase spécifiques
  
  // Configuration finale utilisée
  
  // Variables d'environnement brutes
  
  // Test de validité
  const isValid = SUPABASE_CONFIG.url && SUPABASE_CONFIG.anonKey;
  
  if (!isValid) {
    console.error('❌ ERREUR: Configuration Supabase invalide!');
    console.error('Variables manquantes:');
    if (!SUPABASE_CONFIG.url) console.error('  - VITE_SUPABASE_URL');
    if (!SUPABASE_CONFIG.anonKey) console.error('  - VITE_SUPABASE_ANON_KEY');
  }
  
  
  return {
    isValid,
    url: SUPABASE_CONFIG.url,
    hasKey: !!SUPABASE_CONFIG.anonKey,
    envVars: allEnvVars
  };
}

// Auto-diagnostic au chargement du module
diagnoseEnvironmentVariables();

