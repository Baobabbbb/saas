# 🎼 Comptines Musicales avec DiffRhythm AI

Cette fonctionnalité permet de créer des comptines musicales complètes (paroles + mélodie) en utilisant l'IA DiffRhythm de GoAPI.

## 🚀 Fonctionnalités

### ✨ Génération de comptines musicales
- **Paroles automatiques** : Génération de paroles adaptées aux enfants avec GPT-4o-mini
- **Musique IA** : Création de mélodies avec DiffRhythm AI
- **Styles prédéfinis** : 6 types de comptines avec styles musicaux adaptés
- **Personnalisation** : Options de style musical personnalisé
- **Format optimisé** : Paroles formatées avec timestamps pour la synchronisation

### 🎨 Types de comptines disponibles

1. **🌙 Berceuse musicale** - Mélodie douce et apaisante
2. **🔢 Comptine à compter** - Rythme éducatif et mémorable  
3. **🐘 Comptine animalière** - Sons d'animaux et rythme joueur
4. **🍂 Comptine saisonnière** - Mélodie festive et chaleureuse
5. **🎨 Comptine éducative** - Style simple et mémorable
6. **💃 Comptine de mouvement** - Rythme énergique pour danser

### 🎛️ Styles musicaux

- **🤖 Automatique** - L'IA choisit le meilleur style
- **🕊️ Doux et apaisant** - Pour berceuses et moments calmes
- **🎵 Rythmé et joyeux** - Tempo enjoué et dynamique
- **🎪 Joueur et amusant** - Sons rigolos et interactifs
- **📚 Éducatif** - Mélodie simple et mémorable
- **🎛️ Personnalisé** - Style décrit par l'utilisateur

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# --- GOAPI DIFFRHYTHM (COMPTINES MUSICALES) ---
GOAPI_API_KEY=votre_cle_goapi_ici
DIFFRHYTHM_MODEL=Qubico/diffrhythm
DIFFRHYTHM_TASK_TYPE=txt2audio-base
```

### Installation des dépendances

```bash
# Backend
pip install aiohttp asyncio

# Frontend (déjà inclus)
# framer-motion pour les animations
```

## 📡 API Endpoints

### 1. Génération de comptine musicale

```http
POST /generate_musical_rhyme/
Content-Type: application/json

{
  "rhyme_type": "lullaby",
  "custom_request": "Une berceuse pour un petit chat",
  "generate_music": true,
  "custom_style": "gentle piano with soft vocals",
  "language": "fr"
}
```

**Réponse :**
```json
{
  "status": "success",
  "title": "Dodo Petit Chat",
  "lyrics": "Dodo petit chat orange...",
  "rhyme_type": "lullaby",
  "has_music": true,
  "music_status": "completed",
  "audio_url": "https://...",
  "style_used": "gentle lullaby, soft and soothing",
  "generation_time": 45.2
}
```

### 2. Vérification du statut d'une tâche

```http
POST /check_rhyme_task_status/
Content-Type: application/json

{
  "task_id": "uuid-task-id"
}
```

### 3. Styles disponibles

```http
GET /rhyme_styles/
```

## 🎯 Utilisation Frontend

### Composant MusicalRhymeSelector

```jsx
<MusicalRhymeSelector
  selectedRhyme={selectedRhyme}
  setSelectedRhyme={setSelectedRhyme}
  customRhyme={customRhyme}
  setCustomRhyme={setCustomRhyme}
  generateMusic={generateMusic}
  setGenerateMusic={setGenerateMusic}
  musicStyle={musicStyle}
  setMusicStyle={setMusicStyle}
  customMusicStyle={customMusicStyle}
  setCustomMusicStyle={setCustomMusicStyle}
/>
```

### Activation de la fonctionnalité

La fonctionnalité est activée par défaut dans `src/services/features.js` :

```javascript
musical_rhyme: { enabled: true, name: 'Comptine musicale', icon: '🎼' }
```

## 🧪 Tests

### Script de test Python

```bash
cd backend
python test_musical_rhymes.py
```

### Tests manuels

1. **Interface utilisateur** :
   - Sélectionner "Comptine musicale" dans le type de contenu
   - Choisir un type de comptine
   - Activer/désactiver la génération musicale
   - Tester différents styles musicaux

2. **API directe** :
   - Utiliser le script de test fourni
   - Tester avec différents types de comptines
   - Vérifier la génération audio

## 📊 Architecture

### Services Backend

```
saas/
├── services/
│   ├── diffrhythm_service.py          # Service DiffRhythm API
│   └── musical_nursery_rhyme_service.py # Service comptines complètes
├── models.py                          # Modèles Pydantic
└── main_new.py                        # Endpoints FastAPI
```

### Composants Frontend

```
frontend/src/components/
├── MusicalRhymeSelector.jsx          # Sélecteur de comptines musicales
├── MusicalRhymeSelector.css          # Styles du composant
└── ContentTypeSelector.jsx           # Mis à jour pour inclure l'option
```

## 💡 Fonctionnement

1. **Génération des paroles** : GPT-4o-mini crée les paroles selon le type choisi
2. **Formatage temporal** : Les paroles sont formatées avec des timestamps
3. **Génération musicale** : DiffRhythm crée la mélodie selon le style
4. **Attente de completion** : Le système poll le statut jusqu'à completion
5. **Affichage** : L'audio est affiché avec les informations de style

## 🔒 Sécurité

- Validation des entrées utilisateur
- Gestion des timeouts pour les appels API
- Fallback en cas d'échec de génération musicale
- Limitation de la taille des paroles (10 000 caractères max)

## 🚧 Limitations

- **Durée audio** : ~30-60 secondes par comptine
- **Coût** : Utilise des crédits GoAPI DiffRhythm
- **Langues** : Optimisé pour le français
- **Formats** : Audio retourné par DiffRhythm (généralement MP3)

## 🎯 Roadmap

### Version actuelle (v1.0)
- ✅ Génération de paroles avec GPT-4o-mini
- ✅ Intégration DiffRhythm pour la musique
- ✅ Interface utilisateur complète
- ✅ 6 types de comptines prédéfinis
- ✅ Styles musicaux personnalisables

### Améliorations prévues (v1.1)
- 🔄 Cache local des comptines générées
- 🔄 Export en différents formats audio
- 🔄 Aperçu en temps réel des paroles
- 🔄 Intégration avec la voix off
- 🔄 Paroles synchronisées (karaoké)

### Futures fonctionnalités (v2.0)
- 🔄 Édition post-génération des paroles
- 🔄 Mélange de styles musicaux
- 🔄 Comptines multi-langues
- 🔄 Collaboration parent-enfant
- 🔄 Playlists de comptines

## 🤝 Contribution

Pour améliorer cette fonctionnalité :

1. **Tests** : Utiliser `test_musical_rhymes.py`
2. **Nouveaux styles** : Ajouter dans `NURSERY_RHYME_STYLES`
3. **Frontend** : Améliorer `MusicalRhymeSelector.jsx`
4. **Documentation** : Mettre à jour ce README

## 📞 Support

- **API DiffRhythm** : https://goapi.ai/docs/diffrhythm-api/
- **Problèmes** : Vérifier les logs backend pour les erreurs DiffRhythm
- **Configuration** : S'assurer que `GOAPI_API_KEY` est configurée

---

**Créé avec ❤️ pour FRIDAY - L'assistant créatif pour enfants**

*Powered by DiffRhythm AI de GoAPI*
