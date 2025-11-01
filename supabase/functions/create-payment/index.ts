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
