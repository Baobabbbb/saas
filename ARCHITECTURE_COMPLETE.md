# 🏗️ ARCHITECTURE COMPLÈTE HERBBIE - DOCUMENTATION TECHNIQUE

*Documentation créée le 2025-01-XX après analyse approfondie du projet*

---

## 📊 VUE D'ENSEMBLE

**HERBBIE** est une plateforme SaaS de génération de contenu créatif pour enfants utilisant l'intelligence artificielle. Le projet est déployé sur **Railway** (backend + frontend) et utilise **Supabase** pour l'authentification et la base de données.

### Stack Technique Principal
- **Backend** : FastAPI (Python 3.11)
- **Frontend** : React 18 + Vite
- **Base de données** : Supabase (PostgreSQL)
- **Authentification** : Supabase Auth
- **Paiements** : Stripe
- **Déploiement** : Railway
- **APIs IA** : OpenAI (GPT-4o-mini, GPT-4o, TTS, gpt-image-1), Google Gemini (gemini-3-pro-image-preview), Runway ML (Veo 3.1), Suno AI

---

## 🗂️ STRUCTURE DU PROJET

```
projet/
├── backend/                          # Dossier principal du backend
│   ├── saas/                         # Application SaaS principale
│   │   ├── main.py                   # Point d'entrée FastAPI (1668 lignes)
│   │   ├── requirements.txt          # Dépendances Python
│   │   ├── Procfile                  # Configuration Railway
│   │   ├── railway.json              # Configuration Railway détaillée
│   │   ├── nixpacks.toml            # Configuration build Nixpacks
│   │   ├── static/                   # Frontend build (déployé ici)
│   │   │   ├── index.html            # Point d'entrée React
│   │   │   ├── assets/               # JS/CSS compilés par Vite
│   │   │   ├── sitemap.xml           # Sitemap SEO
│   │   │   └── robots.txt            # Configuration robots
│   │   ├── routes/                   # Routes FastAPI
│   │   │   ├── admin_features.py     # Gestion fonctionnalités
│   │   │   ├── rhyme_routes.py       # Routes comptines
│   │   │   └── stories.py            # Routes histoires
│   │   ├── services/                 # Services métier (29 fichiers)
│   │   │   ├── sora2_zseedance_generator.py  # Animations Veo 3.1
│   │   │   ├── coloring_generator_gpt4o.py   # Coloriages
│   │   │   ├── comics_generator_gpt4o.py     # Bandes dessinées
│   │   │   ├── suno_service.py               # Comptines musicales
│   │   │   └── ... (25 autres services)
│   │   ├── models/                   # Modèles Pydantic
│   │   ├── utils/                    # Utilitaires
│   │   └── config/                   # Configuration
│   ├── frontend/                     # Code source React
│   │   ├── src/                      # Code source
│   │   │   ├── App.jsx               # Composant principal (1915 lignes)
│   │   │   ├── components/           # 53 composants React
│   │   │   ├── services/             # Services API
│   │   │   ├── hooks/                # Hooks React
│   │   │   └── config/               # Configuration
│   │   ├── package.json              # Dépendances npm
│   │   └── vite.config.js            # Configuration Vite
│   ├── supabase/                     # Configuration Supabase
│   │   ├── config.toml               # Configuration locale
│   │   ├── functions/                # Edge Functions (7 fonctions)
│   │   │   ├── stripe-webhook/        # Webhook Stripe
│   │   │   ├── create-payment/       # Création paiement
│   │   │   ├── deduct-tokens/        # Déduction tokens
│   │   │   └── ... (4 autres)
│   │   └── migrations/               # Migrations SQL (14 migrations)
│   └── push.bat                      # Script Git push
└── TARIFICATION_HERBBIE.md           # Grille tarifaire
```

---

## 🔧 ARCHITECTURE BACKEND (FastAPI)

### Point d'Entrée : `main.py`

**Localisation** : `backend/saas/main.py` (1668 lignes)

#### Configuration Principale
- **Framework** : FastAPI
- **Serveur** : Uvicorn
- **Port** : Variable `$PORT` (Railway) ou 8006 (local)
- **CORS** : Configuré pour `herbbie.com`, `panneau-production.up.railway.app`, `localhost`
- **Static Files** : Monté sur `/static` et `/assets`

#### Routes Principales

