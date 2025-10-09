// Service pour gérer les fonctionnalités via l'API backend (panneau admin)
import { getFeaturesFromAPI, updateFeatureAPI, resetFeaturesAPI } from './adminFeaturesAPI';

// Fonction pour récupérer les fonctionnalités depuis l'API
export const getFeatures = async () => {
  try {
    const features = await getFeaturesFromAPI();
    return features;
  } catch (error) {
    console.error('Erreur lors du chargement des fonctionnalités:', error);
    throw error;
  }
};

// Fonction pour mettre à jour une fonctionnalité via l'API
export const updateFeature = async (featureKey, enabled) => {
  try {
    const updatedFeatures = await updateFeatureAPI(featureKey, enabled);
    
    // Déclencher un événement personnalisé pour notifier Herbbie
    window.dispatchEvent(new CustomEvent('featuresUpdated', { 
      detail: updatedFeatures 
    }));
    
    return updatedFeatures;
  } catch (error) {
    console.error('Erreur lors de la mise à jour de la fonctionnalité:', error);
    throw error;
  }
};

// Fonction pour vérifier si une fonctionnalité est activée
export const isFeatureEnabled = async (featureKey) => {
  try {
    const features = await getFeatures();
    return features[featureKey]?.enabled || false;
  } catch (error) {
    console.error(`Erreur lors de la vérification de la fonctionnalité ${featureKey}:`, error);
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
    console.error('Erreur lors de la récupération des fonctionnalités activées:', error);
    return {};
  }
};

// Fonction pour réinitialiser toutes les fonctionnalités via l'API
export const resetFeatures = async () => {
  try {
    const resetFeaturesData = await resetFeaturesAPI();
    
    // Déclencher un événement personnalisé pour notifier Herbbie
    window.dispatchEvent(new CustomEvent('featuresUpdated', { 
      detail: resetFeaturesData 
    }));
    
    return resetFeaturesData;
  } catch (error) {
    console.error('Erreur lors de la réinitialisation des fonctionnalités:', error);
    throw error;
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
    console.error('Erreur lors de la vérification des fonctionnalités requises:', error);
    return false;
  }
};

// Fonction pour synchroniser avec Herbbie (événement personnalisé)
export const syncWithHerbbie = async () => {
  try {
    const features = await getFeatures();
    
    // Déclencher un événement pour notifier Herbbie des changements
    window.dispatchEvent(new CustomEvent('herbbieFeaturesUpdate', { 
      detail: features 
    }));
    
    return true;
  } catch (error) {
    console.error('Erreur lors de la synchronisation avec Herbbie:', error);
    return false;
  }
};

// Export par défaut pour compatibilité
export default {
  getFeatures,
  updateFeature,
  isFeatureEnabled,
  getEnabledFeatures,
  resetFeatures,
  getAllFeatures,
  areRequiredFeaturesEnabled,
  syncWithHerbbie
};
