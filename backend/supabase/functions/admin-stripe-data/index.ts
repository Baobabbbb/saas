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
    // Vérifier l'authentification
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({
        error: 'Authorization header missing'
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
    const { data: { user }, error: authError } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    );

    if (authError || !user) {
      return new Response(JSON.stringify({
        error: 'Invalid authentication'
      }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Vérifier le rôle admin
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single();

    if (profileError || profile?.role !== 'admin') {
      return new Response(JSON.stringify({
        error: 'Admin access required'
      }), {
        status: 403,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const { action, limit = 10, offset = 0 } = await req.json();

    let data, error;

    // Actions autorisées pour les admins
    if (action === 'get_all_payments') {
      ({ data, error } = await supabase.rpc('get_all_stripe_payments_admin', {
        limit_count: limit
      }));
    } else if (action === 'get_payment_stats') {
      // Statistiques basées sur les abonnements actifs
      ({ data, error } = await supabase.rpc('exec_sql', {
        query: `
          SELECT
            COUNT(*) as total_subscriptions,
            SUM(sp.price_monthly) as monthly_revenue,
            AVG(sp.price_monthly) as avg_subscription_price,
            COUNT(DISTINCT s.user_id) as unique_customers
          FROM subscriptions s
          JOIN subscription_plans sp ON s.plan_id = sp.id
          WHERE s.status = 'active'
        `
      }));
    } else if (action === 'get_customers') {
      // Données clients Stripe (via RPC sécurisé)
      ({ data, error } = await supabase.rpc('get_stripe_customers_admin', {
        limit_count: limit
      }));
    } else if (action === 'get_charges') {
      // Données charges Stripe
      ({ data, error } = await supabase.rpc('get_stripe_charges_admin', {
        limit_count: limit
      }));
    } else if (action === 'get_refunds') {
      // Données refunds Stripe
      ({ data, error } = await supabase.rpc('get_stripe_refunds_admin', {
        limit_count: limit
      }));
    } else if (action === 'get_subscriptions') {
      // Données subscriptions Stripe
      ({ data, error } = await supabase.rpc('get_stripe_subscriptions_admin', {
        limit_count: limit
      }));
    } else if (action === 'get_invoices') {
      // Données invoices Stripe
      ({ data, error } = await supabase.rpc('get_stripe_invoices_admin', {
        limit_count: limit
      }));
    } else if (action === 'get_products') {
      // Données products Stripe
      ({ data, error } = await supabase.rpc('get_stripe_products_admin', {
        limit_count: limit
      }));
    } else if (action === 'get_prices') {
      // Données prices Stripe
      ({ data, error } = await supabase.rpc('get_stripe_prices_admin', {
        limit_count: limit
      }));
    } else {
      return new Response(JSON.stringify({
        error: 'Action not allowed',
        allowedActions: [
          'get_all_payments', 'get_payment_stats', 'get_customers',
          'get_charges', 'get_refunds', 'get_subscriptions',
          'get_invoices', 'get_products', 'get_prices'
        ]
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (error) {
      console.error('Database error:', error);
      return new Response(JSON.stringify({
        error: 'Database query failed',
        details: error.message
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({
      success: true,
      data: data || [],
      meta: {
        limit: parseInt(limit),
        offset: parseInt(offset),
        action: action
      }
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Edge Function error:', error);
    return new Response(JSON.stringify({
      error: error.message,
      details: error.stack
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
