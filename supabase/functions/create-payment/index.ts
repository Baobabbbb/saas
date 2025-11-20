import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import Stripe from 'https://esm.sh/stripe@14.21.0?target=deno';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  // Origines autorisées pour les appels frontend
  const allowedOrigins = [
    'https://herbbie.com',
    'https://www.herbbie.com',
    'http://localhost:5173',
    'http://localhost:3000'
  ];
  
  const origin = req.headers.get('origin') || '';
  const corsOrigin = allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': corsOrigin,
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
  };

  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    console.log('=== DEBUT CREATE-PAYMENT ===');
    console.log('Headers reçus:', Object.fromEntries(req.headers.entries()));

    const body = await req.json();
    console.log('Body reçu:', body);

    const { contentType, userId, userEmail, amount, description, successUrl, cancelUrl } = body;

    console.log('Paramètres extraits:', { contentType, userId, userEmail, amount });

    // Validation des paramètres
    if (!contentType || !userId) {
      console.log('ERREUR: Paramètres manquants');
      throw new Error('Paramètres manquants: contentType et userId requis');
    }

    // Initialisation Stripe avec la clé secrète
    const stripeSecretKey = Deno.env.get('STRIPE_SECRET_KEY');
    console.log('Clé Stripe présente:', !!stripeSecretKey);

    if (!stripeSecretKey) {
      console.log('ERREUR: Clé secrète Stripe non configurée');
      throw new Error('Clé secrète Stripe non configurée');
    }

    console.log('Initialisation Stripe...');
    const stripe = new Stripe(stripeSecretKey, {
      apiVersion: '2024-06-20',
      httpClient: Stripe.createFetchHttpClient(),
    });

    // Utiliser le montant calculé côté frontend
    const finalAmount = amount || 49; // 0.49€ par défaut si pas spécifié
    console.log('Montant final:', finalAmount);

    console.log('Création PaymentIntent...');
    // Créer un PaymentIntent pour paiement dans la popup
    const paymentIntent = await stripe.paymentIntents.create({
      amount: finalAmount,
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

    console.log(`✅ PaymentIntent créé pour ${userEmail}: ${paymentIntent.id}, montant: ${finalAmount} centimes`);

    return new Response(JSON.stringify({
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id,
      amount: finalAmount,
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
    console.error('❌ ERREUR dans create-payment:', error);
    console.error('Stack:', error.stack);

    // Retourner 200 avec l'erreur pour que le frontend puisse l'afficher
    // (au lieu de 500 qui est souvent masqué par le client Supabase)
    return new Response(JSON.stringify({
      error: error.message,
      details: error.stack,
      timestamp: new Date().toISOString(),
      success: false
    }), {
      status: 200, 
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }
});
