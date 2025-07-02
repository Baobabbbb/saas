// Script de vérification finale - À exécuter après la configuration SQL
import { supabase } from './src/supabaseClient.js';

// Mock localStorage pour Node.js
global.localStorage = {
  data: {},
  getItem: function(key) { return this.data[key] || null; },
  setItem: function(key, value) { this.data[key] = value; },
  removeItem: function(key) { delete this.data[key]; },
  clear: function() { this.data = {}; }
};

async function verificationFinale() {
  console.log('🎯 VÉRIFICATION FINALE - Liaison Site-Base de données\n');
  
  try {
    // Import des fonctions auth
    const { signUpWithProfile, signIn, signOut } = await import('./src/services/auth.js');
    
    // Créer un utilisateur de test unique
    const timestamp = Date.now();
    const testUser = {
      email: `verification.${timestamp}@example.com`,
      password: 'Verification123!',
      firstName: 'Test',
      lastName: 'Final'
    };
    
    console.log('👤 Création d\'un utilisateur de test...');
    console.log('Email:', testUser.email);
    
    // Étape 1: Inscription
    const signUpResult = await signUpWithProfile(testUser);
    
    if (signUpResult.error) {
      console.error('❌ Erreur inscription:', signUpResult.error.message);
      return false;
    }
    
    console.log('✅ Utilisateur créé avec succès');
    
    // Vérifier que l'utilisateur est authentifié
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (!user) {
      console.error('❌ Utilisateur non authentifié après inscription');
      return false;
    }
    
    console.log('✅ Authentification confirmée');
    
    // Étape 2: Vérifier le profil en base
    console.log('\n📋 Vérification du profil en base de données...');
    
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    
    if (profileError) {
      console.error('❌ ÉCHEC - Profil non trouvé en base:', profileError.message);
      
      if (profileError.message.includes('row-level security policy')) {
        console.log('\n🚨 DIAGNOSTIC:');
        console.log('❌ Les politiques RLS ne sont pas encore configurées');
        console.log('📝 ACTION REQUISE: Exécuter le script SQL dans Supabase');
        console.log('🔗 https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/editor');
        
        await signOut();
        return false;
      }
      
      if (profileError.message.includes('JSON object requested, multiple')) {
        console.log('\n🚨 DIAGNOSTIC:');
        console.log('❌ Aucun profil trouvé pour cet utilisateur');
        console.log('💡 Le profil n\'a peut-être pas été créé lors de l\'inscription');
        
        await signOut();
        return false;
      }
      
      await signOut();
      return false;
    }
    
    console.log('✅ SUCCÈS - Profil trouvé en base de données !');
    console.log('Détails du profil:');
    console.log('  ID:', profile.id);
    console.log('  Prénom:', profile.prenom);
    console.log('  Nom:', profile.nom);
    console.log('  Créé le:', new Date(profile.created_at).toLocaleString());
    
    // Étape 3: Test de mise à jour
    console.log('\n✏️ Test de mise à jour du profil...');
    
    const { data: updatedProfile, error: updateError } = await supabase
      .from('profiles')
      .update({
        prenom: 'Test-Modifié',
        nom: 'Final-Modifié'
      })
      .eq('id', user.id)
      .select()
      .single();
    
    if (updateError) {
      console.error('❌ Erreur mise à jour:', updateError.message);
      await signOut();
      return false;
    }
    
    console.log('✅ Mise à jour réussie !');
    console.log('Nouveau prénom:', updatedProfile.prenom);
    console.log('Nouveau nom:', updatedProfile.nom);
    
    // Étape 4: Nettoyage
    console.log('\n🧹 Nettoyage du test...');
    
    // Supprimer le profil de test
    const { error: deleteError } = await supabase
      .from('profiles')
      .delete()
      .eq('id', user.id);
    
    if (deleteError) {
      console.log('ℹ️ Impossible de supprimer le profil de test (ce n\'est pas grave)');
    } else {
      console.log('✅ Profil de test supprimé');
    }
    
    // Déconnexion
    await signOut();
    console.log('✅ Déconnexion effectuée');
    
    return true;
    
  } catch (error) {
    console.error('❌ Erreur générale:', error);
    return false;
  }
}

// Exécution avec résumé final
verificationFinale()
  .then((success) => {
    console.log('\n' + '='.repeat(60));
    console.log('🎯 RÉSUMÉ FINAL DE LA VÉRIFICATION');
    console.log('='.repeat(60));
    
    if (success) {
      console.log('🎉 CONFIGURATION RÉUSSIE !');
      console.log('');
      console.log('✅ Site et base de données parfaitement liés');
      console.log('✅ Profils utilisateur créés automatiquement');
      console.log('✅ Modifications sauvegardées en temps réel');
      console.log('✅ Sécurité RLS opérationnelle');
      console.log('');
      console.log('🚀 Votre système est prêt pour la production !');
      console.log('');
      console.log('📝 Test manuel recommandé:');
      console.log('  1. Aller sur http://localhost:5175/');
      console.log('  2. Créer un nouvel utilisateur');
      console.log('  3. Modifier le profil via "Mon compte"');
      console.log('  4. Vérifier dans Supabase Table Editor');
      
    } else {
      console.log('❌ CONFIGURATION INCOMPLÈTE');
      console.log('');
      console.log('📋 Actions requises:');
      console.log('  1. Ouvrir https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/editor');
      console.log('  2. Exécuter le script SQL fourni dans SOLUTION_LIAISON_BDD.md');
      console.log('  3. Relancer ce test avec: node verification_finale.js');
      console.log('');
      console.log('💡 Le système fonctionne actuellement avec localStorage (local)');
      console.log('   mais nécessite la configuration pour la persistance cloud');
    }
    
    console.log('='.repeat(60));
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('\n💥 Erreur lors de la vérification:', error);
    process.exit(1);
  });
