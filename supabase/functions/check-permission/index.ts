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
    const { contentType, userId, userEmail, selectedDuration, numPages, selectedVoice } = await req.json();

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
      Deno.env.get('SUPABASE_SERVICE_KEY') || Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
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

    // Vérifier si l'utilisateur a un abonnement actif
    const { data: subscription, error: subError } = await supabase
      .from('subscriptions')
      .select(`
        *,
        subscription_plans(*)
      `)
      .eq('user_id', userId)
      .eq('status', 'active')
      .lte('current_period_start', new Date().toISOString())
      .gte('current_period_end', new Date().toISOString())
      .single();

    if (subscription && !subError) {
      // Calculer le coût en tokens selon le type de contenu
      // Basé sur TARIFICATION_HERBBIE.md : 1 token = 0,01€ de coût API
      let tokensRequired = 4; // Par défaut (histoire/audio)

      // Coûts de base selon le type de contenu
      if (contentType === 'histoire' || contentType === 'story' || contentType === 'audio') {
        tokensRequired = 4; // 0,042€ → 4 tokens
      } else if (contentType === 'coloriage') {
        tokensRequired = 16; // 0,16€ → 16 tokens
      } else if (contentType === 'bd' || contentType === 'comic') {
        tokensRequired = 16; // 0,16€ par page → 16 tokens
        // Multiplier par le nombre de pages
        if (numPages && numPages > 0) {
          tokensRequired = tokensRequired * numPages;
        }
      } else if (contentType === 'comptine' || contentType === 'rhyme') {
        tokensRequired = 15; // 0,15€ → 15 tokens
      } else if (contentType === 'animation') {
        // Coûts animations basés sur la durée (Veo 3.1 Fast: 0,14€/seconde)
        const duration = selectedDuration || 30; // durée en secondes
        const costPerSecond = 0.14; // €
        const totalCost = costPerSecond * duration;
        tokensRequired = Math.ceil(totalCost * 100); // Convertir en tokens (1 token = 0,01€)
        
        // Vérification des coûts selon la tarification:
        // 30s: 4,20€ → 420 tokens
        // 60s: 8,40€ → 840 tokens
        // 120s: 16,80€ → 1680 tokens
        // 180s: 25,20€ → 2520 tokens
        // 240s: 33,60€ → 3360 tokens
        // 300s: 42,00€ → 4200 tokens
      }

      // Vérifier si l'utilisateur a assez de tokens
      if (subscription.tokens_remaining >= tokensRequired) {
        return new Response(JSON.stringify({
          hasPermission: true,
          reason: 'subscription_active',
          userRole: 'subscriber',
          subscription: subscription,
          tokensRequired,
          tokensRemaining: subscription.tokens_remaining,
          contentType,
          userId
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } else {
        return new Response(JSON.stringify({
          hasPermission: false,
          reason: 'insufficient_tokens',
          userRole: 'subscriber',
          subscription: subscription,
          tokensRequired,
          tokensRemaining: subscription.tokens_remaining,
          contentType,
          userId
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // Vérifier si l'utilisateur a des tokens payés non expirés
    const { data: userTokens, error: tokensError } = await supabase
      .from('user_tokens')
      .select('*')
      .eq('user_id', userId)
      .is('used_at', null)
      .or('expires_at.is.null,expires_at.gte.' + new Date().toISOString())
      .order('created_at', { ascending: false });

    if (userTokens && userTokens.length > 0) {
      // Calculer le total des tokens disponibles
      const totalTokens = userTokens.reduce((sum, token) => sum + token.tokens_amount, 0);

      // Coût estimé pour pay-per-use (approximation)
      let estimatedTokensCost = 1; // Par défaut
      if (contentType === 'animation') estimatedTokensCost = 10;
      else if (contentType === 'comptine') estimatedTokensCost = 5;
      else if (contentType === 'bd' || contentType === 'comic') estimatedTokensCost = 4;

      if (totalTokens >= estimatedTokensCost) {
        return new Response(JSON.stringify({
          hasPermission: true,
          reason: 'tokens_available',
          userRole: 'user',
          totalTokens,
          estimatedTokensCost,
          contentType,
          userId
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // Aucun abonnement actif et pas d'accès gratuit → paiement requis
    // Le système pay-per-use est géré côté frontend via contentPaidDirectly
    return new Response(JSON.stringify({
      hasPermission: false,
      reason: 'payment_required',
      userRole: 'user',
      estimatedTokensCost,
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
