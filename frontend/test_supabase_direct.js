// Test des API Supabase directement
import { supabase } from './src/supabaseClient.js';

async function testSupabaseDirectly() {
  console.log('🚀 Test direct des API Supabase\n');
  
  const testUser = {
    email: 'test.profile@example.com',
    password: 'TestPassword123!',
    firstName: 'Jean',
    lastName: 'Dupont'
  };
  
  try {
    // Étape 1: Créer un utilisateur
    console.log('👤 Création d\'utilisateur...');
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email: testUser.email,
      password: testUser.password,
    });
    
    if (signUpError) {
      console.error('❌ Erreur inscription:', signUpError.message);
      
      // Essayer de se connecter si l'utilisateur existe
      if (signUpError.message.includes('already registered')) {
        console.log('ℹ️ Utilisateur existe, tentative de connexion...');
        const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
          email: testUser.email,
          password: testUser.password,
        });
        
        if (signInError) {
          console.error('❌ Erreur connexion:', signInError.message);
          return;
        }
        
        console.log('✅ Connexion réussie:', signInData.user.email);
        var user = signInData.user;
      } else {
        return;
      }
    } else {
      console.log('✅ Inscription réussie:', signUpData.user?.email);
      var user = signUpData.user;
    }
    
    if (!user) {
      console.error('❌ Aucun utilisateur disponible');
      return;
    }
    
    // Étape 2: Créer/Mettre à jour le profil
    console.log('\n📝 Création/Mise à jour du profil...');
    const { data: upsertData, error: upsertError } = await supabase
      .from('profiles')
      .upsert([
        { 
          id: user.id, 
          prenom: testUser.firstName, 
          nom: testUser.lastName 
        }
      ])
      .select()
      .single();
    
    if (upsertError) {
      console.error('❌ Erreur upsert profil:', upsertError.message);
    } else {
      console.log('✅ Profil créé/mis à jour:', upsertData);
    }
    
    // Étape 3: Lire le profil
    console.log('\n📋 Lecture du profil...');
    const { data: readData, error: readError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    
    if (readError) {
      console.error('❌ Erreur lecture profil:', readError.message);
    } else {
      console.log('✅ Profil lu:', readData);
    }
    
    // Étape 4: Mettre à jour le profil
    console.log('\n✏️ Mise à jour du profil...');
    const { data: updateData, error: updateError } = await supabase
      .from('profiles')
      .update({ 
        prenom: 'Jean-Michel', 
        nom: 'Dupont-Martin' 
      })
      .eq('id', user.id)
      .select()
      .single();
    
    if (updateError) {
      console.error('❌ Erreur mise à jour:', updateError.message);
    } else {
      console.log('✅ Profil mis à jour:', updateData);
    }
    
    // Étape 5: Vérifier la mise à jour
    console.log('\n🔍 Vérification finale...');
    const { data: finalData, error: finalError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    
    if (finalError) {
      console.error('❌ Erreur vérification finale:', finalError.message);
    } else {
      console.log('✅ Profil final:', finalData);
    }
    
    // Étape 6: Lister tous les profils
    console.log('\n📊 Liste de tous les profils...');
    const { data: allProfiles, error: listError } = await supabase
      .from('profiles')
      .select('*')
      .limit(10);
    
    if (listError) {
      console.error('❌ Erreur liste profils:', listError.message);
    } else {
      console.log('✅ Profils trouvés:', allProfiles.length);
      allProfiles.forEach((profile, index) => {
        console.log(`  ${index + 1}. ${profile.prenom} ${profile.nom} (${profile.id.substring(0, 8)}...)`);
      });
    }
    
    // Nettoyage
    console.log('\n🧹 Déconnexion...');
    await supabase.auth.signOut();
    console.log('✅ Déconnexion effectuée');
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
  }
}

// Exécution du test
testSupabaseDirectly()
  .then(() => {
    console.log('\n🎉 Test direct terminé avec succès');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n💥 Erreur lors du test:', error);
    process.exit(1);
  });
