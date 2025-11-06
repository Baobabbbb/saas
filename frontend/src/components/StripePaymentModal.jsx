import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardNumberElement, CardExpiryElement, CardCvcElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { supabase } from '../supabaseClient';
import { getContentPrice } from '../services/payment';

const stripeKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
console.log('🔑 Clé Stripe chargée:', stripeKey ? 'Oui (pk_...)' : 'NON - MANQUANTE');
const stripePromise = loadStripe(stripeKey);

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      color: '#32325d',
      fontFamily: '"Baloo 2", sans-serif',
      fontSmoothing: 'antialiased',
      fontSize: '16px',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a'
    }
  }
};

const CheckoutForm = ({ onClose, onSuccess, contentType, options }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [cardholderName, setCardholderName] = useState('');

  const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
  const priceInfo = getContentPrice(normalizedContentType, options);

  useEffect(() => {
    console.log('💳 Stripe chargé:', stripe ? 'Oui' : 'Non');
    console.log('📋 Elements chargé:', elements ? 'Oui' : 'Non');
  }, [stripe, elements]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      setErrorMessage('Stripe n\'est pas encore chargé. Veuillez réessayer.');
      return;
    }

    if (!cardholderName.trim()) {
      setErrorMessage('Veuillez entrer le nom du titulaire de la carte');
      return;
    }

    const cardNumberElement = elements.getElement(CardNumberElement);
    if (!cardNumberElement) {
      setErrorMessage('Impossible de charger le formulaire de paiement.');
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');

    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error('Vous devez être connecté pour effectuer un paiement');
      }

      // Créer un PaymentIntent via l'Edge Function
      const { data: paymentData, error: paymentError } = await supabase.functions.invoke('create-payment', {
        body: {
          amount: priceInfo.amount,
          currency: priceInfo.currency,
          contentType: normalizedContentType,
          description: priceInfo.name,
          userId: user.id,
          userEmail: user.email
        }
      });

      if (paymentError) {
        throw new Error(paymentError.message || 'Erreur lors de la création du paiement');
      }

      if (!paymentData || !paymentData.clientSecret) {
        throw new Error('Impossible de créer le paiement');
      }

      // Confirmer le paiement avec la carte
      const { error: confirmError, paymentIntent } = await stripe.confirmCardPayment(
        paymentData.clientSecret,
        {
          payment_method: {
            card: cardNumberElement,
            billing_details: {
              name: cardholderName,
              email: user.email,
            },
          },
        }
      );

      if (confirmError) {
        throw new Error(confirmError.message || 'Le paiement a échoué');
      }

      if (paymentIntent && paymentIntent.status === 'succeeded') {
        onSuccess();
      } else {
        throw new Error('Le paiement n\'a pas été confirmé');
      }
    } catch (error) {
      console.error('Erreur de paiement:', error);
      setErrorMessage(error.message || 'Une erreur est survenue lors du paiement');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Nom du titulaire */}
      <div style={{ marginBottom: '16px' }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontSize: '14px',
          fontWeight: '600',
          color: '#333',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          Nom du titulaire de la carte
        </label>
        <input
          type="text"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          placeholder="Jean Dupont"
          required
          style={{
            width: '100%',
            padding: '14px 16px',
            fontSize: '16px',
            border: '2px solid #e0e0e0',
            borderRadius: '8px',
            fontFamily: '"Baloo 2", sans-serif',
            boxSizing: 'border-box',
            outline: 'none',
            transition: 'border-color 0.2s',
          }}
          onFocus={(e) => e.target.style.borderColor = '#6B4EFF'}
          onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
        />
      </div>

      {/* Numéro de carte */}
      <div style={{ marginBottom: '16px' }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontSize: '14px',
          fontWeight: '600',
          color: '#333',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          Numéro de carte
        </label>
        <div style={{
          padding: '14px 16px',
          border: '2px solid #e0e0e0',
          borderRadius: '8px',
          backgroundColor: 'white',
        }}>
          <CardNumberElement options={CARD_ELEMENT_OPTIONS} />
        </div>
      </div>

      {/* Date d'expiration et CVC */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        marginBottom: '20px'
      }}>
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontSize: '14px',
            fontWeight: '600',
            color: '#333',
            fontFamily: '"Baloo 2", sans-serif'
          }}>
            Date d'expiration
          </label>
          <div style={{
            padding: '14px 16px',
            border: '2px solid #e0e0e0',
            borderRadius: '8px',
            backgroundColor: 'white',
          }}>
            <CardExpiryElement options={CARD_ELEMENT_OPTIONS} />
          </div>
        </div>
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontSize: '14px',
            fontWeight: '600',
            color: '#333',
            fontFamily: '"Baloo 2", sans-serif'
          }}>
            CVC
          </label>
          <div style={{
            padding: '14px 16px',
            border: '2px solid #e0e0e0',
            borderRadius: '8px',
            backgroundColor: 'white',
          }}>
            <CardCvcElement options={CARD_ELEMENT_OPTIONS} />
          </div>
        </div>
      </div>

      {errorMessage && (
        <div style={{
          padding: '12px',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '8px',
          marginBottom: '20px',
          fontSize: '14px',
          border: '1px solid #ef5350'
        }}>
          ⚠️ {errorMessage}
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <button
          type="button"
          onClick={onClose}
          disabled={isProcessing}
          style={{
            flex: 1,
            padding: '14px',
            fontSize: '16px',
            fontWeight: '600',
            borderRadius: '8px',
            border: '2px solid #6B4EFF',
            backgroundColor: 'white',
            color: '#6B4EFF',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            opacity: isProcessing ? 0.5 : 1,
            fontFamily: '"Baloo 2", sans-serif'
          }}
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={!stripe || isProcessing}
          style={{
            flex: 1,
            padding: '14px',
            fontSize: '16px',
            fontWeight: '600',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: '#6B4EFF',
            color: 'white',
            cursor: (!stripe || isProcessing) ? 'not-allowed' : 'pointer',
            opacity: (!stripe || isProcessing) ? 0.5 : 1,
            fontFamily: '"Baloo 2", sans-serif'
          }}
        >
          {isProcessing ? '⏳ Traitement...' : `💳 Payer ${priceInfo.display}`}
        </button>
      </div>

      <div style={{
        textAlign: 'right',
        fontSize: '13px',
        color: '#666',
        fontFamily: '"Baloo 2", sans-serif'
      }}>
        🔒 Paiement sécurisé par Stripe
      </div>
    </form>
  );
};

