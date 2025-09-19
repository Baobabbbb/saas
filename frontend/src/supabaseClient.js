import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://xfbmdeuzuyixpmouhqcv.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw'

console.log('🔧 SUPABASE CLIENT INITIALIZATION:');
console.log('- URL:', supabaseUrl ? '✅ Chargée' : '❌ Manquante');
console.log('- KEY:', supabaseAnonKey ? '✅ Chargée' : '❌ Manquante');

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

console.log('✅ Supabase client créé avec succès'); 