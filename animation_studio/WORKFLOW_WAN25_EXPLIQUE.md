# 🎬 Workflow Wan 2.5 - Identique à zseedance.json

## 📋 Clarification Importante

Le système Wan 2.5 **suit exactement le même workflow** que zseedance.json (n8n).  
La seule différence : **Wan 2.5 remplace Seedance** et **l'audio est intégré** (plus besoin de FAL AI pour les sons).

---

## 🔄 Comparaison Workflow

### zseedance.json (n8n) → Notre Pipeline Wan 2.5

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ZSEEDANCE.JSON                       │
└─────────────────────────────────────────────────────────────────┘

1️⃣ Ideas AI Agent (OpenAI GPT-4)
   ↓
   Génère 1 idée créative pour le dessin animé
   Format: Caption, Idea, Environment, Sound, Status
   
2️⃣ Prompts AI Agent (OpenAI GPT-4)
   ↓
   Crée 3 scènes détaillées basées sur l'idée
   Format: Scene 1, Scene 2, Scene 3 (chaque scène = 10s)
   
3️⃣ Unbundle Prompts
   ↓
   Sépare les 3 scènes en 3 prompts individuels
   
4️⃣ Create Clips (Seedance via Wavespeed)
   ↓
   Génère 3 clips vidéo de 10s chacun
   POST → Wait 140s → Get Clips
   
5️⃣ Create Sounds (FAL AI mmaudio-v2)
   ↓
   Génère l'audio pour chaque clip
   POST → Wait 60s → Get Sounds
   
6️⃣ Sequence Video (FAL AI ffmpeg-api/compose)
   ↓
   Assemble les 3 clips + audio en une vidéo finale
   POST → Wait 60s → Get Final Video
   
✅ RÉSULTAT: Vidéo de 30s (3 clips × 10s) avec audio
```

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTRE PIPELINE WAN 2.5                        │
└─────────────────────────────────────────────────────────────────┘

1️⃣ idea_generator.py (OpenAI GPT-4o-mini)
   ↓
   IDENTIQUE: Génère 1 idée créative pour le dessin animé
   Format: Caption, Idea, Environment, Sound, Status
   
2️⃣ scene_creator.py (OpenAI GPT-4o-mini)
   ↓
   IDENTIQUE: Crée 3 scènes détaillées basées sur l'idée
   Format: Scene 1, Scene 2, Scene 3 (chaque scène = 10s)
   Distribution automatique: 30s → 3 scènes de 10s
   
3️⃣ wan25_generator.py (Wan 2.5 via Wavespeed)
   ↓
   REMPLACE Seedance: Génère 3 clips vidéo de 10s
   ✨ NOUVEAU: Audio intégré automatiquement dans chaque clip
   POST → Wait (polling) → Get Clips
   
🚫 SUPPRIMÉ: Create Sounds (audio intégré dans Wan 2.5)
   
4️⃣ video_assembler.py (Assemblage simple)
   ↓
   SIMPLIFIÉ: Assemble les 3 clips en une vidéo finale
   Note: Clips Wan 2.5 ont déjà l'audio intégré
   
✅ RÉSULTAT: Vidéo de 30s (3 clips × 10s) avec audio intégré
```

---

## 🎯 Exemple Concret : Animation de 30 secondes

### Entrée Utilisateur
```json
{
  "theme": "nature",
  "duration": 30
}
```

### Workflow Complet

#### Étape 1: Génération d'Idée (OpenAI)
```json
{
  "Caption": "🌿 Voyage dans la forêt magique #nature #animation #viral",
  "Idea": "Un petit renard découvre une clairière enchantée avec des papillons lumineux",
  "Environment": "Forêt dense, rayons de soleil, clairière magique",
  "Sound": "Chants d'oiseaux, bruissement de feuilles, sons magiques",
  "Status": "for production"
}
```

