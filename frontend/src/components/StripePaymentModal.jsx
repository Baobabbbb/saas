import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { loadStripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { getContentPrice } from '../services/payment'
import './PaymentModal.css'

// TODO: Remplacer par votre vraie clé publique Stripe (obtenez-la sur dashboard.stripe.com)
const stripePromise = loadStripe('pk_test_51234567890abcdef...')

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
          userId
        })

        // TODO: Remplacer par un appel réel à votre backend pour créer un Payment Intent
        // Exemple d'appel :
        /*
        const response = await fetch('/api/create-payment-intent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            amount: priceInfo.amount,
            currency: 'eur',
            contentType,
            userId
          })
        })
        const { client_secret } = await response.json()
        setClientSecret(client_secret)
        */

        // Pour le moment, simulation d'un client secret
        const mockClientSecret = `pi_test_${Date.now()}_secret_${Math.random().toString(36).substring(7)}`
        setClientSecret(mockClientSecret)
        
      } catch (error) {
        console.error('❌ Erreur création Payment Intent:', error)
        setError('Erreur lors de l\'initialisation du paiement')
      }
    }

    createPaymentIntent()
  }, [contentType, priceInfo.amount, userId])
  
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

      // TODO: Remplacer par la vraie confirmation de paiement Stripe
      /*
      const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            email: userEmail,
          },
        }
      })

      if (error) {
        throw new Error(error.message)
      }

      if (paymentIntent.status === 'succeeded') {
        onSuccess({
          success: true,
          paymentIntentId: paymentIntent.id,
          amount: paymentIntent.amount / 100,
          contentType
        })
      }
      */

      // Pour le moment, simulation d'un paiement Stripe avec vérification de carte
      console.log('💳 Validation des informations de carte...')
      
      // Vérifier que la carte est valide (simulation)
      const { error: cardError } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
      })

      if (cardError) {
        throw new Error(cardError.message)
      }

      // Simulation d'un délai de traitement Stripe réaliste
      await new Promise(resolve => setTimeout(resolve, 3000))

      // Simulation d'un paiement réussi (95% de réussite avec des cartes valides)
      const paymentSuccess = Math.random() > 0.05
      
      if (paymentSuccess) {
        const mockPaymentIntent = {
          id: `pi_${Date.now()}_${Math.random().toString(36).substring(7)}`,
          status: 'succeeded',
          amount: priceInfo.amount,
          currency: 'eur'
        }
        
        console.log('✅ Paiement Stripe réussi:', mockPaymentIntent)
        
        onSuccess({
          success: true,
          contentType,
          amount: priceInfo.amount / 100, // Convertir centimes en euros
          paymentIntentId: mockPaymentIntent.id,
          stripePayment: true
        })
      } else {
        throw new Error('Votre paiement a été refusé. Veuillez vérifier vos informations de carte.')
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






