# 🎨 HERBBIE - Backend SaaS

## 📋 Vue d'ensemble

Backend FastAPI pour la plateforme HERBBIE - génération de contenu créatif pour enfants avec IA.

## 🏗️ Architecture

```
backend/
├── saas/                     # Application principale
│   ├── main.py               # Point d'entrée FastAPI
│   ├── requirements.txt      # Dépendances Python
│   ├── services/             # Services métier
│   │   ├── cartoon_engine.py       # Dessins animés (WAN 2.5)
│   │   ├── coloring_generator_gpt4o.py  # Coloriages
│   │   ├── comics_generator_gpt4o.py    # Bandes dessinées
│   │   ├── suno_service.py             # Comptines musicales
│   │   ├── story_service.py            # Histoires
│   │   ├── supabase_storage.py         # Stockage cloud
│   │   └── uniqueness_service.py       # Anti-duplication
│   ├── schemas/              # Modèles Pydantic
│   ├── routes/               # Routes API
│   ├── static/               # Frontend build
│   └── config/               # Configuration
├── frontend/                 # Code source React
│   ├── src/
│   │   ├── components/       # Composants UI
│   │   ├── services/         # Services API
│   │   └── config/           # Configuration
│   └── vite.config.js
└── supabase/                 # Fonctions Edge Supabase
```

## 🎯 Fonctionnalités

### Types de contenu
- 🎬 **Dessins animés** : 30s à 5min (WaveSpeed WAN 2.5 Text-to-Video 1080p)
- 📖 **Histoires** : Audio avec narration (OpenAI TTS)
- 🎨 **Coloriages** : Par thème ou photo (gpt-image-1, Gemini)
- 💬 **Bandes dessinées** : 1 à 10 pages (gpt-image-1)
- 🎵 **Comptines** : Avec musique (Suno AI)

## 🔧 Technologies

- **Backend** : FastAPI, Python 3.11
- **Frontend** : React 18, Vite
- **Base de données** : Supabase (PostgreSQL)
- **Stockage** : Supabase Storage
- **Paiements** : Stripe
- **APIs IA** :
  - OpenAI (GPT-4o-mini, TTS, gpt-image-1)
  - Google Gemini (gemini-3-pro-image-preview)
  - WaveSpeed (WAN 2.5 Text-to-Video Fast 1080p)
  - Suno AI (musique)

## 🚀 Déploiement

Le projet est déployé sur **Railway** avec build automatique via Nixpacks.

### Variables d'environnement requises
```
OPENAI_API_KEY=...
FAL_API_KEY=...
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
STRIPE_SECRET_KEY=...
SUNO_API_KEY=...
```

## 📊 API Endpoints principaux

- `POST /generate_audio_story/` - Générer une histoire
- `POST /generate_coloring/` - Générer un coloriage
- `POST /generate_comic/` - Générer une BD
- `POST /generate_rhyme/` - Générer une comptine
- `GET /generate-quick` - Générer un dessin animé

---

*Dernière mise à jour : Décembre 2025*
