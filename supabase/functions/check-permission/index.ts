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
    // Parser le body JSON avec gestion d'erreur
    let requestBody;
    try {
      requestBody = await req.json();
    } catch (jsonError) {
      console.error('Erreur parsing JSON:', jsonError);
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'invalid_json',
        error: 'Erreur lors du parsing du body JSON'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
    
    let { contentType, userId, userEmail, selectedDuration, numPages, selectedVoice } = requestBody;

    if (!contentType) {
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'missing_parameters',
        error: 'contentType requis'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Vérifier les variables d'environnement
    // Les Edge Functions Supabase ont accès par défaut à SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY
    const supabaseUrl = Deno.env.get('SUPABASE_URL');
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || Deno.env.get('SUPABASE_SERVICE_KEY');
    
    if (!supabaseUrl || !supabaseServiceKey) {
      console.error('Variables d\'environnement manquantes:', {
        hasUrl: !!supabaseUrl,
        hasKey: !!supabaseServiceKey,
        urlValue: supabaseUrl ? 'present' : 'missing',
        keyValue: supabaseServiceKey ? 'present' : 'missing'
      });
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'configuration_error',
        error: 'Configuration Supabase manquante',
        debug: {
          hasUrl: !!supabaseUrl,
          hasKey: !!supabaseServiceKey
        }
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    let supabase;
    try {
      supabase = createClient(supabaseUrl, supabaseServiceKey);
    } catch (clientError) {
      console.error('Erreur création client Supabase:', clientError);
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'client_error',
        error: 'Erreur lors de la création du client Supabase',
        details: clientError instanceof Error ? clientError.message : String(clientError)
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Vérifier l'authentification JWT via Supabase
    const authHeader = req.headers.get('Authorization') || req.headers.get('authorization') || '';
    if (!authHeader.startsWith('Bearer ')) {
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'unauthorized',
        error: 'Authorization header manquant'
      }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const jwt = authHeader.replace('Bearer ', '').trim();
    const { data: authData, error: authError } = await supabase.auth.getUser(jwt);

    if (authError || !authData?.user?.id) {
      console.error('Erreur validation JWT:', authError);
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'unauthorized',
        error: 'JWT invalide ou expiré'
      }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Forcer l'utilisation du user_id issu du JWT
    const tokenUserId = authData.user.id;
    if (userId && userId !== tokenUserId) {
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'user_mismatch',
        error: 'userId ne correspond pas au token',
        userIdReceived: userId
      }), {
        status: 403,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    userId = tokenUserId;

    // Vérifier le rôle utilisateur
    let profile, profileError;
    try {
      const result = await supabase
        .from('profiles')
        .select('role')
        .eq('id', userId)
        .single();
      profile = result.data;
      profileError = result.error;
    } catch (queryError) {
      console.error('Erreur exception lors de la requête profil:', queryError);
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'query_exception',
        error: 'Exception lors de la requête profil',
        details: queryError instanceof Error ? queryError.message : String(queryError)
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (profileError) {
      console.error('Erreur récupération profil:', profileError);
      return new Response(JSON.stringify({
        hasPermission: false,
        reason: 'profile_error',
        error: 'Erreur lors de la récupération du profil',
        details: profileError.message || String(profileError),
        code: profileError.code,
        hint: profileError.hint
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
        tokensRequired = 13; // 0,13€ → 13 tokens
      } else if (contentType === 'bd' || contentType === 'comic') {
        tokensRequired = 13; // 0,13€ par page → 13 tokens
        // Multiplier par le nombre de pages
        if (numPages && numPages > 0) {
          tokensRequired = tokensRequired * numPages;
        }
      } else if (contentType === 'comptine' || contentType === 'rhyme') {
        tokensRequired = 15; // 0,15€ → 15 tokens
      } else if (contentType === 'animation') {
        // Coûts animations basés sur la durée (WaveSpeed WAN 2.5 Fast 1080p: 0,102$/s ~0,102€/s)
        const duration = selectedDuration || 30; // durée en secondes
        const costPerSecond = 0.102; // €
        const totalCost = costPerSecond * duration;
        tokensRequired = Math.ceil(totalCost * 100); // Convertir en tokens (1 token = 0,01€)
        
        // Vérification des coûts selon la tarification WAN 2.5 1080p:
        // 30s: 3,06€ → 306 tokens
        // 60s: 6,12€ → 612 tokens
        // 120s: 12,24€ → 1224 tokens
        // 180s: 18,36€ → 1836 tokens
        // 240s: 24,48€ → 2448 tokens
        // 300s: 30,60€ → 3060 tokens
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

    // Coût estimé pour pay-per-use (approximation) - déclaré avant le bloc conditionnel
    let estimatedTokensCost = 1; // Par défaut
    if (contentType === 'animation') estimatedTokensCost = 10;
    else if (contentType === 'comptine') estimatedTokensCost = 5;
    else if (contentType === 'bd' || contentType === 'comic') estimatedTokensCost = 4;

    if (userTokens && userTokens.length > 0) {
      // Calculer le total des tokens disponibles
      const totalTokens = userTokens.reduce((sum, token) => sum + token.tokens_amount, 0);

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
    const errorMessage = error instanceof Error ? error.message : String(error);
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    return new Response(JSON.stringify({
      hasPermission: false,
      reason: 'error',
      error: errorMessage,
      stack: errorStack
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
