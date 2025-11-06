# VÉRIFICATION DES VRAIS COÛTS API

*Date : Novembre 2025 - Sources officielles*

---

## 🔍 COÛTS API RÉELS (Sources officielles)

### Texte (GPT-4 Turbo)
- **Input** : 10,00$ par million tokens
- **Output** : 30,00$ par million tokens

**Calcul pour une histoire de 500 mots** :
- Prompt : ~200 tokens × 0,01$ = 0,002$
- Génération : ~700 tokens × 0,03$ = 0,021$
- **Total** : ~0,023$ ≈ **0,02€**

### Images (DALL-E 3)
- **1024×1024 standard** : 0,04$ ≈ **0,04€** par image

### Audio (ElevenLabs)
- **Standard** : ~0,30$ par 1000 caractères
- Histoire 500 mots ≈ 3000 caractères = 0,90$ ≈ **0,85€**

### Vidéo (Sora-2)
- **Standard** : 0,10$ par seconde
- 30s = 3,00$ ≈ **2,80€**
- 1min = 6,00$ ≈ **5,60€**
- 2min = 12,00$ ≈ **11,20€**
- 3min = 18,00$ ≈ **16,80€**
- 4min = 24,00$ ≈ **22,40€**
- 5min = 30,00$ ≈ **28,00€**

---

## ⚠️ COMPARAISON : TARIFICATION_HERBBIE.md vs RÉALITÉ

| Contenu | Coût actuel | Vrai coût | Différence | Statut |
|---------|-------------|-----------|------------|--------|
| Histoire texte seul | 0,15€ | 0,02€ | **+650%** | ❌ SURÉVALUÉ |
| Histoire + audio | 0,15€ | 0,87€ | **-83%** | ❌ SOUS-ÉVALUÉ |
| Coloriage | 0,20€ | 0,04€ | **+400%** | ❌ SURÉVALUÉ |
| BD | 0,20€ | 0,04€ | **+400%** | ❌ SURÉVALUÉ |
| Comptine (texte+musique) | 0,17€ | ~0,15€ | Approximatif | ⚠️ À vérifier |
| Animation 30s | 6,10€ | 2,80€ | **+118%** | ❌ SURÉVALUÉ |
| Animation 1min | 9,15€ | 5,60€ | **+63%** | ❌ SURÉVALUÉ |
| Animation 2min | 12,20€ | 11,20€ | +9% | ✅ Acceptable |
| Animation 3min | 15,25€ | 16,80€ | -9% | ⚠️ SOUS-ÉVALUÉ |
| Animation 4min | 18,30€ | 22,40€ | -18% | ❌ SOUS-ÉVALUÉ |
| Animation 5min | 21,35€ | 28,00€ | -24% | ❌ SOUS-ÉVALUÉ |

---

## 🎯 PROBLÈME MAJEUR IDENTIFIÉ

### Histoires
Le fichier ne distingue PAS entre :
- **Histoire texte seul** : 0,02€
- **Histoire + audio** : 0,87€

C'est une différence de **43× le coût** !

### Recommandation
Séparer en deux produits :
1. **Histoire texte** : 0,02€ API
2. **Histoire audio** : 0,87€ API (0,02€ texte + 0,85€ voix)

---

## ✅ COÛTS API CORRIGÉS RECOMMANDÉS

| Contenu | Vrai coût API | Marge suggérée | Prix PAY-PER-USE | Tokens |
|---------|---------------|----------------|------------------|--------|
| **Histoire texte** | 0,02€ | 25× (95% marge) | 0,49€ | 2 tokens |
| **Histoire audio** | 0,87€ | 1,15× (13% marge) | 0,99€ | 87 tokens |
| **Coloriage** | 0,04€ | 25× (96% marge) | 0,99€ | 4 tokens |
| **BD (page)** | 0,04€ | 37× (97% marge) | 1,49€ | 4 tokens |
| **Comptine** | ~0,15€ | 10× (90% marge) | 1,49€ | 15 tokens |
| **Animation 30s** | 2,80€ | 2,85× (65% marge) | 7,99€ | 280 tokens |
| **Animation 1min** | 5,60€ | 2,14× (53% marge) | 11,99€ | 560 tokens |
| **Animation 2min** | 11,20€ | 1,43× (30% marge) | 15,99€ | 1120 tokens |
| **Animation 3min** | 16,80€ | 1,19× (16% marge) | 19,99€ | 1680 tokens |
| **Animation 4min** | 22,40€ | 1,07× (7% marge) | 23,99€ | 2240 tokens |
| **Animation 5min** | 28,00€ | 1,00× (0% marge) | 27,99€ | 2800 tokens |

