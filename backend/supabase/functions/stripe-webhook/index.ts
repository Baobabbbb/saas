import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import Stripe from 'https://esm.sh/stripe@14.21.0?target=deno';

serve(async (req) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
  };

  try {
    const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY'), {
      apiVersion: '2023-10-16',
    });

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL'),
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    );

    const body = await req.text();
    const sig = req.headers.get('stripe-signature');

    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(body, sig, Deno.env.get('STRIPE_WEBHOOK_SECRET'));
    } catch (err) {
      console.error('Erreur vérification webhook:', err);
      return new Response('Webhook signature verification failed', { status: 400 });
    }

    console.log('Événement Stripe reçu:', event.type);

    switch (event.type) {
      case 'customer.subscription.created':
      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;

        // Mettre à jour l'abonnement dans notre base
        const { error } = await supabase
          .from('subscriptions')
          .update({
            status: subscription.status,
            current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
            current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
            cancel_at_period_end: subscription.cancel_at_period_end,
            updated_at: new Date().toISOString()
          })
          .eq('stripe_subscription_id', subscription.id);

        if (error) {
          console.error('Erreur mise à jour abonnement:', error);
        } else {
          console.log('Abonnement mis à jour:', subscription.id);
        }
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;

        // Désactiver l'abonnement dans notre base
        const { error } = await supabase
          .from('subscriptions')
          .update({
            status: 'canceled',
            updated_at: new Date().toISOString()
          })
          .eq('stripe_subscription_id', subscription.id);

        if (error) {
          console.error('Erreur désactivation abonnement:', error);
        } else {
          console.log('Abonnement désactivé:', subscription.id);
        }
        break;
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object as Stripe.Invoice;

        if (invoice.subscription) {
          // Renouvellement d'abonnement réussi - remettre les tokens
          const { data: subscription, error: subError } = await supabase
            .from('subscriptions')
            .select('id, plan_id, tokens_used_this_month, subscription_plans(tokens_allocated)')
            .eq('stripe_subscription_id', invoice.subscription)
            .single();

          if (!subError && subscription) {
            const tokensAllocated = subscription.subscription_plans.tokens_allocated;
            const tokensUsed = subscription.tokens_used_this_month;

            // Calculer les tokens restants (conserver les tokens non utilisés + nouveaux tokens)
            const { data: currentSub } = await supabase
              .from('subscriptions')
              .select('tokens_remaining')
              .eq('id', subscription.id)
              .single();

            const newTokensRemaining = (currentSub?.tokens_remaining || 0) - tokensUsed + tokensAllocated;

            // Mettre à jour l'abonnement
            const { error: updateError } = await supabase
              .from('subscriptions')
              .update({
                tokens_remaining: Math.max(0, newTokensRemaining), // Ne pas aller en négatif
                tokens_used_this_month: 0, // Reset du compteur
                status: 'active',
                updated_at: new Date().toISOString()
              })
              .eq('id', subscription.id);

            if (updateError) {
              console.error('Erreur mise à jour tokens renouvellement:', updateError);
            } else {
              console.log('Tokens renouvelés pour abonnement:', subscription.id);
            }

            // Enregistrer la transaction de renouvellement
            await supabase
              .from('user_tokens')
              .insert({
                user_id: subscription.user_id,
                tokens_amount: tokensAllocated,
                transaction_type: 'subscription_renewal',
                subscription_id: subscription.id,
                stripe_payment_id: invoice.payment_intent,
                metadata: {
                  invoice_id: invoice.id,
                  period_start: invoice.period_start,
                  period_end: invoice.period_end
                }
              });
          }
        }
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice;

        // Marquer l'abonnement comme en défaut de paiement
        if (invoice.subscription) {
          const { error } = await supabase
            .from('subscriptions')
            .update({
              status: 'past_due',
              updated_at: new Date().toISOString()
            })
            .eq('stripe_subscription_id', invoice.subscription);

          if (error) {
            console.error('Erreur mise à jour statut abonnement:', error);
          } else {
            console.log('Abonnement marqué en défaut de paiement:', invoice.subscription);
          }
        }
        break;
      }

      case 'payment_intent.succeeded': {
        const paymentIntent = event.data.object as Stripe.PaymentIntent;

        // Traiter les paiements directs de contenus (pas d'abonnement)
        if (paymentIntent.metadata?.contentType && paymentIntent.metadata?.userId) {
          const userId = paymentIntent.metadata.userId;
          const contentType = paymentIntent.metadata.contentType;
          const amount = paymentIntent.amount; // en centimes

          console.log(`Paiement réussi pour ${userId}: ${amount} centimes, type: ${contentType}`);

          // Le contenu est déjà payé, pas besoin de déduire des tokens
          // L'utilisateur peut générer le contenu sans passer par le système de tokens
          // On enregistre juste la transaction pour historique
          const { error } = await supabase
            .from('payments')
            .insert({
              user_id: userId,
              amount: amount,
              currency: 'eur',
              status: 'succeeded',
              stripe_payment_intent_id: paymentIntent.id,
              content_type: contentType,
              metadata: paymentIntent.metadata,
              created_at: new Date().toISOString()
            });

          if (error) {
            console.error('Erreur enregistrement paiement:', error);
          } else {
            console.log('Paiement enregistré pour utilisateur:', userId);
          }
        }
        break;
      }

      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;

        // Traiter les achats de tokens ponctuels
        if (session.metadata?.type === 'token_purchase') {
          const userId = session.metadata.user_id;
          const tokensAmount = parseInt(session.metadata.tokens_amount);

          if (userId && tokensAmount) {
            // Ajouter les tokens à l'utilisateur
            const { error } = await supabase
              .from('user_tokens')
              .insert({
                user_id: userId,
                tokens_amount: tokensAmount,
                transaction_type: 'purchase',
                stripe_payment_id: session.payment_intent,
                expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 an
                metadata: {
                  session_id: session.id,
                  amount_paid: session.amount_total
                }
              });

            if (error) {
              console.error('Erreur ajout tokens:', error);
            } else {
              console.log('Tokens ajoutés pour utilisateur:', userId);
            }
          }
        }
        break;
      }

      default:
        console.log('Événement non traité:', event.type);
    }

    return new Response(JSON.stringify({ received: true }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Erreur webhook Stripe:', error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
