import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import {
  getSubscriptionPlans,
  getUserSubscription,
  createSubscription,
  cancelSubscription,
  getUserTokens
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
    // Prix PAY-PER-USE (en centimes)
    const payPerUse = {
      histoire: 79,      // 0,79€
      coloring: 99,      // 0,99€
      comic: 149,        // 1,49€ par page
      rhyme: 149,        // 1,49€
      animation30: 799,  // 7,99€
      animation60: 1199  // 11,99€
    };

    // Coûts API réels (en centimes)
    const apiCosts = {
      histoire: 15,      // 0,15€
      coloring: 20,      // 0,20€
      comic: 20,         // 0,20€
      rhyme: 17,         // 0,17€
      animation30: 610,  // 6,10€
      animation60: 915   // 9,15€
    };

    const plans = {
      'Découverte': {
        price: 499,  // 4,99€ | Budget API max: 2,50€ (50% de marge)
        generations: {
          histoire: 10,     // Coût API: 1,50€ | Valeur vente: 7,90€
          coloring: 5,      // Coût API: 1,00€ | Valeur vente: 4,95€
          comic: 0,         // Non inclus
          rhyme: 0,         // Non inclus
          animation30: 0,   // Non inclus
          animation60: 0    // Non inclus
        }
        // Total coûts API: 2,50€ | Marge: 2,49€ (50%)
      },
      'Famille': {
        price: 999,  // 9,99€ | Budget API max: 5,00€ (50% de marge)
        generations: {
          histoire: 20,     // Coût API: 3,00€ | Valeur vente: 15,80€
          coloring: 10,     // Coût API: 2,00€ | Valeur vente: 9,90€
          comic: 0,         // Non inclus
          rhyme: 0,         // Non inclus
          animation30: 0,   // Non inclus (6,10€ trop cher)
          animation60: 0    // Non inclus
        }
        // Total coûts API: 5,00€ | Marge: 4,99€ (50%)
      },
      'Créatif': {
        price: 1999,  // 19,99€ | Budget API max: 10,00€ (50% de marge)
        generations: {
          histoire: 40,     // Coût API: 6,00€ | Valeur vente: 31,60€
          coloring: 20,     // Coût API: 4,00€ | Valeur vente: 19,80€
          comic: 0,         // Non inclus
          rhyme: 0,         // Non inclus
          animation30: 0,   // Non inclus (trop cher)
          animation60: 0    // Non inclus
        }
        // Total coûts API: 10,00€ | Marge: 9,99€ (50%)
      },
      'Institut': {
        price: 4999,  // 49,99€ | Budget API max: 25,00€ (50% de marge)
        generations: {
          histoire: 100,    // Coût API: 15,00€ | Valeur vente: 79,00€
          coloring: 50,     // Coût API: 10,00€ | Valeur vente: 49,50€
          comic: 0,         // Non inclus
          rhyme: 0,         // Non inclus
          animation30: 0,   // Non inclus
          animation60: 0    // Non inclus
        }
        // Total coûts API: 25,00€ | Marge: 24,99€ (50%)
      }
    };

    const plan = plans[planName];
    if (!plan) return {};

    // Calculer la valeur totale pay-per-use
    const totalValue = 
      (plan.generations.histoire * payPerUse.histoire) +
      (plan.generations.coloring * payPerUse.coloring) +
      (plan.generations.comic * payPerUse.comic) +
      (plan.generations.rhyme * payPerUse.rhyme) +
      (plan.generations.animation30 * payPerUse.animation30) +
      (plan.generations.animation60 * payPerUse.animation60);

    const savings = Math.round(((totalValue - plan.price) / totalValue) * 100);

    const featuresList = [];
    if (plan.generations.histoire > 0) featuresList.push(`${plan.generations.histoire} histoires`);
    if (plan.generations.coloring > 0) featuresList.push(`${plan.generations.coloring} coloriages`);
    if (plan.generations.comic > 0) featuresList.push(`${plan.generations.comic} pages de BD`);
    if (plan.generations.rhyme > 0) featuresList.push(`${plan.generations.rhyme} comptines`);
    if (plan.generations.animation30 > 0) featuresList.push(`${plan.generations.animation30} animation${plan.generations.animation30 > 1 ? 's' : ''} 30s`);
    if (plan.generations.animation60 > 0) featuresList.push(`${plan.generations.animation60} animation${plan.generations.animation60 > 1 ? 's' : ''} 1min`);

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

  return (
    <div className="subscription-plans-grid">
      {plans.map((plan) => {
        const features = getPlanFeatures(plan.name);
        const isCurrentPlan = currentSubscription?.subscription_plans?.name === plan.name;

        return (
          <div
            key={plan.id}
            className={`subscription-plan-card ${isCurrentPlan ? 'active' : ''}`}
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

const SubscriptionForm = ({ selectedPlan, onSuccess, onCancel, userId, userEmail }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [cardholderName, setCardholderName] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      setError('Stripe n\'est pas chargé');
      return;
    }

    if (!cardholderName.trim()) {
      setError('Le nom du titulaire de la carte est requis');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Créer le payment method
      const cardElement = elements.getElement(CardElement);
      const { error: paymentMethodError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
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

  const cardStyle = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
        fontFamily: 'Inter, system-ui, sans-serif',
      },
      invalid: {
        color: '#9e2146',
      },
    },
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          S'abonner à {selectedPlan.name}
        </h3>
        <div className="bg-violet-50 p-4 rounded-lg mb-6">
          <div className="text-lg font-semibold text-violet-800">
            {(selectedPlan.price_monthly / 100).toFixed(2).replace('.', ',')}€/mois
          </div>
          <div className="text-sm text-violet-600">
            Facturé mensuellement • Annulable à tout moment
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Nom du titulaire de la carte
        </label>
        <input
          type="text"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
          placeholder="Jean Dupont"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Informations de carte bancaire
        </label>
        <div className="border border-gray-300 rounded-md p-3 focus-within:ring-2 focus-within:ring-violet-500 focus-within:border-violet-500">
          <CardElement options={cardStyle} />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <div className="text-red-800 text-sm">{error}</div>
        </div>
      )}

      <div className="flex space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 bg-gray-200 text-gray-800 py-3 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors duration-200"
          disabled={loading}
        >
          Annuler
        </button>
        <button
          type="submit"
          className="flex-1 bg-violet-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-violet-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading || !stripe}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Traitement...
            </div>
          ) : (
            `S'abonner pour ${(selectedPlan.price_monthly / 100).toFixed(2).replace('.', ',')}€/mois`
          )}
        </button>
      </div>

      <div className="text-xs text-gray-500 text-center">
        Vos informations de paiement sont sécurisées et cryptées.
        Vous pouvez annuler votre abonnement à tout moment.
      </div>
    </form>
  );
};

