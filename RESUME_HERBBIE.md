# 📖 HERBBIE - Résumé du Projet

*Document de présentation - Version 2025*

---

## 🎯 Qu'est-ce que HERBBIE ?

**HERBBIE** est une plateforme web qui permet aux parents, enseignants et animateurs de créer **du contenu personnalisé pour enfants** en utilisant l'intelligence artificielle. Le site génère automatiquement des dessins animés, des histoires, des coloriages, des bandes dessinées et des comptines musicales adaptés aux enfants de 3 à 10 ans.

### Concept Principal

Au lieu de chercher pendant des heures du contenu adapté à leurs enfants, les utilisateurs peuvent :
1. **Choisir un type de contenu** (dessin animé, histoire, coloriage, etc.)
2. **Sélectionner un thème** (espace, animaux, aventure, etc.)
3. **Personnaliser** avec des détails (prénom de l'enfant, préférences)
4. **Recevoir en quelques minutes** un contenu unique et adapté

---

## 🎨 Fonctionnalités Principales

### 1. 🎬 Dessins Animés Personnalisés
- **Durées disponibles** : 30 secondes à 5 minutes
- **Thèmes** : Espace, Océan, Forêt, Ville, Aventure, Fantasy, Cartoon
- **Technologie** : Runway ML Veo 3.1 Fast (génération vidéo IA)
- **Résultat** : Vidéo MP4 téléchargeable, format vertical (9:16)
- **Prix** : De 5,99€ (30s) à 46,99€ (5min)

### 2. 📖 Histoires Audio
- **Génération** : Texte d'histoire écrit par IA (GPT-4o-mini)
- **Narration optionnelle** : Voix masculine ou féminine (OpenAI TTS)
- **Thèmes** : Aventure, Animaux, Magie, Amitié, Espace, Nature
- **Format** : Texte + fichier audio MP3
- **Prix** : 0,50€

### 3. 🎨 Coloriages Personnalisés
- **Modes** : 
  - Coloriage à partir d'un thème (licorne, dinosaures, animaux, espace, etc.)
  - Conversion d'une photo en coloriage (upload de photo personnalisée)
- **Options** : Avec ou sans modèle coloré (version colorée en référence)
- **Technologie** : 
  - Thèmes : gemini-3-pro-image-preview (text-to-image)
  - Photos : gpt-image-1 (image-to-image)
- **Format** : Image PNG haute résolution, téléchargeable en PDF
- **Prix** : 0,50€

### 4. 💬 Bandes Dessinées
- **Pages** : 1 à 10 planches
- **Styles** : Cartoon, Manga, Comics, Réaliste, 3D
- **Fonctionnalités** : 
  - Bulles de dialogue automatiques
  - Personnages personnalisables (upload de photo)
  - Thèmes variés (espace, pirates, princesses, dinosaures, super-héros, etc.)
- **Technologie** : 
  - Thèmes : gpt-4o-mini (scénario) + gemini-3-pro-image-preview (images)
  - Photos personnalisées : gpt-4o (analyse photo) + gemini-3-pro-image-preview (génération)
- **Prix** : 0,50€ par page

### 5. 🎵 Comptines Musicales
- **Génération** : Paroles (IA) + Musique (Suno AI)
- **Types** : Animaux, Comptage, Couleurs, Alphabet, Famille, Nature, Saisons, Mouvement, Émotions, Berceuse
- **Personnalisation** : Possibilité d'inclure le prénom de l'enfant
- **Format** : Fichier MP3 téléchargeable
- **Prix** : 0,70€

---

## 💰 Modèles de Tarification

### Pay-Per-Use (Paiement à l'unité)
Chaque création est payée individuellement :
- Histoire : **0,50€**
- Coloriage (thème) : **0,50€**
- Coloriage (photo) : **0,50€**
- Page de BD (thème) : **0,50€**
- Page de BD (photo) : **0,50€**
- Comptine : **0,70€**
- Animation 30s : **5,99€**
- Animation 1min : **9,99€**
- Animation 2min : **18,99€**
- Animation 3min : **27,99€**
- Animation 4min : **36,99€**
- Animation 5min : **46,99€**

### Abonnements Mensuels (Système de Tokens)
Les utilisateurs reçoivent des tokens qu'ils peuvent utiliser pour n'importe quel type de contenu :

| Abonnement | Prix/mois | Tokens | Idéal pour |
|------------|-----------|--------|------------|
| **Découverte** | 4,99€ | 250 tokens | Utilisateurs occasionnels |
| **Famille** | 9,99€ | 500 tokens | Familles actives |
| **Créatif** | 19,99€ | 1000 tokens | Créateurs intensifs, éducateurs |
| **Institut** | 49,99€ | 2500 tokens | Écoles, crèches, centres de loisirs |

**Exemples d'utilisation des tokens** :
- Histoire : 4 tokens
- Coloriage (thème) : 13 tokens
- Coloriage (photo) : 4 tokens
- Page BD (thème) : 13 tokens
- Page BD (photo) : 15 tokens
- Comptine : 15 tokens
- Animation 30s : 420 tokens
- Animation 1min : 840 tokens

**Avantage** : Les abonnements permettent d'économiser jusqu'à 92% par rapport au pay-per-use.

---

## 👥 Public Cible

### Utilisateurs Principaux
1. **Parents** (25-45 ans)
   - Cherchent des activités créatives pour leurs enfants
   - Veulent du contenu personnalisé et éducatif
   - Besoin de gain de temps

2. **Enseignants** (Maternelle, Primaire)
   - Création de supports pédagogiques
   - Activités de classe personnalisées
   - Contenu adapté aux programmes

3. **Animateurs / Centres de Loisirs**
   - Activités pour groupes d'enfants
   - Contenu pour événements (anniversaires, fêtes)
   - Supports d'animation

4. **Thérapeutes / Orthophonistes**
   - Supports personnalisés pour leurs patients
   - Contenu adapté aux besoins spécifiques

---

## 🔧 Technologies Utilisées

### Backend
- **Framework** : FastAPI (Python 3.11)
- **Déploiement** : Railway
- **Base de données** : Supabase (PostgreSQL)
- **Authentification** : Supabase Auth

### Frontend
- **Framework** : React 18 + Vite
- **UI** : Composants React personnalisés
- **Paiements** : Stripe Checkout

### Intelligence Artificielle
- **Texte/Prompts** : OpenAI GPT-4o-mini (histoires, synopsis, paroles, scénarios BD)
- **Analyse d'images** : OpenAI GPT-4o (analyse de photos pour BD personnalisées)
- **Images normales** : Google Gemini 3 Pro Image Preview (coloriages par thème, BD par thème)
- **Images personnalisées** : OpenAI gpt-image-1 (coloriages avec photos uploadées)
- **Vidéo** : Runway ML Veo 3.1 Fast (dessins animés)
- **Audio** : OpenAI TTS (narration), Suno AI (comptines musicales)

### Services Externes
- **Paiements** : Stripe
- **Base de données** : Supabase
- **Emails** : Resend
- **Hébergement** : Railway

---

## 🌐 Architecture de Déploiement

### Production
- **URL** : https://herbbie.com
- **Backend** : Déployé sur Railway (FastAPI)
- **Frontend** : Servi par le backend FastAPI (dossier `static/`)
- **Base de données** : Supabase Cloud
- **Paiements** : Stripe Production

### Workflow de Déploiement
1. **Développement Frontend** : `cd backend/frontend && npm run build`
2. **Copie du build** : Le dossier `dist/` est copié vers `backend/saas/static/`
3. **Push Git** : Depuis `backend/`, exécuter `git push`
4. **Railway** : Détecte le push, build et déploie automatiquement

---

## 📊 Fonctionnalités Techniques Avancées

### Système d'Unicité
- **Détection de doublons** : Le système vérifie que les utilisateurs ne reçoivent jamais deux fois le même contenu
- **Enrichissement des prompts** : Utilise l'historique des créations pour générer du contenu varié
- **Base de données** : Stockage des hashs de contenu dans Supabase

### Gestion des Fonctionnalités
- **Activation/Désactivation** : Les fonctionnalités peuvent être activées ou désactivées via un panneau admin
- **Configuration** : Fichier `features_config.json` pour gérer les fonctionnalités disponibles

### Sécurité
- **Row Level Security (RLS)** : Toutes les tables Supabase sont protégées
- **Authentification** : Supabase Auth avec JWT
- **CORS** : Configuration stricte des origines autorisées
- **Validation** : Toutes les données sont validées côté backend

---

## 📈 Statistiques et Performance

### Temps de Génération
- **Histoire** : ~30 secondes
- **Coloriage** : ~1 minute
- **Page BD** : ~1-2 minutes par page
- **Comptine** : ~2-3 minutes
- **Animation 30s** : ~5-7 minutes
- **Animation 1min+** : ~10-15 minutes

### Capacité
- **Concurrent** : Gestion de multiples générations simultanées
- **Queue** : Système de tâches asynchrones pour les générations longues
- **Stockage** : Créations stockées dans Supabase et accessibles via l'historique utilisateur

---

## 🎯 Cas d'Usage Concrets

### Exemple 1 : Anniversaire d'Enfant
**Scénario** : Un parent veut créer un dessin animé personnalisé pour l'anniversaire de son enfant de 5 ans.

**Processus** :
1. Connexion sur herbbie.com
2. Sélection "Dessin animé"
3. Choix du thème "Espace" (le thème préféré de l'enfant)
4. Durée : 1 minute
5. Paiement : 9,99€ (ou utilisation de tokens si abonné)
6. Génération : 5-7 minutes
7. Téléchargement de la vidéo MP4
8. Projection lors de la fête d'anniversaire

**Résultat** : Un dessin animé unique, adapté à l'âge, avec le thème préféré de l'enfant.

### Exemple 2 : Activité de Classe
**Scénario** : Un enseignant de maternelle veut créer des coloriages sur le thème des animaux pour sa classe.

**Processus** :
1. Connexion avec compte "Institut" (49,99€/mois = 2500 tokens)
2. Sélection "Coloriage"
3. Thème "Animaux"
4. Génération de 10 coloriages différents (130 tokens pour thèmes, ou 40 tokens si photos)
5. Téléchargement en PDF
6. Impression pour la classe

**Résultat** : 10 coloriages uniques, adaptés aux enfants, prêts à imprimer.

### Exemple 3 : Comptine Personnalisée
**Scénario** : Un parent veut créer une comptine avec le prénom de son enfant pour l'aider à s'endormir.

**Processus** :
1. Connexion sur herbbie.com
2. Sélection "Comptine"
3. Type "Berceuse"
4. Personnalisation : "Comptine avec le prénom Léa"
5. Paiement : 0,70€
6. Génération : 2-3 minutes
7. Téléchargement du MP3
8. Écoute au coucher

**Résultat** : Une comptine musicale unique avec le prénom de l'enfant, adaptée pour le sommeil.

---

## 🔐 Sécurité et Confidentialité

### Protection des Données
- **RGPD** : Conformité avec le règlement européen
- **Données utilisateur** : Stockées de manière sécurisée dans Supabase
- **Paiements** : Gérés par Stripe (certifié PCI-DSS)
- **Contenu généré** : Accessible uniquement par l'utilisateur qui l'a créé

### Authentification
- **Inscription** : Email + mot de passe
- **Sessions** : Gérées par Supabase Auth
- **Rôles** : Système de rôles (user, admin, free)

---

## 📱 Accessibilité

### Compatibilité
- **Navigateurs** : Chrome, Firefox, Safari, Edge (versions récentes)
- **Appareils** : Desktop, Tablette, Mobile (responsive design)
- **Connexion** : Fonctionne avec une connexion internet standard

### Interface
- **Langue** : Français
- **Design** : Interface intuitive, adaptée aux parents pressés
- **Accessibilité** : Respect des standards WCAG

---

## 🚀 Évolutions Futures Possibles

### Fonctionnalités Potentielles
- **Application mobile** : iOS et Android
- **Bibliothèque de modèles** : Templates pré-créés
- **Partage social** : Partage des créations sur les réseaux sociaux
- **Mode collaboratif** : Création en famille
- **Export avancé** : Formats multiples (PDF, EPUB, etc.)
- **Personnalisation avancée** : Upload de photos de personnages

### Améliorations Techniques
- **Génération plus rapide** : Optimisation des temps de génération
- **Qualité améliorée** : Intégration de modèles IA plus récents
- **Multilingue** : Support de plusieurs langues
- **API publique** : API pour développeurs tiers

---

## 📞 Support et Contact

### Informations
- **Site web** : https://herbbie.com
- **Email** : contact@herbbie.com
- **Support** : Formulaire de contact sur le site

### Documentation
- **Documentation technique** : `ARCHITECTURE_COMPLETE.md`
- **Grille tarifaire** : `TARIFICATION_HERBBIE.md`
- **Guide utilisateur** : Disponible sur le site

---

## 💡 Points Forts de HERBBIE

### Pour les Utilisateurs
✅ **Gain de temps** : Création en quelques minutes au lieu d'heures de recherche  
✅ **Personnalisation** : Contenu unique adapté à chaque enfant  
✅ **Qualité** : Utilisation des meilleures technologies IA  
✅ **Prix abordables** : À partir de 0,50€ pour une histoire  
✅ **Flexibilité** : Pay-per-use ou abonnements selon les besoins  

### Pour les Développeurs
✅ **Architecture moderne** : FastAPI + React + Supabase  
✅ **Scalable** : Déploiement sur Railway, facilement extensible  
✅ **Maintenable** : Code structuré, documentation complète  
✅ **Sécurisé** : RLS, authentification robuste, validation des données  

---

## 📝 Conclusion

**HERBBIE** est une plateforme innovante qui démocratise la création de contenu personnalisé pour enfants grâce à l'intelligence artificielle. Elle répond à un besoin réel des parents, enseignants et animateurs qui cherchent du contenu adapté, éducatif et unique pour les enfants.

Le projet combine des technologies de pointe (IA générative, cloud computing) avec une interface simple et intuitive, permettant à n'importe qui de créer du contenu professionnel en quelques clics.

---

*Document créé le 2025-01-30*  
*Pour toute question, contactez : contact@herbbie.com*

