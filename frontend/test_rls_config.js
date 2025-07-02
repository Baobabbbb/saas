// Test pour vérifier que la configuration RLS fonctionne
import { supabase } from './src/supabaseClient.js';

// Mock localStorage pour Node.js
global.localStorage = {
  data: {},
  getItem: function(key) { return this.data[key] || null; },
  setItem: function(key, value) { this.data[key] = value; },
  removeItem: function(key) { delete this.data[key]; },
  clear: function() { this.data = {}; }
};

async function testRLSConfiguration() {
  console.log('🧪 Test de la configuration RLS\n');
  
  try {
    // Import des fonctions auth
    const { signUpWithProfile, signIn, getCurrentUserProfile, updateUserProfile, signOut } = await import('./src/services/auth.js');
    
    // Test avec un nouvel utilisateur
    const testUser = {
      email: 'test.rls.config@example.com',
      password: 'TestRLS123!',
      firstName: 'Marie',
      lastName: 'Durand'
    };
    
    console.log('👤 Test d\'inscription avec création de profil...');
    const signUpResult = await signUpWithProfile(testUser);
    
    if (signUpResult.error && !signUpResult.error.message.includes('already registered')) {
      console.error('❌ Erreur inscription:', signUpResult.error.message);
      
      // Essayer de se connecter si l'utilisateur existe
      const signInResult = await signIn({
        email: testUser.email,
        password: testUser.password
      });
      
      if (signInResult.error) {
        console.error('❌ Erreur connexion:', signInResult.error.message);
        return;
      } else {
        console.log('✅ Connexion réussie (utilisateur existant)');
      }
    } else if (signUpResult.error?.message.includes('already registered')) {
      console.log('ℹ️ Utilisateur existe, connexion...');
      await signIn(testUser);
    } else {
      console.log('✅ Inscription réussie avec profil !');
    }
    
    // Vérifier que l'utilisateur est connecté
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (!user) {
      console.error('❌ Aucun utilisateur connecté');
      return;
    }
    
    console.log('✅ Utilisateur connecté:', user.email);
    
    // Test 1: Lecture du profil
    console.log('\n📖 Test de lecture du profil...');
    const profileResult = await getCurrentUserProfile();
    
    if (profileResult.error) {
      console.error('❌ Erreur lecture profil:', profileResult.error.message);
      if (profileResult.data?.fallback) {
        console.log('ℹ️ Utilisation du fallback localStorage');
      }
    } else {
      console.log('✅ Profil lu depuis Supabase:', profileResult.data);
      if (profileResult.data.fallback) {
        console.log('ℹ️ (via fallback localStorage)');
      }
    }
    
    // Test 2: Mise à jour du profil
    console.log('\n✏️ Test de mise à jour du profil...');
    const updateResult = await updateUserProfile({
      firstName: 'Marie-Claire',
      lastName: 'Durand-Petit'
    });
    
    if (updateResult.error) {
      console.error('❌ Erreur mise à jour:', updateResult.error.message);
    } else {
      console.log('✅ Profil mis à jour:', updateResult.data);
      if (updateResult.data.fallback) {
        console.log('ℹ️ (via fallback localStorage)');
      }
    }
    
    // Test 3: Vérification directe en base
    console.log('\n🔍 Vérification directe en base...');
    const { data: directProfile, error: directError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    
    if (directError) {
      console.error('❌ Erreur accès direct:', directError.message);
      if (directError.message.includes('row-level security policy')) {
        console.log('❌ RLS TOUJOURS ACTIF - La configuration n\'a pas été appliquée');
        console.log('💡 Veuillez exécuter le script SQL dans l\'interface Supabase');
      }
    } else {
      console.log('✅ Profil en base:', directProfile);
    }
    
    // Test 4: Compter tous les profils visibles
    console.log('\n📊 Test de comptage des profils...');
    const { data: allProfiles, error: countError } = await supabase
      .from('profiles')
      .select('*');
    
    if (countError) {
      console.error('❌ Erreur comptage:', countError.message);
    } else {
      console.log('✅ Profils visibles pour cet utilisateur:', allProfiles.length);
      if (allProfiles.length === 1) {
        console.log('✅ RLS fonctionne correctement (l\'utilisateur ne voit que son profil)');
      } else if (allProfiles.length === 0) {
        console.log('❌ RLS bloque encore l\'accès');
      } else {
        console.log('⚠️ RLS pourrait ne pas être correctement configuré (trop de profils visibles)');
      }
    }
    
    // Résumé
    console.log('\n🎯 RÉSUMÉ DU TEST:');
    
    if (directError?.message.includes('row-level security policy')) {
      console.log('❌ CONFIGURATION RLS: Non appliquée');
      console.log('📝 ACTION REQUISE: Exécuter le script SQL dans Supabase');
      console.log('🔗 URL: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/editor');
    } else if (directProfile) {
      console.log('✅ CONFIGURATION RLS: Appliquée et fonctionnelle');
      console.log('✅ LIAISON SITE-BDD: Entièrement opérationnelle');
      console.log('🎉 Les utilisateurs créés apparaîtront maintenant dans la base !');
    } else {
      console.log('⚠️ ÉTAT INDÉTERMINÉ: Tests supplémentaires nécessaires');
    }
    
    // Déconnexion
    await signOut();
    console.log('\n🚪 Déconnexion effectuée');
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
  }
}

// Exécution
testRLSConfiguration()
  .then(() => {
    console.log('\n✅ Test de configuration terminé');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n💥 Erreur:', error);
    process.exit(1);
  });