const SubscriptionManagement = ({ subscription, onCancel, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [tokensInfo, setTokensInfo] = useState(null);

  useEffect(() => {
    loadTokensInfo();
  }, []);

  const loadTokensInfo = async () => {
    try {
      const { totalTokens } = await getUserTokens(subscription.user_id);
      setTokensInfo({ totalTokens });
    } catch (error) {
      console.error('Erreur chargement tokens:', error);
    }
  };

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
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          Gestion de l'abonnement
        </h3>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-green-800 font-medium">
            Plan {subscription.subscription_plans.name} actif
          </div>
          <div className="text-green-600 text-sm mt-1">
            Prochaine facturation: {formatDate(subscription.current_period_end)}
          </div>
        </div>
      </div>

      {tokensInfo && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-blue-800 font-medium">
            Tokens disponibles: {tokensInfo.totalTokens}
          </div>
          <div className="text-blue-600 text-sm mt-1">
            Tokens utilisés ce mois: {subscription.tokens_used_this_month || 0}
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Détails de l'abonnement</h4>
        <div className="space-y-2 text-sm text-gray-600">
          <div>Prix: {(subscription.subscription_plans.price_monthly / 100).toFixed(2).replace('.', ',')}€/mois</div>
          <div>Début de période: {formatDate(subscription.current_period_start)}</div>
          <div>Fin de période: {formatDate(subscription.current_period_end)}</div>
          <div>Status: {subscription.status === 'active' ? 'Actif' : subscription.status}</div>
        </div>
      </div>

      <div className="flex space-x-3">
        <button
          onClick={onClose}
          className="flex-1 bg-gray-200 text-gray-800 py-3 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors duration-200"
        >
          Fermer
        </button>
        <button
          onClick={handleCancelSubscription}
          className="flex-1 bg-red-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading || subscription.cancel_at_period_end}
        >
          {loading ? 'Annulation...' : 'Annuler l\'abonnement'}
        </button>
      </div>

      {subscription.cancel_at_period_end && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
          <div className="text-orange-800 text-sm">
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

  const modalContent = (
    <div className="subscription-modal-overlay" onClick={handleOverlayClick}>
      <motion.div
        className="subscription-modal-content"
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
                  <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(107, 78, 255, 0.1)', textAlign: 'center' }}>
                    <button
                      onClick={() => setCurrentStep('management')}
                      className="plan-button primary"
                      style={{ maxWidth: '300px', margin: '0 auto' }}
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
