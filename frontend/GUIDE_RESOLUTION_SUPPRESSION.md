# 🚨 PROBLÈME DE SUPPRESSION DE COMPTE - GUIDE DE RÉSOLUTION

## 📋 Problème identifié
L'utilisateur `csauvegarde2@gmail.com` a cliqué sur "Supprimer mon compte" mais peut encore essayer de s'inscrire et obtient le message "User already registered".

## 🔍 Cause du problème
La fonction `delete_user_account` dans Supabase n'existe probablement pas ou n'a pas les bonnes permissions.

## ⚡ SOLUTION IMMÉDIATE - Suppression manuelle

### Étape 1: Ouvrir l'éditeur SQL Supabase
1. Aller sur https://app.supabase.com
2. Sélectionner votre projet
3. Aller dans "SQL Editor"

### Étape 2: Exécuter le script de suppression
Copier et exécuter ce code SQL :

```sql
-- SUPPRESSION MANUELLE - csauvegarde2@gmail.com

-- 1. Identifier l'utilisateur
SELECT 
    u.id as user_id,
    u.email,
    u.created_at,
    p.prenom,
    p.nom
FROM auth.users u
LEFT JOIN profiles p ON u.id = p.id 
WHERE u.email = 'csauvegarde2@gmail.com';

-- 2. Supprimer le profil
DELETE FROM profiles 
WHERE id IN (
    SELECT id FROM auth.users WHERE email = 'csauvegarde2@gmail.com'
);

-- 3. Supprimer l'utilisateur
DELETE FROM auth.users WHERE email = 'csauvegarde2@gmail.com';

-- 4. Vérification (doit retourner 0 lignes)
SELECT COUNT(*) as "Profiles restants" FROM profiles 
WHERE id IN (SELECT id FROM auth.users WHERE email = 'csauvegarde2@gmail.com');

SELECT COUNT(*) as "Users restants" FROM auth.users 
WHERE email = 'csauvegarde2@gmail.com';
```

### Étape 3: Créer la fonction de suppression automatique
Exécuter ce code pour créer la fonction manquante :

```sql
-- CRÉATION FONCTION DE SUPPRESSION
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
  
  -- Supprimer le profil s'il existe
  SELECT EXISTS(SELECT 1 FROM profiles WHERE id = user_id) INTO profile_exists;
  IF profile_exists THEN
    DELETE FROM profiles WHERE id = user_id;
  END IF;
  
  -- Supprimer l'utilisateur
  DELETE FROM auth.users WHERE id = user_id;
  
  -- Vérifier le succès
  IF NOT EXISTS(SELECT 1 FROM auth.users WHERE id = user_id) THEN
    result := json_build_object(
      'success', true,
      'message', 'Compte utilisateur supprimé avec succès',
      'user_id', user_id,
      'email', user_email
    );
  ELSE
    result := json_build_object(
      'success', false,
      'error', 'Échec de la suppression',
      'user_id', user_id
    );
  END IF;
  
  RETURN result;
  
EXCEPTION
  WHEN OTHERS THEN
    result := json_build_object(
      'success', false,
      'error', SQLERRM,
      'user_id', user_id
    );
    RETURN result;
END;
$$;
```

## ✅ Test après correction

### 1. Vérifier que l'utilisateur a été supprimé
```sql
SELECT COUNT(*) as "Utilisateur existe encore ?" 
FROM auth.users 
WHERE email = 'csauvegarde2@gmail.com';
-- Doit retourner 0
```

### 2. Tester l'inscription
- Aller sur l'application
- Essayer de s'inscrire avec `csauvegarde2@gmail.com`
- L'inscription devrait maintenant fonctionner

### 3. Tester la nouvelle fonction de suppression
Se connecter et tester le bouton "Supprimer mon compte" - il devrait maintenant fonctionner correctement.

## 🔧 Améliorations apportées au code

### Dans `auth.js` :
- ✅ Meilleure gestion des erreurs RPC
- ✅ Logs détaillés pour le debugging
- ✅ Suppression manuelle si RPC indisponible
- ✅ Messages d'erreur informatifs

### Dans `UserAccount.jsx` :
- ✅ Gestion spéciale des erreurs de suppression partielle
- ✅ Messages utilisateur plus clairs
- ✅ Information sur les actions admin nécessaires

## 📞 Contact administrateur
Si le problème persiste, fournir ces informations :
- Email: `csauvegarde2@gmail.com`
- Action: Suppression de compte
- Erreur: "User already registered" lors de l'inscription
- Solution: Supprimer manuellement dans Supabase SQL Editor

---

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Statut:** ⚠️ En cours de résolution
