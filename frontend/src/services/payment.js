import { supabase } from '../supabaseClient'

// Vérifier si l'utilisateur a la permission (admin ou payé)
export const checkPaymentPermission = async (contentType, userId, userEmail) => {
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
    
    // Vérifier si l'utilisateur a payé pour ce type de contenu
    const { data: permission, error: permError } = await supabase
      .from('generation_permissions')
      .select('*')
      .eq('user_id', userId)
      .eq('content_type', contentType)
      .eq('is_active', true)
      .single()

    if (permission) {
      return {
        hasPermission: true,
        reason: 'payment_validated',
        userRole: 'user',
        isAdmin: false
      }
    }
    
    // Paiement requis
    return {
      hasPermission: false,
      reason: 'payment_required',
      userRole: 'user',
      isAdmin: false
    }
    
  } catch (error) {
    return { hasPermission: false, reason: 'error', error, isAdmin: false }
  }
}

// Créer une session de paiement (seulement pour les non-admins)
export const createPaymentSession = async (contentType, userId, userEmail, options = {}) => {
  try {
    // Calculer le prix selon les options
    const priceInfo = getContentPrice(contentType, options)

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
    // Prix selon le fichier TARIFICATION_HERBBIE.md
    'comptine': { amount: 149, name: 'Comptine Musicale', currency: 'EUR', display: '1,49€' },
    'histoire': { amount: 49, name: 'Histoire Texte', currency: 'EUR', display: '0,49€' }, // Texte par défaut
    'audio': { amount: 69, name: 'Histoire Audio', currency: 'EUR', display: '0,69€' }, // Audio
    'coloriage': { amount: 49, name: 'Coloriage Personnalisé', currency: 'EUR', display: '0,49€' },
    'coloring': { amount: 49, name: 'Coloriage personnalisé', currency: 'EUR', display: '0,49€' },
    'bd': { amount: 99, name: 'Page de Bande Dessinée', currency: 'EUR', display: '0,99€' }, // Par page
    'comic': { amount: 99, name: 'Page de Bande Dessinée', currency: 'EUR', display: '0,99€' }, // Par page
    'story': { amount: 49, name: 'Histoire Texte', currency: 'EUR', display: '0,49€' },
    'rhyme': { amount: 149, name: 'Comptine musicale', currency: 'EUR', display: '1,49€' },

    // Animations selon la durée (prix de base pour 30s, ajustable selon options)
    'animation': { amount: 229, name: 'Animation IA 30s', currency: 'EUR', display: '2,29€' }
  }

  // Gestion spéciale pour les animations selon la durée
  if (contentType === 'animation' && options.duration) {
    const durationPrices = {
      30: { amount: 229, name: 'Animation IA 30s', display: '2,29€' },
      60: { amount: 379, name: 'Animation IA 1min', display: '3,79€' },
      120: { amount: 619, name: 'Animation IA 2min', display: '6,19€' },
      180: { amount: 859, name: 'Animation IA 3min', display: '8,59€' },
      240: { amount: 1099, name: 'Animation IA 4min', display: '10,99€' },
      300: { amount: 1339, name: 'Animation IA 5min', display: '13,39€' }
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

