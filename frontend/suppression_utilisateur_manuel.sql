-- SCRIPT DE SUPPRESSION UTILISATEUR - csauvegarde2@gmail.com
-- À copier et exécuter dans l'éditeur SQL Supabase

-- 1. Identifier l'utilisateur et son ID
SELECT 
    u.id as user_id,
    u.email,
    u.created_at,
    p.prenom,
    p.nom
FROM auth.users u
LEFT JOIN profiles p ON u.id = p.id 
WHERE u.email = 'csauvegarde2@gmail.com';

-- 2. Supprimer le profil (si existe)
DELETE FROM profiles 
WHERE id IN (
    SELECT id FROM auth.users WHERE email = 'csauvegarde2@gmail.com'
);

-- 3. Supprimer l'utilisateur de l'authentification
DELETE FROM auth.users WHERE email = 'csauvegarde2@gmail.com';

-- 4. Vérification finale - ces requêtes doivent retourner 0 lignes
SELECT 'Vérification profiles' as etape, COUNT(*) as count
FROM profiles 
WHERE id IN (
    SELECT id FROM auth.users WHERE email = 'csauvegarde2@gmail.com'
);

SELECT 'Vérification auth.users' as etape, COUNT(*) as count
FROM auth.users 
WHERE email = 'csauvegarde2@gmail.com';

-- 5. Message de confirmation
SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM auth.users WHERE email = 'csauvegarde2@gmail.com') = 0 
        THEN 'SUCCÈS: Utilisateur csauvegarde2@gmail.com supprimé'
        ELSE 'ÉCHEC: Utilisateur encore présent'
    END as resultat;
