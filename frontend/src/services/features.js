// Service pour gérer les fonctionnalités disponibles dans Herbbie
const STORAGE_KEY = 'herbbie_features_config';
const API_BASE_URL = 'https://saas-production.up.railway.app/api';

// Configuration par défaut des fonctionnalités
const DEFAULT_FEATURES = {
  animation: { enabled: true, name: 'Dessin animé', icon: '🎬', description: 'Génération de dessins animés personnalisés avec IA' },
  comic: { enabled: true, name: 'Bande dessinée', icon: '💬', description: 'Création de bandes dessinées avec bulles de dialogue' },
  coloring: { enabled: true, name: 'Coloriage', icon: '🎨', description: 'Pages de coloriage à imprimer pour les enfants' },
  audio: { enabled: true, name: 'Histoire', icon: '📖', description: 'Histoires audio avec narration automatique' },
  rhyme: { enabled: true, name: 'Comptine', icon: '🎵', description: 'Comptines musicales avec paroles et mélodies' }
};

// Fonction pour charger les fonctionnalités depuis l'API du backend
const loadFeaturesFromAPI = async () => {
  try {
    console.log('🔄 Chargement des fonctionnalités depuis l\'API...');
    const response = await fetch(`${API_BASE_URL}/features`, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });

    // Vérifier si la réponse est du JSON
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      if (response.ok) {
        const features = await response.json();
        console.log('📋 Fonctionnalités chargées depuis l\'API:', features);

        // Sauvegarder dans localStorage pour le cache
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(features));
        } catch (error) {
          console.warn('Erreur lors de la sauvegarde dans localStorage:', error);
        }

        return features;
      } else {
        console.warn(`API erreur ${response.status}, utilisation du cache local`);
        throw new Error(`API error: ${response.status}`);
      }
    } else {
      console.warn('Réponse API n\'est pas du JSON, utilisation du cache local');
      throw new Error('API returned HTML instead of JSON');
    }
  } catch (error) {
    console.warn('Erreur lors du chargement depuis l\'API:', error.message);
    throw error;
  }
};

// Fonction pour charger les fonctionnalités depuis le localStorage (fallback)
const loadFeaturesFromStorage = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      console.log('📋 Fonctionnalités chargées depuis le localStorage (fallback):', parsed);
      return parsed;
    }
  } catch (error) {
    console.warn('Erreur lors du chargement des fonctionnalités depuis le localStorage:', error);
  }
  return null;
};

// Fonction pour récupérer les fonctionnalités (API en priorité, localStorage en fallback)
export const getFeatures = async () => {
  try {
    // Essayer d'abord de charger depuis l'API
    try {
      const apiFeatures = await loadFeaturesFromAPI();
      return apiFeatures;
    } catch (apiError) {
      console.log('API non disponible, utilisation du cache local');
    }

    // Fallback vers le localStorage
    const storedFeatures = loadFeaturesFromStorage();
    if (storedFeatures) {
      return storedFeatures;
    }

    // Dernier fallback vers les valeurs par défaut
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

// Fonction pour forcer la synchronisation depuis l'API
export const refreshFeatures = async () => {
  try {
    console.log('🔄 Synchronisation forcée depuis l\'API...');
    const features = await loadFeaturesFromAPI();
    return features;
  } catch (error) {
    console.warn('Impossible de synchroniser depuis l\'API:', error);
    // Retourner les fonctionnalités actuelles en cas d'échec
    return await getFeatures();
  }
};

// Fonction pour synchroniser manuellement les fonctionnalités
export const syncFeatures = async () => {
  return await refreshFeatures();
};

// Fonction pour écouter les changements de fonctionnalités depuis le panneau
export const listenForFeatureChanges = (callback) => {
  const handleStorageChange = (event) => {
    if (event.key === STORAGE_KEY && event.newValue) {
      try {
        const newFeatures = JSON.parse(event.newValue);
        console.log('🔄 Changements détectés dans localStorage, synchronisation depuis l\'API...');

        // Essayer de synchroniser depuis l'API pour être sûr d'avoir les données à jour
        loadFeaturesFromAPI().then(apiFeatures => {
          console.log('✅ Synchronisation réussie depuis l\'API');
          if (callback && typeof callback === 'function') {
            callback(apiFeatures);
          }
        }).catch(apiError => {
          console.log('API non disponible, utilisation des données locales');
          if (callback && typeof callback === 'function') {
            callback(newFeatures);
          }
        });
      } catch (error) {
        console.error('Erreur lors du parsing des nouvelles fonctionnalités:', error);
      }
    }
  };

  const handleCustomEvent = (event) => {
    if (event.detail) {
      console.log('🔄 Événement personnalisé reçu, synchronisation depuis l\'API...');

      // Essayer de synchroniser depuis l'API pour être sûr d'avoir les données à jour
      loadFeaturesFromAPI().then(apiFeatures => {
        console.log('✅ Synchronisation réussie depuis l\'API');
        if (callback && typeof callback === 'function') {
          callback(apiFeatures);
        }
      }).catch(apiError => {
        console.log('API non disponible, utilisation des données de l\'événement');
        if (callback && typeof callback === 'function') {
          callback(event.detail);
        }
      });
    }
  };

  // Vérifier périodiquement les changements depuis l'API (fallback plus robuste)
  const checkForChanges = async () => {
    try {
      const apiFeatures = await loadFeaturesFromAPI();
      const currentFeatures = await getFeatures();

      // Comparer les fonctionnalités
      const hasChanged = JSON.stringify(apiFeatures) !== JSON.stringify(currentFeatures);

      if (hasChanged) {
        console.log('🔄 Changements détectés via vérification API:', apiFeatures);
        if (callback && typeof callback === 'function') {
          callback(apiFeatures);
        }
      }
    } catch (error) {
      console.log('Vérification API échouée, pas de changement détecté');
    }
  };

  // Écouter les changements de localStorage (événements cross-domain)
  window.addEventListener('storage', handleStorageChange);

  // Écouter les événements personnalisés (événements locaux)
  window.addEventListener('herbbieFeaturesUpdate', handleCustomEvent);
  window.addEventListener('featuresUpdated', handleCustomEvent);

  // Vérification périodique depuis l'API toutes les 10 secondes (au lieu de 2)
  const intervalId = setInterval(checkForChanges, 10000);

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