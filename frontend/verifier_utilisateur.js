/**
 * Script pour vérifier si l'utilisateur existe encore dans Supabase
 * et créer un script de suppression manuelle si nécessaire
 */

import { supabase } from './src/supabaseClient.js';

const verifierUtilisateur = async () => {
  console.log('🔍 VÉRIFICATION - Existence utilisateur csauvegarde2@gmail.com\n');
  
  try {
    // Vérifier si un profil existe pour cet email
    const { data: profiles, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('email', 'csauvegarde2@gmail.com');
    
    if (profileError) {
      console.log('❌ Erreur lors de la vérification profil:', profileError.message);
    } else {
      console.log(`📊 Profils trouvés: ${profiles.length}`);
      if (profiles.length > 0) {
        console.log('⚠️  PROBLÈME: L\'utilisateur existe encore dans la table profiles');
        profiles.forEach(profile => {
          console.log('📋 Profil:', profile);
        });
      } else {
        console.log('✅ Aucun profil trouvé dans la table profiles');
      }
    }
    
    // Test de connexion pour voir si l'utilisateur auth existe
    console.log('\n🧪 Test de connexion avec csauvegarde2@gmail.com...');
    
    const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
      email: 'csauvegarde2@gmail.com',
      password: 'test123' // Mot de passe probable
    });
    
    if (authError) {
      if (authError.message.includes('Invalid login credentials')) {
        console.log('❓ Utilisateur auth pourrait exister mais mot de passe incorrect');
      } else if (authError.message.includes('Email not confirmed')) {
        console.log('⚠️  Utilisateur auth existe mais email non confirmé');
      } else {
        console.log('❌ Erreur auth:', authError.message);
      }
    } else {
      console.log('⚠️  PROBLÈME: L\'utilisateur peut encore se connecter!');
      console.log('📋 Données auth:', authData.user.email);
      
      // Déconnecter immédiatement
      await supabase.auth.signOut();
    }
    
  } catch (error) {
    console.error('❌ Erreur:', error.message);
  }
};

const creerScriptNettoyage = () => {
  console.log('\n🧹 SCRIPT DE NETTOYAGE MANUEL');
  console.log('═══════════════════════════════');
  console.log('-- À exécuter dans l\'éditeur SQL Supabase');
  console.log('');
  console.log('-- 1. Trouver l\'utilisateur par email');
  console.log("SELECT id, email FROM auth.users WHERE email = 'csauvegarde2@gmail.com';");
  console.log('');
  console.log('-- 2. Supprimer le profil (remplacer USER_ID par l\'ID trouvé)');
  console.log("DELETE FROM profiles WHERE email = 'csauvegarde2@gmail.com';");
  console.log('');
  console.log('-- 3. Supprimer l\'utilisateur auth (remplacer USER_ID par l\'ID trouvé)');
  console.log("DELETE FROM auth.users WHERE email = 'csauvegarde2@gmail.com';");
  console.log('');
  console.log('-- 4. Vérification finale');
  console.log("SELECT * FROM profiles WHERE email = 'csauvegarde2@gmail.com';");
  console.log("SELECT * FROM auth.users WHERE email = 'csauvegarde2@gmail.com';");
  console.log('');
  console.log('📝 Ces requêtes devraient retourner 0 lignes si la suppression a réussi');
};

const creerFonctionSuppression = () => {
  console.log('\n⚙️  CRÉATION DE LA FONCTION DE SUPPRESSION');
  console.log('═══════════════════════════════════════════');
  console.log('-- Si la fonction delete_user_account n\'existe pas, exécuter ceci:');
  console.log('');
  console.log(`CREATE OR REPLACE FUNCTION delete_user_account(user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
BEGIN
  -- Supprimer le profil utilisateur
  DELETE FROM profiles WHERE id = delete_user_account.user_id;
  
  -- Supprimer l'utilisateur de l'authentification
  DELETE FROM auth.users WHERE id = delete_user_account.user_id;
  
  -- Retourner le résultat
  result := json_build_object(
    'success', true,
    'message', 'Compte utilisateur supprimé avec succès',
    'user_id', delete_user_account.user_id
  );
  
  RETURN result;
  
EXCEPTION
  WHEN OTHERS THEN
    result := json_build_object(
      'success', false,
      'error', SQLERRM,
      'user_id', delete_user_account.user_id
    );
    RETURN result;
END;
$$;`);
};

// Exécuter les vérifications
verifierUtilisateur();
creerScriptNettoyage();
creerFonctionSuppression();
