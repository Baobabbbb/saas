// Service pour gérer les fonctionnalités disponibles dans Herbbie
const API_BASE_URL = 'https://saas-production.up.railway.app/api';

// Configuration par défaut des fonctionnalités
const DEFAULT_FEATURES = {
  animation: { enabled: true, name: 'Dessin animé', icon: '🎬' },
  comic: { enabled: true, name: 'Bande dessinée', icon: '💬' },
  coloring: { enabled: true, name: 'Coloriage', icon: '🎨' },
  audio: { enabled: true, name: 'Histoire', icon: '📖' },
  rhyme: { enabled: true, name: 'Comptine', icon: '🎵' }
};

// Cache pour éviter les appels répétés
let featuresCache = null;
let cacheTimestamp = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Fonction pour récupérer les fonctionnalités depuis l'API
export const getFeatures = async () => {
  try {
    // Vérifier le cache
    if (featuresCache && cacheTimestamp && (Date.now() - cacheTimestamp) < CACHE_DURATION) {
      return featuresCache;
    }

    const response = await fetch(`${API_BASE_URL}/features`);
    if (response.ok) {
      const features = await response.json();
      featuresCache = features;
      cacheTimestamp = Date.now();
      return features;
    } else {
      console.warn('Impossible de récupérer les fonctionnalités, utilisation des valeurs par défaut');
      return DEFAULT_FEATURES;
    }
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
export const getAllFeatures = () => {
  return { ...DEFAULT_FEATURES };
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

// Export par défaut pour compatibilité
export default {
  getFeatures,
  isFeatureEnabled,
  getEnabledFeatures,
  getAllFeatures,
  areRequiredFeaturesEnabled,
  refreshFeatures
};