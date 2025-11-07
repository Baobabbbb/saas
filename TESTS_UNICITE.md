# 🧪 Tests Pratiques - Système d'Unicité

## 🎯 Objectif
Vérifier que le système d'unicité fonctionne correctement et empêche les doublons.

---

## 📋 Prérequis

1. **Serveur démarré** :
```bash
cd backend/saas
uvicorn main:app --reload --port 8000
```

2. **Variables d'environnement configurées** :
```bash
SUPABASE_URL=https://xfbmdeuzuyixpmouhqcv.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<votre_clé>
ENABLE_UNIQUENESS_CHECK=true
```

3. **User ID de test** :
```
test-user-unicite-123
```

---

## 🧪 Test 1 : Histoire Unique (Succès attendu)

### Commande
```bash
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "espace",
    "custom_request": "",
    "user_id": "test-user-unicite-123"
  }' | jq
```

### Résultat Attendu
```json
{
  "title": "Voyage dans les étoiles",
  "content": "Il était une fois...",
  "audio_path": null,
  "audio_generated": false,
  "type": "audio",
  "uniqueness_metadata": {
    "content_hash": "a1b2c3d4e5f6...",
    "summary": "Histoire d'un astronaute qui découvre...",
    "variation_tags": {
      "content_type": "histoire",
      "theme": "espace",
      "custom_request": null,
      "generated_at": "2025-11-07T..."
    }
  }
}
```

### Vérification
- ✅ `uniqueness_metadata` présent
- ✅ `content_hash` non null
- ✅ Pas de message d'erreur dans les logs

---

## 🧪 Test 2 : Détection de Doublon (Régénération attendue)

### Étape 1 : Première génération
```bash
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "dinosaures",
    "custom_request": "avec un T-Rex gentil",
    "user_id": "test-user-unicite-456"
  }' | jq '.content' > histoire1.txt
```

### Étape 2 : Deuxième génération (même paramètres)
```bash
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "dinosaures",
    "custom_request": "avec un T-Rex gentil",
    "user_id": "test-user-unicite-456"
  }' | jq '.content' > histoire2.txt
```

### Étape 3 : Comparer
```bash
diff histoire1.txt histoire2.txt
```

### Résultat Attendu
- ✅ Les deux histoires sont **DIFFÉRENTES**
- ✅ Logs montrent : `🔄 Doublon détecté pour histoire dinosaures, régénération...`
- ✅ Les `content_hash` sont différents

---

## 🧪 Test 3 : Enrichissement avec Historique

### Générer 3 histoires sur le même thème
```bash
# Histoire 1
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "océan",
    "user_id": "test-user-unicite-789"
  }' | jq '.title'

# Histoire 2
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "océan",
    "user_id": "test-user-unicite-789"
  }' | jq '.title'

# Histoire 3
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "océan",
    "user_id": "test-user-unicite-789"
  }' | jq '.title'
```

### Résultat Attendu
- ✅ 3 histoires **complètement différentes**
- ✅ Titres différents
- ✅ Personnages différents
- ✅ Scénarios variés

---

## 🧪 Test 4 : Coloriage avec Variation

### Générer 2 coloriages sur le même thème
```bash
# Coloriage 1
curl -X POST http://localhost:8000/generate_coloring/ \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "animaux",
    "with_colored_model": true,
    "user_id": "test-user-unicite-coloring"
  }' | jq '.images[0].image_url'

# Coloriage 2
curl -X POST http://localhost:8000/generate_coloring/ \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "animaux",
    "with_colored_model": true,
    "user_id": "test-user-unicite-coloring"
  }' | jq '.images[0].image_url'
```

### Résultat Attendu
- ✅ 2 images **différentes**
- ✅ Le prompt du 2ème coloriage contient une indication de variation
- ✅ Logs montrent l'historique consulté

---

## 🧪 Test 5 : Service Désactivé (Mode Dégradé)

### Configuration
```bash
export ENABLE_UNIQUENESS_CHECK=false
# Relancer le serveur
```

### Générer une histoire
```bash
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "pirates",
    "user_id": "test-user-unicite-disabled"
  }' | jq '.uniqueness_metadata'
```

### Résultat Attendu
```json
{
  "uniqueness_metadata": null
}
```
- ✅ Pas de métadonnées d'unicité
- ✅ Histoire générée normalement
- ✅ Aucune erreur

---

## 🧪 Test 6 : Sans User ID (Utilisateur Non Connecté)

### Commande
```bash
curl -X POST http://localhost:8000/generate_audio_story/ \
  -H "Content-Type: application/json" \
  -d '{
    "story_type": "espace"
  }' | jq
```

