import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import Stripe from 'https://esm.sh/stripe@14.21.0?target=deno';

serve(async (req) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
  };

  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const { action, userId, planId, paymentMethodId, userEmail } = await req.json();

    if (!userId || !action) {
      return new Response(JSON.stringify({
        success: false,
        error: 'userId et action requis'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL'),
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    );

    const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY'), {
      apiVersion: '2023-10-16',
    });

    switch (action) {
      case 'create_subscription': {
        if (!planId || !paymentMethodId || !userEmail) {
          return new Response(JSON.stringify({
            success: false,
            error: 'planId, paymentMethodId et userEmail requis pour créer un abonnement'
          }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Récupérer les détails du plan
        const { data: plan, error: planError } = await supabase
          .from('subscription_plans')
          .select('*')
          .eq('id', planId)
          .single();

        if (planError || !plan) {
          return new Response(JSON.stringify({
            success: false,
            error: 'Plan d\'abonnement introuvable'
          }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Vérifier si l'utilisateur a déjà un abonnement actif
        const { data: existingSub } = await supabase
          .from('subscriptions')
          .select('id, status')
          .eq('user_id', userId)
          .eq('status', 'active')
          .single();

        if (existingSub) {
          return new Response(JSON.stringify({
            success: false,
            error: 'Utilisateur a déjà un abonnement actif'
          }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Créer ou récupérer le customer Stripe
        let customer;
        const { data: existingCustomer } = await supabase
          .from('subscriptions')
          .select('stripe_customer_id')
          .eq('user_id', userId)
          .neq('stripe_customer_id', null)
          .limit(1)
          .single();

        if (existingCustomer?.stripe_customer_id) {
          customer = await stripe.customers.retrieve(existingCustomer.stripe_customer_id);
        } else {
          customer = await stripe.customers.create({
            email: userEmail,
            payment_method: paymentMethodId,
            invoice_settings: {
              default_payment_method: paymentMethodId,
            },
          });
        }

        // Créer l'abonnement Stripe
        const subscription = await stripe.subscriptions.create({
          customer: customer.id,
          items: [{
            price_data: {
              currency: 'eur',
              product_data: {
                name: plan.name,
                description: plan.description,
              },
              unit_amount: plan.price_monthly,
              recurring: {
                interval: 'month',
              },
            },
          }],
          payment_behavior: 'default_incomplete',
          expand: ['latest_invoice.payment_intent'],
        });

        // Créer l'abonnement dans notre base
        const { data: newSubscription, error: subError } = await supabase
          .from('subscriptions')
          .insert({
            user_id: userId,
            plan_id: planId,
            stripe_subscription_id: subscription.id,
            stripe_customer_id: customer.id,
            status: subscription.status,
            current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
            current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
            tokens_remaining: plan.tokens_allocated,
            tokens_used_this_month: 0,
          })
          .select()
          .single();

        if (subError) {
          console.error('Erreur création abonnement:', subError);
          return new Response(JSON.stringify({
            success: false,
            error: 'Erreur lors de la création de l\'abonnement'
          }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        return new Response(JSON.stringify({
          success: true,
          subscription: newSubscription,
          stripeSubscription: subscription,
          clientSecret: subscription.latest_invoice.payment_intent?.client_secret
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      case 'cancel_subscription': {
        // Récupérer l'abonnement actif de l'utilisateur
        const { data: subscription, error: subError } = await supabase
          .from('subscriptions')
          .select('id, stripe_subscription_id, status')
          .eq('user_id', userId)
          .eq('status', 'active')
          .single();

        if (subError || !subscription) {
          return new Response(JSON.stringify({
            success: false,
            error: 'Aucun abonnement actif trouvé'
          }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Annuler l'abonnement Stripe (à la fin de la période)
        await stripe.subscriptions.update(subscription.stripe_subscription_id, {
          cancel_at_period_end: true,
        });

        // Mettre à jour notre base
        const { error: updateError } = await supabase
          .from('subscriptions')
          .update({
            cancel_at_period_end: true,
            updated_at: new Date().toISOString()
          })
          .eq('id', subscription.id);

        if (updateError) {
          console.error('Erreur mise à jour abonnement:', updateError);
        }

        return new Response(JSON.stringify({
          success: true,
          message: 'Abonnement annulé à la fin de la période'
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      case 'get_subscription': {
        const { data: subscription, error: subError } = await supabase
          .from('subscriptions')
          .select(`
            *,
            subscription_plans(*)
          `)
          .eq('user_id', userId)
          .eq('status', 'active')
          .single();

        if (subError || !subscription) {
          return new Response(JSON.stringify({
            success: true,
            subscription: null
          }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        return new Response(JSON.stringify({
          success: true,
          subscription: subscription
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      case 'get_plans': {
        const { data: plans, error: plansError } = await supabase
          .from('subscription_plans')
          .select('*')
          .eq('is_active', true)
          .order('price_monthly', { ascending: true });

        if (plansError) {
          return new Response(JSON.stringify({
            success: false,
            error: 'Erreur lors de la récupération des plans'
          }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        return new Response(JSON.stringify({
          success: true,
          plans: plans
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      default:
        return new Response(JSON.stringify({
          success: false,
          error: 'Action non reconnue'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }

  } catch (error) {
    console.error('Erreur dans manage-subscription:', error);
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