---

## 🔢 ABONNEMENTS RECALCULÉS (avec vrais coûts)

### Découverte - 4,99€/mois
**Budget API (50%)** : 2,50€ = **250 tokens**

**Générations maximales** :
- 125 histoires texte (250 ÷ 2)
- 2 histoires audio (250 ÷ 87)
- 62 coloriages (250 ÷ 4)
- 62 pages BD (250 ÷ 4)
- 16 comptines (250 ÷ 15)
- 0 animation (besoin 280+)

### Famille - 9,99€/mois
**Budget API (50%)** : 5,00€ = **500 tokens**

**Générations maximales** :
- 250 histoires texte (500 ÷ 2)
- 5 histoires audio (500 ÷ 87)
- 125 coloriages (500 ÷ 4)
- 125 pages BD (500 ÷ 4)
- 33 comptines (500 ÷ 15)
- 1 animation 30s (500 ÷ 280)

### Créatif - 19,99€/mois
**Budget API (50%)** : 10,00€ = **1000 tokens**

**Générations maximales** :
- 500 histoires texte (1000 ÷ 2)
- 11 histoires audio (1000 ÷ 87)
- 250 coloriages (1000 ÷ 4)
- 250 pages BD (1000 ÷ 4)
- 66 comptines (1000 ÷ 15)
- 3 animations 30s (1000 ÷ 280)
- 1 animation 1min (1000 ÷ 560)

### Institut - 49,99€/mois
**Budget API (50%)** : 25,00€ = **2500 tokens**

**Générations maximales** :
- 1250 histoires texte (2500 ÷ 2)
- 28 histoires audio (2500 ÷ 87)
- 625 coloriages (2500 ÷ 4)
- 625 pages BD (2500 ÷ 4)
- 166 comptines (2500 ÷ 15)
- 8 animations 30s (2500 ÷ 280)
- 4 animations 1min (2500 ÷ 560)
- 2 animations 2min (2500 ÷ 1120)
- 1 animation 3min (2500 ÷ 1680)
- 1 animation 4min (2500 ÷ 2240)
- 0 animation 5min (besoin 2800)

---

## ❌ PROBLÈME CRITIQUE : Animation 5min

Avec les vrais coûts :
- **Animation 5min** : 28,00€ API
- **Plan Institut** : 25,00€ budget API

**IMPOSSIBLE** de proposer une animation 5min dans le plan Institut !

### Solutions possibles :

1. **Option A** : Augmenter le plan Institut
   - Prix : 59,99€/mois
   - Budget API : 30,00€ (50%)
   - Tokens : 3000
   - Animation 5min : OUI (3000 ÷ 2800 = 1)

2. **Option B** : Exclure animation 5min des abonnements
   - Uniquement en PAY-PER-USE
   - Prix : 27,99€ (marge quasi nulle)

3. **Option C** : Créer un plan "Studio" spécial
   - Prix : 99,99€/mois
   - Budget API : 50,00€
   - Tokens : 5000
   - 1× animation 5min + autres contenus

---

## 🎯 RECOMMANDATION FINALE

**ACTION REQUISE** : Corriger TOUS les coûts API dans le système

1. Séparer "Histoire texte" et "Histoire audio"
2. Utiliser les vrais coûts API (ceux ci-dessus)
3. Recalculer tous les tokens
4. Décider du sort de l'animation 5min (options A, B ou C)
5. Mettre à jour la documentation
6. Redéployer le frontend

**Aucun des coûts actuels n'est correct sauf animation 2min !**