### Résultat Attendu
- ✅ Histoire générée normalement
- ✅ `uniqueness_metadata` peut être null ou minimal
- ✅ Pas d'erreur (système non-bloquant)

---

## 🧪 Test 7 : Bande Dessinée avec Historique

### Générer une BD
```bash
curl -X POST http://localhost:8000/generate_comic/ \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "super-héros",
    "art_style": "cartoon",
    "num_pages": 1,
    "user_id": "test-user-unicite-bd"
  }' | jq '.task_id'
```

### Vérifier le statut
```bash
# Récupérer le task_id de la réponse, puis :
curl http://localhost:8000/comic_status/<task_id> | jq
```

### Résultat Attendu
- ✅ `uniqueness_metadata` présent dans le résultat final
- ✅ Synopsis différent à chaque génération sur le même thème

---

## 🧪 Test 8 : Comptine avec Personnalisation

### Première comptine
```bash
curl -X POST http://localhost:8000/generate_rhyme/ \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "animals",
    "custom_request": "",
    "user_id": "test-user-unicite-rhyme"
  }' | jq '.title'
```

### Deuxième comptine (même thème)
```bash
curl -X POST http://localhost:8000/generate_rhyme/ \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "animals",
    "custom_request": "",
    "user_id": "test-user-unicite-rhyme"
  }' | jq '.title'
```

### Résultat Attendu
- ✅ Titres différents
- ✅ Paroles différentes
- ✅ Structure musicale variée

---

## 🧪 Test 9 : Animation avec Variation

### Première animation
```bash
curl -X POST http://localhost:8000/generate_animation/ \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "space",
    "duration": 30,
    "style": "cartoon",
    "user_id": "test-user-unicite-anim"
  }' | jq '.task_id'
```

### Deuxième animation (même paramètres)
```bash
curl -X POST http://localhost:8000/generate_animation/ \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "space",
    "duration": 30,
    "style": "cartoon",
    "user_id": "test-user-unicite-anim"
  }' | jq '.task_id'
```

### Résultat Attendu
- ✅ Logs montrent : consultation de l'historique
- ✅ Le custom_prompt de la 2ème animation contient `[Variation #2]`

---

## 🔍 Vérification en Base de Données

### Consulter les hash créés
```sql
SELECT 
  id, 
  user_id, 
  type, 
  title, 
  content_hash, 
  summary,
  data->'variation_tags' as variation_tags,
  created_at
FROM creations
WHERE user_id LIKE 'test-user-unicite-%'
ORDER BY created_at DESC
LIMIT 10;
```

### Résultat Attendu
- ✅ `content_hash` rempli pour chaque création
- ✅ `summary` présent et pertinent
- ✅ `variation_tags` dans le champ data

---

## 📊 Validation Globale

### Checklist Finale
- [ ] ✅ Histoires : doublons détectés et régénérés
- [ ] ✅ Coloriages : variations automatiques
- [ ] ✅ Comptines : prompts enrichis avec historique
- [ ] ✅ BD : custom_prompt avec suggestions
- [ ] ✅ Animations : numéro de variation ajouté
- [ ] ✅ Service désactivable sans erreur
- [ ] ✅ Fonctionne sans user_id
- [ ] ✅ Hash stockés en base
- [ ] ✅ Pas de ralentissement perceptible
- [ ] ✅ Logs clairs et informatifs

---

## 🚨 Troubleshooting

### Problème : Pas de `uniqueness_metadata`

**Solution** :
1. Vérifier `SUPABASE_SERVICE_ROLE_KEY` configurée
2. Vérifier `ENABLE_UNIQUENESS_CHECK=true`
3. Vérifier les logs pour messages d'erreur

### Problème : Toujours les mêmes contenus

**Solution** :
1. Vérifier que `user_id` est fourni
2. Vérifier les logs : `⚠️ Service unicité non disponible`
3. Consulter la table `creations` pour voir si les hash sont stockés

### Problème : Erreur 500

**Solution** :
1. Le système est non-bloquant, ça ne devrait pas arriver
2. Vérifier les logs Python
3. Désactiver temporairement : `ENABLE_UNIQUENESS_CHECK=false`

---

## 📝 Notes Importantes

- Les tests doivent être effectués avec un **serveur fraîchement démarré**
- Utiliser des **user_id différents** pour chaque série de tests
- Les doublons ne sont détectés que pour **le même user_id**
- La régénération n'arrive que **si le hash est identique**

---

## 🎓 Documentation Complète

Pour plus d'informations :
- **`SYSTEME_UNICITE.md`** : Documentation technique
- **`IMPLEMENTATION_UNICITE_RESUME.md`** : Résumé de l'implémentation

---

## ✅ Validation Réussie

Une fois tous les tests passés, le système est **validé et prêt pour la production** ! 🚀

