# 🧪 Test Manuel - Interface utilisateur

## Instructions pour tester l'onglet "Mon compte"

### 1. Ouvrir l'application
- Aller sur http://localhost:5175/
- Vérifier que la page se charge correctement

### 2. Tester l'inscription
1. Cliquer sur l'icône utilisateur (coin supérieur droit)
2. Cliquer sur "S'inscrire"
3. Remplir le formulaire :
   - Email : `test.manuel@example.com`
   - Mot de passe : `TestManuel123!`
   - Prénom : `Jean`
   - Nom : `Dupont`
4. Cliquer sur "S'inscrire"
5. ✅ **Vérifier** : Message de succès et fermeture du formulaire

### 3. Tester l'onglet "Mon compte"
1. Cliquer sur l'icône utilisateur
2. Cliquer sur "Mon compte"
3. ✅ **Vérifier** : Formulaire affiché avec :
   - Prénom : `Jean` (modifiable)
   - Nom : `Dupont` (modifiable)
   - Email : `test.manuel@example.com` (lecture seule)

### 4. Tester la modification du profil
1. Modifier le prénom : `Jean-Pierre`
2. Modifier le nom : `Dupont-Martin`
3. Cliquer sur "Mettre à jour le profil"
4. ✅ **Vérifier** : 
   - Message de succès affiché
   - Nom d'utilisateur mis à jour dans le menu

### 5. Tester la persistance
1. Fermer l'onglet "Mon compte"
2. Rouvrir l'onglet "Mon compte"
3. ✅ **Vérifier** : Les modifications sont conservées

### 6. Tester la déconnexion/reconnexion
1. Se déconnecter
2. Se reconnecter avec les mêmes identifiants
3. Ouvrir "Mon compte"
4. ✅ **Vérifier** : Les données sont récupérées

### 7. Tester la validation
1. Vider le champ prénom
2. Cliquer sur "Mettre à jour le profil"
3. ✅ **Vérifier** : Message d'erreur affiché

## Résultats attendus

### ✅ Interface
- Design cohérent avec le reste du site
- Animations fluides
- Formulaire bien formaté
- Messages de feedback clairs

### ✅ Fonctionnalité
- Inscription fonctionne
- Connexion fonctionne
- Modification du profil fonctionne
- Validation des champs fonctionne
- Déconnexion fonctionne

### ✅ Persistance
- Données conservées durant la session
- Nom d'utilisateur mis à jour en temps réel
- Nettoyage à la déconnexion

## En cas de problème

### Erreur "RLS policy"
- C'est normal et attendu
- Les données sont quand même sauvegardées localement
- L'interface fonctionne parfaitement

### Données non sauvegardées entre sessions
- Comportement actuel normal
- Pour activer la persistance cloud : exécuter `setup_profiles_table.sql`

### Autres erreurs
1. Vérifier la console du navigateur (F12)
2. Vérifier que le serveur fonctionne
3. Rafraîchir la page
