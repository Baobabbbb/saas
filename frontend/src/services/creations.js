import { supabase } from '../supabaseClient'

// Service pour gérer les créations avec Supabase
// Ajouter une création
export async function addCreation({ type, title, data }) {
  try {
    // Récupérer l'utilisateur connecté depuis Supabase Auth
    const { data: userData, error: userError } = await supabase.auth.getUser();
    
    if (userError || !userData?.user) {
      return { error: "Non authentifié" };
    }

    // Ajouter la création dans Supabase
    const { data: newCreation, error } = await supabase
      .from('creations')
      .insert([{
        user_id: userData.user.id,
        type,
        title,
        data
      }])
      .select()
      .single();

    if (error) {
      // Fallback vers localStorage
      const userEmail = localStorage.getItem('userEmail');
      const creations = JSON.parse(localStorage.getItem('creations') || '[]');
      const fallbackCreation = {
        id: Date.now().toString(),
        user_email: userEmail,
        type,
        title,
        data,
        created_at: new Date().toISOString()
      };
      creations.unshift(fallbackCreation);
      localStorage.setItem('creations', JSON.stringify(creations));
      return { data: fallbackCreation };
    }

    return { data: newCreation };
  } catch (error) {
    return { error: error.message };
  }
}

// Récupérer l'historique des créations de l'utilisateur
export async function getUserCreations() {
  try {
    // Récupérer l'utilisateur connecté depuis Supabase Auth
    const { data: userData, error: userError } = await supabase.auth.getUser();
    
    if (userError || !userData?.user) {
      return [];
    }

    // Récupérer les créations depuis Supabase
    const { data, error } = await supabase
      .from('creations')
      .select('*')
      .eq('user_id', userData.user.id)
      .order('created_at', { ascending: false });

    if (error) {
      // Fallback vers localStorage
      const userEmail = localStorage.getItem('userEmail');
      const allCreations = JSON.parse(localStorage.getItem('creations') || '[]');
      const userCreations = allCreations.filter(creation => creation.user_email === userEmail);
      return userCreations;
    }

    return data || [];
  } catch (error) {
    return [];
  }
}

// Supprimer une création
export async function deleteCreation(id) {
  try {
    // Récupérer l'utilisateur connecté depuis Supabase Auth
    const { data: userData, error: userError } = await supabase.auth.getUser();
    
    if (userError || !userData?.user) {
      return { error: "Non authentifié" };
    }

    // Supprimer de Supabase
    const { error: supabaseError } = await supabase
      .from('creations')
      .delete()
      .eq('id', id)
      .eq('user_id', userData.user.id);

    if (supabaseError) {
      console.error('Erreur lors de la suppression Supabase:', supabaseError);
      // Fallback vers localStorage
      const creations = JSON.parse(localStorage.getItem('creations') || '[]');
      const filteredCreations = creations.filter(creation => creation.id !== id);
      localStorage.setItem('creations', JSON.stringify(filteredCreations));
    }

    return { error: null };
  } catch (error) {
    console.error('Erreur lors de la suppression:', error);
    return { error: "Erreur lors de la suppression" };
  }
}
