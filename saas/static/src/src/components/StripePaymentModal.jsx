import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { supabase } from '../supabaseClient';
import { getContentPrice } from '../services/payment';

const StripePaymentModal = ({ isOpen, onClose, onSuccess, contentType, options = {} }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
  const priceInfo = getContentPrice(normalizedContentType, options);

  const handlePayment = async () => {
    console.log('🔵 handlePayment appelé');
    console.log('📦 Props reçues:', { contentType, options, priceInfo });
    
    setIsProcessing(true);
    setErrorMessage('');

    try {
      const { data: { user } } = await supabase.auth.getUser();
      console.log('👤 Utilisateur:', user?.email);
      
      if (!user) {
        throw new Error('Vous devez être connecté pour effectuer un paiement');
      }

      const paymentBody = {
        amount: priceInfo.amount,
        currency: priceInfo.currency,
        contentType: normalizedContentType,
        description: priceInfo.name,
        userId: user.id,
        userEmail: user.email,
        successUrl: window.location.origin + '?payment=success',
        cancelUrl: window.location.origin + '?payment=cancelled'
      };
      
      console.log('📤 Envoi à create-payment:', paymentBody);

      // Créer une session Stripe Checkout
      const { data: sessionData, error: sessionError } = await supabase.functions.invoke('create-payment', {
        body: paymentBody
      });

      console.log('📥 Réponse create-payment:', { sessionData, sessionError });

      if (sessionError) {
        throw new Error(sessionError.message || 'Erreur lors de la création du paiement');
      }

      if (!sessionData || !sessionData.url) {
        throw new Error('Impossible de créer la session de paiement');
      }

      console.log('✅ Redirection vers:', sessionData.url);
      // Rediriger vers Stripe Checkout
      window.location.href = sessionData.url;

    } catch (error) {
      console.error('❌ Erreur de paiement:', error);
      setErrorMessage(error.message || 'Une erreur est survenue lors du paiement');
      setIsProcessing(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && !isProcessing) {
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
          overflowY: 'auto'
        }}>
        <button
          onClick={onClose}
          disabled={isProcessing}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'none',
            border: 'none',
            fontSize: '28px',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            color: '#999',
            width: '36px',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '50%',
            lineHeight: '1',
            opacity: isProcessing ? 0.5 : 1
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

        <div style={{
          padding: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '12px',
          marginBottom: '24px',
          border: '2px solid #e9ecef'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '16px'
          }}>
            <span style={{ fontSize: '32px' }}>💳</span>
            <div>
              <div style={{ fontWeight: '600', fontSize: '18px', color: '#333' }}>
                Paiement par carte bancaire
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                Vous serez redirigé vers notre page de paiement sécurisée
              </div>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap',
            marginTop: '12px'
          }}>
            <span style={{
              padding: '4px 8px',
              backgroundColor: 'white',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#666',
              border: '1px solid #dee2e6'
            }}>
              💳 Visa
            </span>
            <span style={{
              padding: '4px 8px',
              backgroundColor: 'white',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#666',
              border: '1px solid #dee2e6'
            }}>
              💳 Mastercard
            </span>
            <span style={{
              padding: '4px 8px',
              backgroundColor: 'white',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#666',
              border: '1px solid #dee2e6'
            }}>
              💳 American Express
            </span>
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
              fontFamily: '"Baloo 2", sans-serif',
              transition: 'all 0.2s'
            }}
          >
            Annuler
          </button>
          <button
            type="button"
            onClick={handlePayment}
            disabled={isProcessing}
            style={{
              flex: 1,
              padding: '14px',
              fontSize: '16px',
              fontWeight: '600',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: '#6B4EFF',
              color: 'white',
              cursor: isProcessing ? 'not-allowed' : 'pointer',
              opacity: isProcessing ? 0.5 : 1,
              fontFamily: '"Baloo 2", sans-serif',
              transition: 'all 0.2s'
            }}
          >
            {isProcessing ? '⏳ Redirection...' : `💳 Payer ${priceInfo.display}`}
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
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default StripePaymentModal;
