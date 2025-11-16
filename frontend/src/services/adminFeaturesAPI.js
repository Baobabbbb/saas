// Service pour gérer les fonctionnalités via l'API backend
import { supabase } from '../supabaseClient';

const API_URL = '/api/features';

/**
 * Récupère le token JWT Supabase depuis la session actuelle
 */
const getAuthToken = async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token ? `Bearer ${session.access_token}` : null;
  } catch (error) {
    console.error('Erreur lors de la récupération du token:', error);
    return null;
  }
};

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
 * Mettre à jour une fonctionnalité via l'API (requiert admin)
 */
export const updateFeatureAPI = async (featureKey, enabled) => {
  try {
    const authToken = await getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
    };
    
    // Ajouter le header Authorization si un token est disponible
    if (authToken) {
      headers['Authorization'] = authToken;
    }
    
    const response = await fetch(`${API_URL}/${featureKey}`, {
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
    const authToken = await getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
    };
    
    // Ajouter le header Authorization si un token est disponible
    if (authToken) {
      headers['Authorization'] = authToken;
    }
    
    const response = await fetch(`${API_URL}/reset`, {
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

