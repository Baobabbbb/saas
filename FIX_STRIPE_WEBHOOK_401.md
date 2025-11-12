# 🔧 Fix Webhook Stripe 401 Unauthorized

## 🐛 Problème

Stripe ne parvient pas à envoyer des webhooks à l'endpoint Supabase :
- **Erreur** : `401 Unauthorized`
- **Cause** : Supabase Edge Functions nécessitent une authentification JWT par défaut (`verify_jwt: true`)
- **Impact** : 132 tentatives échouées depuis le 9 novembre 2025

## ✅ Solution

Désactiver `verify_jwt` pour la fonction `stripe-webhook` dans le fichier `config.toml` de Supabase.

### 📋 Étapes de Configuration

1. **Modifier `backend/supabase/config.toml`** :
   - Ajouter la section suivante à la fin du fichier :
   ```toml
   [functions.stripe-webhook]
   verify_jwt = false
   ```

2. **Déployer la configuration** :
   - La configuration sera automatiquement appliquée lors du prochain déploiement
   - Ou utiliser `supabase functions deploy stripe-webhook` pour redéployer la fonction

### 🔒 Sécurité

La fonction vérifie toujours la signature Stripe (ligne 32 de `stripe-webhook/index.ts`), donc la sécurité est maintenue. Seule l'authentification JWT Supabase est désactivée, car Stripe n'a pas de token JWT.

### 🔍 Vérification

Après configuration, Stripe devrait pouvoir envoyer les webhooks avec succès. Vérifier dans :
- **Dashboard Stripe** : Section "Webhooks" → Voir les événements récents
- **Logs Supabase** : `mcp_supabase_get_logs` pour `edge-function` → `stripe-webhook`

### 📝 Note

La clé anonyme Supabase (`anon key`) est publique et peut être utilisée pour authentifier les requêtes vers les Edge Functions. Elle est différente de la `service_role_key` qui a des permissions élevées.

---

**Date** : 11 novembre 2025  
**Status** : ⚠️ En attente de configuration dans Stripe Dashboard


