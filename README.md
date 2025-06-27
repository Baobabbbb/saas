# 🎬 API Dessins Animés

Application web pour générer des dessins animés avec IA.

## 🚀 Démarrage rapide

### Backend
```bash
# Démarrer l'API
start.bat
```

### Frontend
```bash
cd frontend
npm run dev
```

## 📱 Utilisation

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
