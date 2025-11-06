import { supabase } from '../supabaseClient'

// Vérifier si l'utilisateur a la permission (admin, abonnement ou payé)
export const checkPaymentPermission = async (contentType, userId, userEmail, options = {}) => {
  try {
    // Simulation temporaire basée sur l'email
    if (userEmail === 'fredagathe77@gmail.com') {
      return {
        hasPermission: true,
        reason: 'admin_access',
        userRole: 'admin',
        isAdmin: true
      }
    }

    // Pour les autres utilisateurs, vérifier dans la vraie table profiles
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', userId)
      .single()

    if (profileError) {
      // Erreur silencieuse - pas critique pour la vérification
    }

    if (profile?.role === 'admin' || profile?.role === 'free') {
      return {
        hasPermission: true,
        reason: profile?.role === 'admin' ? 'admin_access' : 'free_access',
        userRole: profile?.role,
        isAdmin: profile?.role === 'admin'
      }
    }

    // Utiliser la nouvelle fonction Edge pour vérifier les permissions avec tokens
    const { data: permissionData, error: permError } = await supabase.functions.invoke('check-permission', {
      body: {
        contentType,
        userId,
        userEmail,
        selectedDuration: options.duration,
        numPages: options.pages,
        selectedVoice: options.voice
      }
    });

    if (permError) {
      console.error('Erreur check-permission:', permError);
      return {
        hasPermission: false,
        reason: 'error',
        error: permError,
        isAdmin: false
      };
    }

    return {
      ...permissionData,
      isAdmin: false
    };

  } catch (error) {
    return { hasPermission: false, reason: 'error', error, isAdmin: false }
  }
}

// Créer une session de paiement (seulement pour les non-admins)
export const createPaymentSession = async (contentType, userId, userEmail, options = {}) => {
  try {
    // NORMALISATION: Toujours utiliser 'histoire' au lieu de 'audio'
    const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
    
    // Calculer le prix selon les options
    const priceInfo = getContentPrice(normalizedContentType, options)

    const { data, error } = await supabase.functions.invoke('create-payment', {
      body: {
        contentType,
        userId,
        userEmail,
        amount: priceInfo.amount,
        selectedDuration: options.duration,
        numPages: options.pages,
        selectedVoice: options.voice
      }
    })

    if (error) throw error
    return data

  } catch (error) {
    throw error
  }
}

// Obtenir le prix d'un contenu
export const getContentPrice = (contentType, options = {}) => {

  const prices = {
    // NOUVEAUX PRIX 2025-11-06 : Plus accessibles !
    'comptine': { amount: 99, name: 'Comptine Musicale', currency: 'EUR', display: '0,99€' },
    'histoire': { amount: 50, name: 'Histoire', currency: 'EUR', display: '0,50€' },
    'audio': { amount: 50, name: 'Histoire', currency: 'EUR', display: '0,50€' },
    'coloriage': { amount: 99, name: 'Coloriage Personnalisé', currency: 'EUR', display: '0,99€' },
    'coloring': { amount: 99, name: 'Coloriage personnalisé', currency: 'EUR', display: '0,99€' },
    'bd': { amount: 99, name: 'Page de Bande Dessinée', currency: 'EUR', display: '0,99€' },
    'comic': { amount: 99, name: 'Page de Bande Dessinée', currency: 'EUR', display: '0,99€' },
    'story': { amount: 50, name: 'Histoire', currency: 'EUR', display: '0,50€' },
    'rhyme': { amount: 99, name: 'Comptine musicale', currency: 'EUR', display: '0,99€' },

    // Animations avec marges réduites (prix attractifs)
    'animation': { amount: 599, name: 'Animation IA 30s', currency: 'EUR', display: '5,99€' }
  }

  // Gestion spéciale pour les histoires (prix unique : 0,50€)
  if (contentType === 'histoire' || contentType === 'story' || contentType === 'audio') {
    return {
      amount: 50,
      name: 'Histoire',
      currency: 'EUR',
      display: '0,50€'
    }
  }

  // Gestion spéciale pour les animations selon la durée (PRIX RÉDUITS 2025-11-06)
  if (contentType === 'animation' && options.duration) {
              const durationPrices = {
                30: { amount: 599, name: 'Animation IA 30s', display: '5,99€' },
                60: { amount: 999, name: 'Animation IA 1min', display: '9,99€' },
                120: { amount: 1899, name: 'Animation IA 2min', display: '18,99€' },
                180: { amount: 2799, name: 'Animation IA 3min', display: '27,99€' },
                240: { amount: 3699, name: 'Animation IA 4min', display: '36,99€' },
                300: { amount: 4699, name: 'Animation IA 5min', display: '46,99€' }
              }

    const durationKey = options.duration
    if (durationPrices[durationKey]) {
      return {
        ...prices[contentType],
        ...durationPrices[durationKey],
        currency: 'EUR'
      }
    }
  }

  // Gestion spéciale pour les BD selon le nombre de pages
  if ((contentType === 'bd' || contentType === 'comic') && options.pages) {
    const baseAmount = prices[contentType].amount
    const totalAmount = baseAmount * options.pages
    const displayPrice = (totalAmount / 100).toFixed(2).replace('.', ',') + '€'

    return {
      ...prices[contentType],
      amount: totalAmount,
      name: `${options.pages} page${options.pages > 1 ? 's' : ''} de Bande Dessinée`,
      display: displayPrice
    }
  }

  return prices[contentType] || { amount: 149, name: 'Contenu Créatif', currency: 'EUR', display: '1,49€' }
}

