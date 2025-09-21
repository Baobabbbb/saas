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

    if (profile?.role === 'admin') {
      return {
        hasPermission: true,
        reason: 'admin_access',
        userRole: 'admin',
        isAdmin: true
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
    animation: { amount: 4.99, description: 'Animation IA personnalisée' },
    coloring: { amount: 1.99, description: 'Coloriage personnalisé' },
    comic: { amount: 2.99, description: 'Bande dessinée IA' },
    story: { amount: 3.99, description: 'Histoire audio' },
    rhyme: { amount: 2.49, description: 'Comptine musicale' }
  }
  
  return prices[contentType] || prices.animation
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

// Vérifier si un utilisateur est admin (utilisé pour l'affichage UI)
export const isUserAdmin = async (userId) => {
  try {
    const role = await getUserRole(userId)
    return role === 'admin'
  } catch (error) {
    console.error('Erreur vérification admin:', error)
    return false
  }
}
