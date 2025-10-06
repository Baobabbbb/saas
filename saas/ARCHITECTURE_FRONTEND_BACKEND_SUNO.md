# 🎵 Architecture Frontend-Backend Suno AI

## 📊 Vue d'ensemble du flux complet

```
UTILISATEUR → FRONTEND → BACKEND → SUNO API → BACKEND → FRONTEND → UTILISATEUR
```

---

## 🔄 Flux détaillé de génération de comptine

### **Étape 1 : Génération initiale**

#### **Frontend** (`App.jsx`)
```javascript
// 1. Utilisateur clique sur "Générer" pour une comptine
handleGenerateContent() {
  // Appelle l'API backend
  POST /generate_rhyme/
  
  // Reçoit la réponse initiale
  {
    title: "Titre de la comptine",
    content: "Paroles de la comptine...",
    task_id: "suno_task_abc123",
    has_music: true,
    service: "suno"
  }
  
  // Garde isGenerating = true
  // Lance pollTaskStatus()
  // Fait return pour NE PAS arrêter l'animation
}
```

#### **Backend** (`main.py`)
```python
@app.post("/generate_rhyme/")
async def generate_rhyme(request: dict):
    # Détecte si personnalisation nécessaire
    needs_customization = detect_personalization(custom_request)
    
    if needs_customization:
        # MODE PERSONNALISÉ
        # 1. GPT-4o-mini génère les paroles
        lyrics = await openai.generate_lyrics(theme, custom_request)
        
        # 2. Suno en Custom Mode
        suno_result = await suno_service.generate_musical_nursery_rhyme(
            lyrics=lyrics,
            title=title,
            custom_mode=True
        )
    else:
        # MODE AUTOMATIQUE
        # Suno génère tout (paroles + musique)
        suno_result = await suno_service.generate_musical_nursery_rhyme(
            prompt_description=description,
            title=title,
            custom_mode=False
        )
    
    # Retourne immédiatement avec task_id
    return {
        "title": title,
        "content": lyrics_or_description,
        "task_id": suno_result["task_id"],
        "has_music": True
    }
```

#### **Suno Service** (`suno_service.py`)
```python
async def generate_musical_nursery_rhyme(
    lyrics: Optional[str] = None,
    custom_mode: bool = True,
    prompt_description: Optional[str] = None
):
    # Prépare le payload Suno
    if custom_mode:
        payload = {
            "prompt": lyrics,  # Paroles exactes
            "customMode": True,
            "style": "Children's Music",
            "title": title,
            "model": "V4_5",
            "callBackUrl": "https://herbbie.com/suno-callback"
        }
    else:
        payload = {
            "prompt": prompt_description,  # Description
            "customMode": False,
            "model": "V4_5",
            "callBackUrl": "https://herbbie.com/suno-callback"
        }
    
    # Appelle l'API Suno
    POST https://api.sunoapi.org/api/v1/generate
    
    # Retourne le task_id
    return {
        "status": "success",
        "task_id": "suno_task_abc123"
    }
```

---

### **Étape 2 : Polling du statut**

#### **Frontend** (`App.jsx`)
```javascript
pollTaskStatus(taskId) {
  // Vérifie toutes les 5 secondes (max 40 fois)
  setInterval(() => {
    // Appelle l'API backend
    GET /check_task_status/{taskId}
    
    // Reçoit le statut
    if (status === 'completed' && songs.length > 0) {
      // ✅ Musique prête !
      
      // 1. Met à jour generatedResult avec songs[]
      setGeneratedResult(prev => ({
        ...prev,
        songs: status.songs,
        has_music: true
      }));
      
      // 2. Enregistre dans l'historique Supabase
      addCreation({
        type: 'rhyme',
        title: title,
        data: { content, songs }
      });
      
      // 3. Arrête l'animation
      setIsGenerating(false);
    }
  }, 5000);
}
```

#### **Backend** (`main.py`)
```python
@app.get("/check_task_status/{task_id}")
async def check_task_status(task_id: str):
    # Appelle le service Suno
    result = await suno_service.check_task_status(task_id)
    
    # Retourne le statut
    return result
```

#### **Suno Service** (`suno_service.py`)
```python
async def check_task_status(task_id: str):
    # Appelle l'API Suno
    GET https://api.sunoapi.org/api/v1/generate/record-info?taskId={task_id}
    
    # Parse la réponse selon la doc Suno
    data = await response.json()
    task_status = data["data"]["status"]  # "GENERATING", "SUCCESS", "FAILED"
    
    if task_status == "SUCCESS":
        # Extrait les chansons
        clips = data["data"]["response"]["data"]
        
        songs = []
        for clip in clips:
            songs.append({
                "id": clip["id"],
                "title": clip["title"],
                "audio_url": clip["audio_url"],
                "video_url": clip["video_url"],
                "duration": clip["duration"]
            })
        
        return {
            "status": "completed",
            "songs": songs,
            "total_songs": len(songs)
        }
    
    elif task_status == "GENERATING" or task_status == "PENDING":
        return {
            "status": "processing",
            "message": "Génération en cours..."
        }
    
    else:  # FAILED
        return {
            "status": "failed",
            "error": data["data"]["errorMessage"]
        }
```

