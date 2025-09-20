import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://xfbmdeuzuyixpmouhqcv.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw'

console.log('🚀 FRIDAY: Initialisation Supabase client');
console.log('🔗 URL:', supabaseUrl);
console.log('🔑 Clé présente:', !!supabaseAnonKey);

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: false
  }
})

// Test immédiat de connexion avec diagnostics détaillés
console.log('🧪 FRIDAY: Test connexion Supabase...');
supabase.from('creations').select('count', { count: 'exact', head: true })
  .then(({ data, error, count }) => {
    if (error) {
      console.error('❌ FRIDAY: Erreur connexion Supabase:', error.message);
      console.error('🔍 FRIDAY: Détails erreur:', error);
      console.error('🌐 FRIDAY: URL actuelle:', window.location.origin);
      console.error('🔗 FRIDAY: Supabase URL:', supabaseUrl);
    } else {
      console.log('✅ FRIDAY: Connexion Supabase OK -', count, 'créations en base');
    }
  })
  .catch(err => {
    console.error('❌ FRIDAY: Erreur critique Supabase:', err.message);
    console.error('🔍 FRIDAY: Stack trace:', err.stack);
  });

console.log('✅ FRIDAY: Client Supabase initialisé avec succès');