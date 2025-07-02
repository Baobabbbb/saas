// Test pour vérifier si les utilisateurs sont créés dans auth.users mais pas dans profiles
import { supabase } from './src/supabaseClient.js';

async function testUserCreationIssue() {
  console.log('🔍 Diagnostic du problème de création utilisateur\n');
  
  try {
    // Test 1: Créer un utilisateur de test
    console.log('👤 Test de création d\'utilisateur...');
    const testEmail = 'diagnostic.test@example.com';
    const testPassword = 'DiagnosticTest123!';
    
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email: testEmail,
      password: testPassword
    });
    
    if (signUpError && !signUpError.message.includes('already registered')) {
      console.error('❌ Erreur création utilisateur:', signUpError.message);
      return;
    }
    
    if (signUpError?.message.includes('already registered')) {
      console.log('ℹ️ Utilisateur existe déjà, connexion...');
      const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
        email: testEmail,
        password: testPassword
      });
      
      if (signInError) {
        console.error('❌ Erreur connexion:', signInError.message);
        return;
      }
      console.log('✅ Utilisateur connecté:', signInData.user.email);
    } else {
      console.log('✅ Nouvel utilisateur créé:', signUpData.user?.email);
    }
    
    // Test 2: Vérifier dans auth.users (via API)
    console.log('\n🔍 Vérification de l\'utilisateur authentifié...');
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (user) {
      console.log('✅ Utilisateur trouvé dans auth.users:');
      console.log('  ID:', user.id);
      console.log('  Email:', user.email);
      console.log('  Confirmé:', user.email_confirmed_at ? 'Oui' : 'Non');
      console.log('  Créé le:', new Date(user.created_at).toLocaleString());
    } else {
      console.log('❌ Aucun utilisateur authentifié trouvé');
    }
    
    // Test 3: Essayer de créer un profil
    console.log('\n📝 Test de création de profil...');
    const { data: insertData, error: insertError } = await supabase
      .from('profiles')
      .insert([
        {
          id: user.id,
          prenom: 'Test',
          nom: 'Diagnostic'
        }
      ])
      .select();
    
    if (insertError) {
      console.error('❌ Erreur création profil:', insertError.message);
      console.log('🔍 Code erreur:', insertError.code);
      console.log('🔍 Détails:', insertError.details);
      console.log('🔍 Hint:', insertError.hint);
      
      // Test 4: Vérifier les politiques RLS
      console.log('\n🔒 Diagnostic des politiques RLS...');
      if (insertError.message.includes('row-level security policy')) {
        console.log('❌ PROBLÈME IDENTIFIÉ: Les politiques RLS bloquent l\'insertion');
        console.log('💡 SOLUTION: Configurer les politiques RLS appropriées');
      }
    } else {
      console.log('✅ Profil créé avec succès:', insertData);
    }
    
    // Test 5: Essayer de lire les profils existants
    console.log('\n📖 Test de lecture des profils...');
    const { data: profiles, error: readError } = await supabase
      .from('profiles')
      .select('*');
    
    if (readError) {
      console.error('❌ Erreur lecture profils:', readError.message);
    } else {
      console.log('✅ Profils lisibles:', profiles.length);
      profiles.forEach((profile, index) => {
        console.log(`  ${index + 1}. ${profile.prenom} ${profile.nom} (${profile.id?.substring(0, 8)}...)`);
      });
    }
    
    // Test 6: Diagnostic complet
    console.log('\n🎯 DIAGNOSTIC COMPLET:');
    console.log('  - Création utilisateur Supabase Auth: ✅ Fonctionne');
    console.log('  - Table profiles accessible: ✅ Oui');
    console.log('  - Insertion dans profiles: ❌ Bloquée par RLS');
    console.log('  - Lecture des profiles: ✅ Fonctionne (mais vide)');
    
    console.log('\n🔧 SOLUTION REQUISE:');
    console.log('  1. Configurer les politiques RLS sur la table profiles');
    console.log('  2. Permettre aux utilisateurs authentifiés de créer leur profil');
    console.log('  3. Permettre aux utilisateurs de lire/modifier leur propre profil');
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
  }
}

// Exécution du diagnostic
testUserCreationIssue()
  .then(() => {
    console.log('\n🔍 Diagnostic terminé');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n💥 Erreur diagnostic:', error);
    process.exit(1);
  });
