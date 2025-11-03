import React, { useState, useEffect } from 'react';
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

const stripePromise = (import.meta.env?.VITE_STRIPE_PUBLISHABLE_KEY &&
  typeof import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY === 'string' &&
  import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY.length > 0)
  ? loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
  : Promise.resolve(null);

const SubscriptionPlans = ({ onSelectPlan, currentSubscription }) => {
  console.log('SubscriptionPlans rendu avec currentSubscription:', currentSubscription);
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
    const features = {
      'Découverte': {
        tokens: '50 tokens/mois',
        features: [
          'Histoires & Audio: 3 tokens',
          'Coloriages: 2 tokens',
          'BD: 4 tokens/page',
          'Comptines: 5 tokens',
          'Animations: 10 tokens'
        ],
        ideal: 'Parfait pour découvrir Herbbie'
      },
      'Famille': {
        tokens: '150 tokens/mois',
        features: [
          'Histoires & Audio: 3 tokens',
          'Coloriages: 2 tokens',
          'BD: 3 tokens/page',
          'Comptines: 4 tokens',
          'Animations: 8 tokens'
        ],
        ideal: 'Pour les familles actives'
      },
      'Créatif': {
        tokens: '400 tokens/mois',
        features: [
          'Histoires & Audio: 2 tokens',
          'Coloriages: 1 token',
          'BD: 2 tokens/page',
          'Comptines: 3 tokens',
          'Animations: 5 tokens'
        ],
        ideal: 'Pour les créateurs intensifs'
      },
      'Institut': {
        tokens: '1,200 tokens/mois',
        features: [
          'Histoires & Audio: 1 token',
          'Coloriages: 1 token',
          'BD: 1 token/page',
          'Comptines: 2 tokens',
          'Animations: 3 tokens'
        ],
        ideal: 'Pour les écoles et institutions'
      }
    };
    return features[planName] || {};
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {plans.map((plan) => {
        const features = getPlanFeatures(plan.name);
        const isCurrentPlan = currentSubscription?.subscription_plans?.name === plan.name;

        return (
          <motion.div
            key={plan.id}
            className={`relative bg-white rounded-xl p-6 border-2 transition-all duration-300 ${
              isCurrentPlan
                ? 'border-violet-500 shadow-lg shadow-violet-200'
                : 'border-gray-200 hover:border-violet-300 hover:shadow-md'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isCurrentPlan && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-violet-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Plan actuel
                </span>
              </div>
            )}

            <div className="text-center mb-4">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
              <div className="text-3xl font-bold text-violet-600 mb-1">
                {(plan.price_monthly / 100).toFixed(2).replace('.', ',')}€
              </div>
              <div className="text-sm text-gray-500">par mois</div>
              <div className="text-lg font-semibold text-gray-700 mt-2">
                {features.tokens}
              </div>
            </div>

            <div className="space-y-2 mb-6">
              {features.features?.map((feature, index) => (
                <div key={index} className="flex items-center text-sm text-gray-600">
                  <span className="text-green-500 mr-2">✓</span>
                  {feature}
                </div>
              ))}
            </div>

            <div className="text-center mb-4">
              <div className="text-xs text-gray-500 italic">
                {features.ideal}
              </div>
            </div>

            {!isCurrentPlan && (
              <button
                onClick={() => onSelectPlan(plan)}
                className="w-full bg-violet-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-violet-700 transition-colors duration-200"
              >
                Choisir ce plan
              </button>
            )}

            {isCurrentPlan && (
              <div className="w-full bg-gray-100 text-gray-600 py-3 px-4 rounded-lg font-medium text-center">
                Plan actif
              </div>
            )}
          </motion.div>
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

  // Vérifier si Stripe est disponible
  if (!stripe) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 font-medium mb-4">
          Configuration Stripe manquante
        </div>
        <div className="text-gray-600 text-sm">
          Le système de paiement n'est pas encore configuré. Veuillez réessayer plus tard.
        </div>
        <button
          onClick={onCancel}
          className="mt-4 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors duration-200"
        >
          Fermer
        </button>
      </div>
    );
  }

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
  console.log('SubscriptionModal rendu avec isOpen:', isOpen, 'userId:', userId, 'userEmail:', userEmail);

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

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(107, 78, 255, 0.3) transparent' }}
        >
          <div className="p-6 md:p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
                {currentSubscription ? 'Mon abonnement' : 'Choisir un abonnement'}
              </h2>
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            {loading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
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
                  <div className="mt-8 pt-6 border-t border-gray-200">
                    <div className="text-center">
                      <button
                        onClick={() => setCurrentStep('management')}
                        className="bg-violet-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-violet-700 transition-colors duration-200"
                      >
                        Gérer mon abonnement
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SubscriptionModal;
