import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { loadStripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { getContentPrice, grantPermission } from '../services/payment'
import { supabase } from '../supabaseClient'
import './PaymentModal.css'

// Initialiser Stripe avec la clé publique depuis les variables d'environnement
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

const PaymentForm = ({ contentType, userId, userEmail, onSuccess, onCancel, priceInfo }) => {
  const stripe = useStripe()
  const elements = useElements()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [clientSecret, setClientSecret] = useState('')

  // Créer un Payment Intent dès que le composant se charge
  useEffect(() => {
    const createPaymentIntent = async () => {
      try {
        console.log('🔄 Création Payment Intent pour:', {
          contentType,
          amount: priceInfo.amount,
          userId,
          userEmail
        })

        // Appeler l'Edge Function Supabase pour créer le Payment Intent
        const { data, error } = await supabase.functions.invoke('create-payment', {
          body: {
            contentType,
            userId,
            userEmail
          }
        })

        if (error) {
          console.error('Erreur Edge Function:', error)
          throw new Error('Erreur lors de la création du paiement')
        }

        if (!data.client_secret) {
          throw new Error('Client secret manquant dans la réponse')
        }

        console.log('✅ Payment Intent créé avec succès')
        setClientSecret(data.client_secret)

      } catch (error) {
        console.error('❌ Erreur création Payment Intent:', error)
        setError(error.message || 'Erreur lors de l\'initialisation du paiement')
      }
    }

    if (stripe) {
      createPaymentIntent()
    }
  }, [contentType, priceInfo.amount, userId, userEmail, stripe])
  
  const handlePayment = async (event) => {
    event.preventDefault()

    if (!stripe || !elements) {
      setError('Stripe n\'est pas encore chargé. Veuillez patienter.')
      return
    }

    const cardElement = elements.getElement(CardElement)
    if (!cardElement) {
      setError('Élément de carte non trouvé')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('🔄 Traitement paiement Stripe pour:', {
        contentType,
        userId,
        userEmail,
        amount: priceInfo.amount
      })

      // Confirmer le paiement avec Stripe
      const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            email: userEmail,
          },
        },
        return_url: window.location.origin,
      })

      if (error) {
        console.error('Erreur Stripe:', error)
        throw new Error(error.message || 'Erreur lors du paiement')
      }

      if (paymentIntent.status === 'succeeded') {
        console.log('✅ Paiement Stripe réussi:', paymentIntent)

        // Appeler la fonction pour enregistrer la permission après paiement réussi
        try {
          await grantPermission(userId, contentType, paymentIntent.id, priceInfo.amount / 100)
        } catch (grantError) {
          console.error('Erreur lors de l\'enregistrement de la permission:', grantError)
          // Ne pas bloquer le succès du paiement si l'enregistrement échoue
        }

        onSuccess({
          success: true,
          contentType,
          amount: priceInfo.amount / 100, // Convertir centimes en euros
          paymentIntentId: paymentIntent.id,
          stripePayment: true
        })
      } else if (paymentIntent.status === 'requires_action') {
        // Authentification 3D Secure requise
        throw new Error('Authentification supplémentaire requise. Veuillez réessayer.')
      } else {
        throw new Error('Paiement non finalisé. Veuillez vérifier votre carte.')
      }

    } catch (error) {
      console.error('❌ Erreur paiement Stripe:', error)
      setError(error.message || 'Erreur lors du paiement. Veuillez réessayer.')
    } finally {
      setLoading(false)
    }
  }

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
      },
      invalid: {
        color: '#9e2146',
      },
    },
  }

  return (
    <form onSubmit={handlePayment} className="payment-form">
      <div className="payment-summary">
        <h3>Récapitulatif de votre commande</h3>
        <div className="order-item">
          <span className="item-name">{priceInfo.name}</span>
          <span className="item-price">{priceInfo.display}</span>
        </div>
        <div className="order-total">
          <span className="total-label">Total à payer :</span>
          <span className="total-amount">{priceInfo.display}</span>
        </div>
      </div>

      <div className="payment-method">
        <h3>Informations de paiement</h3>
        <div className="card-element-container">
          <CardElement 
            options={cardElementOptions}
            className="card-element"
          />
        </div>
      </div>

      {error && (
        <div className="payment-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="payment-actions">
        <button
          type="button"
          onClick={onCancel}
          className="cancel-button"
          disabled={loading}
        >
          Annuler
        </button>
        <button
          type="submit"
          className="pay-button"
          disabled={!stripe || loading}
        >
          {loading ? (
            <>
              <div className="loading-spinner"></div>
              Traitement en cours...
            </>
          ) : (
            <>
              <span className="lock-icon">🔒</span>
              Payer {priceInfo.display}
            </>
          )}
        </button>
      </div>

      <div className="payment-security">
        <div className="security-info">
          <span className="security-icon">🔒</span>
          <small>Paiement sécurisé par Stripe</small>
        </div>
        <div className="accepted-cards">
          <span>💳 Visa</span>
          <span>💳 Mastercard</span>
          <span>💳 American Express</span>
        </div>
      </div>
    </form>
  )
}

const StripePaymentModal = ({ contentType, userId, userEmail, onSuccess, onCancel }) => {
  const priceInfo = getContentPrice(contentType)

  return (
    <div className="payment-modal-overlay">
      <motion.div
        className="payment-modal stripe-payment-modal"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="payment-header">
          <h2>💳 Paiement sécurisé</h2>
          <button
            className="close-button"
            onClick={onCancel}
            aria-label="Fermer"
          >
            ✕
          </button>
        </div>

        <Elements stripe={stripePromise}>
          <PaymentForm
            contentType={contentType}
            userId={userId}
            userEmail={userEmail}
            onSuccess={onSuccess}
            onCancel={onCancel}
            priceInfo={priceInfo}
          />
        </Elements>
      </motion.div>
    </div>
  )
}

export default StripePaymentModal






