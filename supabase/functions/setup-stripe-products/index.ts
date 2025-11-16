import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import Stripe from 'https://esm.sh/stripe@14.21.0?target=deno';

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
    // Vérifier l'authentification (seulement admin)
    const authHeader = req.headers.get('authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Authentification requise'
      }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL'),
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    );

    // Vérifier que l'utilisateur est admin
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error: userError } = await supabase.auth.getUser(token);

    if (userError || !user) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Utilisateur non authentifié'
      }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single();

    if (profile?.role !== 'admin') {
      return new Response(JSON.stringify({
        success: false,
        error: 'Accès réservé aux administrateurs'
      }), {
        status: 403,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY'), {
      apiVersion: '2023-10-16',
    });

    // Récupérer les plans depuis Supabase
    const { data: plans, error: plansError } = await supabase
      .from('subscription_plans')
      .select('*')
      .eq('is_active', true)
      .order('price_monthly', { ascending: true });

    if (plansError) {
      throw new Error(`Erreur récupération plans: ${plansError.message}`);
    }

    const results = [];

    // Créer ou mettre à jour les produits et prix Stripe
    for (const plan of plans) {
      try {
        // Chercher si un produit existe déjà
        const products = await stripe.products.search({
          query: `name:'${plan.name}' AND active:'true'`,
        });

        let product;
        if (products.data.length > 0) {
          product = products.data[0];
          console.log(`Produit existant trouvé: ${plan.name}`);
        } else {
          // Créer le produit Stripe
          product = await stripe.products.create({
            name: plan.name,
            description: plan.description || `Abonnement ${plan.name} - ${plan.tokens_allocated} tokens/mois`,
            metadata: {
              plan_id: plan.id.toString(),
              tokens_allocated: plan.tokens_allocated.toString()
            }
          });
          console.log(`Produit créé: ${plan.name}`);
        }

        // Créer le prix récurrent
        const price = await stripe.prices.create({
          product: product.id,
          unit_amount: plan.price_monthly,
          currency: 'eur',
          recurring: {
            interval: 'month',
          },
          metadata: {
            plan_id: plan.id.toString()
          }
        });

        console.log(`Prix créé pour ${plan.name}: ${price.id}`);

        // Mettre à jour le plan dans Supabase avec le stripe_price_id
        const { error: updateError } = await supabase
          .from('subscription_plans')
          .update({
            stripe_price_id: price.id,
            updated_at: new Date().toISOString()
          })
          .eq('id', plan.id);

        if (updateError) {
          console.error(`Erreur mise à jour plan ${plan.name}:`, updateError);
        }

        results.push({
          plan: plan.name,
          product_id: product.id,
          price_id: price.id,
          amount: plan.price_monthly,
          success: true
        });

      } catch (error) {
        console.error(`Erreur pour le plan ${plan.name}:`, error);
        results.push({
          plan: plan.name,
          success: false,
          error: error.message
        });
      }
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'Configuration Stripe terminée',
      results: results
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Erreur setup-stripe-products:', error);
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});