##### 1. Routes de Contenu
- `POST /generate_audio_story/` - Génération histoires audio
- `POST /generate_coloring/` - Génération coloriages (gpt-image-1)
- `POST /generate_comic/` - Génération bandes dessinées
- `POST /generate_animation/` - Génération animations (Veo 3.1)
- `POST /generate-quick` - Génération animation rapide

##### 2. Routes de Statut (Tâches Asynchrones)
- `GET /status/{task_id}` - Statut animation
- `GET /status_comic/{task_id}` - Statut BD
- `GET /check_task_status/{task_id}` - Statut comptine Suno

##### 3. Routes Comptines (Suno AI)
- `POST /api/rhyme/generate` - Génération comptine
- `GET /diagnostic/suno` - Diagnostic Suno

##### 4. Routes Authentification/Config
- `GET /api/config` - Configuration frontend (Supabase URLs)
- `GET /health` - Health check

##### 5. Routes Admin
- `GET /api/features` - Liste fonctionnalités
- `PUT /api/features/{feature_key}` - Activer/désactiver fonctionnalité

##### 6. Routes Contact
- `POST /api/contact` - Formulaire de contact (Resend)

##### 7. Routes SPA (Frontend)
- `GET /` - Serve `index.html`
- `GET /{full_path:path}` - Fallback SPA routing
- `GET /sitemap.xml` - Sitemap SEO
- `GET /robots.txt` - Robots.txt

### Services Métier

#### 1. Génération d'Animations
**Fichier** : `services/sora2_zseedance_generator.py`

**Workflow ZSEEDANCE** (inspiré de n8n) :
1. **Ideas Agent** → Génération idée histoire (GPT-4o-mini)
2. **Prompts Agent** → Création scènes détaillées (GPT-4o-mini)
3. **Create Clips** → Génération vidéos (Runway Veo 3.1 Fast)
4. **Sequence Video** → Assemblage final

**Plateformes supportées** :
- **Runway ML** (priorité 1) - Veo 3.1 Fast
- Pika Labs (priorité 3)
- OpenAI Sora (non disponible publiquement)

**Configuration** :
- Durée par clip : 10 secondes
- Aspect ratio : 9:16 (vertical)
- Résolution : 480p
- Style : "2D cartoon animation, Disney Pixar style"

#### 2. Génération de Coloriages
**Fichier** : `services/coloring_generator_gpt4o.py`

**Modèles utilisés** :
- **Thèmes prédéfinis** : gemini-3-pro-image-preview (text-to-image)
- **Photos uploadées** : gpt-image-1 (image-to-image)
- Support avec/sans modèle coloré (version colorée en référence)

#### 3. Génération de Bandes Dessinées
**Fichier** : `services/comics_generator_gpt4o.py`

**Pipeline** :
- **BD par thème** :
  - Génération scénario (GPT-4o-mini)
  - Découpage en pages
  - Génération images par page (gemini-3-pro-image-preview)
  - Ajout bulles de dialogue
- **BD avec photos personnalisées** :
  - Analyse photo détaillée (GPT-4o vision)
  - Génération scénario personnalisé (GPT-4o-mini)
  - Génération images avec personnage personnalisé (gemini-3-pro-image-preview)
  - Ajout bulles de dialogue

#### 4. Comptines Musicales
**Fichier** : `services/suno_service.py`

**API** : Suno AI
- Génération paroles (GPT-4o-mini)
- Génération musique (Suno API)
- Format : MP3 téléchargeable

---

## 🎨 ARCHITECTURE FRONTEND (React)

### Structure

**Code Source** : `backend/frontend/`
**Build Output** : `backend/saas/static/`

### Build Process

1. **Développement** :
   ```bash
   cd backend/frontend
   npm run dev  # Port 5173
   ```

2. **Production Build** :
   ```bash
   cd backend/frontend
   npm run build  # Génère dist/
   ```

3. **Déploiement** :
   - Le build `dist/` doit être copié vers `backend/saas/static/`
   - Railway sert le contenu de `static/` via FastAPI

### Composants Principaux

#### App.jsx (1915 lignes)
- Machine d'état principale
- Gestion des types de contenu (animation, BD, coloriage, histoire, comptine)
- Intégration Stripe (paiements)
- Intégration Supabase (auth, créations)
- Gestion tokens/abonnements

