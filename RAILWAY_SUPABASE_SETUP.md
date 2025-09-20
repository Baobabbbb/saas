# 🔧 Configuration Supabase sur Railway

## Problème identifié
La liaison entre FRIDAY et Supabase ne fonctionne pas car les variables d'environnement Supabase ne sont pas configurées sur Railway.

## Variables à ajouter sur Railway

### Service Principal (saas)
Allez dans **Variables d'environnement** du service `saas` et ajoutez:

```bash
VITE_SUPABASE_URL=https://xfbmdeuzuyixpmouhqcv.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw
```

⚠️ **IMPORTANT**: Ces variables doivent avoir le préfixe `VITE_` pour être injectées lors du build par Vite.

## Configuration CORS Supabase

1. **Allez dans votre dashboard Supabase**: https://supabase.com/dashboard/project/xfbmdeuzuyixpmouhqcv
2. **Authentication > Settings**
3. **Site URL**: Ajoutez votre URL Railway (ex: `https://saas-production-xxxx.up.railway.app`)
4. **Redirect URLs**: Ajoutez aussi votre URL Railway

## Test après configuration

1. **Redéployez le service** sur Railway après avoir ajouté les variables
2. **Ouvrez la console** du navigateur sur votre site Railway
3. **Cherchez les messages**:
   - ✅ `"Connexion Supabase OK"` = Succès
   - ❌ Messages d'erreur avec détails

## Diagnostic supplémentaire

Si ça ne fonctionne toujours pas, vérifiez:

- Les variables sont bien définies (Railway > Variables d'environnement)
- Le redéploiement s'est bien fait après ajout des variables
- Les URLs dans Supabase incluent votre domaine Railway
- Les logs de la console montrent les vraies URLs (pas les valeurs par défaut)

## Logs utiles

Cherchez dans la console:
```
🚀 FRIDAY: Initialisation Supabase client
🔗 URL: https://xfbmdeuzuyixpmouhqcv.supabase.co
🔑 Clé présente: true
🧪 FRIDAY: Test connexion Supabase...
```

Si l'URL ou la clé sont incorrectes, les variables ne sont pas bien injectées.
