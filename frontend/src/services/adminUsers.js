import { authFetch, buildAuthHeaders } from './apiClient';

const API_URL = '/api/users';

export const getUsers = async () => {
  try {
    const response = await authFetch(API_URL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data.users || [];
    } else {
      const errorText = await response.text();
      console.error('Erreur lors du chargement des utilisateurs:', response.status, errorText);
      throw new Error(`Erreur API: ${response.status} ${errorText}`);
    }
  } catch (error) {
    console.error('Erreur lors du chargement des utilisateurs:', error);
    throw error;
  }
};

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
      return true;
    } else {
      const errorText = await response.text();
      console.error('Erreur lors de la suppression de l\'utilisateur:', response.status, errorText);
      throw new Error(`Erreur API: ${response.status} - ${errorText}`);
    }
  } catch (error) {
    console.error('Erreur lors de la suppression de l\'utilisateur:', error);
    throw error;
  }
};


