#### Composants par Fonctionnalité
- **Animation** : `AnimationSelector.jsx`, `AnimationViewer.jsx`
- **BD** : `ComicsSelector.jsx`, `ComicViewer.jsx`
- **Coloriage** : `ColoringSelector.jsx`, `ColoringViewer.jsx`, `ColoringCanvas.jsx`
- **Histoire** : `StorySelector.jsx`, `StoryPopup.jsx`
- **Comptine** : `MusicalRhymeSelector.jsx`, `RhymePopup.jsx`
- **Paiements** : `StripePaymentModal.jsx`, `SubscriptionModal.jsx`
- **Admin** : `AdminPanel.jsx`, `AdminFeatureManager.jsx`

### Configuration

**Fichier** : `frontend/src/config/api.js`
```javascript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
export const ANIMATION_API_BASE_URL = import.meta.env.VITE_ANIMATION_API_BASE_URL || 
  'https://da-production-6222.up.railway.app';
```

**Fichier** : `frontend/src/config/supabase-config.js`
- URL Supabase : `https://xfbmdeuzuyixpmouhqcv.supabase.co`
- Anon Key : Configurée

---

## 🗄️ BASE DE DONNÉES (Supabase)

### Tables Principales

#### 1. `profiles` (4 lignes)
- `id` (UUID, FK → auth.users)
- `prenom`, `nom`, `email`
- `role` (default: 'user')
- `premium` (boolean)
- `status` (default: 'active')

#### 2. `creations` (1 ligne)
- `id` (bigint)
- `user_id` (UUID, FK → profiles)
- `type` (text) - 'animation', 'comic', 'coloring', 'histoire', 'rhyme'
- `title` (text)
- `data` (jsonb) - Contenu de la création
- `created_at` (timestamptz)

#### 3. `subscriptions` (0 lignes)
- `id` (integer)
- `user_id` (UUID)
- `plan_id` (integer, FK → subscription_plans)
- `stripe_subscription_id` (varchar, unique)
- `status` (varchar, default: 'active')
- `tokens_remaining` (integer)
- `tokens_used_this_month` (integer)
- `current_period_start`, `current_period_end`

#### 4. `subscription_plans` (4 lignes)
- Plans : Découverte (4,99€), Famille (9,99€), Créatif (19,99€), Institut (49,99€)
- `tokens_allocated` (integer)
- `stripe_price_id` (varchar, unique)

#### 5. `user_tokens` (0 lignes)
- Historique des transactions de tokens
- `transaction_type` : 'purchase', 'subscription', 'deduction', etc.

#### 6. `token_costs` (24 lignes)
- Coûts en tokens par type de contenu et plan
- Exemples : Histoire = 4 tokens, Coloriage = 16 tokens, Animation 30s = 420 tokens

#### 7. `payments` (0 lignes)
- Paiements PAY-PER-USE
- `stripe_payment_intent_id` (varchar, unique)
- `content_type`, `amount`, `status`

#### 8. `generation_permissions` (0 lignes)
- Permissions de génération (système de paiement)

#### 9. `payment_history` (0 lignes)
- Historique des paiements

### Row Level Security (RLS)

**Toutes les tables ont RLS activé** avec politiques :
- Utilisateurs peuvent lire/écrire leurs propres données
- Admin peut tout voir
- Policies spécifiques par table

### Edge Functions

**Localisation** : `backend/supabase/functions/`

1. **stripe-webhook** - Webhook Stripe
2. **create-payment** - Création PaymentIntent
3. **deduct-tokens** - Déduction tokens après génération
4. **manage-subscription** - Gestion abonnements
5. **setup-stripe-products** - Setup produits Stripe
6. **check-permission** - Vérification permissions
7. **admin-stripe-data** - Admin Stripe

### Migrations

**14 migrations** au total, incluant :
- Setup Stripe (tables, RLS, fonctions)
- Tables abonnements
- Tables tokens
- Tables paiements

---

## 🚀 DÉPLOIEMENT RAILWAY

### Configuration

**Fichiers de configuration** :
- `railway.json` - Configuration Railway
- `Procfile` - Commande de démarrage
- `nixpacks.toml` - Configuration build

