import { supabase } from '../supabaseClient'

// ID utilisateur fictif pour forcer l'utilisation de Supabase
const FORCE_SUPABASE_USER_ID = 'friday-user-' + Date.now().toString();

// Service pour gérer les créations AVEC SUPABASE OBLIGATOIRE
// PATCH TEMPORAIRE : Force l'utilisation de Supabase au lieu du localStorage

// Ajouter une création - VERSION SUPABASE ONLY
export async function addCreation({ type, title, data }) {
  try {
    console.log('🔄 SUPABASE: Tentative de création...', { type, title });

    // FORCER l'utilisation de Supabase - PAS de fallback localStorage
    const { data: newCreation, error } = await supabase
      .from('creations')
      .insert([{
        user_id: FORCE_SUPABASE_USER_ID, // ID fictif pour contourner l'auth
        type,
        title,
        data: {
          ...data,
          created_via: 'web_version',
          timestamp: new Date().toISOString()
        }
      }])
      .select()
      .single();

    if (error) {
      console.error('❌ SUPABASE ERROR:', error);
      throw new Error(`Supabase error: ${error.message}`);
    }

    console.log('✅ SUPABASE SUCCESS: Création sauvegardée', newCreation);
    return { data: newCreation };

  } catch (error) {
    console.error('💥 ERREUR SUPABASE:', error);
    // PAS de fallback - on veut voir les vraies erreurs Supabase
    throw error;
  }
}

// Récupérer l'historique des créations - VERSION SUPABASE ONLY
export async function getUserCreations() {
  try {
    console.log('🔄 SUPABASE: Récupération des créations...');

    // FORCER l'utilisation de Supabase
    const { data, error } = await supabase
      .from('creations')
      .select('*')
      .eq('user_id', FORCE_SUPABASE_USER_ID)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('❌ SUPABASE ERROR récupération:', error);
      throw new Error(`Supabase error: ${error.message}`);
    }

    console.log('✅ SUPABASE SUCCESS: Récupéré', data?.length || 0, 'créations');
    return data || [];

  } catch (error) {
    console.error('💥 ERREUR SUPABASE récupération:', error);
    // PAS de fallback - on veut voir les vraies erreurs Supabase
    throw error;
  }
}

// Supprimer une création - VERSION SUPABASE ONLY
export async function deleteCreation(id) {
  try {
    console.log('🔄 SUPABASE: Suppression de la création...', id);

    // FORCER l'utilisation de Supabase
    const { error } = await supabase
      .from('creations')
      .delete()
      .eq('id', id)
      .eq('user_id', FORCE_SUPABASE_USER_ID);

    if (error) {
      console.error('❌ SUPABASE ERROR suppression:', error);
      throw new Error(`Supabase error: ${error.message}`);
    }

    console.log('✅ SUPABASE SUCCESS: Création supprimée');
    return { error: null };

  } catch (error) {
    console.error('💥 ERREUR SUPABASE suppression:', error);
    throw error;
  }
}

// Fonction de diagnostic Supabase
export async function diagnoseSupabase() {
  try {
    console.log('🔍 DIAGNOSTIC SUPABASE...');

    // Test 1: Variables d'environnement
    console.log('📋 Variables:');
    console.log('- URL:', import.meta.env.VITE_SUPABASE_URL);
    console.log('- KEY présente:', !!import.meta.env.VITE_SUPABASE_ANON_KEY);

    // Test 2: Connexion de base
    const { data: connectionTest, error: connectionError } = await supabase
      .from('creations')
      .select('count', { count: 'exact', head: true });

    if (connectionError) {
      console.log('❌ Connexion échouée:', connectionError.message);
      return { status: 'error', error: connectionError.message };
    }

    console.log('✅ Connexion réussie');

    // Test 3: Test d'insertion
    const testData = {
      user_id: FORCE_SUPABASE_USER_ID,
      type: 'diagnostic',
      title: 'Test de connexion',
      data: { timestamp: new Date().toISOString(), test: true }
    };

    const { data: testResult, error: testError } = await supabase
      .from('creations')
      .insert([testData])
      .select()
      .single();

    if (testError) {
      console.log('❌ Test d\'insertion échoué:', testError.message);
      return { status: 'error', error: testError.message };
    }

    console.log('✅ Test d\'insertion réussi:', testResult.id);

    // Nettoyer le test
    await supabase.from('creations').delete().eq('id', testResult.id);

    return {
      status: 'success',
      message: 'Supabase fonctionne parfaitement !',
      variables: {
        url: !!import.meta.env.VITE_SUPABASE_URL,
        key: !!import.meta.env.VITE_SUPABASE_ANON_KEY
      }
    };

  } catch (error) {
    console.log('💥 Erreur diagnostic:', error);
    return { status: 'error', error: error.message };
  }
}