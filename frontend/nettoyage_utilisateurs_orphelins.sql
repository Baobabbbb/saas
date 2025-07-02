-- SCRIPT DE NETTOYAGE DES UTILISATEURS ORPHELINS
-- À exécuter dans l'éditeur SQL Supabase
-- Résout le problème de csauvegarde2@gmail.com et autres utilisateurs sans profil

-- ===================================================================
-- ÉTAPE 1: DIAGNOSTIC - Identifier les utilisateurs orphelins
-- ===================================================================

-- Voir tous les utilisateurs orphelins (dans auth.users mais pas dans profiles)
SELECT 
  au.id,
  au.email,
  au.created_at,
  au.last_sign_in_at,
  CASE 
    WHEN p.id IS NULL THEN '❌ ORPHELIN'
    ELSE '✅ AVEC PROFIL'
  END as status
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id
ORDER BY au.created_at DESC;

-- Compter les utilisateurs orphelins
SELECT 
  COUNT(CASE WHEN p.id IS NULL THEN 1 END) as orphelins,
  COUNT(CASE WHEN p.id IS NOT NULL THEN 1 END) as avec_profil,
  COUNT(*) as total
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id;

-- Voir spécifiquement csauvegarde2@gmail.com
SELECT 
  au.id,
  au.email,
  au.created_at,
  au.confirmed_at,
  au.last_sign_in_at,
  p.id as profile_id,
  p.prenom,
  p.nom
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id
WHERE au.email = 'csauvegarde2@gmail.com';

-- ===================================================================
-- ÉTAPE 2: NETTOYAGE - Supprimer les utilisateurs orphelins
-- ===================================================================

-- OPTION A: Supprimer uniquement csauvegarde2@gmail.com
-- (Décommentez la ligne suivante pour exécuter)
-- DELETE FROM auth.users WHERE email = 'csauvegarde2@gmail.com';

-- OPTION B: Supprimer tous les utilisateurs orphelins créés il y a plus de 7 jours
-- (Décommentez le bloc suivant pour exécuter)
/*
DELETE FROM auth.users 
WHERE id IN (
  SELECT au.id
  FROM auth.users au
  LEFT JOIN profiles p ON au.id = p.id
  WHERE p.id IS NULL 
    AND au.created_at < NOW() - INTERVAL '7 days'
);
*/

-- OPTION C: Supprimer tous les utilisateurs orphelins (ATTENTION!)
-- (Décommentez le bloc suivant pour exécuter - TRÈS DANGEREUX)
/*
DELETE FROM auth.users 
WHERE id IN (
  SELECT au.id
  FROM auth.users au
  LEFT JOIN profiles p ON au.id = p.id
  WHERE p.id IS NULL
);
*/

-- ===================================================================
-- ÉTAPE 3: PRÉVENTION - Créer un trigger pour éviter les orphelins
-- ===================================================================

-- Fonction pour créer automatiquement un profil lors de l'inscription
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, prenom, nom, created_at)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'prenom', 'Utilisateur'),
    COALESCE(NEW.raw_user_meta_data->>'nom', 'Nouveau'),
    NOW()
  );
  RETURN NEW;
END;
$$ language plpgsql security definer;

-- Supprimer l'ancien trigger s'il existe
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Créer le trigger pour auto-créer les profils
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ===================================================================
-- ÉTAPE 4: VÉRIFICATION - Confirmer les changements
-- ===================================================================

-- Vérifier que csauvegarde2@gmail.com est supprimé
SELECT 
  CASE 
    WHEN EXISTS(SELECT 1 FROM auth.users WHERE email = 'csauvegarde2@gmail.com')
    THEN '❌ ENCORE PRÉSENT'
    ELSE '✅ SUPPRIMÉ'
  END as statut_csauvegarde2;

-- Vérifier qu'il n'y a plus d'orphelins
SELECT 
  COUNT(*) as orphelins_restants
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id
WHERE p.id IS NULL;

-- Message de confirmation
SELECT 'Script de nettoyage des orphelins terminé !' as resultat;

-- ===================================================================
-- INSTRUCTIONS D'UTILISATION
-- ===================================================================

/*
COMMENT UTILISER CE SCRIPT:

1. DIAGNOSTIC (Toujours sûr):
   - Exécutez d'abord les requêtes SELECT de l'ÉTAPE 1
   - Notez les utilisateurs orphelins trouvés

2. NETTOYAGE (Décommentez selon vos besoins):
   - Pour csauvegarde2@gmail.com uniquement: décommentez OPTION A
   - Pour orphelins anciens: décommentez OPTION B  
   - Pour tous les orphelins: décommentez OPTION C (DANGEREUX!)

3. PRÉVENTION (Recommandé):
   - Exécutez l'ÉTAPE 3 pour éviter de futurs orphelins
   - Le trigger créera automatiquement des profils

4. VÉRIFICATION:
   - Exécutez l'ÉTAPE 4 pour confirmer les changements

NOTES IMPORTANTES:
- Les suppressions sont IRRÉVERSIBLES
- Testez d'abord avec un seul utilisateur
- Sauvegardez vos données importantes avant le nettoyage de masse
*/