// Fonction pour vérifier rapidement si l'utilisateur a accès gratuit (admin ou free)
export const hasFreeAccess = async (userId, userEmail) => {
  try {
    // Vérification rapide par email d'abord
    if (userEmail === 'fredagathe77@gmail.com') {
      return true
    }

    // Vérification dans la table profiles
    const { data: profile, error } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', userId)
      .single()

    if (error) {
      return false
    }

    return profile?.role === 'admin' || profile?.role === 'free'

  } catch (error) {
    return false
  }
}

// Obtenir le rôle de l'utilisateur depuis la table profiles
export const getUserRole = async (userId) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', userId)
      .single()
    
    return data?.role || 'user'
    
  } catch (error) {
    return 'user'
  }
}

// Marquer une permission comme accordée après paiement réussi
export const grantPermission = async (userId, contentType, paymentIntentId, amount) => {
  try {
    const { data, error } = await supabase
      .from('generation_permissions')
      .upsert({
        user_id: userId,
        content_type: contentType,
        stripe_payment_intent_id: paymentIntentId,
        amount: amount,
        status: 'completed',
        created_at: new Date().toISOString()
      })

    if (error) throw error
    return data

  } catch (error) {
    throw error
  }
}

// ==========================================
// FONCTIONS ABONNEMENTS ET TOKENS
// ==========================================

// Obtenir tous les plans d'abonnement disponibles
export const getSubscriptionPlans = async () => {
  try {
    const { data, error } = await supabase.functions.invoke('manage-subscription', {
      body: { action: 'get_plans' }
    });

    if (error) throw error;
    return data.plans || [];
  } catch (error) {
    console.error('Erreur récupération plans:', error);
    return [];
  }
};

// Obtenir l'abonnement actif de l'utilisateur
export const getUserSubscription = async (userId) => {
  try {
    const { data, error } = await supabase.functions.invoke('manage-subscription', {
      body: { action: 'get_subscription', userId }
    });

    if (error) throw error;
    return data.subscription;
  } catch (error) {
    console.error('Erreur récupération abonnement:', error);
    return null;
  }
};

// Créer un nouvel abonnement
export const createSubscription = async (planId, userId, paymentMethodId, userEmail) => {
  try {
    const { data, error } = await supabase.functions.invoke('manage-subscription', {
      body: {
        action: 'create_subscription',
        planId,
        userId,
        paymentMethodId,
        userEmail
      }
    });

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Erreur création abonnement:', error);
    throw error;
  }
};

