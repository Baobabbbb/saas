import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { supabase } from '../supabaseClient';
import { getContentPrice } from '../services/payment';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);

const CheckoutForm = ({ onClose, onSuccess, contentType, options }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
  const priceInfo = getContentPrice(normalizedContentType, options);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');

    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error('Utilisateur non connecté');
      }

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

      if (paymentError) throw paymentError;

      const { error: confirmError, paymentIntent } = await stripe.confirmCardPayment(
        paymentData.clientSecret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
            billing_details: {
              email: user.email,
            },
          },
        }
      );

      if (confirmError) {
        throw confirmError;
      }

      if (paymentIntent.status === 'succeeded') {
        onSuccess();
      }
    } catch (error) {
      console.error('Erreur de paiement:', error);
      setErrorMessage(error.message || 'Une erreur est survenue lors du paiement');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      width: '100%'
    }}>
      <div style={{
        padding: '15px',
        border: '2px solid #e0e0e0',
        borderRadius: '8px',
        backgroundColor: '#f9f9f9'
      }}>
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
              },
              invalid: {
                color: '#9e2146',
              },
            },
          }}
        />
      </div>

      {errorMessage && (
        <div style={{
          padding: '12px',
          backgroundColor: '#fee',
          color: '#c33',
          borderRadius: '8px',
          fontSize: '14px'
        }}>
          {errorMessage}
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: '12px',
        justifyContent: 'flex-end'
      }}>
        <button
          type="button"
          onClick={onClose}
          disabled={isProcessing}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: '600',
            borderRadius: '8px',
            border: '2px solid #6B4EFF',
            backgroundColor: 'white',
            color: '#6B4EFF',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            opacity: isProcessing ? 0.6 : 1,
            transition: 'all 0.2s'
          }}
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={!stripe || isProcessing}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: '600',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: '#6B4EFF',
            color: 'white',
            cursor: (!stripe || isProcessing) ? 'not-allowed' : 'pointer',
            opacity: (!stripe || isProcessing) ? 0.6 : 1,
            transition: 'all 0.2s'
          }}
        >
          {isProcessing ? 'Traitement...' : `Payer ${priceInfo.display}`}
        </button>
      </div>

      <div style={{
        textAlign: 'right',
        fontSize: '14px',
        color: '#666',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        gap: '8px'
      }}>
        <span>🔒</span>
        <span>Paiement sécurisé par Stripe</span>
      </div>
    </form>
  );
};

const StripePaymentModal = ({ isOpen, onClose, onSuccess, contentType, options = {} }) => {
  if (!isOpen) return null;

  const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
  const priceInfo = getContentPrice(normalizedContentType, options);

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 99999,
        padding: '20px'
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
          position: 'relative'
        }}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'none',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            color: '#666',
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '50%',
            transition: 'all 0.2s'
          }}
        >
          ×
        </button>

        <h2 style={{
          margin: '0 0 8px 0',
          fontSize: '24px',
          fontWeight: 'bold',
          color: '#333'
        }}>
          Paiement sécurisé
        </h2>

        <p style={{
          margin: '0 0 24px 0',
          fontSize: '16px',
          color: '#666'
        }}>
          {priceInfo.name} - {priceInfo.display}
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
};

export default StripePaymentModal;
