import { supabase } from '../supabaseClient';

/**
 * Récupère le profil complet d'un utilisateur
 */
export async function getUserProfile(userId) {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 = pas de résultat
      console.error('Erreur récupération profil:', error);
      throw new Error(`Erreur récupération profil: ${error.message}`);
    }

    return data;
  } catch (error) {
    console.error('Erreur critique récupération profil:', error);
    throw error;
  }
}

/**
 * Met à jour le profil d'un utilisateur
 */
export async function updateUserProfile(userId, profileData) {
  try {
    // Préparer les données à mettre à jour (utiliser les colonnes correctes)
    const updateData = {
      id: userId,
      prenom: profileData.firstName,
      nom: profileData.lastName
    };

    // Upsert: créer ou mettre à jour
    const { data, error } = await supabase
      .from('profiles')
      .upsert(updateData, {
        onConflict: 'id',
        returning: 'representation'
      })
      .select()
      .single();

    if (error) {
      console.error('Erreur mise à jour profil:', error);
      throw new Error(`Erreur mise à jour profil: ${error.message}`);
    }

    return data;
  } catch (error) {
    console.error('Erreur critique mise à jour profil:', error);
    throw error;
  }
}

/**
 * Synchronise le profil avec les informations de l'utilisateur connecté
 */
export async function syncUserProfile(user) {
  try {
    // Récupérer d'abord le profil existant
    const { data: existingProfile, error: fetchError } = await supabase
      .from('profiles')
      .select('prenom, nom')
      .eq('id', user.id)
      .single();

    const updateData = {
      id: user.id,
      email: user.email,  // Synchroniser l'email
      // NE PAS ÉCRASER prenom/nom s'ils existent déjà
      prenom: existingProfile?.prenom || user.user_metadata?.firstName || user.user_metadata?.prenom || null,
      nom: existingProfile?.nom || user.user_metadata?.lastName || user.user_metadata?.nom || null,
      last_login: new Date().toISOString()  // Mettre à jour la dernière connexion
    };

    const { data, error } = await supabase
      .from('profiles')
      .upsert(updateData, {
        onConflict: 'id',
        returning: 'representation'
      })
      .select()
      .single();

    if (error) {
      console.error('Erreur sync profil:', error);
      throw new Error(`Erreur sync profil: ${error.message}`);
    }

    return data;
  } catch (error) {
    console.error('Erreur critique sync profil:', error);
    throw error;
  }
}

/**
 * Crée un profil pour un nouvel utilisateur
 */
export async function createUserProfile(userId, email, profileData = {}) {
  console.log('👤 HERBBIE: Création profil utilisateur:', userId, email);

  try {
    const newProfile = {
      id: userId,
      email: email,
      prenom: profileData.firstName || profileData.prenom || email.split('@')[0],
      nom: profileData.lastName || profileData.nom || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const { data, error } = await supabase
      .from('profiles')
      .insert([newProfile])
      .select()
      .single();

    if (error) {
      console.error('❌ HERBBIE: Erreur création profil:', error);
      throw new Error(`Erreur création profil: ${error.message}`);
    }

    console.log('✅ HERBBIE: Profil créé avec succès:', data);
    return data;
  } catch (error) {
    console.error('❌ HERBBIE: Erreur critique création profil:', error);
    throw error;
  }
}

/**
 * Supprime le profil d'un utilisateur
 */
export async function deleteUserProfile(userId) {
  try {
    const { error } = await supabase
      .from('profiles')
      .delete()
      .eq('id', userId);

    if (error) {
      console.error('Erreur suppression profil:', error);
      throw new Error(`Erreur suppression profil: ${error.message}`);
    }

    return true;
  } catch (error) {
    console.error('Erreur critique suppression profil:', error);
    throw error;
  }
}
