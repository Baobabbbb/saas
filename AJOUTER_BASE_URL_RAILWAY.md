# 🔧 Ajouter BASE_URL dans Railway

## 🎯 Problème

L'API fonctionne en local mais échoue sur Railway avec une erreur 500.

**Cause** : La variable `BASE_URL` n'est **pas configurée** dans Railway.

---

## ✅ Solution : Ajouter BASE_URL

### **Étape 1 : Accéder aux Variables**

1. Aller sur https://railway.app
2. Sélectionner votre projet **Herbbie**
3. Cliquer sur le service **saas** (backend)
4. Aller dans l'onglet **Variables**

### **Étape 2 : Ajouter la Variable**

Cliquer sur **"+ New Variable"** et ajouter :

```
BASE_URL=https://herbbie.com
```

**Important** :
- ✅ Pas de `/` à la fin
- ✅ Utiliser `https://` (pas `http://`)
- ✅ Respecter la casse exacte

### **Étape 3 : Redéployer**

Railway va automatiquement redéployer le service après l'ajout de la variable.

**Temps d'attente** : 2-3 minutes

---

## 🧪 Vérification

Une fois le redéploiement terminé, testez :

### **1. Vérifier les Logs**

Dans Railway → Service saas → Deployments → Logs, vous devriez voir :

```
✅ Clé Stability AI détectée: sk-pskwCCsN...
✅ ColoringGeneratorSD3ControlNet initialisé
   - Modèle: sd3-medium
   - API: Stability AI Control Sketch
✅ FastAPI démarré
```

### **2. Tester l'Upload**

1. Aller sur https://herbbie.com
2. Cliquer "Coloriages"
3. Cliquer "Ma Photo 📸"
4. Uploader une image

**URL attendue** :
```
https://herbbie.com/static/uploads/coloring/upload_xyz.jpg
```

✅ Plus de `localhost` !

### **3. Tester la Conversion**

1. Après l'upload, cliquer "Générer"
2. Attendre 20-30 secondes
3. Vérifier le coloriage généré

**Logs Railway attendus** :
```
✅ Photo sauvegardée: upload_xyz.jpg
🎨 Conversion photo en coloriage: /app/static/uploads/coloring/upload_xyz.jpg
   - Mode ControlNet: canny
   - Force: 0.7
📡 Appel API Stability AI...
   - URL: https://api.stability.ai/v2beta/stable-image/control/structure
   - API Key présente: Oui
📥 Réponse API: 200
✅ Image SD3 générée: coloring_sd3_abc.png
✅ Post-traitement appliqué
```

---

## 📊 Variables Complètes Railway

Voici toutes les variables **essentielles** pour le système de coloriages :

| Variable | Valeur | Status | Description |
|----------|--------|--------|-------------|
| `STABILITY_API_KEY` | `sk-pskw...` | ✅ Configurée | Clé API Stability AI |
| `BASE_URL` | `https://herbbie.com` | ❌ **À AJOUTER** | URL de base pour production |
| `OPENAI_API_KEY` | `sk-proj-...` | ✅ Configurée | Clé API OpenAI |
| `TEXT_MODEL` | `gpt-4o-mini` | ✅ Configurée | Modèle pour texte |
| `IMAGE_MODEL` | `stability-ai` | ✅ Configurée | Modèle pour images |
| `FAL_API_KEY` | `...` | ✅ Configurée | Pour audio/vidéo |
| `WAVESPEED_API_KEY` | `...` | ✅ Configurée | Pour animations |
| `GOAPI_API_KEY` | `...` | ✅ Configurée | Pour comptines |
| `JWT_SECRET` | `...` | ✅ Configurée | Pour authentification |

---

## 🐛 Dépannage

### **Problème : Erreur 500 Persiste**

**Vérifications** :

1. **Variable ajoutée ?**
   ```
   Railway → Variables → Vérifier BASE_URL
   ```

2. **Redéploiement terminé ?**
   ```
   Railway → Deployments → Status = "Success"
   ```

3. **Logs propres ?**
   ```
   Railway → Logs → Pas d'erreur Python
   ```

### **Problème : Mixed Content Error**

**Symptôme** :
```
Mixed Content: The page at 'https://herbbie.com' was loaded over HTTPS, 
but requested an insecure resource 'http://localhost:8006/...'
```

**Solution** :
```
✅ BASE_URL doit être https://herbbie.com (pas localhost)
```

### **Problème : Clé API Invalide**

**Symptôme** :
```
❌ Erreur API Stability: 401 - {"message": "Invalid API key"}
```

**Solution** :
```
1. Vérifier STABILITY_API_KEY dans Railway
2. La clé doit commencer par "sk-"
3. Tester avec le script test_stability_api.py
```

### **Problème : Crédits Insuffisants**

**Symptôme** :
```
❌ Erreur API Stability: 402 - {"message": "Insufficient credits"}
```

**Solution** :
```
1. Aller sur https://platform.stability.ai
2. Recharger des crédits
3. Vérifier le solde : https://platform.stability.ai/account/credits
```

---

## 📝 Checklist Finale

Avant de tester, vérifier :

- [ ] Variable `BASE_URL=https://herbbie.com` ajoutée dans Railway
- [ ] Redéploiement Railway terminé (logs verts)
- [ ] Aucune erreur dans les logs de démarrage
- [ ] Service accessible sur https://herbbie.com
- [ ] Frontend déployé dans `saas/static/`
- [ ] `STABILITY_API_KEY` valide et avec des crédits

---

## 🎉 Résultat Attendu

Après l'ajout de `BASE_URL`, le workflow complet devrait fonctionner :

```
1. Upload photo
   → URL: https://herbbie.com/static/uploads/coloring/upload_xyz.jpg ✅

2. Conversion ControlNet
   → Chemin: /app/static/uploads/coloring/upload_xyz.jpg ✅
   → Canny appliqué ✅

3. API Stability AI
   → Endpoint: /control/structure ✅
   → Réponse: 200 ✅
   → Image générée ✅

4. Post-traitement
   → Noir/blanc pur ✅
   → Sauvegarde ✅

5. Retour frontend
   → URL: https://herbbie.com/static/coloring/coloring_xyz.png ✅
   → Affichage ✅
   → Téléchargement PDF ✅
```

---

## 🚀 Commande Rapide

Pour ajouter la variable via CLI (si Railway CLI installé) :

```bash
cd C:\Users\freda\Desktop\projet\backend
railway variables set BASE_URL=https://herbbie.com
```

Sinon, utilisez l'interface web (méthode recommandée).

---

**🎨 Une fois BASE_URL ajoutée, le système devrait fonctionner à 100% !** ✨

---

*Guide Railway - Variable BASE_URL*  
*Version 1.0 - Octobre 2025*  
*La dernière pièce du puzzle !* 🧩

