// Script pour forcer le rechargement du cache
console.log('🔄 Forçage du rechargement du cache...');

// Vider le cache du service worker si présent
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(registrations) {
    for(let registration of registrations) {
      registration.unregister();
    }
  });
}

// Vider le localStorage des anciennes clés
localStorage.removeItem('fridayFeatures');
localStorage.removeItem('herbbie_features_config');

// Forcer le rechargement de la page
window.location.reload(true);
