import { supabase } from '../supabaseClient'

console.log('🚀 FRIDAY: Service créations - SUPABASE ONLY MODE');

// Fonction pour obtenir l'ID utilisateur actuel
async function getCurrentUserId() {
  try {
    // 1. Essayer de récupérer depuis la session Supabase DIRECTEMENT
    const { data: { session }, error } = await supabase.auth.getSession();
    if (session?.user?.id) {
      console.log('👤 FRIDAY: ID utilisateur récupéré depuis session Supabase:', session.user.id);
      return session.user.id;
    }
    
    // 2. Essayer le cache localStorage
    const cachedUser = localStorage.getItem('friday_user_cache');
    if (cachedUser) {
      const user = JSON.parse(cachedUser);
      if (user.id) {
        console.log('👤 FRIDAY: ID utilisateur récupéré depuis cache:', user.id);
        return user.id;
      }
    }
    
    console.warn('⚠️ FRIDAY: Aucun ID utilisateur trouvé');
    return null;
  } catch (error) {
    console.error('❌ FRIDAY: Erreur récupération ID utilisateur:', error);
    return null;
  }
}

// Ajouter une création - SUPABASE OBLIGATOIRE
export async function addCreation({ type, title, data }) {
  console.log('💾 FRIDAY: Sauvegarde création en base Supabase', { type, title });
  
  const userId = await getCurrentUserId();
  
  if (!userId) {
    console.warn('⚠️ FRIDAY: Impossible de sauvegarder - pas d\'ID utilisateur');
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
        user_email: localStorage.getItem('userEmail') || 'anonymous',
        timestamp: new Date().toISOString()
      }
    };

    console.log('📤 Envoi vers Supabase:', creationData);
    
    const { data: newCreation, error } = await supabase
      .from('creations')
      .insert([creationData])
      .select()
      .single();

    if (error) {
      console.error('❌ ERREUR Supabase lors de la création:', error);
      console.error('🔍 FRIDAY: Détails erreur Supabase:', {
        message: error.message,
        details: error.details,
        hint: error.hint,
        code: error.code
      });
      console.error('📄 FRIDAY: Données envoyées:', creationData);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    console.log('✅ Création sauvegardée en base:', newCreation);
    return newCreation;
    
  } catch (error) {
    console.error('❌ ERREUR CRITIQUE lors de la sauvegarde:', error);
    throw error;
  }
}

// Récupérer les créations - SUPABASE OBLIGATOIRE
export async function getCreations() {
  console.log('📥 FRIDAY: Récupération créations depuis Supabase');
  
  const userId = await getCurrentUserId();
  
  if (!userId) {
    console.warn('⚠️ FRIDAY: Impossible de récupérer les créations - pas d\'ID utilisateur');
    return [];
  }
  
  try {
    console.log('🔍 FRIDAY: Recherche créations pour user_id:', userId);
    const { data: creations, error } = await supabase
      .from('creations')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('❌ ERREUR Supabase lors de la récupération:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    console.log(`✅ ${creations?.length || 0} créations récupérées de la base`);
    return creations || [];
    
  } catch (error) {
    console.error('❌ ERREUR CRITIQUE lors de la récupération:', error);
    throw error;
  }
}

// Alias pour compatibilité avec History.jsx
export const getUserCreations = getCreations;

// Supprimer une création - SUPABASE OBLIGATOIRE
export async function deleteCreation(id) {
  console.log('🗑️ FRIDAY: Suppression création de Supabase, ID:', id);
  
  try {
    const { error } = await supabase
      .from('creations')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('❌ ERREUR Supabase lors de la suppression:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    console.log('✅ Création supprimée de la base');
    return true;
    
  } catch (error) {
    console.error('❌ ERREUR CRITIQUE lors de la suppression:', error);
    throw error;
  }
}

// Mettre à jour une création - SUPABASE OBLIGATOIRE
export async function updateCreation(id, updates) {
  console.log('📝 FRIDAY: Mise à jour création en base, ID:', id);
  
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
      console.error('❌ ERREUR Supabase lors de la mise à jour:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    console.log('✅ Création mise à jour en base:', updatedCreation);
    return updatedCreation;
    
  } catch (error) {
    console.error('❌ ERREUR CRITIQUE lors de la mise à jour:', error);
    throw error;
  }
}

// Obtenir une création spécifique - SUPABASE OBLIGATOIRE
export async function getCreation(id) {
  console.log('🔍 FRIDAY: Récupération création spécifique, ID:', id);
  
  try {
    const { data: creation, error } = await supabase
      .from('creations')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('❌ ERREUR Supabase lors de la récupération:', error);
      throw new Error(`Erreur base de données: ${error.message}`);
    }

    console.log('✅ Création récupérée:', creation);
    return creation;
    
  } catch (error) {
    console.error('❌ ERREUR CRITIQUE lors de la récupération:', error);
    throw error;
  }
}

// Fonction utilitaire pour vérifier la connexion Supabase
export async function testSupabaseConnection() {
  console.log('🧪 FRIDAY: Test de connexion Supabase...');
  
  try {
    const { data, error, count } = await supabase
      .from('creations')
      .select('*', { count: 'exact', head: true });

    if (error) {
      console.error('❌ Connexion Supabase échouée:', error);
      return { success: false, error: error.message };
    }

    console.log('✅ Connexion Supabase réussie - Créations en base:', count);
    return { success: true, count };
    
  } catch (error) {
    console.error('❌ Test connexion échoué:', error);
    return { success: false, error: error.message };
  }
}

console.log('✅ FRIDAY: Service créations initialisé - Mode Supabase uniquement');