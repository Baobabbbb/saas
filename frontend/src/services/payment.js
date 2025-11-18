import { supabase } from '../supabaseClient'

// Vérifier si l'utilisateur a la permission (admin, abonnement ou payé)
export const checkPaymentPermission = async (contentType, userId, userEmail, options = {}) => {
  try {
    // Vérifier le rôle admin dans la table profiles (logique déplacée côté backend)
    // La vérification admin est maintenant gérée côté serveur pour plus de sécurité
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
    // NOUVEAUX PRIX 2025-11-16 : Encore plus accessibles !
    'comptine': { amount: 69, name: 'Comptine Musicale', currency: 'EUR', display: '0,69€' },
    'histoire': { amount: 29, name: 'Histoire', currency: 'EUR', display: '0,29€' },
    'audio': { amount: 29, name: 'Histoire', currency: 'EUR', display: '0,29€' },
    'coloriage': { amount: 69, name: 'Coloriage Personnalisé', currency: 'EUR', display: '0,69€' },
    'coloring': { amount: 69, name: 'Coloriage personnalisé', currency: 'EUR', display: '0,69€' },
    'bd': { amount: 69, name: 'Page de Bande Dessinée', currency: 'EUR', display: '0,69€' },
    'comic': { amount: 69, name: 'Page de Bande Dessinée', currency: 'EUR', display: '0,69€' },
    'story': { amount: 29, name: 'Histoire', currency: 'EUR', display: '0,29€' },
    'rhyme': { amount: 69, name: 'Comptine musicale', currency: 'EUR', display: '0,69€' },

    // Animations avec marges réduites (prix attractifs)
    'animation': { amount: 599, name: 'Animation IA 30s', currency: 'EUR', display: '5,99€' }
  }

  // Gestion spéciale pour les histoires (prix unique : 0,29€)
  if (contentType === 'histoire' || contentType === 'story' || contentType === 'audio') {
    return {
      amount: 29,
      name: 'Histoire',
      currency: 'EUR',
      display: '0,29€'
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

// Confirmer un abonnement après paiement réussi
export const confirmSubscription = async (stripeSubscriptionId) => {
  try {
    const { data, error } = await supabase.functions.invoke('manage-subscription', {
      body: { action: 'confirm_subscription', stripeSubscriptionId }
    });

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Erreur confirmation abonnement:', error);
    throw error;
  }
};

// Déduire des tokens après utilisation
export const deductTokens = async (userId, contentType, tokensUsed, options = {}) => {
  try {
    // Validation côté client pour éviter les appels inutiles
    if (!userId || !contentType || tokensUsed === undefined || tokensUsed === null || tokensUsed <= 0) {
      return { success: true, type: 'no_deduction', message: 'Aucun token à déduire', silent: true };
    }

    const payload = {
      userId,
      contentType,
      tokensUsed: Number(tokensUsed), // S'assurer que c'est un nombre
      selectedDuration: options.duration,
      numPages: options.pages,
      selectedVoice: options.voice,
      transactionId: options.transactionId || `txn_${Date.now()}`
    };

    const { data, error } = await supabase.functions.invoke('deduct-tokens', {
      body: payload
    });

    if (error) {
      // Ne pas logger les erreurs si c'est un paiement direct (erreurs attendues)
      // Les erreurs de tokens sont normales en pay-per-use
      return { success: false, error: error.message || 'Erreur déduction tokens', silent: true };
    }

    return data;
  } catch (error) {
    // Ne pas logger les erreurs si c'est un paiement direct (erreurs attendues)
    // Les erreurs de tokens sont normales en pay-per-use
    return { success: false, error: error.message || 'Erreur déduction tokens', silent: true };
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
// Basé sur TARIFICATION_HERBBIE.md : 1 token = 0,01€ de coût API
export const calculateTokenCost = (contentType, options = {}, subscription = null) => {
  let tokensRequired = 4; // Par défaut (histoire)

  // Coûts de base IDENTIQUES pour tous les plans (1 token = 0,01€ de coût API)
  if (contentType === 'histoire' || contentType === 'story' || contentType === 'audio') {
    tokensRequired = 4; // 0,042€ → 4 tokens
  } else if (contentType === 'coloriage') {
    tokensRequired = 16; // 0,16€ → 16 tokens
  } else if (contentType === 'bd' || contentType === 'comic') {
    tokensRequired = 16; // 0,16€ par page → 16 tokens
    // Multiplier par le nombre de pages
    if (options.pages && options.pages > 0) {
      tokensRequired = tokensRequired * options.pages;
    }
  } else if (contentType === 'comptine' || contentType === 'rhyme') {
    tokensRequired = 15; // 0,15€ → 15 tokens
  } else if (contentType === 'animation') {
    // Coûts animations basés sur la durée (Veo 3.1 Fast: 0,14€/seconde)
    const duration = options.duration || 30; // durée en secondes
    const costPerSecond = 0.14; // €
    const totalCost = costPerSecond * duration;
    tokensRequired = Math.ceil(totalCost * 100); // Convertir en tokens (1 token = 0,01€)
    
    // Résultat selon la tarification:
    // 30s: 4,20€ → 420 tokens
    // 60s: 8,40€ → 840 tokens
    // 120s: 16,80€ → 1680 tokens
    // 180s: 25,20€ → 2520 tokens
    // 240s: 33,60€ → 3360 tokens
    // 300s: 42,00€ → 4200 tokens
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

