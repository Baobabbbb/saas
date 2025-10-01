// Script agressif pour forcer le nettoyage du cache
console.log('🧹 Nettoyage agressif du cache...');

// 1. Vider tous les storages
try {
    localStorage.clear();
    sessionStorage.clear();
    console.log('✅ Storages vidés');
} catch (e) {
    console.error('❌ Erreur lors du vidage des storages:', e);
}

// 2. Vider le cache du service worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for(let registration of registrations) {
            registration.unregister();
            console.log('✅ Service worker supprimé');
        }
    });
}

// 3. Vider le cache du navigateur
if ('caches' in window) {
    caches.keys().then(function(names) {
        for (let name of names) {
            caches.delete(name);
            console.log('✅ Cache supprimé:', name);
        }
    });
}

// 4. Forcer le rechargement avec vidage du cache
setTimeout(() => {
    console.log('🔄 Rechargement forcé...');
    window.location.reload(true);
}, 1000);

