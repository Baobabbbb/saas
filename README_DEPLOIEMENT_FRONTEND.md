# 🚀 Guide de Déploiement Frontend sur Railway

## 📋 Architecture

Le frontend React est **servi comme fichiers statiques** par FastAPI depuis `backend/saas/static/`.

```
backend/
├── frontend/           # Source React + Vite
│   ├── src/           # Code source
│   ├── dist/          # Build généré
│   └── package.json
└── saas/
    ├── main.py        # FastAPI serveur
    └── static/        # Frontend déployé (copie de frontend/dist)
        ├── index.html
        └── assets/
```

---

## ⚡ Déploiement Rapide (Script Automatique)

### **Windows**
```bash
cd C:\Users\freda\Desktop\projet\backend
deploy_frontend.bat
```

Le script va :
1. ✅ Builder le frontend (`npm run build`)
2. ✅ Copier vers `saas/static/`
3. ✅ Commiter les changements
4. ✅ Pusher vers Railway

---

## 🔧 Déploiement Manuel

### **Étape 1 : Build du Frontend**
```bash
cd C:\Users\freda\Desktop\projet\backend\frontend
npm run build
```

**Résultat** : Les fichiers sont générés dans `frontend/dist/`

### **Étape 2 : Copier vers Static**
```bash
cd C:\Users\freda\Desktop\projet\backend

# Windows
xcopy /E /I /Y frontend\dist saas\static

# Linux/Mac
cp -r frontend/dist/* saas/static/
```

### **Étape 3 : Commit et Push**
```bash
git add frontend/dist saas/static
git commit -m "feat: Update frontend build"
git push origin main
```

### **Étape 4 : Attendre le Déploiement**
Railway détecte le push et redéploie automatiquement (~2-3 minutes).

---

## 🧪 Vérification Post-Déploiement

### **1. Health Check**
```bash
curl https://herbbie.com/
```

### **2. Vérifier le Frontend**
Ouvrir https://herbbie.com dans un navigateur :
- ✅ Interface chargée
- ✅ Bouton "Ma Photo 📸" visible dans Coloriages
- ✅ Upload de photo fonctionnel
- ✅ Console sans erreurs

### **3. Test Complet**
1. Aller sur https://herbbie.com
2. Cliquer "Coloriages"
3. Vérifier les 11 boutons :
   - 📸 Ma Photo
   - ✏️ Coloriage personnalisé
   - 🐾 Animaux
   - 🚀 Espace
   - 🧚 Fées
   - 🦸 Super-héros
   - 🌺 Nature
   - 🚗 Véhicules
   - 🤖 Robots
   - 👸 Princesses
   - 🦕 Dinosaures

---

## 🐛 Dépannage

### **Problème : Bouton "Ma Photo" pas visible**

**Cause** : Frontend pas rebuild ou pas copié vers static/

**Solution** :
```bash
cd backend/frontend
npm run build
cd ..
xcopy /E /I /Y frontend\dist saas\static
git add -A
git commit -m "fix: Rebuild et redeploy frontend"
git push origin main
```

### **Problème : Modifications non visibles**

**Cause** : Cache navigateur

**Solution** :
1. Ouvrir DevTools (F12)
2. Clic droit sur Actualiser → Vider le cache et actualiser
3. Ou CTRL+SHIFT+R (hard refresh)

### **Problème : 404 sur les assets**

**Cause** : Fichiers pas copiés correctement

**Solution** :
```bash
# Vérifier que les fichiers existent
ls saas/static/assets/

# Si vide, recopier
xcopy /E /I /Y frontend\dist saas\static
```

---

## 📊 Checklist de Déploiement

Avant de déployer, vérifier :

- [ ] Tests locaux passent (`npm run dev`)
- [ ] Build réussit (`npm run build`)
- [ ] Aucune erreur dans la console
- [ ] `frontend/dist/` contient les fichiers
- [ ] Copie vers `saas/static/` effectuée
- [ ] Git status vérifié
- [ ] Commit avec message clair
- [ ] Push vers origin/main
- [ ] Attendre fin du déploiement Railway (logs verts)
- [ ] Test sur https://herbbie.com
- [ ] Hard refresh du navigateur

---

## ⚙️ Configuration FastAPI

Le serveur FastAPI sert automatiquement les fichiers statiques :

```python
# main.py
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

**Important** : Ceci doit être la **dernière route** dans `main.py` (après tous les endpoints API).

---

## 🔄 Workflow Développement

### **Développement Local**
```bash
cd frontend
npm run dev
```
Frontend sur http://localhost:5173

### **Test Production Locale**
```bash
cd frontend
npm run build
cd ..

# Lancer FastAPI
cd saas
uvicorn main:app --reload --port 8006
```
Frontend sur http://localhost:8006

### **Déploiement Production**
```bash
./deploy_frontend.bat
```
Frontend sur https://herbbie.com

---

## 📝 Notes Importantes

1. **Ne jamais éditer** directement dans `saas/static/` - éditer dans `frontend/src/`
2. **Toujours rebuild** avant de commiter
3. **Vérifier les logs Railway** après déploiement
4. **Hard refresh** navigateur pour voir les changements
5. **Ne pas commiter** `node_modules/` ou fichiers temporaires

---

## 🚀 Commandes Utiles

```bash
# Build + Deploy complet
npm run build && xcopy /E /I /Y frontend\dist saas\static && git add -A && git commit -m "deploy: Update frontend" && git push

# Vérifier les fichiers static
dir saas\static\assets

# Voir les logs Railway (si CLI installé)
railway logs

# Test local du build
cd saas && uvicorn main:app --reload
```

---

## 🎯 Résumé

**Pour déployer le frontend :**

1. `cd backend/frontend && npm run build`
2. `cd .. && xcopy /E /I /Y frontend\dist saas\static`
3. `git add -A && git commit -m "deploy: frontend" && git push`
4. Attendre 2-3 minutes
5. Tester sur https://herbbie.com

**Ou simplement :**
```bash
./deploy_frontend.bat
```

---

*Guide de Déploiement Frontend - Railway*  
*Version 1.0 - Octobre 2025*