#### Étape 2: Création des Scènes (OpenAI)
```json
{
  "Scene 1": "Le renard marche dans la forêt dense, regardant autour de lui avec curiosité. Les rayons de soleil filtrent à travers les arbres.",
  "Scene 2": "Le renard s'arrête au bord d'une clairière lumineuse. Des papillons colorés volent autour de fleurs brillantes.",
  "Scene 3": "Le renard entre dans la clairière, un papillon se pose sur son nez. Il sourit, émerveillé."
}
```

**Distribution automatique** : 30s → 3 scènes × 10s

#### Étape 3: Génération Clips Wan 2.5
```
Clip 1 (10s) : Renard dans la forêt + audio (bruissement, pas)
Clip 2 (10s) : Découverte clairière + audio (sons magiques)
Clip 3 (10s) : Interaction papillon + audio (musique douce)
```

**URLs générées** :
- `https://wavespeed.ai/output/clip1_abc123.mp4` (10s avec audio)
- `https://wavespeed.ai/output/clip2_def456.mp4` (10s avec audio)
- `https://wavespeed.ai/output/clip3_ghi789.mp4` (10s avec audio)

#### Étape 4: Assemblage Final
```
Clip 1 (0-10s) + Clip 2 (10-20s) + Clip 3 (20-30s)
= 
Vidéo finale de 30 secondes avec audio intégré
```

**URL finale** : `https://wavespeed.ai/output/final_animation_30s.mp4`

---

## 🔍 Différences Clés vs zseedance.json

| Aspect | zseedance.json | Wan 2.5 |
|--------|----------------|---------|
| **Modèle vidéo** | Seedance (480p) | Wan 2.5 (720p/1080p) |
| **Audio** | FAL AI séparé | **Intégré dans clips** |
| **Qualité** | Basique | Supérieure |
| **Lip-sync** | Non | **Oui** |
| **Étapes** | 6 étapes | **4 étapes** |
| **Prix** | ~$1.95/30s | **$1.07/30s** |
| **Temps** | ~10 min | **~6 min** |

---

## 📦 Structure des Données

### AnimationResult (Sortie finale)
```python
{
  "animation_id": "abc-123",
  "status": "completed",
  "story_idea": {
    "caption": "🌿 Voyage dans la forêt magique",
    "idea": "Un petit renard découvre...",
    "environment": "Forêt dense, clairière",
    "sound": "Chants d'oiseaux, sons magiques"
  },
  "scenes": [
    {
      "scene_number": 1,
      "description": "Le renard marche...",
      "duration": 10,
      "prompt": "VIDEO THEME: 2D cartoon... SCENE: Le renard marche...",
      "characters": "petit renard roux",
      "environment": "forêt dense",
      "action": "marche, regarde autour"
    },
    // Scene 2, Scene 3...
  ],
  "video_clips": [
    {
      "scene_number": 1,
      "video_url": "https://wavespeed.ai/output/clip1.mp4",
      "duration": 10,
      "status": "completed",
      "audio_integrated": true
    },
    // Clip 2, Clip 3...
  ],
  "final_video_url": "https://wavespeed.ai/output/final_30s.mp4",
  "processing_time": 360,  // 6 minutes
  "created_at": "2025-10-02T10:30:00"
}
```

---

## ✅ Résumé : Identique à zseedance.json

Le workflow Wan 2.5 **est exactement le même** que zseedance.json :

1. ✅ **Génération d'idée** (OpenAI) - Identique
2. ✅ **Création de 3 scènes** (OpenAI) - Identique
3. ✅ **Génération de 3 clips de 10s** - Wan 2.5 au lieu de Seedance
4. ✅ **Assemblage en vidéo de 30s** - Simplifié (audio déjà inclus)

**Résultat final** : Dessin animé de 30 secondes avec 3 scènes cohérentes et audio intégré

---

**Date** : 2 Octobre 2025  
**Version** : Wan 2.5 v1.0  
**Conforme à** : zseedance.json workflow

