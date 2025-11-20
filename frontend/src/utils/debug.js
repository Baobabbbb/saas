// Utilitaires de diagnostic pour Friday
import { diagnoseSupabase } from '../supabaseClient'

export function runFullDiagnostic() {
  
  // Test Supabase silencieux
  return diagnoseSupabase().then(result => {
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

