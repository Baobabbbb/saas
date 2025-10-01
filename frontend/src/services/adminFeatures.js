// Service pour gérer l'état des fonctionnalités du site (version locale)
// Utilise la même clé que Herbbie pour permettre la synchronisation
const STORAGE_KEY = 'admin_features_config';

// Configuration par défaut des fonctionnalités
const DEFAULT_FEATURES = {
  animation: { 
    enabled: true, 
    name: 'Dessin animé', 
    icon: '🎬',
    description: 'Génération de dessins animés personnalisés avec IA'
  },
  comic: { 
    enabled: true, 
    name: 'Bande dessinée', 
    icon: '💬',
    description: 'Création de bandes dessinées avec bulles de dialogue'
  },
  coloring: { 
    enabled: true, 
    name: 'Coloriage', 
    icon: '🎨',
    description: 'Pages de coloriage à imprimer pour les enfants'
  },
  audio: { 
    enabled: true, 
    name: 'Histoire', 
    icon: '📖',
    description: 'Histoires audio avec narration automatique'
  },
  rhyme: { 
    enabled: true, 
    name: 'Comptine', 
    icon: '🎵',
    description: 'Comptines musicales avec paroles et mélodies'
  }
};

// Fonction pour charger les fonctionnalités depuis le localStorage
const loadFeaturesFromStorage = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Fusionner avec les valeurs par défaut pour s'assurer que toutes les clés existent
      return { ...DEFAULT_FEATURES, ...parsed };
    }
  } catch (error) {
    console.warn('Erreur lors du chargement des fonctionnalités depuis le localStorage:', error);
  }
  return DEFAULT_FEATURES;
};

// Fonction pour sauvegarder les fonctionnalités dans le localStorage
const saveFeaturesToStorage = (features) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(features));
    return true;
  } catch (error) {
    console.error('Erreur lors de la sauvegarde des fonctionnalités:', error);
    return false;
  }
};

// Fonction pour récupérer les fonctionnalités
export const getFeatures = async () => {
  try {
    const features = loadFeaturesFromStorage();
    console.log('📋 Fonctionnalités chargées:', features);
    return features;
  } catch (error) {
    console.error('Erreur lors du chargement des fonctionnalités:', error);
    return DEFAULT_FEATURES;
  }
};

// Fonction pour mettre à jour une fonctionnalité
export const updateFeature = async (featureKey, enabled) => {
  try {
    const currentFeatures = loadFeaturesFromStorage();
    
    if (!currentFeatures[featureKey]) {
      console.error(`Fonctionnalité ${featureKey} non trouvée`);
      return null;
    }
    
    // Mettre à jour la fonctionnalité
    const updatedFeatures = {
      ...currentFeatures,
      [featureKey]: {
        ...currentFeatures[featureKey],
        enabled: enabled,
        updated_at: new Date().toISOString()
      }
    };
    
    // Sauvegarder dans le localStorage
    if (saveFeaturesToStorage(updatedFeatures)) {
      console.log(`✅ Fonctionnalité ${featureKey} mise à jour: ${enabled ? 'activée' : 'désactivée'}`);
      
      // Déclencher un événement personnalisé pour notifier les composants
      window.dispatchEvent(new CustomEvent('featuresUpdated', { 
        detail: updatedFeatures 
      }));
      
      return updatedFeatures;
    } else {
      console.error('Erreur lors de la sauvegarde');
      return null;
    }
  } catch (error) {
    console.error('Erreur lors de la mise à jour de la fonctionnalité:', error);
    return null;
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

// Fonction pour réinitialiser toutes les fonctionnalités
export const resetFeatures = async () => {
  try {
    const resetFeatures = { ...DEFAULT_FEATURES };
    
    // Ajouter un timestamp de réinitialisation
    Object.keys(resetFeatures).forEach(key => {
      resetFeatures[key].updated_at = new Date().toISOString();
    });
    
    if (saveFeaturesToStorage(resetFeatures)) {
      console.log('🔄 Toutes les fonctionnalités ont été réinitialisées');
      
      // Déclencher un événement personnalisé pour notifier les composants
      window.dispatchEvent(new CustomEvent('featuresUpdated', { 
        detail: resetFeatures 
      }));
      
      return resetFeatures;
    } else {
      console.error('Erreur lors de la réinitialisation');
      return null;
    }
  } catch (error) {
    console.error('Erreur lors de la réinitialisation des fonctionnalités:', error);
    return null;
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

// Fonction pour synchroniser avec Herbbie (optionnel)
export const syncWithHerbbie = async () => {
  try {
    // Cette fonction peut être utilisée pour synchroniser avec Herbbie si nécessaire
    const features = await getFeatures();
    
    // Déclencher un événement pour notifier Herbbie des changements
    window.dispatchEvent(new CustomEvent('herbbieFeaturesUpdate', { 
      detail: features 
    }));
    
    console.log('🔄 Synchronisation avec Herbbie déclenchée');
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