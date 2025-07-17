# 🎬 SEEDANCE - Générateur de Dessins Animés IA

Plateforme complète de génération automatique de dessins animés éducatifs utilisant l'intelligence artificielle.

## 🚀 Démarrage Rapide

### Option 1: Lancement Sécurisé (Recommandé)

**Linux/Mac:**
```bash
chmod +x QUICK_START_SECURE.sh && ./QUICK_START_SECURE.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File QUICK_START_SECURE.ps1
```

### Option 2: Lancement Simple
```bash
chmod +x QUICK_START.sh && ./QUICK_START.sh
```

## 🛠️ Outils de Diagnostic

### 1. Diagnostic Général
```bash
python diagnostic.py
```
Vérifie les fichiers, clés API, dépendances et connectivité.

### 2. Test du Service SEEDANCE
```bash
python test_seedance_fix.py
```
Test complet de génération d'animation avec toutes les étapes.

### 3. Test de Connectivité API
```bash
python test_connectivity.py
```
Simule les appels du frontend vers le backend.

## 📋 Configuration Requise

### Clés API (obligatoires)
- **OpenAI API Key** (pour l'IA générative)
- **Wavespeed API Key** (pour la génération vidéo) 
- **Fal AI API Key** (pour l'audio et FFmpeg)

### Fichier `.env`
Créer le fichier `saas/.env` avec:
```env
OPENAI_API_KEY=sk-proj-votre_clé_openai
WAVESPEED_API_KEY=votre_clé_wavespeed
FAL_API_KEY=votre_clé_fal_ai
```

### Dependencies
- Python 3.8+ avec FastAPI, uvicorn, aiohttp
- Node.js 16+ avec npm
- FFmpeg (pour l'assemblage vidéo)

## 🎯 Fonctionnalités

- **Génération d'histoires IA** basée sur des thèmes
- **Création de scènes narratives** structurées
- **Génération de clips vidéo** avec Wavespeed AI
- **Ajout d'effets sonores** avec Fal AI
- **Assemblage final** avec FFmpeg
- **Interface web moderne** et intuitive

## 🌐 Accès

- **Backend API**: http://localhost:8004
- **Interface Web**: http://localhost:5173
- **Diagnostic**: http://localhost:8004/diagnostic

## 📊 Thèmes Disponibles

- 🚀 **Space**: Aventures spatiales avec astronautes
- 🌊 **Ocean**: Explorations sous-marines
- 🌿 **Nature**: Protection de l'environnement
- 🦁 **Animals**: Animaux et leurs habitats
- 👫 **Friendship**: Amitié et entraide
- ⚔️ **Adventure**: Grandes aventures
- ✨ **Magic**: Mondes fantastiques
- 📚 **Learning**: Contenu éducatif

## 🔧 Résolution de Problèmes

### Problèmes Courants

1. **"Failed to fetch"**
   - Vérifier que le backend est démarré
   - Tester avec `python diagnostic.py`

2. **Erreurs de parsing JSON**
   - ✅ **CORRIGÉ** dans la dernière version
   - Parsing robuste avec fallbacks

3. **Timeouts**
   - Normal avec les services IA
   - Réessayer si nécessaire

4. **Clés API invalides**
   - Vérifier le fichier `saas/.env`
   - S'assurer que toutes les clés sont valides

### Documentation Complète
Voir [TROUBLESHOOTING.md](TROUBLESHOOTING.md) pour le guide détaillé.

## 📁 Structure du Projet

```
📁 saas/
├── 🚀 QUICK_START_SECURE.sh/.ps1    # Lancement avec vérifications
├── 🔍 diagnostic.py                  # Outil de diagnostic
├── 🧪 test_seedance_fix.py          # Test complet du service
├── 🌐 test_connectivity.py          # Test de connectivité
├── 📚 TROUBLESHOOTING.md            # Guide de résolution
├── 📁 saas/                         # Backend API
│   ├── 🔑 .env                      # Configuration (clés API)
│   ├── 🌐 main.py                   # Serveur FastAPI
│   └── 📁 services/
│       └── 🎬 seedance_service.py   # Service principal
└── 📁 frontend/                     # Interface web
    ├── 📦 package.json
    └── 🎨 src/
```

## 🎉 Utilisation

1. **Lancer les services** avec un des scripts de démarrage
2. **Ouvrir l'interface** sur http://localhost:5173
3. **Choisir un thème** d'animation
4. **Écrire ou générer** une histoire
5. **Personnaliser** les paramètres (âge, durée, style)
6. **Lancer la génération** et attendre le résultat
7. **Télécharger** l'animation générée

## 🚨 En Cas de Problème

1. **Diagnostiquer**: `python diagnostic.py`
2. **Consulter**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Redémarrer**: `./QUICK_START_SECURE.sh`
4. **Tester**: `python test_connectivity.py`

## � Statut du Projet

- ✅ Génération d'idées IA robuste
- ✅ Parsing JSON amélioré avec fallbacks
- ✅ Génération vidéo parallèle optimisée
- ✅ Assemblage FFmpeg local
- ✅ Interface web moderne
- ✅ Scripts de diagnostic complets
- ✅ Documentation exhaustive

---

**Version:** Stable avec corrections JSON et timeouts optimisés  
**Dernière mise à jour:** Janvier 2025

1. Ouvrir http://localhost:5175
2. Saisir une histoire
3. Choisir un style et thème
4. Cliquer sur "Créer"
5. Regarder le dessin animé généré

## 🛠️ Configuration

Fichier `.env` dans `saas/` :
```
OPENAI_API_KEY=votre_clé_openai
STABILITY_API_KEY=votre_clé_stability
```

## 📁 Structure

```
backend/
├── frontend/           # Interface React
├── saas/
│   ├── main.py        # API FastAPI
│   ├── services/      # Services IA
│   └── .env          # Configuration
└── start.bat         # Démarrage
```
