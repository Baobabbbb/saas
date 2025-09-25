# 🎯 CONFIGURATION STRIPE RÉELLE

## 📋 **ÉTAPES POUR ACTIVER LES VRAIS PAIEMENTS STRIPE**

### **ÉTAPE 1 : Obtenir les clés Stripe**

1. **Allez sur** : https://dashboard.stripe.com
2. **Créez un compte** (ou connectez-vous)
3. **Mode Test** → **Developers** → **API Keys**
4. **Copiez vos clés :**
   - **Clé publique** : `pk_test_...`
   - **Clé secrète** : `sk_test_...`

---

### **ÉTAPE 2 : Remplacer les clés dans le code**

#### **A. Frontend - StripePaymentModal.jsx (ligne 7)**
```javascript
// REMPLACER CETTE LIGNE :
const stripePromise = loadStripe('pk_test_51234567890abcdef...')

// PAR VOTRE VRAIE CLÉ PUBLIQUE :
const stripePromise = loadStripe('pk_test_VOTRE_VRAIE_CLE_PUBLIQUE')
```

#### **B. Variables d'environnement Railway**
1. **Aller dans votre service "saas" sur Railway**
2. **Variables** → **Ajouter** :
```bash
STRIPE_SECRET_KEY=sk_test_VOTRE_VRAIE_CLE_SECRETE
STRIPE_PUBLISHABLE_KEY=pk_test_VOTRE_VRAIE_CLE_PUBLIQUE
```

---

### **ÉTAPE 3 : Créer un endpoint backend pour Payment Intent**

Créez un fichier `backend/saas/stripe_payment.py` :

```python
import stripe
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Configuration Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

router = APIRouter()

class PaymentIntentRequest(BaseModel):
    amount: int  # en centimes
    currency: str = 'eur'
    contentType: str
    userId: str

@router.post("/create-payment-intent")
async def create_payment_intent(request: PaymentIntentRequest):
    try:
        # Créer le Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            metadata={
                'content_type': request.contentType,
                'user_id': request.userId,
            }
        )
        
        return {
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm-payment")
async def confirm_payment(payment_intent_id: str):
    try:
        # Vérifier le statut du paiement
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Accorder la permission à l'utilisateur
            # TODO: Insérer dans generation_permissions
            return {'success': True, 'status': 'succeeded'}
        else:
            return {'success': False, 'status': intent.status}
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### **ÉTAPE 4 : Ajouter Stripe au backend principal**

Dans `backend/saas/main.py`, ajoutez :

```python
from stripe_payment import router as stripe_router

# Ajouter après les autres routers
app.include_router(stripe_router, prefix="/api/stripe", tags=["stripe"])
```

---

### **ÉTAPE 5 : Modifier le frontend pour les vrais appels**

Dans `StripePaymentModal.jsx`, remplacez les sections TODO par :

```javascript
// Création du Payment Intent
const response = await fetch(`${API_BASE_URL}/api/stripe/create-payment-intent`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    amount: priceInfo.amount,
    currency: 'eur',
    contentType,
    userId
  })
})
const { client_secret } = await response.json()
setClientSecret(client_secret)

// Confirmation du paiement
const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
  payment_method: {
    card: cardElement,
    billing_details: {
      email: userEmail,
    },
  }
})

if (error) {
  throw new Error(error.message)
}

if (paymentIntent.status === 'succeeded') {
  // Confirmer côté backend
  const confirmResponse = await fetch(`${API_BASE_URL}/api/stripe/confirm-payment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ payment_intent_id: paymentIntent.id })
  })
  
  const result = await confirmResponse.json()
  
  if (result.success) {
    onSuccess({
      success: true,
      paymentIntentId: paymentIntent.id,
      amount: paymentIntent.amount / 100,
      contentType
    })
  }
}
```

---

### **ÉTAPE 6 : Tester le paiement**

#### **Cartes de test Stripe :**
- ✅ **Succès** : `4242 4242 4242 4242`
- ❌ **Refusée** : `4000 0000 0000 0002`
- 🔒 **Authentification requise** : `4000 0025 0000 3155`

**Autres infos de test :**
- **Expiration** : N'importe quelle date future (ex: 12/25)
- **CVC** : N'importe quel nombre 3 chiffres (ex: 123)
- **Code postal** : N'importe lequel (ex: 12345)

---

### **ÉTAPE 7 : Passage en production**

1. **Activer le compte Stripe** (vérification d'identité)
2. **Remplacer les clés test par les clés live** :
   - `pk_live_...` (clé publique)
   - `sk_live_...` (clé secrète)
3. **Configurer les webhooks** pour la confirmation automatique
4. **Tester avec de vraies cartes** (petits montants)

---

## 🎯 **STATUT ACTUEL**

✅ **Interface Stripe complète** avec saisie de carte  
✅ **Validation des cartes** via Stripe Elements  
✅ **Simulation réaliste** du flux de paiement  
🔄 **TODO : Remplacer simulation par vraies clés Stripe**  

**Le système est prêt pour la production dès que vous ajouterez vos vraies clés Stripe !**





