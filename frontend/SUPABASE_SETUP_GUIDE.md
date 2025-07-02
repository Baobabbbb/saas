# Configuration de la base de données Supabase pour les profils utilisateur

## Problème identifié
La table `profiles` existe dans Supabase mais les politiques RLS (Row Level Security) bloquent l'accès aux données. Les utilisateurs ne peuvent pas créer, lire ou modifier leurs profils.

## Solution
Exécuter le script SQL `setup_profiles_table.sql` dans l'interface Supabase.

## Étapes à suivre

### 1. Accéder à l'interface Supabase
1. Aller sur https://supabase.com/dashboard
2. Se connecter avec le compte du projet
3. Sélectionner le projet `xfbmdeuzuyixpmouhqcv`

### 2. Ouvrir l'éditeur SQL
1. Dans le menu de gauche, cliquer sur "SQL Editor"
2. Cliquer sur "New query"

### 3. Exécuter le script
1. Copier tout le contenu du fichier `setup_profiles_table.sql`
2. Coller dans l'éditeur SQL
3. Cliquer sur "Run" pour exécuter

### 4. Vérifier la configuration
Le script va :
- Créer la table `profiles` si elle n'existe pas
- Configurer les politiques RLS appropriées
- Créer un trigger pour la mise à jour automatique de `updated_at`
- Afficher un résumé de la configuration

## Test après configuration

Une fois le script exécuté, tester avec :
```bash
cd "C:\Users\Admin\Documents\saas\frontend"
node test_auth_complete.js
```

## Statut actuel

✅ **Fonctionnel** :
- Authentification Supabase (connexion/inscription)
- Fallback localStorage (données temporaires)
- Interface utilisateur

⚠️ **À corriger** :
- Politiques RLS pour la table `profiles`
- Persistence des données en base

## Après correction

L'onglet "Mon compte" permettra :
- ✅ Charger les données du profil depuis Supabase
- ✅ Sauvegarder les modifications en base de données
- ✅ Synchronisation entre sessions/appareils
- ✅ Sécurité des données (chaque utilisateur accède uniquement à son profil)

## Alternative temporaire

En attendant la correction RLS, le système fonctionne avec localStorage :
- Les données sont sauvegardées localement
- Persistent durant la session
- L'interface est entièrement fonctionnelle
- Pas de synchronisation entre appareils/sessions
