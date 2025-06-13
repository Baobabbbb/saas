# Intégration Veo3 via fal-ai

## ✅ Migration réussie

L'API de génération d'animations a été migrée avec succès de Google Cloud vers fal-ai pour utiliser le modèle Veo3.

## 🔧 Configuration

### Variables d'environnement (.env)
```bash
# VEO3 via FAL-AI
FAL_API_KEY=votre_clé_fal_ai
FAL_BASE_URL=https://queue.fal.run
```

### Obtenir une clé API fal-ai
1. Rendez-vous sur https://fal.ai/dashboard
2. Créez un compte ou connectez-vous
3. Allez dans "API Keys" 
4. Créez une nouvelle clé API
5. Ajoutez des crédits sur https://fal.ai/dashboard/billing

## 📡 Endpoints disponibles

### Génération d'animation
```
POST /api/animations/generate
```

**Body JSON :**
```json
{
  "style": "cartoon",           // cartoon, fairy_tale, anime, realistic, etc.
  "theme": "animals",           // adventure, magic, animals, friendship, etc.  
  "orientation": "landscape",   // landscape, portrait
  "prompt": "Description personnalisée",
  "title": "Titre de l'animation"
}
```

**Réponse :**
```json
{
  "id": "unique_id",
  "video_url": "https://v3.fal.media/files/...",
  "title": "Titre de l'animation",
  "status": "completed",
  "created_at": "2025-06-13T...",
  "completed_at": "2025-06-13T..."
}
```

### Statut d'animation
```
GET /api/animations/{animation_id}/status
```

### Récupération d'animation
```
GET /api/animations/{animation_id}
```

### Liste des animations
```
GET /api/animations
```

## 🎥 Spécifications Veo3

- **Durée :** 8 secondes (fixe)
- **Formats :** 16:9, 9:16, 1:1
- **Audio :** Activé par défaut (-33% crédits si désactivé)
- **Qualité :** Haute définition
- **Style :** Optimisé pour les contenus enfants/cartoon

## 🔄 Flux de traitement

1. **Soumission** : Envoi du prompt à fal-ai/veo3
2. **Polling** : Vérification du statut toutes les 5 secondes
3. **Récupération** : Téléchargement de la vidéo générée
4. **Retour** : URL de la vidéo accessible

## 🎯 Tests

### Test manuel
```bash
python test_veo3_fal_simple.py
```

### Test via curl
```bash
curl -X POST http://localhost:8000/api/animations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "style": "cartoon",
    "theme": "animals",
    "orientation": "landscape",
    "prompt": "Un chat orange qui joue dans un jardin",
    "title": "Chat Joueur"
  }'
```

## ⚠️ Gestion d'erreurs

- **403 Quota épuisé** : Message clair pour recharger le compte
- **Timeout** : 300 secondes maximum par génération
- **Échec génération** : Retry automatique avec backoff

## 📊 Monitoring

Les logs incluent :
- Temps de génération
- Taille des fichiers vidéo
- Status des requêtes
- Erreurs détaillées

## 🚀 Intégration frontend

Le frontend peut utiliser les endpoints comme avant, la migration est transparente pour l'interface utilisateur.

## 🔗 Liens utiles

- Dashboard fal-ai : https://fal.ai/dashboard
- Documentation API : https://fal.ai/models/fal-ai/veo3/api
- Playground : https://fal.ai/models/fal-ai/veo3
- Billing : https://fal.ai/dashboard/billing
