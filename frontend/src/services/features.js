// Service pour gérer les fonctionnalités disponibles dans Herbbie
const API_URL = '/api/features';

// Cache en mémoire pour éviter les appels API multiples
let cachedFeatures = null;
let lastFetchTime = 0;
const CACHE_DURATION = 3000; // 3 secondes

// Configuration par défaut des fonctionnalités (utilisée uniquement si l'API échoue)
const DEFAULT_FEATURES = {
  animation: { enabled: true, name: 'Dessin animé', icon: '🎬', description: 'Génération de dessins animés personnalisés avec IA' },
  comic: { enabled: true, name: 'Bande dessinée', icon: '💬', description: 'Création de bandes dessinées avec bulles de dialogue' },
  coloring: { enabled: true, name: 'Coloriage', icon: '🎨', description: 'Pages de coloriage à imprimer pour les enfants' },
  audio: { enabled: true, name: 'Histoire', icon: '📖', description: 'Histoires audio avec narration automatique' },
  rhyme: { enabled: true, name: 'Comptine', icon: '🎵', description: 'Comptines musicales avec paroles et mélodies' }
};

// Fonction pour charger les fonctionnalités depuis l'API
const loadFeaturesFromAPI = async () => {
  try {
    const response = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const features = await response.json();
      // Mettre à jour le cache
      cachedFeatures = features;
      lastFetchTime = Date.now();
      return features;
    } else {
      console.error('Erreur API lors du chargement des fonctionnalités:', response.status);
      throw new Error(`Erreur API: ${response.status}`);
    }
  } catch (error) {
    console.error('Erreur lors du chargement depuis l\'API:', error);
    throw error;
  }
};

// Fonction pour récupérer les fonctionnalités (SOURCE UNIQUE: API)
export const getFeatures = async () => {
  try {
    // Utiliser le cache si disponible et récent
    const now = Date.now();
    if (cachedFeatures && (now - lastFetchTime) < CACHE_DURATION) {
      return cachedFeatures;
    }

    // Charger depuis l'API
    const apiFeatures = await loadFeaturesFromAPI();
    return apiFeatures;
  } catch (error) {
    console.error('Erreur lors de la récupération des fonctionnalités:', error);
    // En cas d'erreur, utiliser les valeurs par défaut
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

// Fonction pour récupérer toutes les fonctionnalités (y compris désactivées)
export const getAllFeatures = async () => {
  return await getFeatures();
};

// Fonction pour forcer le rafraîchissement du cache
export const invalidateCache = () => {
  cachedFeatures = null;
  lastFetchTime = 0;
};

// Fonction pour rafraîchir les fonctionnalités
export const refreshFeatures = async () => {
  return await getFeatures();
};

// Fonction pour synchroniser manuellement les fonctionnalités
export const syncFeatures = async () => {
  return await getFeatures();
};

// Fonction pour écouter les changements de fonctionnalités depuis l'API
export const listenForFeatureChanges = (callback) => {
  let previousFeatures = null;

  // Fonction pour vérifier les changements via l'API
  const checkForChanges = async () => {
    try {
      // Invalider le cache pour forcer un appel API frais
      invalidateCache();
      const currentFeatures = await loadFeaturesFromAPI();
      
      // Comparer avec la version précédente
      const featuresChanged = JSON.stringify(currentFeatures) !== JSON.stringify(previousFeatures);
      
      if (featuresChanged && callback && typeof callback === 'function') {
        previousFeatures = currentFeatures;
        callback(currentFeatures);
      }
    } catch (error) {
      console.error('Erreur lors de la vérification des changements:', error);
    }
  };

  // Polling de l'API toutes les 5 secondes pour détecter les changements
  const pollIntervalId = setInterval(checkForChanges, 5000);
  
  // Effectuer une première vérification immédiate
  checkForChanges();

  // Retourner une fonction pour nettoyer l'écouteur
  return () => {
    clearInterval(pollIntervalId);
  };
};

// Export par défaut pour compatibilité
export default {
  getFeatures,
  isFeatureEnabled,
  getEnabledFeatures,
  getAllFeatures,
  refreshFeatures,
  listenForFeatureChanges,
  invalidateCache
};