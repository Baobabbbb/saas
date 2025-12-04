import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardNumberElement, CardExpiryElement, CardCvcElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { supabase } from '../supabaseClient';
import { getContentPrice } from '../services/payment';

const stripeKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
// Configuration Stripe avec options pour réduire les erreurs
const stripePromise = stripeKey ? loadStripe(stripeKey, {
  // Options pour réduire les erreurs de réseau Stripe
  betas: [],
  locale: 'fr'
}) : null;

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

const CheckoutForm = ({ onClose, onSuccess, contentType, options, showCheckbox, onOpenCGV }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [cardholderName, setCardholderName] = useState('');
  const [acceptCGV, setAcceptCGV] = useState(false);
  const [cardComplete, setCardComplete] = useState(false);

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

    if (showCheckbox && !acceptCGV) {
      setErrorMessage('Veuillez accepter les Conditions Générales de Vente');
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
      
      // Créer un PaymentIntent via l'Edge Function (même sans user)
      const { data: paymentData, error: paymentError } = await supabase.functions.invoke('create-payment', {
        body: {
          amount: priceInfo.amount,
          currency: priceInfo.currency,
          contentType: normalizedContentType,
          description: priceInfo.name,
          userId: user?.id || 'anonymous',
          userEmail: user?.email || 'anonymous@guest.com'
        }
      });

      if (paymentError) {
        console.error('Erreur Edge Function:', paymentError);
        try {
          // Essayer de parser le body de l'erreur si c'est du JSON
          const errorBody = JSON.parse(paymentError.message);
          if (errorBody && errorBody.error) {
             throw new Error(errorBody.error);
          }
        } catch (e) {
          // Si ce n'est pas du JSON, utiliser le message tel quel
        }
        throw new Error(paymentError.message || 'Erreur lors de la création du paiement');
      }

      // Vérifier si l'Edge Function a retourné une erreur logique (status 200 mais success: false)
      if (paymentData && paymentData.error) {
        console.error('Erreur logique create-payment:', paymentData);
        throw new Error(paymentData.error);
      }

      if (!paymentData || !paymentData.clientSecret) {
        console.error('Réponse create-payment invalide:', paymentData);
        throw new Error('Impossible de créer le paiement (réponse invalide)');
      }

      // Confirmer le paiement avec la carte
      const { error: confirmError, paymentIntent } = await stripe.confirmCardPayment(
        paymentData.clientSecret,
        {
          payment_method: {
            card: cardNumberElement,
            billing_details: {
              name: cardholderName,
              email: user?.email || 'anonymous@guest.com',
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
    padding: '12px 14px',
    fontSize: '15px',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    fontFamily: '"Baloo 2", sans-serif',
    boxSizing: 'border-box',
    outline: 'none',
    transition: 'border-color 0.2s ease',
    backgroundColor: 'white',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '5px',
    fontSize: '13px',
    fontWeight: '500',
    color: '#666',
    fontFamily: '"Baloo 2", sans-serif'
  };

  const stripeContainerStyle = {
    padding: '12px 14px',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    backgroundColor: 'white',
    transition: 'border-color 0.2s ease',
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Nom du titulaire */}
      <div style={{ marginBottom: '14px' }}>
        <label style={labelStyle}>
          Nom du titulaire
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
          }}
          onBlur={(e) => {
            e.target.style.borderColor = '#e0e0e0';
          }}
        />
      </div>

      {/* Numéro de carte */}
      <div style={{ marginBottom: '14px' }}>
        <label style={labelStyle}>
          Numéro de carte
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
        gap: '12px',
      }}>
        <div>
          <label style={labelStyle}>
            Date d'expiration
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
            CVC
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
          padding: '12px',
          backgroundColor: '#fff5f5',
          color: '#e53e3e',
          borderRadius: '6px',
          marginBottom: '14px',
          fontSize: '14px',
          border: '1px solid #feb2b2',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          {errorMessage}
        </div>
      )}

      {showCheckbox && (
        <div style={{
          marginTop: '0px',
          marginBottom: '6px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <input
            type="checkbox"
            id="accept-cgv-payment"
            checked={acceptCGV}
            onChange={(e) => setAcceptCGV(e.target.checked)}
            style={{
              cursor: 'pointer',
              width: '14px',
              height: '14px',
              accentColor: '#6B4EFF',
              flexShrink: 0
            }}
          />
          <label
            htmlFor="accept-cgv-payment"
            style={{
              fontSize: '12px',
              color: '#333',
              fontFamily: '"Baloo 2", sans-serif',
              cursor: 'pointer',
              lineHeight: '1.4',
              flex: 1
            }}
          >
            J'ai lu et j'accepte les{' '}
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                if (onOpenCGV) {
                  onOpenCGV('terms');
                }
              }}
              style={{
                color: '#6B4EFF',
                textDecoration: 'underline',
                cursor: 'pointer'
              }}
            >
              CGV
            </a>
            {' '}et l'accès immédiat au service.
          </label>
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '0'
      }}>
        <button
          type="button"
          onClick={onClose}
          disabled={isProcessing}
          style={{
            flex: 1,
            padding: '12px 20px',
            fontSize: '15px',
            fontWeight: '500',
            borderRadius: '8px',
            border: '1px solid #d0d0d0',
            backgroundColor: 'white',
            color: '#666',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            opacity: isProcessing ? 0.5 : 1,
            fontFamily: '"Baloo 2", sans-serif',
            transition: 'background-color 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (!isProcessing) {
              e.target.style.backgroundColor = '#f9f9f9';
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'white';
          }}
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={!stripe || isProcessing || (showCheckbox && !acceptCGV) || !cardholderName.trim()}
          style={{
            flex: 1,
            padding: '12px 20px',
            fontSize: '15px',
            fontWeight: '500',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: '#6B4EFF',
            color: 'white',
            cursor: (!stripe || isProcessing || (showCheckbox && !acceptCGV) || !cardholderName.trim()) ? 'not-allowed' : 'pointer',
            opacity: (!stripe || isProcessing || (showCheckbox && !acceptCGV) || !cardholderName.trim()) ? 0.6 : 1,
            fontFamily: '"Baloo 2", sans-serif',
            transition: 'background-color 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (stripe && !isProcessing && (!showCheckbox || acceptCGV) && cardholderName.trim()) {
              e.target.style.backgroundColor = '#5a3eef';
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = '#6B4EFF';
          }}
        >
          {isProcessing ? 'Traitement...' : `Payer ${priceInfo.display}`}
        </button>
      </div>
    </form>
  );
};

