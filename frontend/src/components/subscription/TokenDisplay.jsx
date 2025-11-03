import React, { useState, useEffect } from 'react';
import { getUserTokens, getUserSubscription } from '../../services/payment';

const TokenDisplay = ({ userId, compact = false }) => {
  const [tokensInfo, setTokensInfo] = useState({ totalTokens: 0, tokens: [] });
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      loadData();
    }
  }, [userId]);

  const loadData = async () => {
    try {
      const [tokensResult, subscriptionResult] = await Promise.all([
        getUserTokens(userId),
        getUserSubscription(userId)
      ]);

      setTokensInfo(tokensResult);
      setSubscription(subscriptionResult);
    } catch (error) {
      console.error('Erreur chargement données tokens:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center ${compact ? 'text-sm' : 'text-base'}`}>
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-violet-600 mr-2"></div>
        <span className="text-gray-500">Chargement...</span>
      </div>
    );
  }

  // Si l'utilisateur a un abonnement actif
  if (subscription) {
    const tokensRemaining = subscription.tokens_remaining || 0;
    const tokensUsed = subscription.tokens_used_this_month || 0;
    const totalTokens = tokensRemaining + tokensUsed;

    return (
      <div className={`flex items-center ${compact ? 'text-sm' : 'text-base'}`}>
        <div className="bg-violet-100 text-violet-800 px-3 py-1 rounded-full font-medium flex items-center">
          <span className="mr-1">🎫</span>
          <span>{tokensRemaining}</span>
          {!compact && (
            <span className="text-violet-600 text-xs ml-1">
              /{totalTokens}
            </span>
          )}
        </div>
        {!compact && (
          <div className="ml-2 text-xs text-gray-600">
            <div>Plan {subscription.subscription_plans?.name}</div>
            <div className="text-gray-500">
              Renouvellement: {new Date(subscription.current_period_end).toLocaleDateString('fr-FR')}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Si l'utilisateur a des tokens payés
  if (tokensInfo.totalTokens > 0) {
    return (
      <div className={`flex items-center ${compact ? 'text-sm' : 'text-base'}`}>
        <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full font-medium flex items-center">
          <span className="mr-1">🎫</span>
          <span>{tokensInfo.totalTokens}</span>
          {!compact && (
            <span className="text-green-600 text-xs ml-1">tokens</span>
          )}
        </div>
        {!compact && (
          <div className="ml-2 text-xs text-gray-600">
            <div>Crédits disponibles</div>
            <div className="text-gray-500">
              {tokensInfo.tokens.length} transaction{tokensInfo.tokens.length > 1 ? 's' : ''}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Aucun token/abonnement
  return (
    <div className={`flex items-center ${compact ? 'text-sm' : 'text-base'}`}>
      <div className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full font-medium flex items-center">
        <span className="mr-1">🎫</span>
        <span>0</span>
        {!compact && (
          <span className="text-gray-500 text-xs ml-1">tokens</span>
        )}
      </div>
      {!compact && (
        <div className="ml-2 text-xs text-gray-600">
          <div>Aucun crédit</div>
          <div className="text-violet-600 cursor-pointer hover:underline">
            S'abonner pour des tokens illimités
          </div>
        </div>
      )}
    </div>
  );
};

export default TokenDisplay;