### Procfile
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 300 --timeout-graceful-shutdown 30
```

### Build Process Railway

1. **Détection** : Nixpacks détecte Python
2. **Installation** : `pip install -r requirements.txt`
3. **Démarrage** : Commande du Procfile

### Variables d'Environnement Requises

#### APIs IA
- `OPENAI_API_KEY` - OpenAI (GPT-4o-mini, GPT-4o, TTS, gpt-image-1)
- `GEMINI_API_KEY` - Google Gemini (gemini-3-pro-image-preview)
- `RUNWAY_API_KEY` - Runway ML (Veo 3.1 Fast)
- `SUNO_API_KEY` - Suno AI (comptines)
- `FAL_API_KEY` - FAL AI (optionnel)
- `STABILITY_API_KEY` - Stability AI (optionnel)

#### Supabase
- `SUPABASE_URL` - `https://xfbmdeuzuyixpmouhqcv.supabase.co`
- `SUPABASE_ANON_KEY` - Clé anonyme
- `SUPABASE_SERVICE_ROLE_KEY` - Clé service (backend)

#### Stripe
- `STRIPE_SECRET_KEY` - Clé secrète Stripe
- `STRIPE_PUBLISHABLE_KEY` - Clé publique (frontend)
- `STRIPE_WEBHOOK_SECRET` - Secret webhook

#### Autres
- `BASE_URL` - `https://herbbie.com`
- `TEXT_MODEL` - `gpt-4o-mini`
- `RESEND_API_KEY` - Resend (emails)
- `CONTACT_EMAIL` - `contact@herbbie.com`

### Workflow de Déploiement

1. **Push Git** → Railway détecte le push
2. **Build** → Nixpacks build l'image
3. **Deploy** → Démarre le serveur FastAPI
4. **Frontend** → Doit être dans `saas/static/` avant le push

**⚠️ IMPORTANT** : Le frontend doit être buildé et copié dans `saas/static/` avant chaque push vers Railway.

### Scripts Utiles

**push.bat** (dans `backend/`) :
```batch
git add .
git commit -m "%message%"
git push origin main
```

**Note** : Les pushs doivent être faits depuis `backend/` selon les instructions.

---

## 🔐 AUTHENTIFICATION & SÉCURITÉ

### Supabase Auth

- **Provider** : Email/Password
- **JWT** : Géré par Supabase
- **Sessions** : Stockées côté client (localStorage)
- **RLS** : Toutes les tables protégées

### CORS

**Origines autorisées** :
- `https://herbbie.com`
- `https://www.herbbie.com`
- `https://panneau-production.up.railway.app`
- `http://localhost:3000`
- `http://localhost:5173`

### Trusted Hosts

- `herbbie.com`
- `www.herbbie.com`
- `*.railway.app`
- `localhost`

---

## 💳 SYSTÈME DE PAIEMENT (Stripe)

### Modèles de Tarification

#### PAY-PER-USE
- Histoire : 0,50€
- Coloriage (thème) : 0,50€
- Coloriage (photo) : 0,50€
- BD (par page, thème) : 0,50€
- BD (par page, photo) : 0,50€
- Comptine : 0,70€
- Animation 30s : 5,99€
- Animation 1min : 9,99€
- Animation 2min : 18,99€
- Animation 3min : 27,99€
- Animation 4min : 36,99€
- Animation 5min : 46,99€

#### ABONNEMENTS (Tokens)
- **Découverte** : 4,99€/mois → 250 tokens
- **Famille** : 9,99€/mois → 500 tokens
- **Créatif** : 19,99€/mois → 1000 tokens
- **Institut** : 49,99€/mois → 2500 tokens

**Système de tokens** :
- 1 token = 0,01€ de coût API
- Tokens utilisables pour n'importe quel contenu
- Exemples : 
  - Histoire = 4 tokens
  - Coloriage (thème) = 13 tokens
  - Coloriage (photo) = 4 tokens
  - BD (thème) = 13 tokens
  - BD (photo) = 15 tokens
  - Comptine = 15 tokens
  - Animation 30s = 420 tokens

### Flow de Paiement

1. **Sélection contenu** → Vérification tokens/permissions
2. **Si insuffisant** → Modal Stripe
3. **PaymentIntent** → Créé via Edge Function
4. **Paiement** → Stripe Checkout
5. **Webhook** → Confirmation → Crédit tokens
6. **Génération** → Déduction tokens

---

## 📊 FONCTIONNALITÉS

### Types de Contenu Générés

1. **🎬 Dessins Animés**
   - Durées : 30s, 1min, 2min, 3min, 4min, 5min
   - Thèmes : espace, océan, forêt, ville, aventure, fantasy, cartoon
   - Modèle : Runway Veo 3.1 Fast
   - Workflow : ZSEEDANCE (n8n)