const StripePaymentModal = ({ isOpen, onClose, onSuccess, contentType, options = {} }) => {
  if (!isOpen) return null;

  const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
  const priceInfo = getContentPrice(normalizedContentType, options);

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const modalContent = (
    <div
      onClick={handleOverlayClick}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999999,
        padding: '20px',
        fontFamily: '"Baloo 2", sans-serif'
      }}
    >
      <div 
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          position: 'relative',
          maxHeight: '90vh',
          overflowY: 'auto',
          isolation: 'isolate'
        }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'none',
            border: 'none',
            fontSize: '28px',
            cursor: 'pointer',
            color: '#999',
            width: '36px',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '50%',
            lineHeight: '1',
            zIndex: 10
          }}
          aria-label="Fermer"
        >
          ×
        </button>

        <h2 style={{
          margin: '0 0 8px 0',
          fontSize: '26px',
          fontWeight: '700',
          color: '#333',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          Paiement sécurisé
        </h2>

        <p style={{
          margin: '0 0 28px 0',
          fontSize: '16px',
          color: '#666',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          {priceInfo.name} • <strong>{priceInfo.display}</strong>
        </p>

        <Elements stripe={stripePromise}>
          <CheckoutForm
            onClose={onClose}
            onSuccess={onSuccess}
            contentType={contentType}
            options={options}
          />
        </Elements>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default StripePaymentModal;
