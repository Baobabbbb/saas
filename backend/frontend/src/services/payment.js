import { supabase } from '../supabaseClient'

// Vérifier si l'utilisateur a la permission (admin ou payé)
export const checkPaymentPermission = async (contentType, userId, userEmail) => {
  try {
    // TODO: Remplacer par les vraies Edge Functions quand créées
    console.log('🔍 Vérification permission temporaire pour:', { contentType, userId, userEmail })
    
    // Simulation temporaire basée sur l'email
    if (userEmail === 'fredagathe77@gmail.com') {
      console.log('👑 Admin détecté - accès gratuit')
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
      console.error('❌ Erreur récupération profil:', profileError)
    }

    console.log('👤 Profil utilisateur:', profile)

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
    console.log('💳 Paiement requis pour utilisateur normal')
    return {
      hasPermission: false,
      reason: 'payment_required',
      userRole: 'user',
      isAdmin: false
    }
    
  } catch (error) {
    console.error('Erreur vérification permission:', error)
    return { hasPermission: false, reason: 'error', error, isAdmin: false }
  }
}

// Créer une session de paiement (seulement pour les non-admins)
export const createPaymentSession = async (contentType, userId) => {
  try {
    const { data, error } = await supabase.functions.invoke('create-payment', {
      body: { contentType, userId }
    })
    
    if (error) throw error
    return data
    
  } catch (error) {
    console.error('Erreur création paiement:', error)
    throw error
  }
}

// Obtenir le prix d'un contenu
export const getContentPrice = (contentType) => {
  const prices = {
    'comptine': { amount: 299, name: 'Comptine Musicale', currency: 'EUR', display: '2,99€' },
    'histoire': { amount: 399, name: 'Histoire Audio', currency: 'EUR', display: '3,99€' },
    'coloriage': { amount: 199, name: 'Coloriage Personnalisé', currency: 'EUR', display: '1,99€' },
    'bd': { amount: 499, name: 'Bande Dessinée', currency: 'EUR', display: '4,99€' },
    animation: { amount: 499, name: 'Animation IA personnalisée', currency: 'EUR', display: '4,99€' },
    coloring: { amount: 199, name: 'Coloriage personnalisé', currency: 'EUR', display: '1,99€' },
    comic: { amount: 299, name: 'Bande dessinée IA', currency: 'EUR', display: '2,99€' },
    story: { amount: 399, name: 'Histoire audio', currency: 'EUR', display: '3,99€' },
    rhyme: { amount: 249, name: 'Comptine musicale', currency: 'EUR', display: '2,49€' }
  }
  
  return prices[contentType] || { amount: 299, name: 'Contenu Créatif', currency: 'EUR', display: '2,99€' }
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
      console.error('Erreur vérification accès gratuit:', error)
      return false
    }

    return profile?.role === 'admin' || profile?.role === 'free'

  } catch (error) {
    console.error('Erreur hasFreeAccess:', error)
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
    console.error('Erreur récupération rôle:', error)
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
    console.error('Erreur accordement permission:', error)
    throw error
  }
}