---

### **Étape 3 : Affichage du résultat**

#### **Frontend** (`App.jsx`)
```javascript
// Condition d'affichage stricte
{isGenerating ? (
  // Animation de chargement
  <div>Création de la comptine en cours...</div>
) : generatedResult && contentType === 'rhyme' 
    && generatedResult.songs && generatedResult.songs.length > 0 ? (
  // ✅ Affiche le résultat COMPLET
  <div>
    <p>{generatedResult.content}</p>
    {generatedResult.songs.map(song => (
      <audio src={song.audio_url} controls />
    ))}
    <button>Télécharger</button>
  </div>
) : null}
```

---

## 🔑 Points critiques de synchronisation

### **1. Structure de données cohérente**

**Backend envoie** :
```json
{
  "title": "Titre",
  "content": "Paroles",
  "task_id": "suno_task_xxx",
  "has_music": true
}
```

**Frontend reçoit et stocke** :
```javascript
generatedResult = {
  title: "Titre",
  content: "Paroles",
  task_id: "suno_task_xxx",
  has_music: true,
  songs: []  // Ajouté après polling
}
```

---

### **2. Gestion de l'état `isGenerating`**

```javascript
// ✅ BON
setIsGenerating(true);  // Au début
pollTaskStatus(task_id);  // Lance le polling
return;  // NE PAS arrêter isGenerating

// Dans pollTaskStatus :
if (completed) {
  setIsGenerating(false);  // Arrête seulement quand musique prête
}

// ❌ MAUVAIS
setIsGenerating(true);
pollTaskStatus(task_id);
setIsGenerating(false);  // ❌ Trop tôt !
```

---

### **3. Enregistrement dans l'historique**

```javascript
// ✅ BON : Enregistrer dans pollTaskStatus quand musique prête
pollTaskStatus() {
  if (completed && songs.length > 0) {
    addCreation({ title, content, songs });  // ✅ Tout est disponible
    setIsGenerating(false);
  }
}

// ❌ MAUVAIS : Enregistrer avant la musique
handleGenerateContent() {
  addCreation({ title, content });  // ❌ songs[] pas encore disponible
  pollTaskStatus(task_id);
}
```

---

## 📚 Endpoints utilisés

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/generate_rhyme/` | POST | Génération initiale, retourne `task_id` |
| `/check_task_status/{task_id}` | GET | Vérification du statut Suno |
| `/suno-callback` | POST | Callback Suno (requis mais pas utilisé car polling) |
| `/diagnostic/suno` | GET | Diagnostic configuration Suno |

---

## 🎯 Statuts Suno API

| Statut Backend | Statut Suno API | Frontend Action |
|----------------|-----------------|-----------------|
| `processing` | `GENERATING` | Continue polling |
| `processing` | `PENDING` | Continue polling |
| `completed` | `SUCCESS` | Affiche résultat + arrête polling |
| `failed` | `FAILED` | Affiche erreur + arrête polling |

---

## ✅ Checklist de vérification

### **Backend**
- [ ] Endpoint `/generate_rhyme/` retourne `task_id`
- [ ] Endpoint `/check_task_status/{task_id}` utilise `/generate/record-info?taskId=xxx`
- [ ] Parse `data.status` = "SUCCESS" / "GENERATING" / "FAILED"
- [ ] Extrait `data.response.data[]` pour les clips
- [ ] Retourne `songs[]` avec `audio_url`, `video_url`, `title`, `duration`

### **Frontend**
- [ ] `pollTaskStatus()` vérifie `status.status === 'completed'`
- [ ] Vérifie `status.songs && status.songs.length > 0`
- [ ] Met à jour `generatedResult` avec `songs[]`
- [ ] Appelle `setIsGenerating(false)` seulement quand terminé
- [ ] Enregistre dans l'historique avec toutes les données
- [ ] Condition d'affichage : `songs.length > 0`

### **Suno Service**
- [ ] URL correcte : `https://api.sunoapi.org/api/v1/generate`
- [ ] Header : `Authorization: Bearer {SUNO_API_KEY}`
- [ ] Payload inclut `callBackUrl`
- [ ] `customMode: true` → paroles fournies
- [ ] `customMode: false` → Suno génère les paroles

---

## 🚀 Tester l'intégration complète

1. **Génération personnalisée** :
   ```
   Thème : Animaux
   Demande : "Avec le prénom Axel qui joue avec un lapin"
   Attendu : GPT + Suno Custom Mode
   ```

2. **Génération automatique** :
   ```
   Thème : Animaux
   Demande : Aucune
   Attendu : Suno Non-Custom Mode
   ```

3. **Vérifications console** :
   ```
   📊 Statut tâche Suno: GENERATING
   📊 Statut tâche Suno: SUCCESS
   ✅ 2 chanson(s) Suno extraite(s)
   ```

4. **Vérifications visuelles** :
   - Animation reste active pendant 2-3 minutes
   - Résultat apparaît avec 2 chansons + boutons
   - Historique enregistré avec titre + musique

---

**Dernière mise à jour** : 2025-10-06
**Documentation Suno** : https://docs.sunoapi.org/suno-api/quickstart