const StripePaymentModal = ({ isOpen, onClose, onSuccess, contentType, options = {}, onOpenCGV }) => {
  if (!isOpen) return null;

  const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
  const priceInfo = getContentPrice(normalizedContentType, options);
  const [showCheckbox, setShowCheckbox] = useState(false);
  const [userRole, setUserRole] = useState(null);

  // Vérifier le rôle utilisateur pour déterminer si on affiche la checkbox
  useEffect(() => {
    const checkUserRole = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          // Utilisateur anonyme = afficher la checkbox
          setShowCheckbox(true);
          return;
        }

        const { data: profile, error } = await supabase
          .from('profiles')
          .select('role')
          .eq('id', user.id)
          .single();

        if (error || !profile) {
          // Erreur ou pas de profil = afficher la checkbox par sécurité
          setShowCheckbox(true);
          return;
        }

        // Afficher la checkbox uniquement si l'utilisateur n'est pas admin ni free
        setShowCheckbox(profile.role !== 'admin' && profile.role !== 'free');
        setUserRole(profile.role);
      } catch (error) {
        console.error('Erreur vérification rôle:', error);
        // En cas d'erreur, afficher la checkbox par sécurité
        setShowCheckbox(true);
      }
    };

    if (isOpen) {
      checkUserRole();
    }
  }, [isOpen]);

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
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 25px 50px rgba(107, 78, 255, 0.25), 0 10px 20px rgba(0, 0, 0, 0.1)',
          position: 'relative',
          maxHeight: '90vh',
          overflowY: 'auto',
          isolation: 'isolate',
          border: '3px solid #6B4EFF'
        }}>
        <div style={{ padding: '32px' }}>
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
          margin: '0 0 12px 0',
          fontSize: '24px',
          fontWeight: '600',
          color: '#333',
          fontFamily: '"Baloo 2", sans-serif',
          textAlign: 'center'
        }}>
          Paiement sécurisé
        </h2>

        <div style={{
          margin: '0 0 20px 0',
          padding: '12px 16px',
          backgroundColor: '#f8f7ff',
          borderRadius: '12px',
          border: '2px solid #6B4EFF',
          textAlign: 'center',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          <div style={{
            fontSize: '14px',
            color: '#666',
            marginBottom: '2px'
          }}>
            {priceInfo.name}
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#6B4EFF'
          }}>
            {priceInfo.display}
          </div>
        </div>

        <Elements stripe={stripePromise}>
          <CheckoutForm
            onClose={onClose}
            onSuccess={onSuccess}
            contentType={contentType}
            options={options}
            showCheckbox={showCheckbox}
            onOpenCGV={onOpenCGV}
          />
        </Elements>

        <div style={{
          marginTop: '12px',
          textAlign: 'right',
          fontSize: '11px',
          color: '#999',
          fontFamily: '"Baloo 2", sans-serif'
        }}>
          🔒 Paiement sécurisé par Stripe
        </div>
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default StripePaymentModal;

