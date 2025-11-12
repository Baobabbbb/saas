# 🔧 Fix Webhook Stripe 401 Unauthorized

## 🐛 Problème

Stripe ne parvient pas à envoyer des webhooks à l'endpoint Supabase :
- **Erreur** : `401 Unauthorized`
- **Cause** : Supabase Edge Functions nécessitent une authentification JWT par défaut (`verify_jwt: true`)
- **Impact** : 132 tentatives échouées depuis le 9 novembre 2025

## ✅ Solution

Configurer Stripe pour envoyer le header `apikey` avec la clé anonyme Supabase dans les paramètres du webhook.

### 📋 Étapes de Configuration

1. **Aller dans le Dashboard Stripe** :
   - https://dashboard.stripe.com/webhooks
   - Sélectionner l'endpoint : `https://xfbmdeuzuyixpmouhqcv.supabase.co/functions/v1/stripe-webhook`

2. **Ajouter le header `apikey`** :
   - Cliquer sur "Modifier" ou "Settings" de l'endpoint
   - Dans la section "Headers" ou "Custom headers", ajouter :
     - **Header name** : `apikey`
     - **Header value** : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw`

3. **Sauvegarder** et tester

### 🔍 Vérification

Après configuration, Stripe devrait pouvoir envoyer les webhooks avec succès. Vérifier dans :
- **Dashboard Stripe** : Section "Webhooks" → Voir les événements récents
- **Logs Supabase** : `mcp_supabase_get_logs` pour `edge-function` → `stripe-webhook`

### 📝 Note

La clé anonyme Supabase (`anon key`) est publique et peut être utilisée pour authentifier les requêtes vers les Edge Functions. Elle est différente de la `service_role_key` qui a des permissions élevées.

---

**Date** : 11 novembre 2025  
**Status** : ⚠️ En attente de configuration dans Stripe Dashboard

