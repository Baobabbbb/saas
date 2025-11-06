# SYSTÈME DE TOKENS HERBBIE

*Date de mise à jour : Novembre 2025*

---

## 🎯 CONCEPT

### Fonctionnement
- **Backend** : Système de tokens (flexible, technique)
- **Frontend** : Affichage en nombre de générations (clair, commercial)

### Formule de base
```
1 token = 0,01€ de coût API
```

---

## 📊 COÛTS EN TOKENS PAR CONTENU

| Contenu | Coût API réel | Tokens requis | Calcul |
|---------|---------------|---------------|--------|
| **Histoire** | 0,15€ | **15 tokens** | 0,15€ ÷ 0,01€ |
| **Coloriage** | 0,20€ | **20 tokens** | 0,20€ ÷ 0,01€ |
| **BD (page)** | 0,20€ | **20 tokens** | 0,20€ ÷ 0,01€ |
| **Comptine** | 0,17€ | **17 tokens** | 0,17€ ÷ 0,01€ |
| **Animation 30s** | 6,10€ | **610 tokens** | 6,10€ ÷ 0,01€ |
| **Animation 1min** | 9,15€ | **915 tokens** | 9,15€ ÷ 0,01€ |

---

## 💳 ABONNEMENTS

### Calcul des tokens par abonnement

**Règle** : 50% du prix de l'abonnement = budget API = tokens disponibles

| Abonnement | Prix | Budget API (50%) | Tokens disponibles |
|------------|------|------------------|-------------------|
| **Découverte** | 4,99€ | 2,50€ | **250 tokens** |
| **Famille** | 9,99€ | 5,00€ | **500 tokens** |
| **Créatif** | 19,99€ | 10,00€ | **1000 tokens** |
| **Institut** | 49,99€ | 25,00€ | **2500 tokens** |

---

## 📈 AFFICHAGE UTILISATEUR

### Abonnement Découverte (250 tokens)

**Affichage frontend** :
- ✅ Jusqu'à **16 histoires** (250 ÷ 15)
- ✅ Jusqu'à **12 coloriages** (250 ÷ 20)
- ✅ Jusqu'à **12 pages de BD** (250 ÷ 20)
- ✅ Jusqu'à **14 comptines** (250 ÷ 17)
- ❌ **0 animations 30s** (besoin de 610 tokens)
- ❌ **0 animations 1min** (besoin de 915 tokens)

**Backend** : L'utilisateur a 250 tokens et peut les dépenser comme il veut.

---

### Abonnement Famille (500 tokens)

**Affichage frontend** :
- ✅ Jusqu'à **33 histoires** (500 ÷ 15)
- ✅ Jusqu'à **25 coloriages** (500 ÷ 20)
- ✅ Jusqu'à **25 pages de BD** (500 ÷ 20)
- ✅ Jusqu'à **29 comptines** (500 ÷ 17)
- ❌ **0 animations 30s** (besoin de 610 tokens)
- ❌ **0 animations 1min** (besoin de 915 tokens)

---

### Abonnement Créatif (1000 tokens)

**Affichage frontend** :
- ✅ Jusqu'à **66 histoires** (1000 ÷ 15)
- ✅ Jusqu'à **50 coloriages** (1000 ÷ 20)
- ✅ Jusqu'à **50 pages de BD** (1000 ÷ 20)
- ✅ Jusqu'à **58 comptines** (1000 ÷ 17)
- ✅ Jusqu'à **1 animation 30s** (1000 ÷ 610)
- ✅ Jusqu'à **1 animation 1min** (1000 ÷ 915)

---

### Abonnement Institut (2500 tokens)

**Affichage frontend** :
- ✅ Jusqu'à **166 histoires** (2500 ÷ 15)
- ✅ Jusqu'à **125 coloriages** (2500 ÷ 20)
- ✅ Jusqu'à **125 pages de BD** (2500 ÷ 20)
- ✅ Jusqu'à **147 comptines** (2500 ÷ 17)
- ✅ Jusqu'à **4 animations 30s** (2500 ÷ 610)
- ✅ Jusqu'à **2 animations 1min** (2500 ÷ 915)

---

