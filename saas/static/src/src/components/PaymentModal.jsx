import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { createPaymentSession, getContentPrice } from '../services/payment'
import './PaymentModal.css'

const PaymentModal = ({
  contentType,
  selectedDuration,
  numPages,
  selectedVoice,
  userId,
  userEmail,
  onSuccess,
  onCancel
}) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Préparer les options selon le type de contenu
  let options = {};

  if (contentType === 'animation') {
    options.duration = selectedDuration;
  } else if (contentType === 'comic' || contentType === 'bd') {
    options.pages = numPages || 1; // Par défaut 1 page si non défini
  }

  // NORMALISATION: Toujours utiliser 'histoire' au lieu de 'audio'
  const normalizedContentType = contentType === 'audio' ? 'histoire' : contentType;
  const priceInfo = getContentPrice(normalizedContentType, options)
  
  const handlePayment = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Pour le moment, on simule un paiement réussi
      // Plus tard, on intégrera Stripe Checkout réel

      // Simuler un délai de paiement
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Simuler un paiement réussi (90% de réussite)
      const paymentSuccess = Math.random() > 0.1

      if (paymentSuccess) {
        // Ici on devrait marquer la permission dans la base
        // Pour le moment, on simule juste le succès
        
        onSuccess({
          success: true,
          message: 'Paiement réussi ! Vous pouvez maintenant générer votre contenu.',
          paymentId: `sim_${Date.now()}`
        })
      } else {
        throw new Error('Échec du paiement simulé')
      }
      
    } catch (error) {
      console.error('Erreur paiement:', error)
      setError('Erreur lors du paiement. Veuillez réessayer.')
    } finally {
      setLoading(false)
    }
  }
  
  const getContentTypeDisplay = (type) => {
    const types = {
      animation: '🎬 Animation',
      coloring: '🎨 Coloriage',
      comic: '💬 Bande dessinée',
      story: '📖 Histoire audio',
      rhyme: '🎵 Comptine'
    }
    return types[type] || type
  }
  
  return (
    <motion.div 
      className="payment-modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div 
        className="payment-modal"
        initial={{ scale: 0.8, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.8, y: 50 }}
        transition={{ type: "spring", damping: 25, stiffness: 500 }}
      >
        <div className="payment-header">
          <h2>💳 Paiement requis</h2>
          <p>Pour créer votre contenu personnalisé</p>
        </div>
        
        <div className="payment-content">
          <div className="content-info">
            <div className="content-type">
              {getContentTypeDisplay(contentType)}
            </div>
            <div className="content-description">
              {priceInfo.description}
            </div>
          </div>
          
          <div className="price-display">
            <div className="price-amount">{priceInfo.amount}€</div>
            <div className="price-label">Prix unique</div>
          </div>
          
          <div className="payment-benefits">
            <h4>✅ Ce que vous obtenez :</h4>
            <ul>
              <li>Contenu 100% personnalisé avec IA</li>
              <li>Génération en haute qualité</li>
              <li>Téléchargement illimité</li>
              <li>Support technique</li>
              <li>Accès permanent à votre création</li>
            </ul>
          </div>
          
          {error && (
            <div className="payment-error">
              <span className="error-icon">⚠️</span>
              <span className="error-message">{error}</span>
            </div>
          )}
        </div>
        
        <div className="payment-actions">
          <motion.button 
            className="payment-button"
            onClick={handlePayment}
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Traitement...
              </>
            ) : (
              <>
                <span className="button-icon">💳</span>
                Payer {priceInfo.amount}€
              </>
            )}
          </motion.button>
          
          <motion.button 
            className="cancel-button"
            onClick={onCancel}
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Annuler
          </motion.button>
        </div>
        
        <div className="payment-footer">
          <p>🔒 Paiement sécurisé avec Stripe</p>
          <p>💡 Mode simulation pour les tests</p>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default PaymentModal






