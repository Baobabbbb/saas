// Service pour gérer les fonctionnalités via l'API backend
const API_URL = '/api/features';

/**
 * Récupérer toutes les fonctionnalités depuis l'API
 */
export const getFeaturesFromAPI = async () => {
  try {
    const response = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const features = await response.json();
      return features;
    } else {
      console.error('Erreur lors de la récupération des fonctionnalités:', response.statusText);
      throw new Error(`Erreur API: ${response.status}`);
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des fonctionnalités:', error);
    throw error;
  }
};

/**
 * Mettre à jour une fonctionnalité via l'API
 */
export const updateFeatureAPI = async (featureKey, enabled) => {
  try {
    const response = await fetch(`${API_URL}/${featureKey}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ enabled }),
    });

    if (response.ok) {
      const data = await response.json();
      return data.features;
    } else {
      console.error('Erreur lors de la mise à jour:', response.statusText);
      throw new Error(`Erreur API: ${response.status}`);
    }
  } catch (error) {
    console.error('Erreur lors de la mise à jour de la fonctionnalité:', error);
    throw error;
  }
};

/**
 * Réinitialiser toutes les fonctionnalités via l'API
 */
export const resetFeaturesAPI = async () => {
  try {
    const response = await fetch(`${API_URL}/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data.features;
    } else {
      console.error('Erreur lors de la réinitialisation:', response.statusText);
      throw new Error(`Erreur API: ${response.status}`);
    }
  } catch (error) {
    console.error('Erreur lors de la réinitialisation:', error);
    throw error;
  }
};

export default {
  getFeaturesFromAPI,
  updateFeatureAPI,
  resetFeaturesAPI
};

