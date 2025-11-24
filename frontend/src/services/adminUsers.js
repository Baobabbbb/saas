// Service pour gérer les utilisateurs via l'API backend (panneau admin)
import { authFetch, buildAuthHeaders } from './apiClient';

const API_URL = '/api/users';

/**
 * Récupérer tous les utilisateurs depuis l'API
 */
export const getUsers = async () => {
  try {
    const headers = await buildAuthHeaders({
      'Content-Type': 'application/json',
    });
    
    const response = await authFetch(API_URL, {
      method: 'GET',
      headers,
    });

    if (response.ok) {
      const users = await response.json();
      return users;
    } else {
      const errorText = await response.text();
      console.error('Erreur lors de la récupération des utilisateurs:', response.status, errorText);
      throw new Error(`Erreur API: ${response.status}`);
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des utilisateurs:', error);
    throw error;
  }
};

/**
 * Supprimer un utilisateur et toutes ses créations via l'API (requiert admin)
 */
export const deleteUser = async (userId) => {
  try {
    const headers = await buildAuthHeaders({
      'Content-Type': 'application/json',
    });
    
    const response = await authFetch(`${API_URL}/${userId}`, {
      method: 'DELETE',
      headers,
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const errorText = await response.text();
      console.error('Erreur lors de la suppression:', response.status, errorText);
      throw new Error(`Erreur API: ${response.status} - ${errorText}`);
    }
  } catch (error) {
    console.error('Erreur lors de la suppression de l\'utilisateur:', error);
    throw error;
  }
};

export default {
  getUsers,
  deleteUser
};

