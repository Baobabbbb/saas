// Test complet avec création d'utilisateur et mise à jour de profil
import { supabase } from './src/supabaseClient.js';
import { signUpWithProfile, signIn, getCurrentUserProfile, updateUserProfile, signOut } from './src/services/auth.js';

async function testCompleteUserFlow() {
  console.log('🚀 Test complet du flux utilisateur\n');
  
  const testUser = {
    email: 'test.profile@example.com',
    password: 'TestPassword123!',
    firstName: 'Jean',
    lastName: 'Dupont'
  };
  
  try {
    // Étape 1: Nettoyer un éventuel utilisateur existant
    console.log('🧹 Nettoyage préalable...');
    await signOut();
    
    // Essayer de supprimer l'utilisateur de test s'il existe
    const { data: existingUsers } = await supabase
      .from('profiles')
      .select('id')
      .limit(10);
    
    console.log('Profils existants:', existingUsers?.length || 0);
    
    // Étape 2: Créer un nouvel utilisateur
    console.log('\n👤 Test d\'inscription...');
    const signUpResult = await signUpWithProfile({
      email: testUser.email,
      password: testUser.password,
      firstName: testUser.firstName,
      lastName: testUser.lastName
    });
    
    if (signUpResult.error) {
      console.error('❌ Erreur inscription:', signUpResult.error.message);
      
      // Si l'utilisateur existe déjà, essayer de se connecter
      if (signUpResult.error.message.includes('already registered')) {
        console.log('ℹ️ Utilisateur existe déjà, tentative de connexion...');
        
        const signInResult = await signIn({
          email: testUser.email,
          password: testUser.password
        });
        
        if (signInResult.error) {
          console.error('❌ Erreur connexion:', signInResult.error.message);
          return;
        } else {
          console.log('✅ Connexion réussie');
        }
      } else {
        return;
      }
    } else {
      console.log('✅ Inscription réussie');
      console.log('Utilisateur créé:', signUpResult.data?.user?.email);
    }
    
    // Attendre un peu pour que l'insertion soit effective
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Étape 3: Récupérer le profil utilisateur
    console.log('\n📋 Test de récupération du profil...');
    const profileResult = await getCurrentUserProfile();
    
    if (profileResult.error) {
      console.error('❌ Erreur récupération profil:', profileResult.error.message);
    } else {
      console.log('✅ Profil récupéré:', profileResult.data);
    }
    
    // Étape 4: Mettre à jour le profil
    console.log('\n✏️ Test de mise à jour du profil...');
    const updateResult = await updateUserProfile({
      firstName: 'Jean-Michel',
      lastName: 'Dupont-Martin'
    });
    
    if (updateResult.error) {
      console.error('❌ Erreur mise à jour:', updateResult.error.message);
    } else {
      console.log('✅ Profil mis à jour:', updateResult.data);
    }
    
    // Étape 5: Vérifier la mise à jour
    console.log('\n🔍 Vérification de la mise à jour...');
    const updatedProfileResult = await getCurrentUserProfile();
    
    if (updatedProfileResult.error) {
      console.error('❌ Erreur vérification:', updatedProfileResult.error.message);
    } else {
      console.log('✅ Profil après mise à jour:', updatedProfileResult.data);
    }
    
    // Étape 6: Vérifier directement dans la base
    console.log('\n🔍 Vérification directe en base...');
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      const { data: dbProfile, error: dbError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();
      
      if (dbError) {
        console.error('❌ Erreur lecture BDD:', dbError.message);
      } else {
        console.log('✅ Profil en base:', dbProfile);
      }
    }
    
    // Étape 7: Nettoyage
    console.log('\n🧹 Nettoyage final...');
    await signOut();
    console.log('✅ Déconnexion effectuée');
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
  }
}

// Exécution du test
testCompleteUserFlow()
  .then(() => {
    console.log('\n🎉 Test complet terminé');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n💥 Erreur lors du test:', error);
    process.exit(1);
  });
