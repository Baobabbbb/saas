# 🚀 Variables Railway à configurer pour Suno AI

## ⚠️ URGENT - Configurer ces variables dans Railway

### 📝 Variables à AJOUTER :

```bash
SUNO_API_KEY=9f66bd58bf7e20ef99f9bf138b6bbde5
SUNO_BASE_URL=https://api.sunoapi.org/api/v1
```

### 🗑️ Variables à SUPPRIMER (si elles existent) :

```bash
GOAPI_API_KEY
UDIO_MODEL
UDIO_TASK_TYPE
```

## 📋 Comment ajouter les variables dans Railway :

1. Aller sur https://railway.app
2. Sélectionner le projet `saas-production`
3. Cliquer sur l'onglet **Variables**
4. Ajouter les 2 nouvelles variables Suno
5. Supprimer les anciennes variables Udio (si présentes)
6. Railway redéploiera automatiquement

## ✅ Vérification :

Une fois les variables ajoutées, le backend devrait :
- ✅ Démarrer sans erreur 500
- ✅ Générer des comptines avec Suno AI
- ✅ Retourner 2 chansons par génération
- ✅ Afficher correctement dans le frontend

## 🔍 Variables déjà configurées (à garder) :

```bash
OPENAI_API_KEY=(déjà configurée - ne pas toucher)
STABILITY_API_KEY=(déjà configurée - ne pas toucher)
TEXT_MODEL=gpt-4o-mini
BASE_URL=https://herbbie.com
```

---

**Note** : Les variables sensibles (clés API) ne doivent JAMAIS être commitées dans Git. Elles doivent être configurées uniquement dans Railway.

