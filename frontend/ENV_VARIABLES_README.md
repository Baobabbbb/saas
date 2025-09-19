# 🔧 Variables d'Environnement FRIDAY Frontend

## Variables Requises

### Supabase (OBLIGATOIRE)
```bash
VITE_SUPABASE_URL=https://xfbmdeuzuyixpmouhqcv.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw
```

### APIs (Optionnel - pour développement local)
```bash
VITE_API_BASE_URL=http://localhost:8006
VITE_ANIMATION_API_BASE_URL=http://localhost:8007
```

## 🚀 Configuration Railway

1. **Allez dans votre projet Railway**
2. **Variables d'environnement**
3. **Ajoutez ces variables :**

```
VITE_SUPABASE_URL=https://xfbmdeuzuyixpmouhqcv.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw
```

## 🧪 Test de Connexion

Après déploiement, testez avec :
`https://votre-domaine-railway.up.railway.app/test-supabase-connection.html`

## ✅ Vérifications

- ✅ Variables avec préfixe `VITE_` (obligatoire pour Vite)
- ✅ URL Supabase correcte
- ✅ Clé API valide (non expirée)
- ✅ Origines CORS configurées dans Supabase
- ✅ Tables `profiles` et `creations` créées
