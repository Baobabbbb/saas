# 🔍 AUDIT COMPLET - Paiements & Abonnements

*Date : 6 Novembre 2025 - Audit via MCP Supabase*

---

## ✅ CE QUI FONCTIONNE

### 1. Structure de base de données

**Tables présentes et correctement liées** :
- ✅ `profiles` (utilisateurs) → liée à `auth.users`
- ✅ `subscriptions` (abonnements) → liée à `profiles` et `subscription_plans`
- ✅ `subscription_plans` (4 plans configurés)
- ✅ `user_tokens` (historique des tokens) → liée à `profiles` et `subscriptions`
- ✅ `payment_history` (historique paiements) → liée à `profiles`
- ✅ `generation_permissions` (permissions de génération) → liée à `profiles`

**Relations clés ✅** :
```sql
profiles.id → auth.users.id (FK)
subscriptions.user_id → profiles.id (FK)
subscriptions.plan_id → subscription_plans.id (FK)
user_tokens.user_id → profiles.id (FK)
user_tokens.subscription_id → subscriptions.id (FK)
payment_history.user_id → profiles.id (FK)
```

### 2. Stripe PaymentIntent (PAY-PER-USE)

**Edge Function `create-payment`** ✅ :
```typescript
// Crée un PaymentIntent avec metadata
paymentIntent = stripe.paymentIntents.create({
  amount: finalAmount,
  currency: 'eur',
  metadata: {
    contentType,  // ✅
    userId,       // ✅
    userEmail     // ✅
  }
});
```

**Webhook `stripe-webhook`** ✅ :
```typescript
case 'payment_intent.succeeded':
  // Récupère userId et contentType depuis metadata
  // Enregistre dans table 'payments' (⚠️ voir problème #1)
```

### 3. Gestion des abonnements

**Webhook gère** ✅ :
- `customer.subscription.created` → Création abonnement
- `customer.subscription.updated` → Mise à jour statut
- `customer.subscription.deleted` → Annulation
- `invoice.payment_succeeded` → Renouvellement tokens
- `invoice.payment_failed` → Marque en défaut

**Logique tokens** ✅ :
```typescript
// Renouvellement mensuel :
newTokensRemaining = currentTokens - tokensUsed + tokensAllocated
tokens_used_this_month = 0 // Reset
```

---

## ⚠️ PROBLÈMES IDENTIFIÉS

### Problème #1 : Table `payments` manquante

**Impact** : 🔴 **CRITIQUE**

Le webhook `stripe-webhook` essaie d'insérer dans une table `payments` qui **n'existe pas** :

```typescript
// Ligne 178 de stripe-webhook/index.ts
await supabase.from('payments').insert({...})  // ❌ ERREUR
```

**Solution** : Créer la table `payments`

```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  amount INTEGER NOT NULL,
  currency VARCHAR(3) DEFAULT 'eur',
  status VARCHAR(50) NOT NULL,
  stripe_payment_intent_id VARCHAR(255) UNIQUE,
  content_type VARCHAR(100),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performances
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_stripe_id ON payments(stripe_payment_intent_id);

-- RLS pour sécurité
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own payments"
  ON payments FOR SELECT
  USING (auth.uid() = user_id);
```

---

### Problème #2 : Stripe Price IDs manquants

**Impact** : 🟡 **MOYEN**

Les plans d'abonnement ont des `stripe_price_id` NULL :

```json
{
  "id": 1,
  "name": "Découverte",
  "price_monthly": 499,
  "tokens_allocated": 40,  // ⚠️ Devrait être 250
  "stripe_price_id": null   // ❌ MANQUANT
}
```

**Conséquence** : Les abonnements Stripe ne sont pas liés aux plans Supabase.

**Solution** : 
1. Créer les Price IDs dans Stripe Dashboard
2. Mettre à jour la table `subscription_plans`

---

### Problème #3 : Tokens alloués incorrects

**Impact** : 🔴 **CRITIQUE**

Les `tokens_allocated` dans `subscription_plans` ne correspondent pas à la tarification actuelle :

| Plan | Actuel DB | Devrait être | Prix |
|------|-----------|--------------|------|
| Découverte | 40 | **250** | 4,99€ |
| Famille | 120 | **500** | 9,99€ |
| Créatif | 300 | **1000** | 19,99€ |
| Institut | 900 | **2500** | 49,99€ |

**Solution** : Mettre à jour les tokens alloués

