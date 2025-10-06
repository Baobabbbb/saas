# 🔍 Guide de dépannage HTTP 500 sur /generate_rhyme/

## 🐛 Problème rencontré

**Erreur** : `HTTP 500 (Internal Server Error)` sur `/generate_rhyme/`
**Message mystérieux** : `"await in yt"` dans le stack trace

---

## ✅ Solutions appliquées

### **1. Refactorisation complète de la logique**

**Avant** : Logique complexe mêlée dans l'endpoint async
```python
@app.post("/generate_rhyme/")
async def generate_rhyme(request: dict):
    # Logique de détection directement dans async
    import re
    needs_customization = False
    for indicator in personalization_indicators:
        if isinstance(indicator, str):
            ...
        else:  # regex
            ...
```

**Après** : Fonction helper isolée
```python
def _detect_customization(custom_request: str) -> bool:
    """Fonction synchrone pure - pas de async"""
    import re
    # Logique claire et testable
    return needs_customization

@app.post("/generate_rhyme/")
async def generate_rhyme(request: dict):
    needs_customization = _detect_customization(custom_request)
    # Suite...
```

---

### **2. Endpoint de test ajouté**

```python
@app.post("/test_rhyme_simple/")
async def test_rhyme_simple():
    return {"status": "ok", "message": "Test OK"}
```

**Test** :
```bash
curl -X POST https://herbbie.com/test_rhyme_simple/
```

---

## 🧪 Étapes de diagnostic

### **Étape 1 : Vérifier que Railway a redéployé**
1. Aller sur https://railway.app
2. Vérifier que le dernier commit est déployé
3. Attendre 2-3 minutes pour le build

### **Étape 2 : Tester l'endpoint simple**
```bash
curl -X POST https://herbbie.com/test_rhyme_simple/
```

**Attendu** : `{"status":"ok","message":"Test endpoint fonctionne","timestamp":"..."}`

### **Étape 3 : Tester /generate_rhyme/ mode auto**
```bash
curl -X POST https://herbbie.com/generate_rhyme/ \
  -H "Content-Type: application/json" \
  -d '{"theme":"animal","custom_request":""}'
```

**Attendu** : `{"title":"...","content":"...","task_id":"suno_task_..."}`

### **Étape 4 : Vérifier les logs Railway**
1. Console Railway → Logs
2. Chercher : `📥 Requête comptine`
3. Vérifier : `📊 Détection: False/True`
4. Suivre : `🤖 MODE AUTOMATIQUE` ou `🎨 MODE PERSONNALISÉ`

---

## 🔑 Points critiques vérifiés

### **Variables d'environnement Railway**
- ✅ `SUNO_API_KEY` = `9f66bd58bf...`
- ✅ `SUNO_BASE_URL` = `https://api.sunoapi.org/api/v1`
- ✅ `OPENAI_API_KEY` = Configurée

### **Structure du code**
- ✅ `_detect_customization()` : Fonction synchrone isolée
- ✅ `generate_rhyme()` : Appelle la fonction helper
- ✅ Import `re` dans la fonction (pas global)
- ✅ Pas de mix regex/string dans une boucle

### **Syntaxe Python**
```bash
python -m py_compile main.py
# Pas d'erreur = OK
```

---

## 🚨 Si le problème persiste

### **Option 1 : Vider le cache Railway**
1. Railway Dashboard → Settings
2. Redeploy from scratch
3. Attendre le build complet

### **Option 2 : Vérifier les dépendances**
```bash
# Dans Railway
pip list | grep -E "openai|aiohttp|fastapi"
```

### **Option 3 : Logs détaillés**
Ajouter des logs dans `main.py` :
```python
@app.post("/generate_rhyme/")
async def generate_rhyme(request: dict):
    print("🔵 START generate_rhyme")
    try:
        print("🔵 Parsing request...")
        theme = request.get("theme", "animaux")
        print(f"🔵 Theme: {theme}")
        
        custom_request = request.get("custom_request", "")
        print(f"🔵 Custom request: {custom_request[:50]}")
        
        print("🔵 Calling _detect_customization...")
        needs_customization = _detect_customization(custom_request)
        print(f"🔵 Result: {needs_customization}")
        
        # ... suite
```

### **Option 4 : Rollback vers version stable**
```bash
git log --oneline -10
# Trouver le dernier commit qui marchait
git reset --hard <commit-hash>
git push --force origin main
```

---

## 📚 Documentation de référence

- **Suno API** : https://docs.sunoapi.org/suno-api/quickstart
- **FastAPI Async** : https://fastapi.tiangolo.com/async/
- **Python re module** : https://docs.python.org/3/library/re.html

---

## ✅ Checklist finale

Avant de dire "ça ne marche pas" :

- [ ] Railway a bien redéployé (check commit hash)
- [ ] Attendu 3 minutes après le push
- [ ] Testé `/test_rhyme_simple/` → OK
- [ ] Testé `/diagnostic/suno` → `"status":"ready"`
- [ ] Vérifié les logs Railway (pas d'erreur 500)
- [ ] Testé avec demande simple (pas de custom_request)
- [ ] Vidé le cache du navigateur (Ctrl+Shift+R)
- [ ] Testé avec curl (pas juste le navigateur)

---

**Dernière mise à jour** : 2025-10-06
**Commit de référence** : `4aedadb` - Refactor complet logique personnalisation

