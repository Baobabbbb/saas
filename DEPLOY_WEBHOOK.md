# Déploiement de l'Edge Function stripe-webhook

## 🎯 Objectif

Déployer la fonction `stripe-webhook` pour gérer les événements Stripe, notamment `payment_intent.succeeded` pour les paiements directs de contenus.

## 📝 Modifications apportées

### 1. Support de `payment_intent.succeeded`

Ajout de la gestion de l'événement `payment_intent.succeeded` dans le webhook Stripe pour :
- Enregistrer les paiements directs dans la table `payments`
- Éviter les erreurs 400 de `deduct-tokens` après un paiement réussi

### 2. Fix Frontend

Ajout du flag `contentPaidDirectly` dans `App.jsx` pour :
- Éviter la déduction de tokens après un paiement direct
- Marquer qu'un contenu a été payé et ne nécessite pas de tokens

## 🚀 Déploiement

### Option 1 : Via Supabase CLI (local)

```bash
cd C:/Users/freda/Desktop/projet
npx supabase login
npx supabase functions deploy stripe-webhook --no-verify-jwt
```

### Option 2 : Via Supabase Dashboard

1. Aller sur https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv/functions
2. Cliquer sur "New function" ou sélectionner `stripe-webhook`
3. Copier le contenu de `backend/supabase/functions/stripe-webhook/index.ts`
4. Coller dans l'éditeur en ligne
5. Cliquer sur "Deploy"

### Option 3 : Via GitHub Actions (recommandé)

Si vous avez configuré GitHub Actions avec Supabase, le déploiement se fera automatiquement à chaque push sur `main`.

## ✅ Vérification

Après déploiement, vérifier dans les logs Supabase que l'événement `payment_intent.succeeded` est bien traité :

```
Événement Stripe reçu: payment_intent.succeeded
Paiement réussi pour [userId]: [amount] centimes, type: [contentType]
Paiement enregistré pour utilisateur: [userId]
```

## 🔧 Configuration requise

Assurez-vous que les variables d'environnement suivantes sont configurées dans Supabase :
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## 📊 Table `payments` requise

La fonction nécessite une table `payments` avec la structure suivante :

```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  amount INTEGER NOT NULL,
  currency VARCHAR(3) NOT NULL DEFAULT 'eur',
  status VARCHAR(50) NOT NULL,
  stripe_payment_intent_id VARCHAR(255) UNIQUE,
  content_type VARCHAR(50),
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Si la table n'existe pas, créez-la via le SQL Editor de Supabase.

## 🎉 Résultat attendu

Après le déploiement, les paiements directs de contenus ne déclencheront plus d'erreur `deduct-tokens` car :
1. Le webhook enregistre le paiement dans la table `payments`
2. Le frontend ne tente plus de déduire des tokens (`contentPaidDirectly = true`)
3. La génération se lance normalement après le paiement

