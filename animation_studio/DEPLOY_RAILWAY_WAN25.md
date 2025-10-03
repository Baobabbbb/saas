# 🚀 Guide Déploiement Railway - Animation Studio Wan 2.5

## 📋 Prérequis

- Compte Railway avec projet configuré
- API Keys : OpenAI + Wavespeed
- CLI Railway installée (optionnel)

## 🔑 Variables d'Environnement

### Configuration Railway

Dans l'onglet **Variables** de votre service Railway, ajoutez :

```bash
# ========== APIs REQUISES ==========
OPENAI_API_KEY=sk-proj-votre-cle-openai
WAVESPEED_API_KEY=votre-cle-wavespeed

# ========== CONFIGURATION WAN 2.5 ==========
WAN25_MODEL=alibaba/wan-2.5/text-to-video-fast
WAN25_DEFAULT_RESOLUTION=720p
WAN25_MAX_DURATION=10

# ========== SERVEUR ==========
PORT=8007
HOST=0.0.0.0

# ========== JWT (optionnel mais recommandé) ==========
JWT_SECRET=votre-secret-jwt-securise

# ========== CACHE ==========
CACHE_DIR=./cache
MAX_CACHE_SIZE_GB=10
CACHE_CLEANUP_HOURS=24
```

## 📦 Structure du Projet

```
animation_studio/
├── backend/
│   ├── config.py              ✅ Configuration Wan 2.5
│   ├── main.py                ✅ API FastAPI
│   ├── requirements.txt       ✅ Dépendances nettoyées
│   ├── models/
│   │   └── schemas.py         ✅ Schémas enrichis
│   └── services/
│       ├── idea_generator.py       (inchangé)
│       ├── scene_creator.py        ✅ Adapté Wan 2.5
│       ├── wan25_generator.py      ✅ NOUVEAU
│       ├── animation_pipeline.py   ✅ Pipeline Wan 2.5
│       └── video_assembler.py      ✅ Simplifié
├── MIGRATION_WAN25.md         ✅ Documentation migration
└── DEPLOY_RAILWAY_WAN25.md    📄 Ce fichier
```

## 🛠 Configuration Railway

### 1. Build Settings

```bash
# Build Command (si Railway ne le détecte pas)
pip install -r requirements.txt

# Start Command
python main.py
```

### 2. Procfile (optionnel)

Si Railway ne démarre pas automatiquement, créer un `Procfile` :

```
web: python main.py
```

### 3. Root Directory

Si votre projet est dans un sous-dossier :

```
Root Directory: backend/animation_studio/backend
```

## 🔗 Endpoints API

Une fois déployé, votre API sera accessible à :

```
https://votre-service.railway.app
```

### Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Informations API |
| `/diagnostic` | GET | État des services |
| `/themes` | GET | Thèmes disponibles |
| `/generate` | POST | Générer une animation |
| `/status/{id}` | GET | Statut d'une animation |

## 📝 Tester l'API

### 1. Diagnostic

```bash
curl https://votre-service.railway.app/diagnostic
```

Réponse attendue :
```json
{
  "openai_configured": true,
  "wavespeed_configured": true,
  "wan25_model": "alibaba/wan-2.5/text-to-video-fast",
  "all_systems_operational": true,
  "details": {
    "services": {
      "idea_generator": {"status": "configured"},
      "wan25_generator": {"status": "configured", "audio_integrated": true}
    }
  }
}
```

### 2. Génération Animation

```bash
curl -X POST https://votre-service.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "nature",
    "duration": 30
  }'
```

### 3. Vérifier Statut

```bash
curl https://votre-service.railway.app/status/votre-animation-id
```

## 🎯 Intégration avec Herbbie

### Frontend Configuration

Dans votre fichier `api.js` :

