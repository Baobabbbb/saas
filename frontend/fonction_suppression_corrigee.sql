-- FONCTION DE SUPPRESSION CORRIGÉE
-- À exécuter dans l'éditeur SQL Supabase pour créer/corriger la fonction

-- Supprimer l'ancienne fonction si elle existe
DROP FUNCTION IF EXISTS delete_user_account(UUID);

-- Créer la fonction corrigée
CREATE OR REPLACE FUNCTION delete_user_account(user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  user_email TEXT;
  profile_exists BOOLEAN := FALSE;
BEGIN
  -- Vérifier si l'utilisateur existe
  SELECT email INTO user_email FROM auth.users WHERE id = user_id;
  
  IF user_email IS NULL THEN
    result := json_build_object(
      'success', false,
      'error', 'Utilisateur introuvable',
      'user_id', user_id
    );
    RETURN result;
  END IF;
  
  -- Vérifier si un profil existe
  SELECT EXISTS(SELECT 1 FROM profiles WHERE id = user_id) INTO profile_exists;
  
  -- Supprimer le profil s'il existe
  IF profile_exists THEN
    DELETE FROM profiles WHERE id = user_id;
  END IF;
  
  -- Supprimer l'utilisateur de l'authentification
  DELETE FROM auth.users WHERE id = user_id;
  
  -- Vérifier que la suppression a réussi
  IF NOT EXISTS(SELECT 1 FROM auth.users WHERE id = user_id) THEN
    result := json_build_object(
      'success', true,
      'message', 'Compte utilisateur supprimé avec succès',
      'user_id', user_id,
      'email', user_email,
      'profile_deleted', profile_exists
    );
  ELSE
    result := json_build_object(
      'success', false,
      'error', 'Échec de la suppression utilisateur',
      'user_id', user_id
    );
  END IF;
  
  RETURN result;
  
EXCEPTION
  WHEN OTHERS THEN
    result := json_build_object(
      'success', false,
      'error', SQLERRM,
      'user_id', user_id,
      'email', COALESCE(user_email, 'inconnu')
    );
    RETURN result;
END;
$$;

-- Test de la fonction (optionnel)
-- SELECT delete_user_account('USER_ID_HERE');

-- Message de confirmation
SELECT 'Fonction delete_user_account créée avec succès' as resultat;
