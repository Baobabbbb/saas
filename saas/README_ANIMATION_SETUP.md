# 🚀 Configuration du Système d'Animation HERBBIE

## 📋 Vue d'ensemble

Le système d'animation HERBBIE nécessite plusieurs APIs pour fonctionner correctement. Voici la configuration complète requise.

---

## 🔑 APIs Obligatoires

### 1. OpenAI API (CRITIQUE)
```env
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```
- **Utilisation** : GPT-4o-mini (idées/scénarios) + gpt-image-1-mini-mini (coloriages/BD)
- **Coût** : ~$0.01 par animation
- **Organisation** : Nécessite une organisation OpenAI vérifiée

### 2. Suno API (Comptines)
```env
SUNO_API_KEY=your-suno-api-key-here
SUNO_BASE_URL=https://api.sunoapi.org/api/v1
```
- **Utilisation** : Génération de comptines musicales
- **Coût** : Variable selon l'usage

### 3. Supabase (Authentification)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```
- **Utilisation** : Authentification utilisateur et stockage

---

## 🎬 APIs Animation (Au moins une requise)

### Option 1: Runway ML (RECOMMANDÉ)
```env
RUNWAY_API_KEY=your-runway-api-key-here
```
- **Avantages** : Qualité cinéma, Veo 3.1 Fast
- **Coût** : ~$0.02 par seconde de vidéo
- **Utilisation** : Mode Sora 2 et Production

### Option 2: Wavespeed AI
```env
WAVESPEED_API_KEY=your-wavespeed-api-key-here
```
- **Avantages** : Bon rapport qualité/prix
- **Modèle** : SeedANce v1 Pro T2V 480p
- **Utilisation** : Mode démo et production

### Option 3: FAL AI (Assemblage)
```env
FAL_API_KEY=your-fal-api-key-here
```
- **Utilisation** : Audio MMAudio + assemblage FFmpeg
- **Coût** : ~$0.005 par génération

---

## 🎯 Modes de Génération

### Mode Demo (Par défaut)
- **Générateur** : `RealAnimationGenerator`
- **APIs requises** : Aucune (utilise des vidéos de démo)
- **Qualité** : Standard
- **Durée** : 2-5 minutes
- **Coût** : Gratuit

### Mode Sora 2
- **Générateur** : `Sora2Generator`
- **APIs requises** : RUNWAY_API_KEY ou PIKA_API_KEY
- **Qualité** : Haute (cinéma)
- **Durée** : 5-10 minutes
- **Coût** : ~$0.02/s

### Mode Production
- **Générateur** : `Sora2ZseedanceGenerator`
- **APIs requises** : RUNWAY_API_KEY + FAL_API_KEY
- **Qualité** : Maximum
- **Durée** : 10-15 minutes
- **Coût** : ~$0.03/s

---

## ⚙️ Configuration Complète

### Fichier .env complet :
```env
# APIs OBLIGATOIRES
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
SUNO_API_KEY=your-suno-api-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key

# APIs Animation (au moins une)
RUNWAY_API_KEY=your-runway-api-key-here
WAVESPEED_API_KEY=your-wavespeed-api-key-here
FAL_API_KEY=your-fal-api-key-here

# APIs Optionnelles
STABILITY_API_KEY=sk-your-stability-api-key-here
PIKA_API_KEY=your-pika-api-key-here
LUMA_API_KEY=your-luma-api-key-here
RESEND_API_KEY=your-resend-api-key

# Configuration
BASE_URL=https://herbbie.com
TEXT_MODEL=gpt-4o-mini
PORT=8000
ENVIRONMENT=production
```

---

## 🧪 Tests et Validation

### Vérifier la configuration :
```bash
# Test du backend
cd backend/saas
python -c "from main import app; print('✅ Backend OK')"

# Test des APIs
curl http://localhost:8000/diagnostic

# Test génération
curl "http://localhost:8000/generate-quick?theme=space&duration=30&mode=demo"
```

### Résultats attendus :
- **Mode Demo** : ✅ Toujours fonctionnel (fallback automatique)
- **Mode Sora 2** : ✅ Si RUNWAY_API_KEY configuré
- **Mode Production** : ✅ Si RUNWAY_API_KEY + FAL_API_KEY configurés

---

## 🚨 Dépannage

### Problème : "Aucune plateforme Sora 2 disponible"
**Solution** : Configurer au moins une API (RUNWAY_API_KEY, PIKA_API_KEY, etc.)

### Problème : "Erreur génération idée"
**Solution** : Vérifier OPENAI_API_KEY

### Problème : "Timeout génération"
**Solution** : Réduire la durée ou utiliser le mode demo

### Problème : "Erreur assemblage vidéo"
**Solution** : Vérifier FAL_API_KEY ou utiliser un seul clip

---

## 💰 Estimation des Coûts

### Par animation (30 secondes) :
- **Demo** : $0.00 (gratuit)
- **Sora 2** : $0.60 (0.02$/s × 30s)
- **Production** : $0.90 (0.03$/s × 30s)

### APIs supplémentaires :
- **GPT-4o-mini** : ~$0.01 par animation
- **gpt-image-1-mini-mini** : ~$0.02 par coloriage/BD
- **Suno** : Variable selon la durée

---

## 🎯 Recommandations

1. **Pour commencer** : Configurer `OPENAI_API_KEY` + mode demo
2. **Pour la production** : Ajouter `RUNWAY_API_KEY` + `FAL_API_KEY`
3. **Pour les économies** : Utiliser le mode demo pour les tests
4. **Monitoring** : Vérifier les logs et les diagnostics régulièrement

---

*Dernière mise à jour : Octobre 2025*
