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
    const { contentType, userId, userEmail, amount, description, successUrl, cancelUrl } = await req.json();

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

    // Utiliser le montant calculé côté frontend
    const finalAmount = amount || 49; // 0.49€ par défaut si pas spécifié

    // Créer une session Stripe Checkout
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'eur',
            product_data: {
              name: description || 'Contenu Herbbie',
              description: `Création de contenu personnalisé - ${contentType}`,
            },
            unit_amount: finalAmount,
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: successUrl || `${req.headers.get('origin')}?payment=success`,
      cancel_url: cancelUrl || `${req.headers.get('origin')}?payment=cancelled`,
      customer_email: userEmail,
      metadata: {
        contentType,
        userId,
        userEmail,
      },
    });

    console.log(`Checkout Session créée pour ${userEmail}: ${session.id}, montant: ${finalAmount} centimes`);

    return new Response(JSON.stringify({
      url: session.url,
      session_id: session.id,
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
