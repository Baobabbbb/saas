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
    console.log('🔄 updateUserProfile - Données reçues:', {
      userId,
      profileData,
      firstName: profileData?.firstName,
      lastName: profileData?.lastName
    });

    // Préparer les données à mettre à jour (utiliser les colonnes correctes)
    const updateData = {
      id: userId,
      prenom: profileData.firstName,
      nom: profileData.lastName
    };

    console.log('📤 updateUserProfile - Données à envoyer:', updateData);

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
      console.error('❌ updateUserProfile - Erreur Supabase:', error);
      throw new Error(`Erreur mise à jour profil: ${error.message}`);
    }

    console.log('✅ updateUserProfile - Succès, données retournées:', data);
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
    const updateData = {
      id: user.id,
      email: user.email,  // Synchroniser l'email
      prenom: user.user_metadata?.firstName || user.user_metadata?.prenom || null,
      nom: user.user_metadata?.lastName || user.user_metadata?.nom || null,
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

    console.log('✅ Profil synchronisé:', data.id, data.email);
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