```javascript
const ANIMATION_API_BASE_URL = "https://votre-service-wan25.railway.app";

export const generateAnimation = async (theme, duration) => {
  const response = await fetch(`${ANIMATION_API_BASE_URL}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme, duration })
  });
  return await response.json();
};
```

### Polling Statut

```javascript
export const pollAnimationStatus = async (animationId) => {
  const response = await fetch(
    `${ANIMATION_API_BASE_URL}/status/${animationId}`
  );
  return await response.json();
};
```

## 🎨 Bouton "Dessin animé" Herbbie

Le bouton "Dessin animé" dans Herbbie doit appeler l'API Wan 2.5 déployée.

### Vérifications

1. ✅ Le service est accessible via l'URL Railway
2. ✅ Les variables d'environnement sont configurées
3. ✅ Le diagnostic retourne `all_systems_operational: true`
4. ✅ Le frontend pointe vers la bonne URL Railway

## 🔍 Monitoring

### Logs Railway

```bash
# Via CLI
railway logs

# Via Dashboard
Onglet "Deployments" > Voir les logs
```

### Points à Surveiller

- ✅ **Startup** : "🎬 Animation Studio Wan 2.5 - Démarrage du serveur..."
- ✅ **APIs** : "✅ Clé OpenAI détectée", "✅ Clé Wavespeed détectée"
- ✅ **Config** : "🎨 Résolution par défaut: 720p", "🎵 Audio intégré: True"
- ✅ **Ready** : "🚀 Prêt pour génération Wan 2.5!"

### Erreurs Communes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Module not found` | Dépendances manquantes | Vérifier `requirements.txt` |
| `API Key invalid` | Clé Wavespeed incorrecte | Vérifier variables Railway |
| `Connection timeout` | Service non accessible | Vérifier port et HOST=0.0.0.0 |
| `CORS error` | Frontend bloqué | Vérifier CORS_ORIGINS |

## 💰 Estimation Coûts

### Par Animation (30s)

| Service | Coût | Détails |
|---------|------|---------|
| **OpenAI GPT-4** | ~$0.05 | Idée + Scènes (GPT-4o-mini) |
| **Wan 2.5** | $1.02 | 3 clips × $0.34 (720p, 10s) |
| **Total** | **$1.07** | Audio inclus, pas de FAL AI |

### Économies vs Seedance

- ✅ **-32%** sur vidéo ($1.02 vs $1.50)
- ✅ **-100%** sur audio ($0 vs $0.45, intégré)
- ✅ **-40%** sur temps (6 min vs 10 min)

## 🎉 Checklist Déploiement

### Avant Déploiement

- [ ] Variables d'environnement configurées
- [ ] Clés API valides et actives
- [ ] Code poussé sur GitHub/Railway
- [ ] `requirements.txt` à jour

### Après Déploiement

- [ ] Service démarré sans erreur
- [ ] `/diagnostic` retourne OK
- [ ] Test `/generate` avec durée 30s
- [ ] Frontend Herbbie mis à jour avec nouvelle URL
- [ ] Monitoring actif sur Railway

### Tests Production

- [ ] Génération animation complète (30s)
- [ ] Audio intégré dans clips
- [ ] Vidéo finale accessible
- [ ] Cohérence narrative validée
- [ ] Performance acceptable (<7 min)

## 🚀 Commandes Utiles

### Railway CLI

```bash
# Se connecter
railway login

# Lier le projet
railway link

# Voir les logs en direct
railway logs

# Définir une variable
railway variables set WAVESPEED_API_KEY=votre-cle

# Redéployer
railway up
```

### Debugging

```bash
# Tester en local avant déploiement
cd backend/animation_studio/backend
pip install -r requirements.txt
python main.py

# Vérifier API locale
curl http://localhost:8007/diagnostic
```

## 📞 Support

### Documentation

- [Railway Docs](https://docs.railway.app/)
- [Wan 2.5 API](https://wavespeed.ai/docs/docs-api/alibaba/alibaba-wan-2.5-text-to-video-fast)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Troubleshooting

1. **Logs Railway** : Toujours commencer par les logs
2. **Health Check** : Utiliser `/diagnostic` pour identifier le problème
3. **Variables** : Vérifier que toutes les variables sont définies
4. **Network** : S'assurer que le service écoute sur 0.0.0.0

---

**Version** : Wan 2.5 v1.0  
**Date** : 2 Octobre 2025  
**Status** : ✅ Prêt pour production

