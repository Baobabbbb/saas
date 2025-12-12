import { supabase } from '../supabaseClient'

// Fonction pour obtenir l'ID utilisateur actuel
async function getCurrentUserId() {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (session?.user?.id) {
      return session.user.id;
    }
    
    const cachedUser = localStorage.getItem('friday_user_cache');
    if (cachedUser) {
      const user = JSON.parse(cachedUser);
      if (user.id) {
        return user.id;
      }
    }
    
    return null;
  } catch (error) {
    console.error('Erreur récupération ID utilisateur:', error);
    return null;
  }
}

// Ajouter une création
export async function addCreation({ type, title, data }) {
  const userId = await getCurrentUserId();
  
  if (!userId) {
    throw new Error('Utilisateur non connecté');
  }
  
  try {
    const creationData = {
      user_id: userId,
      type,
      title,
      data: {
        ...data,
        created_via: 'friday_web',
        timestamp: new Date().toISOString()
      }
    };
    
    const { data: newCreation, error } = await supabase
      .from('creations')
      .insert([creationData])
      .select()
      .single();

    if (error) {
      console.error('Erreur Supabase lors de la création:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    return newCreation;
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error);
    throw error;
  }
}

// Récupérer les créations
export async function getCreations() {
  const userId = await getCurrentUserId();
  
  if (!userId) {
    return [];
  }
  
  try {
    const { data: creations, error } = await supabase
      .from('creations')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Erreur Supabase lors de la récupération:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    return creations || [];
    
  } catch (error) {
    console.error('Erreur lors de la récupération:', error);
    throw error;
  }
}

// Alias pour compatibilité avec History.jsx
export const getUserCreations = getCreations;

// Supprimer une création
export async function deleteCreation(id) {
  try {
    // D'abord, supprimer les fichiers du Storage Supabase
    const userId = await getCurrentUserId();
    if (!userId) {
      throw new Error('Utilisateur non connecté');
    }
    
    // Récupérer le token d'authentification
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.access_token) {
      throw new Error('Token d\'authentification manquant');
    }
    
    // Appeler l'endpoint backend pour supprimer les fichiers
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://herbbie.com';
    try {
      const deleteFilesResponse = await fetch(`${API_BASE_URL}/delete_creation_files/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!deleteFilesResponse.ok) {
        const errorData = await deleteFilesResponse.json().catch(() => ({}));
        console.warn('⚠️ Erreur lors de la suppression des fichiers (non-bloquant):', errorData);
        // Continuer quand même la suppression de la base de données
      } else {
        const deleteResult = await deleteFilesResponse.json();
        console.log(`✅ Fichiers supprimés: ${deleteResult.deleted_count || 0} fichier(s)`);
      }
    } catch (filesError) {
      console.warn('⚠️ Erreur lors de la suppression des fichiers (non-bloquant):', filesError);
      // Continuer quand même la suppression de la base de données
    }
    
    // Ensuite, supprimer la création de la base de données
    const { error } = await supabase
      .from('creations')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Erreur Supabase lors de la suppression:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    return true;
    
  } catch (error) {
    console.error('Erreur lors de la suppression:', error);
    throw error;
  }
}

// Mettre à jour une création
export async function updateCreation(id, updates) {
  try {
    const { data: updatedCreation, error } = await supabase
      .from('creations')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Erreur Supabase lors de la mise à jour:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    return updatedCreation;
    
  } catch (error) {
    console.error('Erreur lors de la mise à jour:', error);
    throw error;
  }
}

// Obtenir une création spécifique
export async function getCreation(id) {
  try {
    const { data: creation, error } = await supabase
      .from('creations')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Erreur Supabase lors de la récupération:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    return creation;
    
  } catch (error) {
    console.error('Erreur lors de la récupération:', error);
    throw error;
  }
}

// Fonction utilitaire pour vérifier la connexion Supabase
export async function testSupabaseConnection() {
  try {
    const { data, error, count } = await supabase
      .from('creations')
      .select('*', { count: 'exact', head: true });

    if (error) {
      console.error('Connexion Supabase échouée:', error);
      return { success: false, error: error.message };
    }

    return { success: true, count };
    
  } catch (error) {
    console.error('Test connexion échoué:', error);
    return { success: false, error: error.message };
  }
}