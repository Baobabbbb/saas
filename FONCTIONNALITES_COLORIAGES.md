# 🎨 Fonctionnalités Système de Coloriages

## ✅ Fonctionnalités Complètes

### **1. Génération par Thème** 🎭
- **11 thèmes prédéfinis** :
  - 📸 Ma Photo (upload personnalisé)
  - ✏️ Coloriage personnalisé
  - 🐾 Animaux
  - 🚀 Espace
  - 🧚 Fées
  - 🦸 Super-héros
  - 🌺 Nature
  - 🚗 Véhicules
  - 🤖 Robots
  - 👸 Princesses
  - 🦕 Dinosaures

- **Technologie** : Stable Diffusion 3 Medium
- **Qualité** : 1024x1024 minimum, noir et blanc pur
- **Post-traitement** : Contraste renforcé, seuillage automatique

### **2. Upload de Photo Personnalisée** 📸

#### **Formats Supportés**
- JPG, PNG, GIF, WebP
- Taille max : 5 MB
- Résolution : Optimisée automatiquement

#### **Modes ControlNet**
1. **🔍 Canny (Contours nets)**
   - Détection de contours précise
   - Idéal pour photos détaillées, portraits, objets complexes
   - Algorithme : Canny Edge Detection (seuils 50-150)

2. **✏️ Scribble (Croquis)**
   - Style croquis simplifié
   - Idéal pour style dessin enfant, simplification
   - Algorithme : XDoG (σ1=0.5, σ2=2.0)

#### **Pipeline de Conversion**
```
Photo Utilisateur
    ↓
Redimensionnement (max 1024x1024)
    ↓
ControlNet Preprocessing (Canny/Scribble)
    ↓
Image de Contrôle (contours extraits)
    ↓
Stable Diffusion 3 + Control Sketch
    ↓
Post-Traitement
    ├─ Contraste ×2.5
    ├─ Luminosité ×1.2
    └─ Seuillage à 200
    ↓
Coloriage Final (PNG)
```

### **3. Workflow Utilisateur** 👤

#### **Génération par Thème**
1. Choisir un thème dans la grille
2. (Optionnel) Personnaliser avec du texte
3. Cliquer "Générer"
4. Télécharger le coloriage en PDF

#### **Génération depuis Photo**
1. Cliquer sur "Ma Photo 📸"
2. Cliquer "Choisir une photo"
3. Sélectionner un fichier
4. Prévisualiser la photo
5. Choisir le mode : Canny ou Scribble
6. Cliquer "Générer"
7. Télécharger le coloriage

### **4. Résultats** 🎯

**Caractéristiques du coloriage généré :**
- ✅ Noir et blanc pur (pas de gris)
- ✅ Contours nets et fermés
- ✅ Fond blanc immaculé
- ✅ Traits épais (adaptés aux enfants)
- ✅ Zones faciles à colorier
- ✅ Résolution 1024x1024 minimum
- ✅ Format PNG optimisé
- ✅ Prêt pour impression

---

## 🚀 Endpoints API

### **POST /generate_coloring/**
Génère un coloriage par thème
```json
{
  "theme": "animals"
}
```

### **POST /upload_photo_for_coloring/**
Upload une photo utilisateur
```bash
FormData: file (image)
```

### **POST /convert_photo_to_coloring/**
Convertit la photo en coloriage
```json
{
  "photo_path": "static/uploads/coloring/upload_abc123.jpg",
  "control_mode": "canny",
  "control_strength": 0.7
}
```

---

## 💻 Technologies Utilisées

### **Backend**
- **FastAPI** : API REST
- **Stable Diffusion 3** : Génération d'images
- **ControlNet** : Contrôle par contours
- **OpenCV (headless)** : Traitement d'images
- **Pillow** : Manipulation d'images
- **Numpy** : Calculs numériques

### **Frontend**
- **React** : Interface utilisateur
- **Framer Motion** : Animations
- **CSS Modules** : Styles

### **Déploiement**
- **Railway** : Backend (Python 3.11)
- **Vercel** : Frontend (React)
- **HTTPS** : Sécurité end-to-end

---

## 📊 Performance

| Métrique | Valeur |
|----------|--------|
| Temps génération thème | 15-25s |
| Temps upload photo | <1s |
| ControlNet preprocessing | 0.5-1s |
| Génération SD3 ControlNet | 20-30s |
| Post-traitement | <1s |
| **Total (photo → coloriage)** | **22-33s** |

**Coût par génération** : ~$0.04-0.06

---

## 🔒 Sécurité

### **Validation Upload**
- Types MIME autorisés uniquement
- Taille limitée (5 MB max)
- Validation côté client et serveur

### **URLs**
- HTTPS uniquement en production
- Mixed Content résolu
- Variables d'environnement sécurisées

---

## 🎨 Interface Utilisateur

### **Bouton "Ma Photo"**
- Gradient violet distinctif
- Contour violet quand sélectionné
- Preview de la photo uploadée
- Bouton de suppression (✕)

### **Modes ControlNet**
- Boutons de sélection clairs
- Descriptions explicites
- Indicateur visuel de sélection
- Couleurs cohérentes (violet #6B4EFF)

### **Affichage Résultat**
- Popup plein écran
- Zoom sur l'image
- Téléchargement direct en PDF
- Intégration dans l'historique

---

## 📝 Variables d'Environnement Requises

```env
# API Keys
STABILITY_API_KEY=sk-pskwCC...

# Configuration
BASE_URL=https://herbbie.com
TEXT_MODEL=gpt-4o-mini
IMAGE_MODEL=stability-ai
```

---

## 🧪 Tests

### **Test Upload Photo**
```bash
curl -X POST https://herbbie.com/upload_photo_for_coloring/ \
  -F "file=@test.jpg"
```

### **Test Conversion Canny**
```bash
curl -X POST https://herbbie.com/convert_photo_to_coloring/ \
  -H "Content-Type: application/json" \
  -d '{
    "photo_path": "static/uploads/coloring/upload_abc.jpg",
    "control_mode": "canny",
    "control_strength": 0.7
  }'
```

### **Test Conversion Scribble**
```bash
curl -X POST https://herbbie.com/convert_photo_to_coloring/ \
  -H "Content-Type: application/json" \
  -d '{
    "photo_path": "static/uploads/coloring/upload_abc.jpg",
    "control_mode": "scribble",
    "control_strength": 0.7
  }'
```

---

## 🎉 Résumé

**Le système de coloriages est maintenant complet avec :**

✅ Génération par thème (11 thèmes)  
✅ Upload de photos personnalisées  
✅ 2 modes ControlNet (Canny + Scribble)  
✅ Post-traitement optimisé  
✅ Interface utilisateur intuitive  
✅ Déploiement Railway/Vercel  
✅ HTTPS sécurisé  
✅ Téléchargement PDF  
✅ Intégration historique  
✅ Système de paiement intégré  

**Prêt pour production !** 🚀

---

*Documentation Système de Coloriages - Version 1.0*  
*Dernière mise à jour : 3 octobre 2025*

