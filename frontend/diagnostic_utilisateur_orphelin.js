/**
 * Script pour diagnostiquer et supprimer l'utilisateur orphelin csauvegarde2@gmail.com
 * Cet utilisateur existe dans auth.users mais pas dans profiles
 */

import { supabase } from './src/supabaseClient.js';

const diagnostiquerUtilisateurOrphelin = async () => {
  console.log('🔍 DIAGNOSTIC UTILISATEUR ORPHELIN - csauvegarde2@gmail.com\n');
  
  const emailRecherche = 'csauvegarde2@gmail.com';
  
  try {
    // MÉTHODE 1: Essayer de se connecter pour récupérer l'ID utilisateur
    console.log('1️⃣ Tentative de connexion pour récupérer l\'ID utilisateur...');
    
    // Note: Cette méthode nécessite de connaître le mot de passe
    // Nous allons utiliser une autre approche
    
    // MÉTHODE 2: Chercher dans les profils existants
    console.log('2️⃣ Recherche dans la table profiles...');
    
    const { data: profiles, error: profilesError } = await supabase
      .from('profiles')
      .select('*');
    
    if (profilesError) {
      console.log('❌ Erreur accès profiles:', profilesError.message);
    } else {
      console.log(`📋 ${profiles.length} profil(s) trouvé(s) en base`);
      
      // Chercher un profil qui pourrait correspondre
      const profileCorrespondant = profiles.find(p => 
        p.email === emailRecherche || 
        (p.prenom && p.prenom.includes('csauvegarde2')) ||
        (p.nom && p.nom.includes('csauvegarde2'))
      );
      
      if (profileCorrespondant) {
        console.log('✅ Profil trouvé:', profileCorrespondant);
      } else {
        console.log('❌ Aucun profil correspondant trouvé dans la table profiles');
        console.log('💡 Cet utilisateur existe uniquement dans auth.users');
      }
    }
    
    // MÉTHODE 3: Utiliser l'API admin (si configurée)
    console.log('\n3️⃣ Vérification de l\'existence dans auth.users...');
    
    // Puisque nous ne pouvons pas accéder directement à auth.users avec l'API client,
    // nous devons utiliser des méthodes indirectes
    
    console.log('ℹ️ L\'API client ne permet pas d\'accéder directement à auth.users');
    console.log('ℹ️ Nous devons utiliser l\'interface admin Supabase ou des requêtes SQL\n');
    
    // SOLUTION: Générer les scripts SQL pour supprimer l'utilisateur orphelin
    console.log('📋 SCRIPTS DE SUPPRESSION POUR UTILISATEUR ORPHELIN');
    console.log('═'.repeat(60));
    
    console.log('\n🔧 OPTION 1 - Via l\'interface Supabase (RECOMMANDÉ):');
    console.log('1. Aller sur: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/auth/users');
    console.log('2. Utiliser la barre de recherche pour chercher: csauvegarde2@gmail.com');
    console.log('3. Cliquer sur les "..." à droite de l\'utilisateur');
    console.log('4. Cliquer sur "Delete user"');
    console.log('5. Confirmer la suppression\n');
    
    console.log('🔧 OPTION 2 - Via SQL direct (Pour administrateurs):');
    console.log('Aller sur: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/sql/new');
    console.log('Exécuter ce script:\n');
    
    console.log(`-- Script pour supprimer l'utilisateur orphelin
-- ATTENTION: Vérifiez bien l'email avant d'exécuter !

-- 1. Vérifier l'existence de l'utilisateur
SELECT id, email, created_at 
FROM auth.users 
WHERE email = '${emailRecherche}';

-- 2. Supprimer l'utilisateur (décommentez après vérification)
-- DELETE FROM auth.users WHERE email = '${emailRecherche}';

-- 3. Vérifier la suppression
-- SELECT COUNT(*) as utilisateurs_restants 
-- FROM auth.users 
-- WHERE email = '${emailRecherche}';`);
    
    console.log('\n🔧 OPTION 3 - Script automatisé sécurisé:');
    console.log('Utilisez la fonction que nous avons créée:\n');
    
    console.log(`-- 1. D'abord, trouvez l'ID utilisateur
SELECT id FROM auth.users WHERE email = '${emailRecherche}';

-- 2. Puis utilisez notre fonction (remplacez USER_ID_ICI par l'ID trouvé)
-- SELECT delete_user_account('USER_ID_ICI');`);
    
    console.log('\n⚠️  IMPORTANT:');
    console.log('- Cet utilisateur n\'a PAS de profil dans votre application');
    console.log('- Il existe uniquement dans l\'authentification Supabase');
    console.log('- Sa suppression n\'affectera pas les données de l\'application');
    console.log('- Après suppression, il pourra se réinscrire normalement\n');
    
    // MÉTHODE 4: Essayer la fonction de suppression si l'utilisateur est connecté
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (user && user.email === emailRecherche) {
      console.log('🎯 UTILISATEUR ACTUELLEMENT CONNECTÉ !');
      console.log('Vous pouvez utiliser la fonction de suppression directement...\n');
      
      console.log('4️⃣ Test de suppression avec fonction RPC...');
      
      const { data: rpcResult, error: rpcError } = await supabase.rpc('delete_user_account', {
        user_id: user.id
      });
      
      if (rpcError) {
        console.log('❌ Erreur RPC:', rpcError.message);
      } else {
        console.log('✅ Suppression réussie:', rpcResult);
        console.log('🔄 Déconnexion en cours...');
        await supabase.auth.signOut();
        console.log('✅ Utilisateur supprimé et déconnecté !');
      }
    } else if (user) {
      console.log(`ℹ️ Utilisateur connecté différent: ${user.email}`);
      console.log(`ℹ️ Pour supprimer ${emailRecherche}, utilisez l'une des options ci-dessus`);
    } else {
      console.log('ℹ️ Aucun utilisateur connecté');
      console.log(`ℹ️ Pour supprimer ${emailRecherche}, utilisez l'option 1 ou 2 ci-dessus`);
    }
    
  } catch (error) {
    console.error('❌ Erreur générale:', error.message);
  }
};

