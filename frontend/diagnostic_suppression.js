/**
 * Script de diagnostic pour identifier pourquoi la suppression de compte ne fonctionne pas
 */

import { supabase } from './src/supabaseClient.js';

const diagnosticSuppression = async () => {
  console.log('🔍 DIAGNOSTIC - Suppression de compte\n');
  
  try {
    // Test 1: Vérifier si l'utilisateur est connecté
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      console.log('❌ Aucun utilisateur connecté');
      return;
    }
    
    console.log('✅ Utilisateur connecté:', user.email);
    console.log('📧 User ID:', user.id);
    
    // Test 2: Vérifier si le profil existe
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    
    if (profileError) {
      console.log('❌ Erreur profil:', profileError.message);
    } else {
      console.log('✅ Profil trouvé:', profile);
    }
    
    // Test 3: Vérifier si la fonction RPC existe
    console.log('\n🧪 Test de la fonction RPC delete_user_account...');
    
    const { data: rpcResult, error: rpcError } = await supabase.rpc('delete_user_account', {
      user_id: user.id
    });
    
    if (rpcError) {
      console.log('❌ Erreur RPC:', rpcError.message);
      console.log('📋 Code erreur:', rpcError.code);
      console.log('📋 Détails:', rpcError.details);
      
      if (rpcError.message.includes('function') && rpcError.message.includes('does not exist')) {
        console.log('\n⚠️  PROBLÈME IDENTIFIÉ: La fonction delete_user_account n\'existe pas dans Supabase');
        console.log('💡 SOLUTION: Créer la fonction dans l\'éditeur SQL Supabase');
      }
    } else {
      console.log('✅ Fonction RPC disponible');
      console.log('📋 Résultat:', rpcResult);
    }
    
    // Test 4: Vérifier les permissions
    console.log('\n🔐 Test des permissions...');
    
    const { data: testDelete, error: testError } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', user.id);
    
    if (testError) {
      console.log('❌ Erreur de permission:', testError.message);
    } else {
      console.log('✅ Permissions de lecture OK');
    }
    
  } catch (error) {
    console.error('❌ Erreur générale:', error.message);
  }
};

// Fonction pour créer un script de suppression manuelle
const createManualDeletionScript = async () => {
  console.log('\n📝 SCRIPT DE SUPPRESSION MANUELLE');
  console.log('═══════════════════════════════════');
  
  const { data: { user } } = await supabase.auth.getUser();
  
  if (user) {
    console.log(`-- Script SQL à exécuter dans Supabase pour supprimer ${user.email}`);
    console.log(`-- User ID: ${user.id}`);
    console.log('');
    console.log('-- 1. Supprimer le profil');
    console.log(`DELETE FROM profiles WHERE id = '${user.id}';`);
    console.log('');
    console.log('-- 2. Supprimer l\'utilisateur auth');
    console.log(`DELETE FROM auth.users WHERE id = '${user.id}';`);
    console.log('');
    console.log('-- 3. Vérification');
    console.log(`SELECT * FROM profiles WHERE id = '${user.id}';`);
    console.log(`SELECT * FROM auth.users WHERE id = '${user.id}';`);
  }
};

// Exécuter les diagnostics
diagnosticSuppression();
createManualDeletionScript();
