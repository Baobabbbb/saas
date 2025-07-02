-- CORRECTION DES ERREURS DE BASE DE DONNÉES
-- À exécuter dans l'éditeur SQL Supabase

-- 1. CRÉER LA FONCTION DE SUPPRESSION D'UTILISATEUR
DROP FUNCTION IF EXISTS delete_user_account(UUID);

CREATE OR REPLACE FUNCTION delete_user_account(user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSON;
  user_email TEXT;
  profile_exists BOOLEAN := FALSE;
  stories_exists BOOLEAN := FALSE;
  animations_exists BOOLEAN := FALSE;
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
  
  -- Vérifier et supprimer le profil s'il existe
  SELECT EXISTS(SELECT 1 FROM profiles WHERE id = user_id) INTO profile_exists;
  IF profile_exists THEN
    DELETE FROM profiles WHERE id = user_id;
  END IF;
  
  -- Vérifier et supprimer les stories si la table existe
  SELECT EXISTS(
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'stories'
  ) INTO stories_exists;
  
  IF stories_exists THEN
    DELETE FROM stories WHERE user_id = delete_user_account.user_id;
  END IF;
  
  -- Vérifier et supprimer les animations si la table existe
  SELECT EXISTS(
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'animations'
  ) INTO animations_exists;
  
  IF animations_exists THEN
    DELETE FROM animations WHERE user_id = delete_user_account.user_id;
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
      'profile_deleted', profile_exists,
      'stories_deleted', stories_exists,
      'animations_deleted', animations_exists
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

-- 2. CRÉER LES TABLES MANQUANTES SI NÉCESSAIRES

-- Table stories (si elle n'existe pas)
CREATE TABLE IF NOT EXISTS stories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT,
  content TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table animations (si elle n'existe pas)
CREATE TABLE IF NOT EXISTS animations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT,
  data JSONB,
  video_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. CRÉER LES POLITIQUES RLS SI NÉCESSAIRES

-- RLS pour stories
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own stories" ON stories;
CREATE POLICY "Users can view own stories" ON stories
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own stories" ON stories;
CREATE POLICY "Users can insert own stories" ON stories
  FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own stories" ON stories;
CREATE POLICY "Users can delete own stories" ON stories
  FOR DELETE USING (auth.uid() = user_id);

-- RLS pour animations
ALTER TABLE animations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own animations" ON animations;
CREATE POLICY "Users can view own animations" ON animations
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own animations" ON animations;
CREATE POLICY "Users can insert own animations" ON animations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own animations" ON animations;
CREATE POLICY "Users can delete own animations" ON animations
  FOR DELETE USING (auth.uid() = user_id);

-- 4. VÉRIFICATIONS
SELECT 'Fonction delete_user_account créée avec succès' as step_1;
SELECT 'Tables stories et animations créées/vérifiées' as step_2;
SELECT 'Politiques RLS configurées' as step_3;

-- Test de la fonction (décommentez et remplacez par un UUID réel pour tester)
-- SELECT delete_user_account('VOTRE_USER_ID_ICI');
