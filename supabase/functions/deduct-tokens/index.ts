import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
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
    // Parser le body JSON avec gestion d'erreurs
    let requestBody;
    try {
      requestBody = await req.json();
    } catch (jsonError) {
      console.error('Erreur parsing JSON:', jsonError);
      return new Response(JSON.stringify({
        success: false,
        error: 'Erreur lors du parsing du body JSON',
        details: jsonError instanceof Error ? jsonError.message : String(jsonError)
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const {
      userId,
      contentType,
      tokensUsed,
      selectedDuration,
      numPages,
      selectedVoice,
      transactionId
    } = requestBody;

    console.log('[DEBUG deduct-tokens] Paramètres reçus:', {
      userId: userId ? 'présent' : 'manquant',
      contentType: contentType ? 'présent' : 'manquant',
      tokensUsed: tokensUsed !== undefined ? `présent (${tokensUsed})` : 'manquant',
      selectedDuration,
      numPages,
      selectedVoice,
      transactionId
    });

    if (!userId || !contentType || tokensUsed === undefined || tokensUsed === null) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Paramètres requis manquants: userId, contentType, tokensUsed',
        received: {
          hasUserId: !!userId,
          hasContentType: !!contentType,
          hasTokensUsed: tokensUsed !== undefined && tokensUsed !== null,
          tokensUsedValue: tokensUsed
        }
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Utiliser SUPABASE_SERVICE_KEY avec fallback sur SUPABASE_SERVICE_ROLE_KEY
    const supabaseUrl = Deno.env.get('SUPABASE_URL');
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_KEY') || Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    
    if (!supabaseUrl || !supabaseServiceKey) {
      console.error('Variables d\'environnement manquantes:', {
        hasUrl: !!supabaseUrl,
        hasKey: !!supabaseServiceKey
      });
      return new Response(JSON.stringify({
        success: false,
        error: 'Configuration Supabase manquante'
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Vérifier si l'utilisateur a un abonnement actif
    const { data: subscription, error: subError } = await supabase
      .from('subscriptions')
      .select('id, tokens_remaining, tokens_used_this_month, status')
      .eq('user_id', userId)
      .eq('status', 'active')
      .single();

    if (subscription && !subError) {
      // Déduire les tokens de l'abonnement
      const newTokensRemaining = subscription.tokens_remaining - tokensUsed;
      const newTokensUsed = subscription.tokens_used_this_month + tokensUsed;

      if (newTokensRemaining < 0) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Tokens insuffisants dans l\'abonnement'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Mettre à jour l'abonnement
      const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
          tokens_remaining: newTokensRemaining,
          tokens_used_this_month: newTokensUsed,
          updated_at: new Date().toISOString()
        })
        .eq('id', subscription.id);

      if (updateError) {
        console.error('Erreur mise à jour abonnement:', updateError);
        return new Response(JSON.stringify({
          success: false,
          error: 'Erreur lors de la mise à jour de l\'abonnement'
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Enregistrer la transaction
      const { error: transactionError } = await supabase
        .from('user_tokens')
        .insert({
          user_id: userId,
          tokens_amount: -tokensUsed,
          transaction_type: 'usage',
          subscription_id: subscription.id,
          metadata: {
            contentType,
            selectedDuration,
            numPages,
            selectedVoice,
            transactionId
          }
        });

      if (transactionError) {
        console.error('Erreur enregistrement transaction:', transactionError);
      }

      return new Response(JSON.stringify({
        success: true,
        type: 'subscription',
        tokensDeducted: tokensUsed,
        tokensRemaining: newTokensRemaining,
        subscription: subscription
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } else {
      // Déduire des tokens payés
      const { data: userTokens, error: tokensError } = await supabase
        .from('user_tokens')
        .select('id, tokens_amount')
        .eq('user_id', userId)
        .is('used_at', null)
        .or('expires_at.is.null,expires_at.gte.' + new Date().toISOString())
        .order('created_at', { ascending: true }); // FIFO

      if (tokensError) {
        console.error('[DEBUG deduct-tokens] Erreur récupération tokens:', tokensError);
        return new Response(JSON.stringify({
          success: false,
          error: 'Erreur lors de la récupération des tokens',
          details: tokensError.message || String(tokensError)
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
      
      if (!userTokens || userTokens.length === 0) {
        // Si l'utilisateur n'a pas de tokens, retourner succès (pay-per-use)
        // Ne pas logger pour éviter le bruit dans les logs
        return new Response(JSON.stringify({
          success: true,
          type: 'no_tokens',
          message: 'Aucun token disponible (pay-per-use)',
          tokensDeducted: 0,
          tokensRemaining: 0,
          silent: true
        }), {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Calculer le total des tokens disponibles
      let totalTokens = 0;
      const tokenEntries = userTokens.map(token => ({
        id: token.id,
        amount: token.tokens_amount,
        remaining: token.tokens_amount
      }));

      totalTokens = tokenEntries.reduce((sum, token) => sum + token.amount, 0);

      if (totalTokens < tokensUsed) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Tokens insuffisants'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Déduire les tokens (FIFO)
      let remainingToDeduct = tokensUsed;
      const tokensToUpdate = [];

      for (const token of tokenEntries) {
        if (remainingToDeduct <= 0) break;

        if (token.remaining >= remainingToDeduct) {
          // Utiliser partiellement ce token
          token.remaining -= remainingToDeduct;
          tokensToUpdate.push({
            id: token.id,
            newAmount: token.remaining,
            used: remainingToDeduct
          });
          remainingToDeduct = 0;
        } else {
          // Utiliser complètement ce token
          tokensToUpdate.push({
            id: token.id,
            newAmount: 0,
            used: token.remaining
          });
          remainingToDeduct -= token.remaining;
          token.remaining = 0;
        }
      }

      // Mettre à jour les tokens dans la base
      for (const tokenUpdate of tokensToUpdate) {
        if (tokenUpdate.newAmount === 0) {
          // Marquer comme utilisé
          await supabase
            .from('user_tokens')
            .update({
              used_at: new Date().toISOString(),
              tokens_amount: tokenUpdate.used // Garder le montant utilisé
            })
            .eq('id', tokenUpdate.id);
        } else {
          // Mettre à jour le montant restant
          await supabase
            .from('user_tokens')
            .update({
              tokens_amount: tokenUpdate.newAmount,
              updated_at: new Date().toISOString()
            })
            .eq('id', tokenUpdate.id);
        }
      }

      // Enregistrer la transaction globale
      const { error: transactionError } = await supabase
        .from('user_tokens')
        .insert({
          user_id: userId,
          tokens_amount: -tokensUsed,
          transaction_type: 'usage',
          metadata: {
            contentType,
            selectedDuration,
            numPages,
            selectedVoice,
            transactionId,
            tokensDeducted: tokensToUpdate
          }
        });

      if (transactionError) {
        console.error('Erreur enregistrement transaction:', transactionError);
      }

      // Calculer les tokens restants
      const newTotalTokens = totalTokens - tokensUsed;

      return new Response(JSON.stringify({
        success: true,
        type: 'tokens',
        tokensDeducted: tokensUsed,
        tokensRemaining: newTotalTokens,
        tokensUsed: tokensToUpdate
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

  } catch (error) {
    console.error('Erreur dans deduct-tokens:', error);
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
