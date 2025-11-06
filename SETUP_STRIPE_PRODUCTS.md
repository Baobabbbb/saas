# 🔧 Configuration Automatique des Produits Stripe

*Script pour créer automatiquement les produits et prix Stripe*

---

## 🎯 Ce que fait ce script

Cette Edge Function va automatiquement :
1. ✅ Créer 4 produits Stripe (Découverte, Famille, Créatif, Institut)
2. ✅ Créer les Prix récurrents mensuels associés
3. ✅ Mettre à jour `stripe_price_id` dans la base de données Supabase
4. ✅ Lier les métadonnées (tokens_allocated, plan_id)

---

## 📋 Prérequis

1. **Clé API Stripe** configurée dans Supabase (déjà fait)
2. **Compte admin** sur Herbbie (vous l'avez déjà)
3. **Token d'authentification** Supabase

---

## 🚀 Comment l'exécuter

### Option 1 : Via curl (recommandé)

```bash
# 1. Récupérer votre token d'authentification
# Allez sur https://herbbie.com et connectez-vous avec votre compte admin
# Ouvrez la console (F12) et tapez :
# localStorage.getItem('supabase.auth.token')

# 2. Exécuter la fonction
curl -X POST \
  https://xfbmdeuzuyixpmouhqcv.supabase.co/functions/v1/setup-stripe-products \
  -H "Authorization: Bearer VOTRE_TOKEN_ICI" \
  -H "Content-Type: application/json"
```

### Option 2 : Via l'interface Supabase

1. Allez sur https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/functions
2. Cliquez sur `setup-stripe-products`
3. Cliquez sur "Invoke"
4. Ajoutez votre token d'authentification dans les headers

---

## 📊 Résultat attendu

```json
{
  "success": true,
  "message": "Configuration Stripe terminée",
  "results": [
    {
      "plan": "Découverte",
      "product_id": "prod_xxxxx",
      "price_id": "price_xxxxx",
      "amount": 499,
      "success": true
    },
    {
      "plan": "Famille",
      "product_id": "prod_yyyyy",
      "price_id": "price_yyyyy",
      "amount": 999,
      "success": true
    },
    {
      "plan": "Créatif",
      "product_id": "prod_zzzzz",
      "price_id": "price_zzzzz",
      "amount": 1999,
      "success": true
    },
    {
      "plan": "Institut",
      "product_id": "prod_aaaaa",
      "price_id": "price_aaaaa",
      "amount": 4999,
      "success": true
    }
  ]
}
```

---

## ✅ Vérification

### 1. Dans Stripe Dashboard

Allez sur https://dashboard.stripe.com/products

Vous devriez voir :
- ✅ **Découverte** - 4,99€/mois
- ✅ **Famille** - 9,99€/mois
- ✅ **Créatif** - 19,99€/mois
- ✅ **Institut** - 49,99€/mois

### 2. Dans Supabase

```sql
SELECT 
  name,
  price_monthly,
  tokens_allocated,
  stripe_price_id
FROM subscription_plans
ORDER BY price_monthly ASC;
```

Résultat attendu :
```
name         | price_monthly | tokens_allocated | stripe_price_id
-------------|---------------|------------------|----------------
Découverte   | 499           | 250              | price_xxxxx
Famille      | 999           | 500              | price_yyyyy
Créatif      | 1999          | 1000             | price_zzzzz
Institut     | 4999          | 2500             | price_aaaaa
```

---

## 🔒 Sécurité

- ✅ Fonction accessible uniquement aux **admins**
- ✅ Vérification du rôle via Supabase
- ✅ Token d'authentification requis
- ✅ Aucune donnée sensible exposée

---

## 🐛 Dépannage

### Erreur "Authentification requise"
→ Vous devez fournir un token d'authentification valide

### Erreur "Accès réservé aux administrateurs"
→ Votre compte n'a pas le rôle `admin` dans la table `profiles`

### Erreur "Produit existant trouvé"
→ Normal ! La fonction réutilise les produits existants et crée juste un nouveau prix

### Les price_id ne sont pas mis à jour
→ Vérifiez les logs de la fonction dans Supabase Dashboard

---

## 🔄 Pour réexécuter

Si vous changez les prix ou voulez mettre à jour :
1. La fonction ne créera pas de doublons
2. Elle créera de nouveaux prix pour les produits existants
3. Les anciens prix restent accessibles dans Stripe

---

## 📝 Logs

Pour voir les logs d'exécution :
1. Allez sur https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/logs
2. Sélectionnez "Edge Functions"
3. Filtrez par "setup-stripe-products"

---

## ✅ Une fois terminé

Après l'exécution réussie :
1. ✅ Tous les produits Stripe sont créés
2. ✅ Tous les prix sont configurés
3. ✅ La base de données Supabase est mise à jour
4. ✅ Les utilisateurs peuvent s'abonner via la popup

**Votre système d'abonnements est 100% opérationnel !** 🎉

