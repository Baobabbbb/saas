# Configuration des Clés API

## ⚠️ Clés API Requises

Pour que l'application fonctionne correctement, vous devez configurer les clés API suivantes dans le fichier `.env` :

### 1. OpenAI API (Requis pour les histoires et comptines)
- **Site** : https://platform.openai.com/api-keys
- **Variable** : `OPENAI_API_KEY=sk-votre-vraie-cle-openai-ici`
- **Usage** : Génération de texte (histoires, comptines)

### 2. Stability AI (Optionnel pour les coloriages améliorés)
- **Site** : https://platform.stability.ai/account/keys
- **Variable** : `STABILITY_API_KEY=sk-votre-vraie-cle-stability-ici`
- **Usage** : Génération d'images pour les coloriages

### 3. Fal AI (Optionnel pour les animations)
- **Site** : https://www.fal.ai/dashboard
- **Variable** : `FAL_API_KEY=votre-vraie-cle-fal-ici`
- **Usage** : Génération de vidéos d'animation

## 📝 Comment configurer

1. Ouvrez le fichier `.env` dans le dossier `saas/saas/`
2. Remplacez les placeholders par vos vraies clés :

```env
# AVANT (ne fonctionne pas)
OPENAI_API_KEY=sk-votre-cle-openai-ici

# APRÈS (exemple avec une vraie clé)
OPENAI_API_KEY=sk-proj-abcd1234...
```

3. Redémarrez le serveur après modification

## 🔍 Diagnostic

Testez la configuration avec : http://localhost:8000/diagnostic

## 💰 Coûts estimés

- **OpenAI** : ~0.01€ par histoire/comptine
- **Stability AI** : ~0.04€ par image de coloriage
- **Fal AI** : ~0.05€ par seconde de vidéo

## 🔄 Fallbacks

Si les clés ne sont pas configurées :
- **Histoires/Comptines** : ❌ Erreur (OpenAI requis)
- **Coloriages** : ✅ Version simplifiée générée localement
- **Animations** : ✅ Message d'erreur explicite
