# 🔐 Variables d'Environnement Railway - Service Coloriages SD3

## ✅ Variables Actuelles sur Railway

D'après votre capture d'écran, vous avez déjà **16 variables configurées** :

1. `DATABASE_URL` ⚠️
2. `ENVIRONMENT` ⚠️
3. `FAL_API_KEY` ✅
4. `GOAPI_API_KEY` ✅
5. `IMAGE_MODEL` ✅
6. `JWT_SECRET` ✅
7. `NIXPACKS_PYTHON_VERSION` ⚠️
8. `OPENAI_API_KEY` ✅
9. `STABILITY_API_KEY` ✅
10. `TEXT_MODEL` ✅
11. `TTS_MODEL` ✅
12. `VIDEO_MODEL` ✅
13. `VITE_STRIPE_PUBLISHABLE_KEY` ❌ (pas nécessaire backend)
14. `VITE_SUPABASE_ANON_KEY` ❌ (pas nécessaire backend)
15. `VITE_SUPABASE_URL` ❌ (pas nécessaire backend)
16. `WAVESPEED_API_KEY` ✅

---

## 🆕 Variables à AJOUTER pour SD3 + ControlNet

Ajoutez ces variables dans Railway → Service "saas" → Variables :

### **Essentielles pour Coloriages**
```env
# URL de base pour les images générées (OBLIGATOIRE pour éviter Mixed Content)
BASE_URL=https://herbbie.com

# Note: STABILITY_API_KEY est déjà configurée ✅
```

### **Optionnelles (Recommandées)**
```env
# Configuration avancée SD3
SD3_QUALITY_MODE=professional
SD3_FALLBACK_ENABLED=true
SD3_MAX_BUBBLES_PER_IMAGE=4
SD3_PROCESSING_TIMEOUT=120

# Configuration ControlNet
CONTROLNET_DEFAULT_MODE=canny
CONTROLNET_DEFAULT_STRENGTH=0.7

# URLs base
WAVESPEED_BASE_URL=https://api.wavespeed.ai/api/v3
FAL_BASE_URL=https://queue.fal.run

# Modèles
WAVESPEED_MODEL=bytedance/seedance-v1-pro-t2v-480p
FAL_AUDIO_MODEL=fal-ai/mmaudio-v2
FAL_FFMPEG_MODEL=fal-ai/ffmpeg-api/compose
UDIO_MODEL=music-u
UDIO_TASK_TYPE=generate_music

# Comics
COMIC_VISION_MODEL=gpt-4o
COMIC_TEXT_MODEL=gpt-4o-mini
ENABLE_AI_BUBBLES=false
ENABLE_SD3_BUBBLES=true

# Cartoon
CARTOON_ASPECT_RATIO=16:9
CARTOON_DURATION=15
CARTOON_STYLE=2D cartoon animation, Disney style
CARTOON_QUALITY=high quality animation, smooth movement

# TTS/STT
TTS_MODEL=gpt-4o-mini-tts
STT_MODEL=gpt-4o-mini-transcribe

# Public AI
USE_PUBLIC_AI_MODEL=true
```

---

## 🧹 Variables à SUPPRIMER (Optionnel)

Ces variables ne sont PAS nécessaires côté backend :

```
❌ VITE_STRIPE_PUBLISHABLE_KEY    → Frontend uniquement
❌ VITE_SUPABASE_ANON_KEY          → Frontend uniquement
❌ VITE_SUPABASE_URL                → Frontend uniquement
```

---

## ⚙️ Configuration Nixpacks (Déjà en Place)

Le fichier `saas/nixpacks.toml` est configuré pour installer OpenCV :

```toml
[phases.setup]
nixPkgs = ["python311", "libGL", "libGLU", "opencv4"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**Vérifiez dans Railway Settings → Deploy :**
- **Root Directory** : `saas`
- **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 📊 Résumé des Variables pour SD3 + ControlNet

| Variable | Valeur Actuelle | Status | Action |
|----------|-----------------|--------|--------|
| `STABILITY_API_KEY` | ✅ Configurée | ✅ OK | Aucune |
| `OPENAI_API_KEY` | ✅ Configurée | ✅ OK | Aucune |
| `TEXT_MODEL` | ✅ Configurée | ✅ OK | Aucune |
| `IMAGE_MODEL` | ✅ Configurée | ✅ OK | Aucune |
| `FAL_API_KEY` | ✅ Configurée | ✅ OK | Aucune |
| `WAVESPEED_API_KEY` | ✅ Configurée | ✅ OK | Aucune |
| `GOAPI_API_KEY` | ✅ Configurée | ✅ OK | Aucune |
| `JWT_SECRET` | ✅ Configurée | ✅ OK | Aucune |

**🎉 Toutes les variables essentielles sont déjà configurées !**

---

## 🚀 Prêt pour le Déploiement

Aucune variable supplémentaire n'est **obligatoire** pour que les coloriages SD3 + ControlNet fonctionnent.

Vous pouvez faire le push directement :

```bash
cd C:\Users\freda\Desktop\projet\backend
git add .
git commit -m "feat: Ajout système de coloriages SD3 + ControlNet avec upload photo"
git push origin main
```

Railway détectera automatiquement le push et redéploiera le service ! 🎉

---

## 📝 Notes

- **OpenCV** est installé via `nixpacks.toml`
- **Numpy** est dans `requirements.txt`
- **Root Directory** sur Railway doit être `saas`
- Le service écoutera sur `$PORT` (géré automatiquement par Railway)

---

*Variables Railway - Système Coloriages SD3 + ControlNet*  
*Version 1.0 - Octobre 2025*

