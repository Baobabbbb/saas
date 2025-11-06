import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardNumberElement, CardExpiryElement, CardCvcElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { supabase } from '../supabaseClient';
import { getContentPrice } from '../services/payment';

const stripeKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
const stripePromise = loadStripe(stripeKey);

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      color: '#333',
      fontFamily: '"Baloo 2", sans-serif',
      fontSmoothing: 'antialiased',
      fontSize: '16px',
      '::placeholder': {
        color: '#b8b5d1'
      }
    },
    invalid: {
      color: '#d32f2f',
      iconColor: '#d32f2f'
    },
    complete: {
      color: '#6B4EFF',
      iconColor: '#6B4EFF'
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

  const inputStyle = {
    width: '100%',
    padding: '14px 16px',
    fontSize: '16px',
    border: '2px solid #e8e8f5',
    borderRadius: '12px',
    fontFamily: '"Baloo 2", sans-serif',
    boxSizing: 'border-box',
    outline: 'none',
    transition: 'all 0.3s ease',
    backgroundColor: '#fafafe',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '600',
    color: '#6B4EFF',
    fontFamily: '"Baloo 2", sans-serif'
  };

  const stripeContainerStyle = {
    padding: '14px 16px',
    border: '2px solid #e8e8f5',
    borderRadius: '12px',
    backgroundColor: '#fafafe',
    transition: 'all 0.3s ease',
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Nom du titulaire */}
      <div style={{ marginBottom: '18px' }}>
        <label style={labelStyle}>
          👤 Nom du titulaire de la carte
        </label>
        <input
          type="text"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          placeholder="Jean Dupont"
          required
          style={inputStyle}
          onFocus={(e) => {
            e.target.style.borderColor = '#6B4EFF';
            e.target.style.backgroundColor = 'white';
            e.target.style.boxShadow = '0 0 0 3px rgba(107, 78, 255, 0.1)';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = '#e8e8f5';
            e.target.style.backgroundColor = '#fafafe';
            e.target.style.boxShadow = 'none';
          }}
        />
      </div>

      {/* Numéro de carte */}
      <div style={{ marginBottom: '18px' }}>
        <label style={labelStyle}>
          💳 Numéro de carte
        </label>
        <div 
          style={stripeContainerStyle}
          className="stripe-card-element"
        >
          <CardNumberElement options={CARD_ELEMENT_OPTIONS} />
        </div>
      </div>

      {/* Date d'expiration et CVC */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div>
          <label style={labelStyle}>
            📅 Date d'expiration
          </label>
          <div 
            style={stripeContainerStyle}
            className="stripe-card-element"
          >
            <CardExpiryElement options={CARD_ELEMENT_OPTIONS} />
          </div>
        </div>
        <div>
          <label style={labelStyle}>
            🔒 CVC
          </label>
          <div 
            style={stripeContainerStyle}
            className="stripe-card-element"
          >
            <CardCvcElement options={CARD_ELEMENT_OPTIONS} />
          </div>
        </div>
      </div>

      {errorMessage && (
        <div style={{
          padding: '16px',
          backgroundColor: '#fff0f5',
          color: '#d32f2f',
          borderRadius: '12px',
          marginBottom: '24px',
          fontSize: '14px',
          border: '2px solid #ffc4d0',
          fontFamily: '"Baloo 2", sans-serif',
          fontWeight: '500'
        }}>
          ⚠️ {errorMessage}
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '20px'
      }}>
        <button
          type="button"
          onClick={onClose}
          disabled={isProcessing}
          style={{
            flex: 1,
            padding: '16px 24px',
            fontSize: '16px',
            fontWeight: '600',
            borderRadius: '12px',
            border: '2px solid #6B4EFF',
            backgroundColor: 'white',
            color: '#6B4EFF',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            opacity: isProcessing ? 0.5 : 1,
            fontFamily: '"Baloo 2", sans-serif',
            transition: 'all 0.3s ease',
            boxShadow: '0 2px 8px rgba(107, 78, 255, 0.1)'
          }}
          onMouseEnter={(e) => {
            if (!isProcessing) {
              e.target.style.backgroundColor = '#f8f7ff';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(107, 78, 255, 0.2)';
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'white';
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 2px 8px rgba(107, 78, 255, 0.1)';
          }}
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={!stripe || isProcessing}
          style={{
            flex: 1,
            padding: '16px 24px',
            fontSize: '16px',
            fontWeight: '600',
            borderRadius: '12px',
            border: 'none',
            background: 'linear-gradient(135deg, #6B4EFF 0%, #8B6FFF 100%)',
            color: 'white',
            cursor: (!stripe || isProcessing) ? 'not-allowed' : 'pointer',
            opacity: (!stripe || isProcessing) ? 0.6 : 1,
            fontFamily: '"Baloo 2", sans-serif',
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 16px rgba(107, 78, 255, 0.3)'
          }}
          onMouseEnter={(e) => {
            if (stripe && !isProcessing) {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 20px rgba(107, 78, 255, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 16px rgba(107, 78, 255, 0.3)';
          }}
        >
          {isProcessing ? '⏳ Traitement...' : `💳 Payer ${priceInfo.display}`}
        </button>
      </div>

      <div style={{
        textAlign: 'center',
        fontSize: '13px',
        color: '#9b8fd9',
        fontFamily: '"Baloo 2", sans-serif',
        fontWeight: '500',
        padding: '12px',
        backgroundColor: '#f8f7ff',
        borderRadius: '8px'
      }}>
        🔒 Paiement 100% sécurisé par Stripe
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
          fontSize: '28px',
          fontWeight: '700',
          background: 'linear-gradient(135deg, #6B4EFF 0%, #8B6FFF 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          💳 Paiement sécurisé
        </h2>

        <p style={{
          margin: '0 0 32px 0',
          fontSize: '16px',
          color: '#666',
          fontFamily: '"Baloo 2", sans-serif',
          padding: '12px 16px',
          backgroundColor: '#f8f7ff',
          borderRadius: '8px',
          border: '1px solid #e8e8f5'
        }}>
          {priceInfo.name} • <strong style={{ color: '#6B4EFF' }}>{priceInfo.display}</strong>
        </p>

        <Elements stripe={stripePromise}>
          <CheckoutForm
            onClose={onClose}
            onSuccess={onSuccess}
            contentType={contentType}
            options={options}
          />
        </Elements>

        <div style={{
          marginTop: '20px',
          textAlign: 'center',
          fontSize: '12px',
          color: '#999',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          En cliquant sur "Payer", vous acceptez nos{' '}
          <a href="/legal" style={{ color: '#6B4EFF', textDecoration: 'none' }}>
            conditions générales de vente
          </a>
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default StripePaymentModal;