// Fonction pour créer un script de nettoyage général
const creerScriptNettoyageOrphelins = () => {
  console.log('\n\n🧹 SCRIPT DE NETTOYAGE DES UTILISATEURS ORPHELINS');
  console.log('═'.repeat(60));
  console.log(`
-- Script pour identifier et nettoyer tous les utilisateurs orphelins
-- (utilisateurs dans auth.users sans profil correspondant)

-- 1. Identifier les utilisateurs orphelins
SELECT 
  au.id,
  au.email,
  au.created_at,
  'ORPHELIN' as status
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id
WHERE p.id IS NULL
ORDER BY au.created_at DESC;

-- 2. Compter les orphelins
SELECT COUNT(*) as orphelins_total
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id
WHERE p.id IS NULL;

-- 3. Supprimer tous les orphelins (ATTENTION ! Décommentez seulement après vérification)
-- DELETE FROM auth.users 
-- WHERE id IN (
--   SELECT au.id
--   FROM auth.users au
--   LEFT JOIN profiles p ON au.id = p.id
--   WHERE p.id IS NULL
-- );

-- 4. Supprimer un orphelin spécifique par email
-- DELETE FROM auth.users WHERE email = 'csauvegarde2@gmail.com';
`);
};

// Exécution
console.log('🚀 DÉMARRAGE DU DIAGNOSTIC...\n');
diagnostiquerUtilisateurOrphelin()
  .then(() => {
    creerScriptNettoyageOrphelins();
    console.log('\n✅ Diagnostic terminé !');
    console.log('💡 Choisissez la méthode qui vous convient le mieux pour supprimer l\'utilisateur orphelin.');
  })
  .catch(error => {
    console.error('\n💥 Erreur:', error.message);
  });
