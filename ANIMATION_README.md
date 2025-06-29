# 🎬 Pipeline d'Animation IA - FRIDAY

Cette nouvelle fonctionnalité permet de créer des dessins animés fluides et cohérents à partir d'histoires textuelles, en utilisant une pipeline optimisée sans CrewAI.

## 🚀 Fonctionnalités

### ✨ Générateur d'animations IA
- **Découpage narratif intelligent** : Analyse automatique du texte et création de 8-12 scènes clés
- **Style visuel cohérent** : Palette de couleurs et seeds réutilisables pour la cohérence
- **Génération vidéo** : Utilise SD3-Turbo pour créer des clips fluides
- **Assemblage automatique** : Combine tous les clips avec transitions
- **Durée personnalisable** : De 30 secondes à 5 minutes

### 🎨 Styles disponibles
- **Cartoon** : Style dessin animé coloré et enfantin
- **Anime** : Style manga japonais
- **Réaliste** : Style cinématographique
- **Pastel** : Couleurs douces et tendres

### 🎯 Thèmes prédéfinis
- Aventure, Animaux, Magie, Amitié
- Espace, Océan, Forêt, Pirates
- Dinosaures, Contes de fées, Super-héros
- + Histoire personnalisée

## 🛠️ Architecture technique

### Backend (Pipeline IA)
```
saas/services/animation_pipeline.py
├── 1. Découpage narratif (GPT-4o-mini)
├── 2. Définition du style graphique
├── 3. Génération des prompts vidéo
├── 4. Génération clips (SD3-Turbo)
└── 5. Assemblage final
```

### Frontend (Interface utilisateur)
```
frontend/src/components/
├── AnimationSelector.jsx     # Sélection thème/durée/style
├── AnimationViewer.jsx       # Visualisation du résultat
└── Integration dans App.jsx
```

### API Endpoints
- `POST /generate_animation/` - Génération complète
- `POST /api/animations/test-duration` - Endpoint de compatibilité

## 📋 Utilisation

### 1. Interface utilisateur
1. Sélectionner "Dessin animé IA" dans FRIDAY
2. Choisir un thème ou écrire une histoire personnalisée
3. Configurer la durée (30s - 5min)
4. Sélectionner le style visuel
5. Cliquer sur "Créer mon dessin animé IA"

### 2. API directe
```bash
curl -X POST http://127.0.0.1:8000/generate_animation/ \
  -H "Content-Type: application/json" \
  -d '{
    "story": "Il était une fois...",
    "duration": 60,
    "style": "cartoon",
    "theme": "magie"
  }'
```

## ⚙️ Configuration

### Variables d'environnement (.env)
```bash
# Requis pour la pipeline d'animation
OPENAI_API_KEY=sk-...          # GPT-4o-mini pour analyse narrative
STABILITY_API_KEY=sk-...       # SD3-Turbo pour génération vidéo
TEXT_MODEL=gpt-4o-mini        # Modèle de texte
VIDEO_MODEL=sd3-large-turbo   # Modèle vidéo
```

### Installation des dépendances
```bash
# Backend
pip install -r saas/requirements_new.txt

# Frontend (déjà inclus)
cd frontend
npm install
```

## 🧪 Tests

### Test rapide
```bash
python test_animation_pipeline.py
```

### Test manuel
1. Démarrer le backend : `python saas/main_new.py`
2. Démarrer le frontend : `cd frontend && npm run dev`
3. Aller sur http://localhost:5175
4. Tester la création d'animation

## 📊 Performance

### Temps de génération estimé
- **30s d'animation** : 2-4 minutes
- **1min d'animation** : 4-8 minutes  
- **2min d'animation** : 8-15 minutes
- **5min d'animation** : 20-30 minutes

### Optimisations incluses
- ✅ Génération en parallèle (batches de 3 clips)
- ✅ Système de fallback robuste
- ✅ Cache intelligent des résultats
- ✅ Retry automatique avec backoff
- ✅ Pipeline modulaire et réutilisable

## 🔧 Dépannage

### Erreurs communes

#### "Clé API non configurée"
- Vérifier le fichier `.env` dans `/saas/`
- S'assurer que les clés commencent par `sk-` et ne contiennent pas "votre"

#### "Timeout de génération"
- Réduire la durée de l'animation
- Vérifier la connectivité internet
- Augmenter le timeout dans le code

#### "Clips en fallback"
- Normal lors de pics de charge de l'API
- Les clips fallback sont automatiquement gérés
- Retry manuel possible via l'interface

### Logs utiles
```bash
# Backend logs
tail -f saas/logs/animation_pipeline.log

# Test de diagnostic
curl http://127.0.0.1:8000/diagnostic
```

## 🎯 Roadmap

### Version actuelle (v1.0)
- ✅ Pipeline complète fonctionnelle
- ✅ Interface utilisateur intégrée
- ✅ Système de fallback
- ✅ Styles multiples

### Améliorations prévues (v1.1)
- 🔄 Assemblage vidéo avec ffmpeg
- 🔄 Transitions personnalisées
- 🔄 Ajout de musique de fond
- 🔄 Export en différents formats
- 🔄 Aperçu en temps réel

### Futures fonctionnalités (v2.0)
- 🔄 Édition post-génération
- 🔄 Voix off automatique
- 🔄 Animations 3D
- 🔄 Collaboration multi-utilisateurs

## 📝 Notes importantes

- **Coût** : Utilise des APIs payantes (OpenAI + Stability AI)
- **Limites** : SD3-Turbo max 30s par clip (assemblage automatique)
- **Qualité** : Dépend de la qualité du prompt narratif
- **Cache** : Les résultats sont automatiquement sauvegardés

## 🤝 Contribution

Pour améliorer cette pipeline :
1. Fork le projet
2. Créer une branche feature
3. Tester avec `test_animation_pipeline.py`
4. Soumettre une pull request

---

**Créé avec ❤️ pour FRIDAY - L'assistant créatif pour enfants**
