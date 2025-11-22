// Service pour gérer les fonctionnalités via l'API backend
import { authFetch, buildAuthHeaders } from './apiClient';

const API_URL = '/api/features';

/**
 * Récupérer toutes les fonctionnalités depuis l'API
 */
export const getFeaturesFromAPI = async () => {
  try {
    const response = await authFetch(API_URL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
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
 * Mettre à jour une fonctionnalité via l'API (requiert admin)
 */
export const updateFeatureAPI = async (featureKey, enabled) => {
  try {
    const headers = await buildAuthHeaders({
      'Content-Type': 'application/json',
    });
    
    const response = await authFetch(`${API_URL}/${featureKey}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify({ enabled }),
    });

    if (response.ok) {
      const data = await response.json();
      return data.features;
    } else {
      const errorText = await response.text();
      console.error('Erreur lors de la mise à jour:', response.status, errorText);
      throw new Error(`Erreur API: ${response.status} - ${errorText}`);
    }
  } catch (error) {
    console.error('Erreur lors de la mise à jour de la fonctionnalité:', error);
    throw error;
  }
};

/**
 * Réinitialiser toutes les fonctionnalités via l'API (requiert admin)
 */
export const resetFeaturesAPI = async () => {
  try {
    const headers = await buildAuthHeaders({
      'Content-Type': 'application/json',
    });
    
    const response = await authFetch(`${API_URL}/reset`, {
      method: 'POST',
      headers,
    });

    if (response.ok) {
      const data = await response.json();
      return data.features;
    } else {
      const errorText = await response.text();
      console.error('Erreur lors de la réinitialisation:', response.status, errorText);
      throw new Error(`Erreur API: ${response.status} - ${errorText}`);
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

