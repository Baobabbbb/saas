import { supabase } from '../supabaseClient';

console.log('🚀 FRIDAY: Service profil - SUPABASE INTEGRATION');

/**
 * Récupère le profil complet d'un utilisateur
 */
export async function getUserProfile(userId) {
  console.log('👤 FRIDAY: Récupération profil utilisateur:', userId);
  
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 = pas de résultat
      console.error('❌ FRIDAY: Erreur récupération profil:', error);
      throw new Error(`Erreur récupération profil: ${error.message}`);
    }

    console.log('✅ FRIDAY: Profil récupéré:', data);
    return data;
  } catch (error) {
    console.error('❌ FRIDAY: Erreur critique récupération profil:', error);
    throw error;
  }
}

/**
 * Met à jour le profil d'un utilisateur
 */
export async function updateUserProfile(userId, profileData) {
  console.log('💾 FRIDAY: Mise à jour profil utilisateur:', userId, profileData);
  
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
      console.error('❌ FRIDAY: Erreur mise à jour profil:', error);
      throw new Error(`Erreur mise à jour profil: ${error.message}`);
    }

    console.log('✅ FRIDAY: Profil mis à jour avec succès:', data);
    return data;
  } catch (error) {
    console.error('❌ FRIDAY: Erreur critique mise à jour profil:', error);
    throw error;
  }
}

/**
 * Crée un profil pour un nouvel utilisateur
 */
export async function createUserProfile(userId, email, profileData = {}) {
  console.log('👤 FRIDAY: Création profil utilisateur:', userId, email);
  
  try {
    const newProfile = {
      id: userId,
      email: email,
      first_name: profileData.firstName || email.split('@')[0],
      last_name: profileData.lastName || '',
      full_name: `${profileData.firstName || email.split('@')[0]} ${profileData.lastName || ''}`.trim(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const { data, error } = await supabase
      .from('profiles')
      .insert([newProfile])
      .select()
      .single();

    if (error) {
      console.error('❌ FRIDAY: Erreur création profil:', error);
      throw new Error(`Erreur création profil: ${error.message}`);
    }

    console.log('✅ FRIDAY: Profil créé avec succès:', data);
    return data;
  } catch (error) {
    console.error('❌ FRIDAY: Erreur critique création profil:', error);
    throw error;
  }
}

/**
 * Supprime le profil d'un utilisateur
 */
export async function deleteUserProfile(userId) {
  console.log('🗑️ FRIDAY: Suppression profil utilisateur:', userId);
  
  try {
    const { error } = await supabase
      .from('profiles')
      .delete()
      .eq('id', userId);

    if (error) {
      console.error('❌ FRIDAY: Erreur suppression profil:', error);
      throw new Error(`Erreur suppression profil: ${error.message}`);
    }

    console.log('✅ FRIDAY: Profil supprimé avec succès');
    return true;
  } catch (error) {
    console.error('❌ FRIDAY: Erreur critique suppression profil:', error);
    throw error;
  }
}