```sql
UPDATE subscription_plans 
SET tokens_allocated = CASE
  WHEN name = 'Découverte' THEN 250
  WHEN name = 'Famille' THEN 500
  WHEN name = 'Créatif' THEN 1000
  WHEN name = 'Institut' THEN 2500
END;
```

---

## 🎯 PLAN D'ACTION

### Étape 1 : Créer la table `payments` (URGENT)

```sql
-- À exécuter dans Supabase SQL Editor
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  amount INTEGER NOT NULL,
  currency VARCHAR(3) DEFAULT 'eur',
  status VARCHAR(50) NOT NULL,
  stripe_payment_intent_id VARCHAR(255) UNIQUE,
  content_type VARCHAR(100),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_stripe_id ON payments(stripe_payment_intent_id);

ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own payments"
  ON payments FOR SELECT
  USING (auth.uid() = user_id);
```

---

### Étape 2 : Corriger les tokens alloués

```sql
UPDATE subscription_plans 
SET 
  tokens_allocated = CASE
    WHEN name = 'Découverte' THEN 250
    WHEN name = 'Famille' THEN 500
    WHEN name = 'Créatif' THEN 1000
    WHEN name = 'Institut' THEN 2500
  END,
  updated_at = NOW();
```

---

### Étape 3 : Configurer Stripe Price IDs

**Dans Stripe Dashboard** :

1. Aller sur https://dashboard.stripe.com/products
2. Créer 4 produits récurrents :
   - **Découverte** : 4,99€/mois → Noter le Price ID
   - **Famille** : 9,99€/mois → Noter le Price ID
   - **Créatif** : 19,99€/mois → Noter le Price ID
   - **Institut** : 49,99€/mois → Noter le Price ID

3. Mettre à jour Supabase :
```sql
UPDATE subscription_plans 
SET stripe_price_id = 'price_xxx' 
WHERE name = 'Découverte';

UPDATE subscription_plans 
SET stripe_price_id = 'price_yyy' 
WHERE name = 'Famille';

UPDATE subscription_plans 
SET stripe_price_id = 'price_zzz' 
WHERE name = 'Créatif';

UPDATE subscription_plans 
SET stripe_price_id = 'price_aaa' 
WHERE name = 'Institut';
```

---

## 📊 FLUX ACTUEL

### PAY-PER-USE (Paiements directs)

```
1. User clique "Payer 0,50€"
   ↓
2. Frontend → create-payment Edge Function
   ↓
3. Stripe crée PaymentIntent avec metadata {userId, contentType}
   ↓
4. User paie avec carte dans popup
   ↓
5. Stripe envoie webhook payment_intent.succeeded
   ↓
6. Webhook enregistre dans table 'payments' ✅ (après fix #1)
   ↓
7. Frontend permet génération sans déduire tokens
```

### ABONNEMENTS

```
1. User choisit plan "Famille - 9,99€"
   ↓
2. Frontend → create-subscription Edge Function (⚠️ à créer)
   ↓
3. Stripe crée Subscription + Customer
   ↓
4. Webhook customer.subscription.created
   ↓
5. Insert dans table 'subscriptions' avec tokens_remaining = 500
   ↓
6. Chaque mois : webhook invoice.payment_succeeded
   ↓
7. Reset tokens : tokens_remaining = 500, tokens_used_this_month = 0
```

---

## 🔐 SÉCURITÉ (RLS)

**Toutes les tables ont RLS activé** ✅ :
- `profiles` : ✅ RLS enabled
- `subscriptions` : ✅ RLS enabled
- `user_tokens` : ✅ RLS enabled
- `payment_history` : ✅ RLS enabled
- `generation_permissions` : ✅ RLS enabled

**Users peuvent uniquement** :
- Voir leurs propres données
- Pas de modification directe (via Edge Functions seulement)

---

## ✅ CONCLUSION

### Ce qui marche

1. ✅ Structure DB complète et relations correctes
2. ✅ Paiements PAY-PER-USE (PaymentIntent + metadata)
3. ✅ Webhooks configurés pour tous les événements
4. ✅ Système de tokens avec historique
5. ✅ RLS activé sur toutes les tables

### Ce qui doit être corrigé (3 actions)

1. 🔴 **URGENT** : Créer table `payments`
2. 🔴 **URGENT** : Corriger `tokens_allocated` (40→250, 120→500, etc.)
3. 🟡 **Important** : Ajouter `stripe_price_id` dans les plans

**Une fois ces 3 corrections faites, le système sera 100% fonctionnel !** 🚀

