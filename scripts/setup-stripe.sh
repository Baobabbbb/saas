#!/bin/bash

# 🔧 Script de configuration automatique des produits Stripe
# Ce script crée les produits et prix Stripe automatiquement

echo "🚀 Configuration des produits Stripe pour Herbbie..."
echo ""

# Vérifier que curl est installé
if ! command -v curl &> /dev/null; then
    echo "❌ curl n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Variables
SUPABASE_URL="https://xfbmdeuzuyixpmouhqcv.supabase.co"
FUNCTION_NAME="setup-stripe-products"

echo "📋 Instructions :"
echo ""
echo "1. Connectez-vous sur https://herbbie.com avec votre compte ADMIN"
echo "2. Ouvrez la console du navigateur (F12)"
echo "3. Tapez : JSON.parse(localStorage.getItem('sb-xfbmdeuzuyixpmouhqcv-auth-token')).access_token"
echo "4. Copiez le token affiché"
echo ""
echo -n "Collez votre token d'authentification ici : "
read AUTH_TOKEN

if [ -z "$AUTH_TOKEN" ]; then
    echo "❌ Token vide. Abandon."
    exit 1
fi

echo ""
echo "⏳ Exécution de la configuration..."
echo ""

# Appeler la fonction Edge
RESPONSE=$(curl -s -X POST \
  "$SUPABASE_URL/functions/v1/$FUNCTION_NAME" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json")

# Vérifier la réponse
if echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✅ Configuration Stripe réussie !"
    echo ""
    echo "📊 Résultats :"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "🎉 Prochaines étapes :"
    echo "1. Vérifiez vos produits sur https://dashboard.stripe.com/products"
    echo "2. Les utilisateurs peuvent maintenant s'abonner via la popup"
else
    echo "❌ Erreur lors de la configuration :"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

