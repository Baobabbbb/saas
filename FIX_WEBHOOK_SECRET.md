# 🔐 Fix : Webhook signature verification failed

## Problème
Erreur "Webhook signature verification failed" avec code 400. Cela signifie que le `STRIPE_WEBHOOK_SECRET` dans Supabase ne correspond pas au secret du webhook dans Stripe.

## Solution

### Étape 1 : Récupérer le bon secret dans Stripe

1. Va dans **Stripe Dashboard** > **Developers** > **Webhooks**
2. Clique sur ton endpoint : `https://xfbmdeuzuyixpmouhqcv.supabase.co/functions/v1/stripe-webhook`
3. Dans la section **"Signing secret"**, clique sur **"Reveal"** (Révéler)
4. **Copie le secret** (il commence par `whsec_...`)
   - ⚠️ **Important :** Il y a peut-être plusieurs webhooks. Assure-toi de prendre le secret du webhook qui correspond exactement à cette URL.

### Étape 2 : Mettre à jour le secret dans Supabase

1. Va dans **Supabase Dashboard** > **Project Settings** > **Edge Functions** > **Secrets**
2. Cherche la variable `STRIPE_WEBHOOK_SECRET`
3. Si elle existe :
   - Clique dessus pour la modifier
   - Colle le nouveau secret copié depuis Stripe
   - Sauvegarde
4. Si elle n'existe pas :
   - Clique sur **"Add new secret"**
   - Nom : `STRIPE_WEBHOOK_SECRET`
   - Valeur : Colle le secret copié depuis Stripe
   - Sauvegarde

### Étape 3 : Vérifier qu'il n'y a qu'un seul webhook

Si tu as plusieurs webhooks dans Stripe :

1. Vérifie que chaque webhook a son propre secret
2. Assure-toi d'utiliser le secret du webhook qui correspond à l'URL Supabase
3. Si tu as plusieurs environnements (test/production), assure-toi d'utiliser le bon secret pour chaque environnement

### Étape 4 : Tester

1. Dans Stripe, va dans **Developers** > **Webhooks** > ton endpoint
2. Clique sur **"Send test webhook"**
3. Sélectionne un événement (ex: `customer.subscription.created`)
4. Clique sur **"Send test webhook"**
5. Vérifie que tu reçois maintenant un code **200 OK**

## Vérification dans les logs Supabase

Après avoir mis à jour le secret, vérifie les logs dans Supabase :

1. Va dans **Edge Functions** > **stripe-webhook** > **Logs**
2. Envoie un test webhook depuis Stripe
3. Les logs devraient maintenant montrer :
   - ✅ `Événement Stripe reçu: customer.subscription.created` (ou autre)
   - ❌ Plus d'erreur "Webhook signature verification failed"

## Points importants

⚠️ **Le secret doit correspondre exactement** au webhook Stripe :
- Si tu régénères le secret dans Stripe, tu dois le mettre à jour dans Supabase
- Chaque webhook a son propre secret unique
- Le secret commence toujours par `whsec_...`

## Si le problème persiste

1. Vérifie que le secret est bien copié **sans espaces** avant/après
2. Vérifie qu'il n'y a pas de caractères invisibles
3. Supprime et recrée le secret dans Supabase si nécessaire
4. Vérifie les logs Supabase pour voir les détails de l'erreur

