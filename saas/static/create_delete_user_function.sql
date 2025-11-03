-- Fonction pour supprimer complètement un compte utilisateur
-- À exécuter dans l'éditeur SQL Supabase

-- Créer la fonction de suppression complète d'utilisateur
CREATE OR REPLACE FUNCTION delete_user_account(user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
BEGIN
  -- Supprimer toutes les données associées à l'utilisateur
  
  -- Supprimer les histoires générées
  DELETE FROM stories WHERE user_id = delete_user_account.user_id;
  
  -- Supprimer les animations générées
  DELETE FROM animations WHERE user_id = delete_user_account.user_id;
  
  -- Supprimer le contenu généré
  DELETE FROM generated_content WHERE user_id = delete_user_account.user_id;
  
  -- Supprimer l'historique des générations
  DELETE FROM generation_history WHERE user_id = delete_user_account.user_id;
  
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
    -- En cas d'erreur, retourner les détails
    result := json_build_object(
      'success', false,
      'error', SQLERRM,
      'user_id', delete_user_account.user_id
    );
    
    RETURN result;
END;
$$;

-- Donner les permissions nécessaires
GRANT EXECUTE ON FUNCTION delete_user_account(UUID) TO authenticated;

-- Test de la fonction (optionnel - décommenter pour tester)
-- SELECT delete_user_account('00000000-0000-0000-0000-000000000000'::UUID);

SELECT 'Fonction de suppression de compte créée avec succès !' as resultat;
