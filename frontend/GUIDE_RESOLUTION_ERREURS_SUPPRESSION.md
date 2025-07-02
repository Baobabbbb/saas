# 🔧 GUIDE DE RÉSOLUTION - ERREURS SUPPRESSION COMPTE

## Problèmes identifiés
- ❌ Table "stories" manquante dans la base de données
- ❌ Fonction `delete_user_account` manquante  
- ❌ Erreurs 406 (Not Acceptable) lors des requêtes
- ❌ Problèmes de récupération de profil utilisateur

## Solution étape par étape

### ÉTAPE 1: Corriger la base de données Supabase 🗄️

1. **Ouvrir l'éditeur SQL Supabase**
   - Aller sur: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/sql/new

2. **Copier le contenu du fichier `fix_database_errors.sql`**
   - Ouvrir le fichier `fix_database_errors.sql` 
   - Copier tout le contenu

3. **Exécuter le script**
   - Coller le script dans l'éditeur SQL
   - Cliquer sur "Run" ou "Exécuter"
   - Vérifier qu'aucune erreur n'apparaît

### ÉTAPE 2: Tester les corrections 🧪

1. **Exécuter le test de vérification**
   ```bash
   cd frontend
   node test_database_fixes.js
   ```

2. **Vérifier les résultats**
   - ✅ Fonction delete_user_account DISPONIBLE
   - ✅ Table "stories" DISPONIBLE  
   - ✅ Table "animations" DISPONIBLE
   - ✅ Permissions profil OK

### ÉTAPE 3: Tester la suppression de compte 🗑️

1. **Se connecter à l'application**
   - Aller sur http://localhost:5173 (ou votre port)
   - Se connecter avec un compte de test

2. **Tester la suppression**
   - Cliquer sur le profil utilisateur
   - Aller dans "Supprimer mon compte"
   - Saisir "SUPPRIMER" pour confirmer
   - Vérifier que la suppression fonctionne sans erreur

### ÉTAPE 4: Vérifications supplémentaires 🔍

1. **Vérifier les logs de la console**
   - Ouvrir les DevTools (F12)
   - Onglet "Console"
   - Vérifier qu'il n'y a plus d'erreurs 406

2. **Tester avec un nouveau compte**
   - Créer un nouveau compte
   - Tester la suppression
   - Vérifier que tout fonctionne

## Commandes utiles

### Tester les corrections
```bash
node test_database_fixes.js
```

### Diagnostic de suppression (avec utilisateur connecté)
```bash
node diagnostic_suppression.js
```

### Test complet de suppression
```bash
node test_delete_account.js
```

## Si les problèmes persistent

### Option 1: Suppression manuelle via SQL
```sql
-- Remplacez USER_EMAIL par l'email problématique
DELETE FROM profiles WHERE id IN (
  SELECT id FROM auth.users WHERE email = 'USER_EMAIL'
);
DELETE FROM auth.users WHERE email = 'USER_EMAIL';
```

### Option 2: Suppression via interface Supabase
1. Aller sur: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/auth/users
2. Chercher l'utilisateur problématique
3. Cliquer sur "..." puis "Delete user"

## Prévention des problèmes futurs

1. **Sauvegardes régulières**
   - Exporter la structure de la base
   - Sauvegarder les fonctions importantes

2. **Tests automatisés**
   - Exécuter `test_database_fixes.js` régulièrement
   - Ajouter des tests pour nouvelles fonctionnalités

3. **Monitoring des erreurs**
   - Surveiller les logs d'erreur 406
   - Vérifier les permissions RLS

## Fichiers importants

- `fix_database_errors.sql` - Script de correction principal
- `test_database_fixes.js` - Test de vérification
- `src/services/auth.js` - Service d'authentification corrigé
- `diagnostic_suppression.js` - Diagnostic des problèmes
