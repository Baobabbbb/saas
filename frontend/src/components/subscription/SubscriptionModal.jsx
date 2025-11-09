import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
// CACHE-BUST: v1762479000 - 2025-11-07 02:30:00 - FORCE RELOAD
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardNumberElement,
  CardExpiryElement,
  CardCvcElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import {
  getSubscriptionPlans,
  getUserSubscription,
  createSubscription,
  cancelSubscription,
  confirmSubscription
} from '../../services/payment';
import './SubscriptionModal.css';

// Initialiser Stripe avec la clé publique depuis les variables d'environnement
const stripePromise = (import.meta.env?.VITE_STRIPE_PUBLISHABLE_KEY &&
  typeof import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY === 'string' &&
  import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY.length > 0)
  ? loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
  : Promise.resolve(null);

const SubscriptionPlans = ({ onSelectPlan, currentSubscription }) => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const subscriptionPlans = await getSubscriptionPlans();
      setPlans(subscriptionPlans);
    } catch (error) {
      console.error('Erreur chargement plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPlanFeatures = (planName) => {
    // Cache-bust v1762466112
    if (false) console.log('Cache-bust: 2025-11-06-22:56:12');
    // Prix PAY-PER-USE (en centimes) - NOUVEAUX PRIX RÉDUITS 2025-11-06
    const payPerUse = {
      histoire: 50,       // 0,50€
      coloring: 99,       // 0,99€
      comic: 99,          // 0,99€ par page
      rhyme: 99,          // 0,99€
      animation30: 599,   // 5,99€
      animation60: 999,   // 9,99€
      animation120: 1899, // 18,99€ (2min)
      animation180: 2799, // 27,99€ (3min)
      animation240: 3699, // 36,99€ (4min)
      animation300: 4699  // 46,99€ (5min)
    };

    // Coûts en TOKENS (1 token = 0,01€ de coût API)
    // Basés sur les VRAIS coûts API des modèles utilisés :
    // - gpt-4o-mini (texte) : ~0,0004€
    // - OpenAI TTS (audio) : 0,042€
    // - gpt-image-1 (images) : 0,16€
    // - Suno (musique) : ~0,15€
    // - Veo 3.1 Fast (vidéo) : 0,14€/seconde
    const tokenCosts = {
      histoire: 4,        // 0,042€ API (texte + audio TTS) = 4 tokens
      coloring: 16,       // 0,16€ API (gpt-image-1) = 16 tokens
      comic: 16,          // 0,16€ API (gpt-image-1) = 16 tokens
      rhyme: 15,          // 0,15€ API (Suno) = 15 tokens
      animation30: 420,   // 4,20€ API (30s × 0,14€) = 420 tokens
      animation60: 840,   // 8,40€ API (60s × 0,14€) = 840 tokens
      animation120: 1680, // 16,80€ API (120s × 0,14€) = 1680 tokens
      animation180: 2520, // 25,20€ API (180s × 0,14€) = 2520 tokens
      animation240: 3360, // 33,60€ API (240s × 0,14€) = 3360 tokens
      animation300: 4200  // 42,00€ API (300s × 0,14€) = 4200 tokens
    };

    const plans = {
      'Découverte': {
        price: 499,        // 4,99€
        totalTokens: 250   // Budget API: 2,50€ (50% de marge)
      },
      'Famille': {
        price: 999,        // 9,99€
        totalTokens: 500   // Budget API: 5,00€ (50% de marge)
      },
      'Créatif': {
        price: 1999,       // 19,99€
        totalTokens: 1000  // Budget API: 10,00€ (50% de marge)
      },
      'Institut': {
        price: 4999,       // 49,99€
        totalTokens: 2500  // Budget API: 25,00€ (50% de marge)
      }
    };

    const plan = plans[planName];
    if (!plan) return {};

    // Calculer combien de chaque contenu peut être généré avec les tokens
    const maxGenerations = {
      histoire: Math.floor(plan.totalTokens / tokenCosts.histoire),
      coloring: Math.floor(plan.totalTokens / tokenCosts.coloring),
      comic: Math.floor(plan.totalTokens / tokenCosts.comic),
      rhyme: Math.floor(plan.totalTokens / tokenCosts.rhyme),
      animation30: Math.floor(plan.totalTokens / tokenCosts.animation30),
      animation60: Math.floor(plan.totalTokens / tokenCosts.animation60),
      animation120: Math.floor(plan.totalTokens / tokenCosts.animation120),
      animation180: Math.floor(plan.totalTokens / tokenCosts.animation180),
      animation240: Math.floor(plan.totalTokens / tokenCosts.animation240),
      animation300: Math.floor(plan.totalTokens / tokenCosts.animation300)
    };

    // Calculer la valeur totale si on utilise tous les tokens pour chaque type
    const totalValue = 
      (maxGenerations.histoire * payPerUse.histoire) +
      (maxGenerations.coloring * payPerUse.coloring) +
      (maxGenerations.comic * payPerUse.comic) +
      (maxGenerations.rhyme * payPerUse.rhyme) +
      (maxGenerations.animation30 * payPerUse.animation30) +
      (maxGenerations.animation60 * payPerUse.animation60) +
      (maxGenerations.animation120 * payPerUse.animation120) +
      (maxGenerations.animation180 * payPerUse.animation180) +
      (maxGenerations.animation240 * payPerUse.animation240) +
      (maxGenerations.animation300 * payPerUse.animation300);

    const savings = Math.round(((totalValue - plan.price) / totalValue) * 100);

              // Construire la liste des fonctionnalités avec exemples de MIX (léger)
              const featuresList = [`${plan.totalTokens} tokens par mois pour créer librement`];
              
              // Seulement 2-3 exemples pour alléger le visuel
              const mixExamples = {
                'Découverte': [
                  '40 histoires + 5 coloriages',
                  '30 histoires + 3 coloriages + 5 comptines'
                ],
                'Famille': [
                  '80 histoires + 10 coloriages',
                  '1 animation 30s + 20 histoires'
                ],
                'Créatif': [
                  '150 histoires + 20 coloriages',
                  '2 animations 30s + 40 histoires'
                ],
                'Institut': [
                  '300 histoires + 50 coloriages',
                  '5 animations 30s + 100 histoires',
                  '1 animation 2min + 150 histoires'
                ]
              };
              
              // Ajouter les exemples (max 2-3 pour rester léger)
              if (mixExamples[planName]) {
                mixExamples[planName].forEach(example => {
                  featuresList.push(`• ${example}`);
                });
              }

    const features = {
      'Découverte': {
        features: featuresList,
        ideal: 'Parfait pour découvrir Herbbie',
        economy: `Économisez ${savings}%`
      },
      'Famille': {
        features: featuresList,
        ideal: 'Pour les familles actives',
        economy: `Économisez ${savings}%`
      },
      'Créatif': {
        features: featuresList,
        ideal: 'Pour les créateurs intensifs',
        economy: `Économisez ${savings}%`
      },
      'Institut': {
        features: featuresList,
        ideal: 'Pour les écoles et institutions',
        economy: `Économisez ${savings}%`
      }
    };

    return features[planName] || {};
  };

  if (loading) {
    return (
      <div className="subscription-modal-loading">
        <div className="subscription-modal-spinner"></div>
      </div>
    );
  }

  const hasActiveSubscription = Boolean(currentSubscription);

  return (
    <div className={`subscription-plans-grid ${hasActiveSubscription ? 'has-active-subscription' : ''}`}>
      {plans.map((plan) => {
        const features = getPlanFeatures(plan.name);
        const isCurrentPlan = currentSubscription?.subscription_plans?.name === plan.name;

        return (
          <div
            key={plan.id}
            className={`subscription-plan-card ${isCurrentPlan ? 'active' : ''} ${hasActiveSubscription ? 'compact' : ''}`}
          >
            <div className="plan-name">{plan.name}</div>
            <div className="plan-price">
              {(plan.price_monthly / 100).toFixed(2).replace('.', ',')}€
            </div>
            <div className="plan-price-period">par mois</div>

            <ul className="plan-features">
              {features.features?.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>

            <div className="plan-ideal">
              {features.ideal}
            </div>

            {!isCurrentPlan && (
              <button
                onClick={() => onSelectPlan(plan)}
                className="plan-button primary"
              >
                Choisir ce plan
              </button>
            )}

            {isCurrentPlan && (
              <button className="plan-button secondary" disabled>
                Plan actif
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
};

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

const SubscriptionForm = ({ selectedPlan, onSuccess, onCancel, userId, userEmail }) => {
  // FORCE RELOAD 2025-11-07 02:30:00 - NOUVEAU DESIGN AVEC CHAMPS SÉPARÉS
  console.log('🎨 SubscriptionForm NOUVEAU DESIGN chargé - 3 champs séparés');
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [cardholderName, setCardholderName] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      setError('Stripe n\'est pas encore chargé. Veuillez réessayer.');
      return;
    }

    if (!cardholderName.trim()) {
      setError('Veuillez entrer le nom du titulaire de la carte');
      return;
    }

    const cardNumberElement = elements.getElement(CardNumberElement);
    if (!cardNumberElement) {
      setError('Impossible de charger le formulaire de paiement.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Créer le payment method
      const { error: paymentMethodError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardNumberElement,
        billing_details: {
          name: cardholderName.trim(),
          email: userEmail,
        },
      });

      if (paymentMethodError) {
        setError(paymentMethodError.message);
        return;
      }

      // Créer l'abonnement
      const result = await createSubscription(
        selectedPlan.id,
        userId,
        paymentMethod.id,
        userEmail
      );

      if (result.success) {
        if (result.clientSecret) {
          // Confirmer le paiement
          const { error: confirmError } = await stripe.confirmCardPayment(result.clientSecret);

          if (confirmError) {
            setError(confirmError.message);
            return;
          }

          // Confirmer l'abonnement dans Supabase après paiement réussi
          try {
            await confirmSubscription(result.stripeSubscription.id);
          } catch (confirmErr) {
            console.error('Erreur confirmation abonnement:', confirmErr);
            // Ne pas bloquer si la confirmation échoue, l'abonnement existe déjà
          }
        }

        onSuccess();
      } else {
        setError(result.error || 'Erreur lors de la création de l\'abonnement');
      }

    } catch (err) {
      console.error('Erreur abonnement:', err);
      setError('Erreur lors de la création de l\'abonnement');
    } finally {
      setLoading(false);
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
      {/* En-tête avec prix */}
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
          S'abonner à {selectedPlan.name}
        </div>
        <div style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#6B4EFF'
        }}>
          {(selectedPlan.price_monthly / 100).toFixed(2).replace('.', ',')}€/mois
        </div>
        <div style={{
          fontSize: '12px',
          color: '#888',
          marginTop: '4px'
        }}>
          Facturé mensuellement • Annulable à tout moment
        </div>
      </div>

      {/* Nom du titulaire */}
      <div style={{ marginBottom: '14px' }}>
        <label style={labelStyle}>
          Nom du titulaire de la carte
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
        marginBottom: '16px'
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

      {/* Message d'erreur */}
      {error && (
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
          {error}
        </div>
      )}

      {/* Boutons */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '0'
      }}>
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          style={{
            flex: 1,
            padding: '12px 20px',
            fontSize: '15px',
            fontWeight: '500',
            borderRadius: '8px',
            border: '1px solid #d0d0d0',
            backgroundColor: 'white',
            color: '#666',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1,
            fontFamily: '"Baloo 2", sans-serif',
            transition: 'background-color 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (!loading) {
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
          disabled={!stripe || loading}
          style={{
            flex: 1,
            padding: '12px 20px',
            fontSize: '15px',
            fontWeight: '500',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: '#6B4EFF',
            color: 'white',
            cursor: (!stripe || loading) ? 'not-allowed' : 'pointer',
            opacity: (!stripe || loading) ? 0.6 : 1,
            fontFamily: '"Baloo 2", sans-serif',
            transition: 'background-color 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (stripe && !loading) {
              e.target.style.backgroundColor = '#5a3eef';
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = '#6B4EFF';
          }}
        >
          {loading ? 'Traitement...' : `S'abonner pour ${(selectedPlan.price_monthly / 100).toFixed(2).replace('.', ',')}€/mois`}
        </button>
      </div>

      {/* Message de sécurité */}
      <div style={{
        marginTop: '12px',
        marginBottom: '20px',
        textAlign: 'center',
        fontSize: '11px',
        color: '#999',
        fontFamily: '"Baloo 2", sans-serif'
      }}>
        🔒 Vos informations de paiement sont sécurisées et cryptées. Vous pouvez annuler votre abonnement à tout moment.
      </div>
    </form>
  );
};

const SubscriptionManagement = ({ subscription, onCancel, onClose }) => {
  const [loading, setLoading] = useState(false);

  const handleCancelSubscription = async () => {
    if (!confirm('Êtes-vous sûr de vouloir annuler votre abonnement ? Il restera actif jusqu\'à la fin de la période en cours.')) {
      return;
    }

    setLoading(true);
    try {
      await cancelSubscription(subscription.user_id);
      alert('Votre abonnement a été annulé. Il restera actif jusqu\'à la fin de la période en cours.');
      onCancel();
    } catch (error) {
      console.error('Erreur annulation:', error);
      alert('Erreur lors de l\'annulation de l\'abonnement');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      fontFamily: '"Baloo 2", sans-serif'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h3 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#1a1a1a',
          marginBottom: '8px'
        }}>
          Gestion de l'abonnement
        </h3>
        <div style={{
          backgroundColor: '#f0fdf4',
          border: '1px solid #bbf7d0',
          borderRadius: '12px',
          padding: '12px'
        }}>
          <div style={{
            color: '#166534',
            fontWeight: '500',
            fontSize: '15px'
          }}>
            Plan {subscription.subscription_plans.name} actif
          </div>
          <div style={{
            color: '#16a34a',
            fontSize: '13px',
            marginTop: '6px'
          }}>
            Prochaine facturation: {formatDate(subscription.current_period_end)}
          </div>
        </div>
      </div>

      <div style={{
        backgroundColor: '#eff6ff',
        border: '1px solid #bfdbfe',
        borderRadius: '12px',
        padding: '12px'
      }}>
        <div style={{
          color: '#1e40af',
          fontWeight: '500',
          fontSize: '15px'
        }}>
          Tokens disponibles: {subscription.tokens_remaining}
        </div>
        <div style={{
          color: '#2563eb',
          fontSize: '13px',
          marginTop: '6px'
        }}>
          Tokens utilisés ce mois: {subscription.tokens_used_this_month || 0}
        </div>
      </div>

      <div style={{
        backgroundColor: '#f9fafb',
        borderRadius: '12px',
        padding: '12px'
      }}>
        <h4 style={{
          fontWeight: '500',
          color: '#1a1a1a',
          marginBottom: '10px',
          fontSize: '15px'
        }}>
          Détails de l'abonnement
        </h4>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          fontSize: '13px',
          color: '#6b7280'
        }}>
          <div>Prix: {(subscription.subscription_plans.price_monthly / 100).toFixed(2).replace('.', ',')}€/mois</div>
          <div>Début de période: {formatDate(subscription.current_period_start)}</div>
          <div>Fin de période: {formatDate(subscription.current_period_end)}</div>
          <div>Status: {subscription.status === 'active' ? 'Actif' : subscription.status}</div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '4px'
      }}>
        <button
          onClick={onClose}
          style={{
            flex: 1,
            backgroundColor: '#e5e7eb',
            color: '#1f2937',
            padding: '10px 14px',
            borderRadius: '8px',
            fontWeight: '500',
            border: 'none',
            cursor: 'pointer',
            fontSize: '14px',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.backgroundColor = '#d1d5db'}
          onMouseLeave={(e) => e.target.style.backgroundColor = '#e5e7eb'}
        >
          Fermer
        </button>
        <button
          onClick={handleCancelSubscription}
          disabled={loading || subscription.cancel_at_period_end}
          style={{
            flex: 1,
            backgroundColor: subscription.cancel_at_period_end ? '#9ca3af' : '#dc2626',
            color: 'white',
            padding: '10px 14px',
            borderRadius: '8px',
            fontWeight: '500',
            border: 'none',
            cursor: (loading || subscription.cancel_at_period_end) ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            opacity: (loading || subscription.cancel_at_period_end) ? 0.5 : 1,
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => {
            if (!loading && !subscription.cancel_at_period_end) {
              e.target.style.backgroundColor = '#b91c1c';
            }
          }}
          onMouseLeave={(e) => {
            if (!loading && !subscription.cancel_at_period_end) {
              e.target.style.backgroundColor = '#dc2626';
            }
          }}
        >
          {loading ? 'Annulation...' : 'Annuler l\'abonnement'}
        </button>
      </div>

      {subscription.cancel_at_period_end && (
        <div style={{
          backgroundColor: '#fff7ed',
          border: '1px solid #fed7aa',
          borderRadius: '12px',
          padding: '10px',
          marginTop: '4px',
          marginBottom: '12px'
        }}>
          <div style={{
            color: '#9a3412',
            fontSize: '13px'
          }}>
            ⚠️ Votre abonnement sera annulé le {formatDate(subscription.current_period_end)}
          </div>
        </div>
      )}
    </div>
  );
};

const SubscriptionModal = ({ isOpen, onClose, userId, userEmail }) => {
  const [currentStep, setCurrentStep] = useState('plans'); // 'plans', 'payment', 'management'
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen && userId) {
      loadUserSubscription();
    }
  }, [isOpen, userId]);

  const loadUserSubscription = async () => {
    try {
      const subscription = await getUserSubscription(userId);
      setCurrentSubscription(subscription);
    } catch (error) {
      console.error('Erreur chargement abonnement:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setCurrentStep('payment');
  };

  const handlePaymentSuccess = () => {
    setCurrentStep('plans');
    setSelectedPlan(null);
    loadUserSubscription(); // Recharger l'abonnement
    alert('🎉 Félicitations ! Votre abonnement a été activé avec succès.');
  };

  const handleCancel = () => {
    setCurrentStep('plans');
    setSelectedPlan(null);
  };

  const handleClose = () => {
    setCurrentStep('plans');
    setSelectedPlan(null);
    onClose();
  };

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  const isPaymentStep = currentStep === 'payment';
  const isManagementStep = currentStep === 'management';

  const modalContent = (
    <div className="subscription-modal-overlay" onClick={handleOverlayClick}>
      <motion.div
        className={`subscription-modal-content ${isPaymentStep ? 'subscription-modal-payment' : ''} ${isManagementStep ? 'subscription-modal-management' : ''}`}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ duration: 0.3 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="subscription-modal-header">
          <h2>
            {currentSubscription ? 'Mon abonnement' : 'Choisir un abonnement'}
          </h2>
          <button
            onClick={handleClose}
            className="subscription-modal-close"
            aria-label="Fermer"
          >
            ×
          </button>
        </div>

        {loading ? (
          <div className="subscription-modal-loading">
            <div className="subscription-modal-spinner"></div>
          </div>
        ) : (
              <>
                {currentStep === 'plans' && (
                  <SubscriptionPlans
                    onSelectPlan={handleSelectPlan}
                    currentSubscription={currentSubscription}
                  />
                )}

                {currentStep === 'payment' && selectedPlan && (
                  <Elements stripe={stripePromise}>
                    <SubscriptionForm
                      selectedPlan={selectedPlan}
                      onSuccess={handlePaymentSuccess}
                      onCancel={handleCancel}
                      userId={userId}
                      userEmail={userEmail}
                    />
                  </Elements>
                )}

                {currentStep === 'management' && currentSubscription && (
                  <SubscriptionManagement
                    subscription={currentSubscription}
                    onCancel={loadUserSubscription}
                    onClose={handleClose}
                  />
                )}

                {currentSubscription && currentStep === 'plans' && (
                  <div style={{ marginTop: '1.2rem', paddingTop: '1rem', borderTop: '1px solid rgba(107, 78, 255, 0.12)', textAlign: 'center' }}>
                    <button
                      onClick={() => setCurrentStep('management')}
                      className="plan-button primary"
                      style={{ maxWidth: '300px', margin: '0.5rem auto 0.75rem auto' }}
                    >
                      Gérer mon abonnement
                    </button>
                  </div>
                )}
              </>
            )}
      </motion.div>
    </div>
  );

  // Utiliser ReactDOM.createPortal pour rendre le modal directement dans le body
  return ReactDOM.createPortal(modalContent, document.body);
};

export default SubscriptionModal;
