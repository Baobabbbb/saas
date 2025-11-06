# 🚀 Guide d'Intégration Stripe Production pour Herbbie

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :
- ✅ Un compte Stripe en mode **production** (pas test)
- ✅ Les clés API Stripe (publique et secrète)
- ✅ Accès administrateur à Supabase
- ✅ Accès à Railway pour déployer

## 🎯 Étapes de Configuration

### 1. **Configuration Railway (Frontend)**

Dans votre projet Railway, ajoutez cette variable d'environnement :

```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_VOTRE_CLE_PUBLIQUE_ICI
```

> ⚠️ **Important** : Utilisez votre **clé publique** (`pk_live_...`) qui commence par `pk_live_`

### 2. **Configuration Supabase (Backend)**

#### Variables d'environnement Edge Functions :
Dans Supabase Dashboard → Edge Functions → Environment Variables, ajoutez :

```bash
STRIPE_SECRET_KEY=sk_live_VOTRE_CLE_SECRETE_ICI
```

> 🔐 **Important** : Utilisez votre **clé secrète** (`sk_live_...`) qui commence par `sk_live_`

### 3. **Migration de Base de Données**

Exécutez cette migration SQL dans Supabase SQL Editor :

```sql
-- Fix generation_permissions table
ALTER TABLE generation_permissions
DROP COLUMN IF EXISTS is_active,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ALTER COLUMN user_id TYPE uuid USING user_id::uuid,
ADD CONSTRAINT fk_generation_permissions_user_id
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

-- Fix payment_history table
ALTER TABLE payment_history
ALTER COLUMN user_id TYPE uuid USING user_id::uuid,
ADD CONSTRAINT fk_payment_history_user_id
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

-- Add updated_at columns for tracking
ALTER TABLE generation_permissions
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

ALTER TABLE payment_history
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_generation_permissions_user_content
ON generation_permissions(user_id, content_type, is_active);

CREATE INDEX IF NOT EXISTS idx_generation_permissions_stripe_payment
ON generation_permissions(stripe_payment_intent_id);

CREATE INDEX IF NOT EXISTS idx_payment_history_user
ON payment_history(user_id);

CREATE INDEX IF NOT EXISTS idx_payment_history_stripe
ON payment_history(stripe_payment_id);
```

### 4. **Mise à Jour des Edge Functions**

#### Mettre à jour `create-payment` :

Remplacez le contenu de l'Edge Function `create-payment` par :

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import Stripe from 'https://esm.sh/stripe@14.21.0?target=deno';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
  };

  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const { contentType, userId, userEmail } = await req.json();

    // Validation des paramètres
    if (!contentType || !userId) {
      throw new Error('Paramètres manquants: contentType et userId requis');
    }

    // Initialisation Stripe avec la clé secrète
    const stripeSecretKey = Deno.env.get('STRIPE_SECRET_KEY');
    if (!stripeSecretKey) {
      throw new Error('Clé secrète Stripe non configurée');
    }

    const stripe = new Stripe(stripeSecretKey, {
      apiVersion: '2024-06-20',
      httpClient: Stripe.createFetchHttpClient(),
    });

    // Prix par contenu (en centimes)
    const prices = {
      animation: 499,    // 4.99€
      coloring: 199,    // 1.99€
      comic: 299,       // 2.99€
      story: 399,       // 3.99€
      rhyme: 249        // 2.49€
    };

    const amount = prices[contentType] || 299;

    // Créer un Payment Intent avec Stripe
    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount,
      currency: 'eur',
      automatic_payment_methods: {
        enabled: true,
      },
      metadata: {
        contentType,
        userId,
        userEmail,
      },
      receipt_email: userEmail,
    });

    console.log(`Payment Intent créé pour ${userEmail}: ${paymentIntent.id}, montant: ${amount} centimes`);

    return new Response(JSON.stringify({
      client_secret: paymentIntent.client_secret,
      payment_intent_id: paymentIntent.id,
      amount: amount,
      currency: 'eur',
      contentType,
      userId,
      userEmail
    }), {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });

  } catch (error) {
    console.error('Erreur dans create-payment:', error);
    return new Response(JSON.stringify({
      error: error.message,
      details: error.stack
    }), {
      status: 500,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }
});
```

#### Mettre à jour `check-permission` :

Remplacez le contenu de l'Edge Function `check-permission` par :

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
  };

  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const { contentType, userId, userEmail } = await req.json();

    if (!userId || !contentType) {
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'missing_parameters',
        error: 'userId et contentType requis'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL'),
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    );

    // Vérifier le rôle utilisateur
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', userId)
      .single();

    if (profileError) {
      console.error('Erreur récupération profil:', profileError);
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'profile_error',
        error: 'Erreur lors de la récupération du profil'
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Admin a toujours accès
    if (profile?.role === 'admin') {
      return new Response(JSON.stringify({
        hasPermission: true,
        reason: 'admin_access',
        userRole: 'admin',
        contentType,
        userId
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Utilisateur free a accès gratuit
    if (profile?.role === 'free') {
      return new Response(JSON.stringify({
        hasPermission: true,
        reason: 'free_access',
        userRole: 'free',
        contentType,
        userId
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Vérifier les permissions payées actives
    const { data: permission, error: permError } = await supabase
      .from('generation_permissions')
      .select('*')
      .eq('user_id', userId)
      .eq('content_type', contentType)
      .eq('status', 'completed')
      .eq('is_active', true)
      .single();

    const hasPermission = !!permission && !permError;

    return new Response(JSON.stringify({
      hasPermission,
      reason: hasPermission ? 'payment_verified' : 'payment_required',
      userRole: 'user',
      permission: permission || null,
      contentType,
      userId
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Erreur dans check-permission:', error);
    return new Response(JSON.stringify({
      hasPermission: false,
      reason: 'error',
      error: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
```

### 5. **Déploiement et Test**

1. **Redéployez** votre application Railway
2. **Testez** avec un vrai paiement (utilisez une carte de test Stripe si nécessaire)
3. **Vérifiez** les logs Supabase pour confirmer que les paiements sont enregistrés

## 🔍 Prix Configurés

| Type de Contenu | Prix (€) | Prix (centimes) |
|----------------|----------|-----------------|
| Animation IA | 4,99€ | 499 |
| Histoire Audio | 3,99€ | 399 |
| Bande Dessinée | 2,99€ | 299 |
| Comptine Musicale | 2,49€ | 249 |
| Coloriage | 1,99€ | 199 |

## 🐛 Dépannage

### Erreur "Clé secrète Stripe non configurée"
- Vérifiez que `STRIPE_SECRET_KEY` est bien définie dans Supabase Edge Functions

### Erreur "Client secret manquant"
- Vérifiez que l'Edge Function `create-payment` retourne bien un `client_secret`

### Paiement refusé
- Vérifiez vos clés Stripe (elles doivent être en `live_` pour la production)
- Consultez les logs Stripe Dashboard

### Permission non accordée après paiement
- Vérifiez que la fonction `grantPermission` est appelée correctement
- Vérifiez les logs Supabase pour les erreurs d'insertion

## 📊 Monitoring

Après déploiement, surveillez :
- **Supabase Logs** : Erreurs Edge Functions
- **Stripe Dashboard** : Paiements réussis/échoués
- **Base de données** : Nouvelles entrées dans `generation_permissions`

---

✅ **Configuration terminée !** Votre intégration Stripe est maintenant prête pour la production.
