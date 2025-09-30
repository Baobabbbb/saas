// Service pour gérer les fonctionnalités disponibles dans Herbbie
const STORAGE_KEY = 'herbbie_features_config';

// Configuration par défaut des fonctionnalités
const DEFAULT_FEATURES = {
  animation: { enabled: true, name: 'Dessin animé', icon: '🎬', description: 'Génération de dessins animés personnalisés avec IA' },
  comic: { enabled: true, name: 'Bande dessinée', icon: '💬', description: 'Création de bandes dessinées avec bulles de dialogue' },
  coloring: { enabled: true, name: 'Coloriage', icon: '🎨', description: 'Pages de coloriage à imprimer pour les enfants' },
  audio: { enabled: true, name: 'Histoire', icon: '📖', description: 'Histoires audio avec narration automatique' },
  rhyme: { enabled: true, name: 'Comptine', icon: '🎵', description: 'Comptines musicales avec paroles et mélodies' }
};

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

// Fonction pour récupérer les fonctionnalités
export const getFeatures = async () => {
  try {
    // Charger depuis le localStorage
    const storedFeatures = loadFeaturesFromStorage();
    if (storedFeatures) {
      return storedFeatures;
    }

    // Fallback vers les valeurs par défaut
    console.log('📋 Aucune configuration trouvée, utilisation des valeurs par défaut');
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

// Fonction pour récupérer toutes les fonctionnalités (y compris désactivées)
export const getAllFeatures = async () => {
  return await getFeatures();
};

// Fonction pour sauvegarder les fonctionnalités dans le localStorage
export const saveFeatures = (features) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(features));
    console.log('💾 Fonctionnalités sauvegardées dans localStorage');
    return true;
  } catch (error) {
    console.error('Erreur lors de la sauvegarde des fonctionnalités:', error);
    return false;
  }
};

// Fonction pour mettre à jour une fonctionnalité
export const updateFeature = (featureKey, enabled) => {
  try {
    const currentFeatures = loadFeaturesFromStorage() || DEFAULT_FEATURES;
    const updatedFeatures = {
      ...currentFeatures,
      [featureKey]: {
        ...currentFeatures[featureKey],
        enabled: enabled,
        updated_at: new Date().toISOString()
      }
    };

    return saveFeatures(updatedFeatures) ? updatedFeatures : null;
  } catch (error) {
    console.error('Erreur lors de la mise à jour de la fonctionnalité:', error);
    return null;
  }
};

// Fonction pour synchroniser manuellement les fonctionnalités (solution temporaire)
export const syncFeatures = async () => {
  console.log('🔄 Tentative de synchronisation...');
  return await getFeatures();
};

// Fonction pour écouter les changements de fonctionnalités depuis le panneau
export const listenForFeatureChanges = (callback) => {
  const handleStorageChange = (event) => {
    if (event.key === STORAGE_KEY && event.newValue) {
      try {
        const newFeatures = JSON.parse(event.newValue);
        console.log('🔄 Changements détectés dans localStorage:', newFeatures);

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
      console.log('🔄 Événement personnalisé reçu:', event.detail);

      if (callback && typeof callback === 'function') {
        callback(event.detail);
      }
    }
  };

  // Vérifier périodiquement les changements (fallback)
  const checkForChanges = () => {
    const storedFeatures = loadFeaturesFromStorage();
    if (storedFeatures) {
      console.log('🔄 Vérification périodique des fonctionnalités');
      if (callback && typeof callback === 'function') {
        callback(storedFeatures);
      }
    }
  };

  // Écouter les changements de localStorage (événements cross-domain)
  window.addEventListener('storage', handleStorageChange);

  // Écouter les événements personnalisés (événements locaux)
  window.addEventListener('herbbieFeaturesUpdate', handleCustomEvent);
  window.addEventListener('featuresUpdated', handleCustomEvent);

  // Vérification périodique toutes les 3 secondes
  const intervalId = setInterval(checkForChanges, 3000);

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
  refreshFeatures,
  listenForFeatureChanges
};