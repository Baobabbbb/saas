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
    const { contentType, userId, userEmail } = await req.json();

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

    // Vérifier les permissions payées actives
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
