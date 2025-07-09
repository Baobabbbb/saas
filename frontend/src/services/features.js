// Service pour gérer l'état des fonctionnalités du site
const FEATURES_STORAGE_KEY = 'fridayFeatures';

// Configuration par défaut des fonctionnalités
const DEFAULT_FEATURES = {
  animation: { enabled: true, name: 'Dessin animé', icon: '🎬' },
  seedance: { enabled: true, name: 'Animation SEEDANCE', icon: '🚀' },
  comic: { enabled: true, name: 'Bande dessinée', icon: '📚' },
  coloring: { enabled: true, name: 'Coloriage', icon: '🎨' },
  audio: { enabled: true, name: 'Histoire', icon: '📖' },
  rhyme: { enabled: true, name: 'Comptine', icon: '🎵' }
};

export const getFeatures = () => {
  const stored = localStorage.getItem(FEATURES_STORAGE_KEY);
  if (stored) {
    try {
      const parsedFeatures = JSON.parse(stored);
      // Nettoyer les anciennes fonctionnalités obsolètes
      delete parsedFeatures.musical_rhyme;
      
      const cleanedFeatures = { ...DEFAULT_FEATURES, ...parsedFeatures };
      // Sauvegarder la version nettoyée
      localStorage.setItem(FEATURES_STORAGE_KEY, JSON.stringify(cleanedFeatures));
      return cleanedFeatures;
    } catch (error) {
      console.error('Erreur lors du parsing des fonctionnalités:', error);
    }
  }
  return DEFAULT_FEATURES;
};

export const updateFeature = (featureKey, enabled) => {
  const features = getFeatures();
  features[featureKey] = { ...features[featureKey], enabled };
  localStorage.setItem(FEATURES_STORAGE_KEY, JSON.stringify(features));
  
  // Déclencher un événement personnalisé pour notifier les composants
  window.dispatchEvent(new CustomEvent('featuresUpdated', { detail: features }));
  
  return features;
};

export const isFeatureEnabled = (featureKey) => {
  const features = getFeatures();
  return features[featureKey]?.enabled || false;
};

export const getEnabledFeatures = () => {
  const features = getFeatures();
  return Object.entries(features)
    .filter(([key, feature]) => feature.enabled)
    .reduce((enabled, [key, feature]) => {
      enabled[key] = feature;
      return enabled;
    }, {});
};

export const resetFeatures = () => {
  localStorage.setItem(FEATURES_STORAGE_KEY, JSON.stringify(DEFAULT_FEATURES));
  window.dispatchEvent(new CustomEvent('featuresUpdated', { detail: DEFAULT_FEATURES }));
  return DEFAULT_FEATURES;
};

export const getAllFeatures = () => {
  return { ...DEFAULT_FEATURES };
};

// Fonction utilitaire pour vérifier si toutes les fonctionnalités requises sont activées
export const areRequiredFeaturesEnabled = (requiredFeatures = []) => {
  const enabledFeatures = getEnabledFeatures();
  return requiredFeatures.every(feature => enabledFeatures[feature]);
};

// Export par défaut pour compatibilité
export default {
  getFeatures,
  updateFeature,
  isFeatureEnabled,
  getEnabledFeatures,
  resetFeatures,
  getAllFeatures,
  areRequiredFeaturesEnabled
};
