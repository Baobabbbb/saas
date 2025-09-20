// Utilitaires de diagnostic pour Friday
import { diagnoseSupabase } from '../supabaseClient'

export function runFullDiagnostic() {
  console.log('🔧 DIAGNOSTIC COMPLET FRIDAY');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  // Diagnostic environnement
  console.log('🌍 ENVIRONNEMENT:');
  console.log('  NODE_ENV:', import.meta.env.NODE_ENV);
  console.log('  MODE:', import.meta.env.MODE);
  console.log('  DEV:', import.meta.env.DEV);
  console.log('  PROD:', import.meta.env.PROD);
  
  // Variables Supabase
  console.log('🗃️ VARIABLES SUPABASE:');
  console.log('  VITE_SUPABASE_URL:', import.meta.env.VITE_SUPABASE_URL);
  console.log('  VITE_SUPABASE_ANON_KEY présente:', !!import.meta.env.VITE_SUPABASE_ANON_KEY);
  
  // Test Supabase
  console.log('🔌 TEST SUPABASE:');
  return diagnoseSupabase().then(result => {
    console.log('  Résultat:', result);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    return result;
  });
}

// Fonction d'aide pour déboguer
export function debugLog(message, data) {
  if (import.meta.env.DEV || window.location.search.includes('debug=true')) {
    console.log(`🐛 [DEBUG] ${message}`, data);
  }
}

// Ajout d'un bouton de diagnostic global
export function addDebugButton() {
  if (document.getElementById('friday-debug-btn')) return;
  
  const button = document.createElement('button');
  button.id = 'friday-debug-btn';
  button.textContent = '🔧 Debug';
  button.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 9999;
    padding: 8px 12px;
    background: #6B4EFF;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
  `;
  
  button.onclick = () => {
    runFullDiagnostic().then(result => {
      alert(`Diagnostic terminé! Vérifiez la console pour les détails.\n\nRésultat Supabase: ${result.connectionTest}`);
    });
  };
  
  document.body.appendChild(button);
}

// Auto-ajout du bouton en dev ou avec ?debug=true
if (import.meta.env.DEV || window.location.search.includes('debug=true')) {
  document.addEventListener('DOMContentLoaded', addDebugButton);
}

