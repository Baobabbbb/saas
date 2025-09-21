# 🔑 Configuration des API Keys pour VRAIE Génération d'Animations

## 📋 Vue d'ensemble

Actuellement, le système fonctionne en **mode démo** avec des vidéos de haute qualité. Pour obtenir des **VRAIS dessins animés générés par IA**, il faut configurer les API keys suivantes.

## 🎯 APIs Requises (basées sur zseedance.json)

### 1. 🎬 Wavespeed AI - Génération Vidéo
- **Usage** : Génère les clips vidéo à partir de prompts textuels
- **Endpoint** : `seedance-v1-pro-t2v-480p`
- **Où s'inscrire** : https://wavespeed.ai
- **Variable** : `WAVESPEED_API_KEY`

### 2. 🎵 Fal AI - Audio & Assemblage
- **Usage** : 
  - `mmaudio-v2` : Génère l'audio synchronisé
  - `ffmpeg-api/compose` : Assemble la vidéo finale
- **Où s'inscrire** : https://fal.ai
- **Variable** : `FAL_API_KEY`

### 3. 🧠 OpenAI - Idées Créatives
- **Usage** : Génère les idées d'animations et descriptions de scènes
- **Où s'inscrire** : https://platform.openai.com
- **Variable** : `OPENAI_API_KEY`

## ⚙️ Configuration sur Railway

### Étape 1 : Obtenir les clés
1. Créez des comptes sur les 3 plateformes
2. Générez vos API keys
3. Conservez-les en sécurité

### Étape 2 : Configurer Railway
1. Allez sur votre dashboard Railway
2. Sélectionnez votre projet backend
3. Onglet **Variables**
4. Ajoutez les variables :

```env
WAVESPEED_API_KEY=your_wavespeed_key_here
FAL_API_KEY=your_fal_key_here  
OPENAI_API_KEY=your_openai_key_here
```

### Étape 3 : Redémarrer
1. Redéployez le service
2. Le système détectera automatiquement les APIs

## 🔄 Pipeline de Génération RÉELLE

Avec les APIs configurées, voici ce qui se passera :

```
1. 🧠 OpenAI → Génère idée créative selon thème
2. 🎬 Wavespeed → Crée 3 clips vidéo de 10s chacun
3. 🎵 Fal AI → Ajoute audio synchronisé aux clips
4. 🔧 Fal AI → Assemble en vidéo finale de 30s
5. ✅ Animation unique et personnalisée !
```

## ⏱️ Temps de Génération

- **Mode démo** : 3 minutes (vidéos Google existantes)
- **Mode réel** : 5-7 minutes (génération IA complète)

## 🎯 Différences Mode Démo vs Réel

| Aspect | Mode Démo | Mode Réel |
|--------|-----------|-----------|
| Vidéos | Google samples | Générées par IA |
| Audio | Aucun | Synchronisé thématique |
| Unicité | Répétitif | Unique à chaque fois |
| Qualité | Haute mais générique | Personnalisée |
| Coût | Gratuit | Selon usage APIs |

## 🚨 Vérification du Mode Actif

Dans les logs du serveur, vous verrez :
- **Mode démo** : `"pipeline_type": "demo_mode"`
- **Mode réel** : `"pipeline_type": "real_ai_generation"`

## 💡 Conseils

1. **Testez d'abord** avec une seule API pour vérifier la connexion
2. **Surveillance des coûts** : Les APIs sont payantes selon usage
3. **Sauvegarde** : Gardez une copie de vos API keys
4. **Sécurité** : Ne jamais exposer les clés dans le code

Une fois configuré, chaque génération d'animation sera **unique, personnalisée et créée spécialement selon vos paramètres** ! 🎬✨