// Annuler un abonnement
export const cancelSubscription = async (userId) => {
  try {
    const { data, error } = await supabase.functions.invoke('manage-subscription', {
      body: { action: 'cancel_subscription', userId }
    });

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Erreur annulation abonnement:', error);
    throw error;
  }
};

// Déduire des tokens après utilisation
export const deductTokens = async (userId, contentType, tokensUsed, options = {}) => {
  try {
    const { data, error } = await supabase.functions.invoke('deduct-tokens', {
      body: {
        userId,
        contentType,
        tokensUsed,
        selectedDuration: options.duration,
        numPages: options.pages,
        selectedVoice: options.voice,
        transactionId: options.transactionId || `txn_${Date.now()}`
      }
    });

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Erreur déduction tokens:', error);
    throw error;
  }
};

// Obtenir les tokens disponibles de l'utilisateur
export const getUserTokens = async (userId) => {
  try {
    const { data: tokens, error } = await supabase
      .from('user_tokens')
      .select('*')
      .eq('user_id', userId)
      .is('used_at', null)
      .or('expires_at.is.null,expires_at.gte.' + new Date().toISOString())
      .order('created_at', { ascending: false });

    if (error) throw error;

    const totalTokens = tokens.reduce((sum, token) => sum + token.tokens_amount, 0);
    return { totalTokens, tokens };
  } catch (error) {
    console.error('Erreur récupération tokens:', error);
    return { totalTokens: 0, tokens: [] };
  }
};

// Calculer le coût en tokens pour un contenu
export const calculateTokenCost = (contentType, options = {}, subscription = null) => {
  let tokensRequired = 1; // Par défaut

  if (subscription) {
    // Récupérer le coût depuis la base de données des coûts par plan
    // Pour l'instant, approximation basée sur le document TARIFICATION_HERBBIE.md
    const planName = subscription.subscription_plans?.name;

    const tokenCosts = {
      'Découverte': {
        'histoire': 3, 'audio': 3, 'coloriage': 2, 'bd': 4, 'comptine': 5, 'animation': 10
      },
      'Famille': {
        'histoire': 3, 'audio': 3, 'coloriage': 2, 'bd': 3, 'comptine': 4, 'animation': 8
      },
      'Créatif': {
        'histoire': 2, 'audio': 2, 'coloriage': 1, 'bd': 2, 'comptine': 3, 'animation': 5
      },
      'Institut': {
        'histoire': 1, 'audio': 1, 'coloriage': 1, 'bd': 1, 'comptine': 2, 'animation': 3
      }
    };

    if (planName && tokenCosts[planName]) {
      tokensRequired = tokenCosts[planName][contentType] || 1;
    }
  } else {
    // Coûts approximatifs pour pay-per-use
    const payPerUseCosts = {
      'histoire': 1, 'audio': 1, 'coloriage': 1, 'bd': 4, 'comptine': 5, 'animation': 10
    };
    tokensRequired = payPerUseCosts[contentType] || 1;
  }

  // Ajustements pour les animations selon la durée
  if (contentType === 'animation' && options.duration) {
    const duration = options.duration;
    if (duration === 60) tokensRequired = Math.ceil(tokensRequired * 1.5);
    else if (duration === 120) tokensRequired = Math.ceil(tokensRequired * 2.5);
    else if (duration === 180) tokensRequired = Math.ceil(tokensRequired * 4);
    else if (duration === 240) tokensRequired = Math.ceil(tokensRequired * 5);
    else if (duration === 300) tokensRequired = Math.ceil(tokensRequired * 6);
  }

  // Ajustements pour les BD selon le nombre de pages
  if ((contentType === 'bd' || contentType === 'comic') && options.pages) {
    tokensRequired = tokensRequired * options.pages;
  }

  return tokensRequired;
};

// Obtenir l'historique des tokens de l'utilisateur
export const getTokenHistory = async (userId, limit = 50) => {
  try {
    const { data, error } = await supabase
      .from('user_tokens')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Erreur récupération historique tokens:', error);
    return [];
  }
};

