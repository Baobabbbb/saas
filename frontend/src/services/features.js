// Service pour gérer les fonctionnalités disponibles dans Herbbie (version localStorage uniquement)
const STORAGE_KEY = 'herbbie_features_config';

// Configuration par défaut des fonctionnalités
const DEFAULT_FEATURES = {
  animation: { enabled: true, name: 'Dessin animé', icon: '🎬', description: 'Génération de dessins animés personnalisés avec IA' },
  comic: { enabled: true, name: 'Bande dessinée', icon: '💬', description: 'Création de bandes dessinées avec bulles de dialogue' },
  coloring: { enabled: true, name: 'Coloriage', icon: '🎨', description: 'Pages de coloriage à imprimer pour les enfants' },
  audio: { enabled: true, name: 'Histoire', icon: '📖', description: 'Histoires audio avec narration automatique' },
  rhyme: { enabled: true, name: 'Comptine', icon: '🎵', description: 'Comptines musicales avec paroles et mélodies' }
};

// Cache pour éviter les appels répétés
let featuresCache = null;
let cacheTimestamp = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Fonction pour charger les fonctionnalités depuis le localStorage
const loadFeaturesFromStorage = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      console.log('📋 Fonctionnalités chargées depuis le localStorage:', parsed);
      return parsed;
    }
  } catch (error) {
    console.warn('Erreur lors du chargement des fonctionnalités depuis le localStorage:', error);
  }
  return null;
};

// Fonction pour récupérer les fonctionnalités (UNIQUEMENT depuis localStorage)
export const getFeatures = async () => {
  try {
    // Vérifier le cache
    if (featuresCache && cacheTimestamp && (Date.now() - cacheTimestamp) < CACHE_DURATION) {
      return featuresCache;
    }

    // Charger depuis le localStorage
    const storedFeatures = loadFeaturesFromStorage();
    if (storedFeatures) {
      featuresCache = storedFeatures;
      cacheTimestamp = Date.now();
      return storedFeatures;
    }

    // Fallback vers les valeurs par défaut
    console.log('📋 Aucune configuration trouvée, utilisation des valeurs par défaut');
    featuresCache = DEFAULT_FEATURES;
    cacheTimestamp = Date.now();
    return DEFAULT_FEATURES;
  } catch (error) {
    console.warn('Erreur lors de la récupération des fonctionnalités:', error);
    return DEFAULT_FEATURES;
  }
};

// Fonction pour vérifier si une fonctionnalité est activée
export const isFeatureEnabled = async (featureKey) => {
  try {
    const features = await getFeatures();
    return features[featureKey]?.enabled || false;
  } catch (error) {
    console.warn(`Erreur lors de la vérification de la fonctionnalité ${featureKey}:`, error);
    return false;
  }
};

// Fonction pour récupérer les fonctionnalités activées
export const getEnabledFeatures = async () => {
  try {
    const features = await getFeatures();
    return Object.entries(features)
      .filter(([key, feature]) => feature.enabled)
      .reduce((enabled, [key, feature]) => {
        enabled[key] = feature;
        return enabled;
      }, {});
  } catch (error) {
    console.warn('Erreur lors de la récupération des fonctionnalités activées:', error);
    return {};
  }
};

// Fonction pour récupérer toutes les fonctionnalités
export const getAllFeatures = async () => {
  return await getFeatures();
};

// Fonction utilitaire pour vérifier si toutes les fonctionnalités requises sont activées
export const areRequiredFeaturesEnabled = async (requiredFeatures = []) => {
  try {
    const enabledFeatures = await getEnabledFeatures();
    return requiredFeatures.every(feature => enabledFeatures[feature]);
  } catch (error) {
    console.warn('Erreur lors de la vérification des fonctionnalités requises:', error);
    return false;
  }
};

// Fonction pour forcer le rechargement du cache
export const refreshFeatures = async () => {
  featuresCache = null;
  cacheTimestamp = null;
  return await getFeatures();
};

// Fonction pour écouter les changements de fonctionnalités depuis le panneau
export const listenForFeatureChanges = (callback) => {
  const handleStorageChange = (event) => {
    if (event.key === STORAGE_KEY && event.newValue) {
      try {
        const newFeatures = JSON.parse(event.newValue);
        console.log('🔄 Fonctionnalités mises à jour depuis le panneau (storage):', newFeatures);
        
        // Invalider le cache
        featuresCache = null;
        cacheTimestamp = null;
        
        if (callback && typeof callback === 'function') {
          callback(newFeatures);
        }
      } catch (error) {
        console.error('Erreur lors du parsing des nouvelles fonctionnalités:', error);
      }
    }
  };
  
  const handleCustomEvent = (event) => {
    if (event.detail) {
      console.log('🔄 Fonctionnalités mises à jour via événement personnalisé:', event.detail);
      
      // Invalider le cache
      featuresCache = null;
      cacheTimestamp = null;
      
      if (callback && typeof callback === 'function') {
        callback(event.detail);
      }
    }
  };
  
  // Vérifier périodiquement les changements (fallback)
  const checkForChanges = () => {
    const storedFeatures = loadFeaturesFromStorage();
    if (storedFeatures && (!featuresCache || JSON.stringify(storedFeatures) !== JSON.stringify(featuresCache))) {
      console.log('🔄 Changements détectés via vérification périodique:', storedFeatures);
      featuresCache = null;
      cacheTimestamp = null;
      if (callback && typeof callback === 'function') {
        callback(storedFeatures);
      }
    }
  };
  
  // Écouter les changements de localStorage
  window.addEventListener('storage', handleStorageChange);
  
  // Écouter les événements personnalisés
  window.addEventListener('herbbieFeaturesUpdate', handleCustomEvent);
  window.addEventListener('featuresUpdated', handleCustomEvent);
  
  // Vérification périodique toutes les 2 secondes
  const intervalId = setInterval(checkForChanges, 2000);
  
  // Retourner une fonction pour nettoyer les écouteurs
  return () => {
    window.removeEventListener('storage', handleStorageChange);
    window.removeEventListener('herbbieFeaturesUpdate', handleCustomEvent);
    window.removeEventListener('featuresUpdated', handleCustomEvent);
    clearInterval(intervalId);
  };
};

// Export par défaut pour compatibilité
export default {
  getFeatures,
  isFeatureEnabled,
  getEnabledFeatures,
  getAllFeatures,
  areRequiredFeaturesEnabled,
  refreshFeatures,
  listenForFeatureChanges
};