2. **💬 Bandes Dessinées**
   - Pages : 1-10 planches
   - Styles : cartoon, manga, comics, réaliste, 3D
   - Bulles de dialogue automatiques
   - Personnages personnalisables (upload de photo)
   - Modèles : 
     - Thèmes : GPT-4o-mini (scénario) + gemini-3-pro-image-preview (images)
     - Photos : GPT-4o (analyse) + GPT-4o-mini (scénario) + gemini-3-pro-image-preview (images)

3. **🎨 Coloriages**
   - Thèmes prédéfinis (licorne, dinosaures, animaux, espace, etc.)
   - Option avec/sans modèle coloré (version colorée en référence)
   - Upload photo → coloriage personnalisé
   - Modèles :
     - Thèmes : gemini-3-pro-image-preview (text-to-image)
     - Photos : gpt-image-1 (image-to-image)

4. **📖 Histoires Audio**
   - Histoires écrites (GPT-4o-mini)
   - Narration audio optionnelle (OpenAI TTS)
   - Voix : male, female
   - Format : texte + MP3

5. **🎵 Comptines Musicales**
   - Paroles générées (GPT-4o-mini)
   - Musique générée (Suno AI)
   - Format : MP3 téléchargeable

### Gestion des Fonctionnalités

**Endpoint** : `/api/features`
- Activation/désactivation par fonctionnalité
- Stockage : `features_config.json`
- Fonctionnalités : animation, comic, coloring, histoire, rhyme

---

## 🔍 SEO & RÉFÉRENCEMENT

### Sitemap

**Fichier** : `saas/static/sitemap.xml`
- **38 URLs** indexables
- Pages principales : 6 fonctionnalités
- Pages utilisateur : 3
- Abonnements/Paiements : 3
- Pages légales : 6
- Thèmes populaires : 9

### Robots.txt

**Fichier** : `saas/static/robots.txt`
- Autorise tous les bots principaux
- Bloque les scrapers (Ahrefs, Semrush, etc.)
- Sitemap : `https://herbbie.com/sitemap.xml`

### Métadonnées

**Fichier** : `saas/static/index.html`
- Open Graph (Facebook)
- Twitter Cards
- Schema.org (Organization, WebApplication)
- Meta description optimisée

---

## 🛠️ DÉVELOPPEMENT LOCAL

### Prérequis
- Python 3.11+
- Node.js 18+
- Git

### Setup Backend

```bash
cd backend/saas
pip install -r requirements.txt
python main.py  # Port 8006
```

### Setup Frontend

```bash
cd backend/frontend
npm install
npm run dev  # Port 5173
```

### Setup Supabase Local (Optionnel)

```bash
cd backend
supabase start
```

### Variables d'Environnement

Créer `.env` dans `backend/saas/` :
```env
OPENAI_API_KEY=sk-...
RUNWAY_API_KEY=key_...
SUNO_API_KEY=...
SUPABASE_URL=https://xfbmdeuzuyixpmouhqcv.supabase.co
SUPABASE_ANON_KEY=...
STRIPE_SECRET_KEY=sk_...
BASE_URL=http://localhost:8006
```

---

## 📝 NOTES IMPORTANTES

### Déploiement Frontend

**⚠️ CRITIQUE** : Le frontend doit être buildé et copié dans `saas/static/` avant chaque push vers Railway.

**Processus recommandé** :
1. `cd backend/frontend`
2. `npm run build`
3. Copier le contenu de `dist/` vers `saas/static/`
4. `cd backend`
5. `git add . && git commit && git push`

### Push Git

**⚠️ IMPORTANT** : Les pushs doivent être faits depuis `backend/` selon les instructions utilisateur.

### Cache Railway

- Le cache CDN Railway peut prendre jusqu'à 5 minutes à se rafraîchir
- Utiliser "Redeploy from scratch" si nécessaire

### Logs

- **Railway** : Dashboard → Logs
- **Supabase** : Dashboard → Logs
- **Local** : Console Python

---

## 🔗 LIENS UTILES

- **Production** : https://herbbie.com
- **Railway Dashboard** : https://railway.app
- **Supabase Dashboard** : https://supabase.com/dashboard
- **Stripe Dashboard** : https://dashboard.stripe.com
- **API Docs** : https://herbbie.com/docs (FastAPI auto-docs)

---

## 📚 DOCUMENTATION COMPLÉMENTAIRE

- `TARIFICATION_HERBBIE.md` - Grille tarifaire complète
- `SITEMAP_COMPLET_HERBBIE.md` - Stratégie SEO

---

*Documentation générée automatiquement après analyse complète du projet*

