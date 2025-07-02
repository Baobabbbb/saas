// Script pour supprimer un utilisateur spécifique de Supabase Auth
import { supabase } from './src/supabaseClient.js';

async function supprimerUtilisateur() {
  console.log('🗑️ SUPPRESSION UTILISATEUR - csauvegarde2@gmail.com\n');
  
  const emailASupprimer = 'csauvegarde2@gmail.com';
  
  try {
    // Étape 1: Vérifier si l'utilisateur existe dans auth.users
    console.log('🔍 Recherche de l\'utilisateur...');
    
    // Méthode 1: Essayer de se connecter pour vérifier l'existence
    console.log('Tentative de connexion pour vérifier l\'existence...');
    
    // Note: Nous ne pouvons pas lister tous les utilisateurs avec l'API client
    // Nous devons utiliser une approche différente
    
    // Étape 2: Supprimer via l'API Admin (si possible)
    console.log('\n🗑️ Tentative de suppression...');
    
    // Avec l'API client standard, nous ne pouvons pas supprimer directement un utilisateur
    // Nous devons passer par l'interface admin ou utiliser la Management API
    
    console.log('❌ LIMITATION: L\'API client ne permet pas la suppression directe d\'utilisateurs');
    console.log('');
    console.log('🔧 SOLUTIONS ALTERNATIVES:');
    console.log('');
    console.log('OPTION 1 - Via l\'interface Supabase (Recommandé):');
    console.log('1. Aller sur: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/auth/users');
    console.log('2. Chercher l\'utilisateur: csauvegarde2@gmail.com');
    console.log('3. Cliquer sur les "..." à droite de l\'utilisateur');
    console.log('4. Cliquer sur "Delete user"');
    console.log('5. Confirmer la suppression');
    console.log('');
    console.log('OPTION 2 - Via SQL (Plus technique):');
    console.log('1. Aller sur: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/editor');
    console.log('2. Exécuter cette requête SQL:');
    console.log('   DELETE FROM auth.users WHERE email = \'csauvegarde2@gmail.com\';');
    console.log('');
    console.log('OPTION 3 - Réinitialiser le mot de passe:');
    console.log('1. Utiliser "Mot de passe oublié" sur votre site');
    console.log('2. Se connecter avec le nouveau mot de passe');
    console.log('3. Le profil sera créé automatiquement à la connexion');
    
    // Étape 3: Vérifier s'il y a un profil associé à supprimer
    console.log('\n🔍 Vérification des profils orphelins...');
    
    const { data: profiles, error: profilesError } = await supabase
      .from('profiles')
      .select('*');
    
    if (profilesError) {
      console.log('ℹ️ Impossible de vérifier les profils:', profilesError.message);
    } else {
      console.log(`✅ ${profiles.length} profil(s) trouvé(s) en base`);
      
      // Chercher un profil qui pourrait correspondre
      const profilesOrphelins = profiles.filter(p => !p.prenom || !p.nom || p.prenom.includes('@'));
      
      if (profilesOrphelins.length > 0) {
        console.log('⚠️ Profils potentiellement orphelins trouvés:');
        profilesOrphelins.forEach((profile, index) => {
          console.log(`  ${index + 1}. ID: ${profile.id.substring(0, 8)}... - ${profile.prenom} ${profile.nom}`);
        });
        console.log('💡 Ces profils seront automatiquement nettoyés si les utilisateurs n\'existent plus');
      } else {
        console.log('✅ Aucun profil orphelin détecté');
      }
    }
    
    // Étape 4: Instructions pour recréer le compte
    console.log('\n📝 INSTRUCTIONS POUR RECRÉER LE COMPTE:');
    console.log('');
    console.log('1. Supprimer l\'utilisateur via l\'interface Supabase (Option 1 ci-dessus)');
    console.log('2. Aller sur votre site: http://localhost:5175/');
    console.log('3. Cliquer sur "S\'inscrire"');
    console.log('4. Utiliser l\'email: csauvegarde2@gmail.com');
    console.log('5. Choisir un nouveau mot de passe');
    console.log('6. Renseigner prénom et nom');
    console.log('7. Valider l\'inscription');
    console.log('8. Le profil sera automatiquement créé en base de données !');
    
    return true;
    
  } catch (error) {
    console.error('❌ Erreur:', error);
    return false;
  }
}

// Fonction pour créer un script SQL de suppression
function genererScriptSQL() {
  console.log('\n📋 SCRIPT SQL DE SUPPRESSION:');
  console.log('─'.repeat(50));
  console.log(`
-- Script à exécuter dans l'éditeur SQL Supabase
-- Pour supprimer l'utilisateur csauvegarde2@gmail.com

-- 1. Supprimer le profil s'il existe
DELETE FROM profiles 
WHERE id IN (
  SELECT id FROM auth.users 
  WHERE email = 'csauvegarde2@gmail.com'
);

-- 2. Supprimer l'utilisateur de auth.users
DELETE FROM auth.users 
WHERE email = 'csauvegarde2@gmail.com';

-- 3. Vérifier la suppression
SELECT 'Utilisateur supprimé avec succès' as resultat
WHERE NOT EXISTS (
  SELECT 1 FROM auth.users 
  WHERE email = 'csauvegarde2@gmail.com'
);
`);
  console.log('─'.repeat(50));
}

// Exécution
supprimerUtilisateur()
  .then(() => {
    genererScriptSQL();
    console.log('\n✅ Instructions de suppression générées');
    console.log('💡 Choisissez l\'option qui vous convient le mieux !');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n💥 Erreur:', error);
    process.exit(1);
  });
