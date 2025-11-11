# 🗑️ Nettoyage Tables Inutilisées - 11 novembre 2025

## 📋 Résumé

Suppression de 3 tables qui n'étaient jamais alimentées et dont le système n'avait pas besoin pour fonctionner.

---

## ❌ Tables Supprimées

### 1. **`payments`** 
- **Objectif initial** : Historique des paiements directs (pay-per-use)
- **Pourquoi supprimée** : 
  - Le webhook Stripe ne l'alimentait jamais
  - Le système pay-per-use fonctionne via le flag `contentPaidDirectly` côté frontend
  - Aucune fonctionnalité ne dépendait de cette table
- **Lignes** : 0

### 2. **`payment_history`**
- **Objectif initial** : Historique global de tous les paiements
- **Pourquoi supprimée** :
  - Aucun code ne l'alimentait (table orpheline)
  - Jamais utilisée nulle part dans le code
  - Pure table legacy
- **Lignes** : 0

### 3. **`generation_permissions`**
- **Objectif initial** : Permissions temporaires pour générer du contenu après paiement direct
- **Pourquoi supprimée** :
  - Ancien système remplacé par `contentPaidDirectly` (frontend)
  - Aucune permission n'était jamais créée
  - Le système actuel utilise les abonnements (`subscriptions`) pour les permissions
- **Lignes** : 0

---

## ✅ Tables Conservées (Fonctionnelles)

| Table | Lignes | Usage |
|-------|--------|-------|
| `subscriptions` | 1 | ✅ Abonnements actifs, tokens restants |
| `user_tokens` | 7 | ✅ Historique des usages de tokens (déductions) |
| `subscription_plans` | 4 | ✅ Plans d'abonnements disponibles |
| `profiles` | 4 | ✅ Profils utilisateurs |
| `token_costs` | 20 | ✅ Coûts en tokens par type de contenu |
| `creations` | 0 | ✅ Historique des créations générées |

---

## 🔧 Modifications du Code

### Edge Functions Modifiées

#### 1. **`stripe-webhook/index.ts`**
- **Avant** : Tentait d'insérer dans `payments` après `payment_intent.succeeded`
- **Après** : Simple log, pas d'insertion (système géré côté frontend)

```typescript
case 'payment_intent.succeeded': {
  // Paiements directs (pay-per-use) gérés côté frontend via contentPaidDirectly
  if (paymentIntent.metadata?.contentType && paymentIntent.metadata?.userId) {
    console.log(`Paiement pay-per-use réussi pour ${paymentIntent.metadata.userId}`);
  }
  break;
}
```

#### 2. **`check-permission/index.ts`**
- **Avant** : Vérifiait `generation_permissions` comme fallback
- **Après** : Retourne directement `payment_required` si pas d'abonnement

```typescript
// Aucun abonnement actif → paiement requis
// Le système pay-per-use est géré côté frontend via contentPaidDirectly
return new Response(JSON.stringify({
  hasPermission: false,
  reason: 'payment_required',
  estimatedTokensCost,
  contentType,
  userId
}));
```

#### 3. **`admin-stripe-data/index.ts`**
- **Avant** : Stats basées sur `generation_permissions`
- **Après** : Stats basées sur `subscriptions` actives

```typescript
SELECT
  COUNT(*) as total_subscriptions,
  SUM(sp.price_monthly) as monthly_revenue,
  AVG(sp.price_monthly) as avg_subscription_price,
  COUNT(DISTINCT s.user_id) as unique_customers
FROM subscriptions s
JOIN subscription_plans sp ON s.plan_id = sp.id
WHERE s.status = 'active'
```

---

## 🎯 Système Actuel (Inchangé)

### **Abonnements** ✅
- Utilisateur souscrit → `subscriptions` créée
- Tokens alloués → `subscriptions.tokens_remaining`
- Chaque usage → déduction dans `subscriptions` + enregistrement dans `user_tokens`
- Lien : `user_id` + `stripe_subscription_id` + `stripe_customer_id`

### **Pay-Per-Use** ✅
- Utilisateur clique "Acheter pour X€" → `StripePaymentModal`
- Paiement réussi → `contentPaidDirectly = true`
- Génération lancée → **pas de déduction de tokens**
- Flag réinitialisé après génération
- Lien : `metadata.userId` dans Stripe PaymentIntent

---

## 📊 Migration Appliquée

```sql
-- Migration: remove_unused_payment_tables
-- Date: 2025-11-11

DROP TABLE IF EXISTS generation_permissions CASCADE;
DROP TABLE IF EXISTS payment_history CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
```

**Version** : `20251111013405`

---

## ✅ Vérifications Post-Nettoyage

- ✅ Aucune table fonctionnelle n'a été supprimée
- ✅ Aucune foreign key orpheline
- ✅ Edge Functions mises à jour et déployées
- ✅ Système abonnements : fonctionnel
- ✅ Système pay-per-use : fonctionnel
- ✅ Tous les paiements sont liés aux utilisateurs

---

## 🚀 Déploiement

```bash
# Migration Supabase
✅ Migration appliquée via MCP Supabase

# Edge Functions
✅ Commit: c184f5f1
✅ Push: main → origin/main
```

---

## 📝 Notes

- Le système fonctionne **exactement comme avant** la suppression
- Aucune fonctionnalité n'a été perdue
- La base de données est maintenant plus propre et plus facile à maintenir
- Si besoin d'un historique pay-per-use à l'avenir, il faudra recréer une table dédiée

---

**Date** : 11 novembre 2025  
**Auteur** : Assistant IA (Claude)  
**Validé par** : Utilisateur

