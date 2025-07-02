/**
 * Script de test pour vérifier que les corrections de base de données fonctionnent
 */

import { supabase } from './src/supabaseClient.js';

const testDatabaseFixes = async () => {
  console.log('🔍 TEST DES CORRECTIONS BASE DE DONNÉES\n');
  
  try {
    // Test 1: Vérifier si la fonction delete_user_account existe
    console.log('1️⃣ Test de la fonction delete_user_account...');
    
    // Utiliser un UUID fictif pour tester l'existence de la fonction
    const testUserId = '00000000-0000-0000-0000-000000000000';
    
    const { data: rpcResult, error: rpcError } = await supabase.rpc('delete_user_account', {
      user_id: testUserId
    });
    
    if (rpcError) {
      if (rpcError.message.includes('function') && rpcError.message.includes('does not exist')) {
        console.log('❌ Fonction delete_user_account MANQUANTE');
        console.log('💡 Solution: Exécutez le script fix_database_errors.sql dans Supabase');
        return;
      } else if (rpcError.message.includes('Utilisateur introuvable')) {
        console.log('✅ Fonction delete_user_account DISPONIBLE');
      } else {
        console.log('⚠️  Erreur inattendue:', rpcError.message);
      }
    } else {
      console.log('✅ Fonction delete_user_account DISPONIBLE');
    }
    
    // Test 2: Vérifier si les tables existent
    console.log('\n2️⃣ Test des tables...');
    
    // Test table stories
    const { error: storiesError } = await supabase
      .from('stories')
      .select('id')
      .limit(1);
    
    if (storiesError) {
      if (storiesError.message.includes('does not exist')) {
        console.log('❌ Table "stories" MANQUANTE');
        console.log('💡 Solution: Exécutez le script fix_database_errors.sql dans Supabase');
      } else {
        console.log('⚠️  Erreur table stories:', storiesError.message);
      }
    } else {
      console.log('✅ Table "stories" DISPONIBLE');
    }
    
    // Test table animations
    const { error: animationsError } = await supabase
      .from('animations')
      .select('id')
      .limit(1);
    
    if (animationsError) {
      if (animationsError.message.includes('does not exist')) {
        console.log('❌ Table "animations" MANQUANTE');
        console.log('💡 Solution: Exécutez le script fix_database_errors.sql dans Supabase');
      } else {
        console.log('⚠️  Erreur table animations:', animationsError.message);
      }
    } else {
      console.log('✅ Table "animations" DISPONIBLE');
    }
    
    // Test 3: Vérifier les permissions utilisateur actuel
    console.log('\n3️⃣ Test des permissions...');
    
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      console.log('ℹ️ Aucun utilisateur connecté - connexion requise pour tester les permissions');
    } else {
      console.log('✅ Utilisateur connecté:', user.email);
      
      // Test permission profil
      const { data: profile, error: profileError } = await supabase
        .from('profiles')
        .select('id')
        .eq('id', user.id)
        .single();
      
      if (profileError) {
        console.log('⚠️  Erreur permission profil:', profileError.message);
      } else {
        console.log('✅ Permissions profil OK');
      }
    }
    
    console.log('\n📋 RÉSUMÉ DES TESTS TERMINÉ');
    console.log('═══════════════════════════════════');
    console.log('Si des erreurs apparaissent, exécutez le script fix_database_errors.sql');
    console.log('dans l\'éditeur SQL de Supabase.');
    
  } catch (error) {
    console.error('❌ Erreur générale:', error.message);
  }
};

// Instructions d'utilisation
console.log('📋 INSTRUCTIONS:');
console.log('1. Assurez-vous d\'avoir un utilisateur connecté pour tester les permissions');
console.log('2. Si des erreurs apparaissent, exécutez fix_database_errors.sql dans Supabase');
console.log('3. Relancez ce test après avoir exécuté le script SQL\n');

// Exécuter les tests
testDatabaseFixes();
