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

    // Vérifier si l'utilisateur a un abonnement actif
    const { data: subscription, error: subError } = await supabase
      .from('subscriptions')
      .select(`
        *,
        subscription_plans!inner(*),
        token_costs!inner(content_type, tokens_required)
      `)
      .eq('user_id', userId)
      .eq('status', 'active')
      .eq('token_costs.content_type', contentType)
      .lte('current_period_start', new Date().toISOString())
      .gte('current_period_end', new Date().toISOString())
      .single();

    if (subscription && !subError) {
      // Calculer le coût en tokens selon le contenu
      let tokensRequired = subscription.token_costs[0]?.tokens_required || 1;

      // Ajustements pour les animations selon la durée
      if (contentType === 'animation') {
        const duration = selectedDuration || 30; // durée en secondes
        if (duration === 60) tokensRequired = Math.ceil(tokensRequired * 1.5);
        else if (duration === 120) tokensRequired = Math.ceil(tokensRequired * 2.5);
        else if (duration === 180) tokensRequired = Math.ceil(tokensRequired * 4);
        else if (duration === 240) tokensRequired = Math.ceil(tokensRequired * 5);
        else if (duration === 300) tokensRequired = Math.ceil(tokensRequired * 6);
      }

      // Ajustements pour les BD selon le nombre de pages
      if ((contentType === 'bd' || contentType === 'comic') && numPages) {
        tokensRequired = tokensRequired * numPages;
      }

      // Ajustements pour les histoires avec audio
      // Si l'utilisateur choisit une voix, c'est une histoire audio qui coûte plus cher
      if ((contentType === 'histoire' || contentType === 'story') && selectedVoice && (selectedVoice === 'female' || selectedVoice === 'male')) {
        // Histoire audio coûte légèrement plus que histoire texte
        // On utilise le coût de 'audio' si disponible, sinon on garde le coût histoire
        const { data: audioCost } = await supabase
          .from('token_costs')
          .select('tokens_required')
          .eq('plan_id', subscription.plan_id)
          .eq('content_type', 'audio')
          .single();
        
        if (audioCost) {
          tokensRequired = audioCost.tokens_required;
        }
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

    // Vérifier les permissions payées actives (système legacy)
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