## ✅ AVANTAGES DU SYSTÈME

### 1. Flexibilité maximale
- L'utilisateur **choisit** comment dépenser ses tokens
- Pas de quota fixe par type de contenu
- Adaptation aux besoins réels

### 2. Transparence
- Affichage clair en "nombre de générations"
- L'utilisateur comprend immédiatement ce qu'il peut faire
- Pas de confusion avec les tokens (technique en backend)

### 3. Rentabilité garantie
- **50% de marge** sur tous les abonnements
- Budget API = 50% du prix de l'abonnement
- Aucun risque de perte

### 4. Évolutivité
- Facile d'ajuster les coûts en tokens si les API changent
- Possibilité d'ajouter de nouveaux types de contenu
- Système scalable

---

## 🔧 IMPLÉMENTATION TECHNIQUE

### Backend (système de tokens)

```javascript
// Coûts en tokens (1 token = 0,01€ API)
const tokenCosts = {
  histoire: 15,      // 0,15€ API
  coloring: 20,      // 0,20€ API
  comic: 20,         // 0,20€ API
  rhyme: 17,         // 0,17€ API
  animation30: 610,  // 6,10€ API
  animation60: 915   // 9,15€ API
};

// Plans avec tokens
const plans = {
  'Découverte': { totalTokens: 250 },   // 2,50€ API
  'Famille': { totalTokens: 500 },      // 5,00€ API
  'Créatif': { totalTokens: 1000 },     // 10,00€ API
  'Institut': { totalTokens: 2500 }     // 25,00€ API
};
```

### Frontend (affichage en générations)

```javascript
// Calcul des générations maximales
const maxGenerations = {
  histoire: Math.floor(totalTokens / tokenCosts.histoire),
  coloring: Math.floor(totalTokens / tokenCosts.coloring),
  comic: Math.floor(totalTokens / tokenCosts.comic),
  rhyme: Math.floor(totalTokens / tokenCosts.rhyme),
  animation30: Math.floor(totalTokens / tokenCosts.animation30),
  animation60: Math.floor(totalTokens / tokenCosts.animation60)
};

// Affichage utilisateur
const features = [
  `Jusqu'à ${maxGenerations.histoire} histoires`,
  `Jusqu'à ${maxGenerations.coloring} coloriages`,
  // etc.
];
```

---

## 🎨 EXEMPLE D'USAGE UTILISATEUR

### Utilisateur avec plan Créatif (1000 tokens)

**Option 1 : Mix équilibré**
- 30 histoires (450 tokens)
- 20 coloriages (400 tokens)
- 8 comptines (136 tokens)
- **Total** : 986 tokens utilisés

**Option 2 : Focus histoires**
- 66 histoires (990 tokens)
- **Total** : 990 tokens utilisés

**Option 3 : Focus animations**
- 1 animation 30s (610 tokens)
- 20 histoires (300 tokens)
- 4 coloriages (80 tokens)
- **Total** : 990 tokens utilisés

**Option 4 : Maximum de contenu simple**
- 50 coloriages (1000 tokens)
- **Total** : 1000 tokens utilisés

---

## 📊 VALIDATION FINANCIÈRE

### Découverte (4,99€)
- Tokens : 250
- Budget API : 2,50€
- Marge : 2,49€ (50%)
- ✅ **RENTABLE**

### Famille (9,99€)
- Tokens : 500
- Budget API : 5,00€
- Marge : 4,99€ (50%)
- ✅ **RENTABLE**

### Créatif (19,99€)
- Tokens : 1000
- Budget API : 10,00€
- Marge : 9,99€ (50%)
- ✅ **RENTABLE**

### Institut (49,99€)
- Tokens : 2500
- Budget API : 25,00€
- Marge : 24,99€ (50%)
- ✅ **RENTABLE**

---

## 🚀 CONCLUSION

Ce système combine :
- ✅ **Flexibilité** : tokens en backend
- ✅ **Clarté** : générations en frontend
- ✅ **Rentabilité** : 50% de marge garantie
- ✅ **Transparence** : utilisateur comprend ce qu'il peut faire
- ✅ **Simplicité** : pas de quota fixe par contenu

