# 🛠️ GUIDE DE RÉSOLUTION DES PROBLÈMES SEEDANCE

## ❌ Problèmes Courants et Solutions

### 1. "Failed to fetch" / Erreur de génération

**Symptômes:**
- Message "Failed to fetch" dans l'interface
- Erreur "Vérifiez que les clés API sont configurées"
- Console du navigateur montre des erreurs 500/400

**Solutions:**
1. **Vérifier le backend:**
   ```bash
   # Dans un terminal
   cd saas/saas
   python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
   ```

2. **Tester la connectivité:**
   ```bash
   # Depuis la racine du projet
   python test_connectivity.py
   ```

3. **Vérifier les clés API:**
   - Ouvrir `saas/saas/.env`
   - S'assurer que toutes les clés sont remplies
   - Pas de texte comme "votre_clé_ici"

### 2. Erreurs de parsing JSON

**Symptômes:**
- "Unterminated string" dans les logs
- "JSONDecodeError" 
- Génération qui s'arrête à l'étape 1 ou 2

**Solutions:**
✅ **CORRIGÉ** dans la dernière version:
- Parsing JSON robuste avec nettoyage
- Fallback automatique si JSON invalide
- Gestion des caractères de contrôle

### 3. Timeouts audio/vidéo

**Symptômes:**
- "Timeout audio après 45s"
- Génération qui prend très longtemps
- Clips générés mais pas d'audio

**Solutions:**
1. **Normal:** Les services IA peuvent être lents
2. **Réessayer:** La génération peut réussir au 2ème essai
3. **Fallback:** Le système utilise des clips sans audio si nécessaire

### 4. Erreurs de clés API

**Symptômes:**
- "Clé OpenAI manquante ou invalide"
- "Clé Wavespeed manquante ou invalide"
- Status 401/403 dans les logs

**Solutions:**
1. **Vérifier le fichier .env:**
   ```bash
   cat saas/saas/.env | grep -E "OPENAI|WAVESPEED|FAL"
   ```

2. **Clés valides requises:**
   - `OPENAI_API_KEY`: Commence par `sk-proj-` ou `sk-`
   - `WAVESPEED_API_KEY`: Chaîne hexadécimale longue
   - `FAL_API_KEY`: Format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:xxxxxx`

### 5. Problèmes de lancement

**Symptômes:**
- Script se ferme immédiatement
- "Permission denied"
- "Command not found"

**Solutions:**
1. **Permissions Unix:**
   ```bash
   chmod +x QUICK_START.sh
   chmod +x QUICK_START_SECURE.sh
   ```

2. **Script sécurisé:**
   ```bash
   # Utiliser la version avec vérifications
   chmod +x QUICK_START_SECURE.sh && ./QUICK_START_SECURE.sh
   ```

3. **Lancement manuel:**
   ```bash
   # Backend
   cd saas/saas && python -m uvicorn main:app --host 0.0.0.0 --port 8004
   
   # Frontend (nouveau terminal)
   cd frontend && npm run dev
   ```

## 🔧 Outils de Diagnostic

### 1. Test complet du service
```bash
python test_seedance_fix.py
```

### 2. Test de connectivité API
```bash
python test_connectivity.py
```

### 3. Vérification des clés API
```bash
cd saas/saas && python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OPENAI:', 'OK' if os.getenv('OPENAI_API_KEY') and not os.getenv('OPENAI_API_KEY').startswith('sk-votre') else 'MANQUANTE')
print('WAVESPEED:', 'OK' if os.getenv('WAVESPEED_API_KEY') and not os.getenv('WAVESPEED_API_KEY').startswith('votre_') else 'MANQUANTE')
print('FAL:', 'OK' if os.getenv('FAL_API_KEY') and not os.getenv('FAL_API_KEY').startswith('votre_') else 'MANQUANTE')
"
```

### 4. Diagnostic web
Aller sur: http://localhost:8004/diagnostic

## 📋 Checklist de Démarrage

- [ ] Fichier `.env` existe dans `saas/saas/`
- [ ] Toutes les clés API sont remplies et valides
- [ ] Dependencies Python installées (`pip install -r requirements.txt`)
- [ ] Dependencies Node.js installées (`npm install` dans frontend/)
- [ ] Ports 8004 et 5173 libres
- [ ] Backend démarre sans erreur
- [ ] Test de connectivité réussi
- [ ] Frontend accessible sur http://localhost:5173

## 🚨 En Cas d'Échec

1. **Redémarrer proprement:**
   ```bash
   # Tuer tous les processus
   pkill -f "uvicorn\|npm.*dev"
   
   # Attendre 5 secondes
   sleep 5
   
   # Relancer avec le script sécurisé
   ./QUICK_START_SECURE.sh
   ```

2. **Logs détaillés:**
   ```bash
   # Backend avec debug
   cd saas/saas
   python -m uvicorn main:app --host 0.0.0.0 --port 8004 --log-level debug
   
   # Frontend avec debug
   cd frontend
   npm run dev -- --debug
   ```

3. **Reset cache:**
   ```bash
   rm -rf cache/seedance/*
   rm -rf saas/cache/*
   ```

## 📞 Support

Si le problème persiste:
1. Copier les logs d'erreur complets
2. Noter les étapes exactes qui causent l'erreur
3. Vérifier les versions (Python, Node.js, npm)
4. Tester avec le script `test_connectivity.py`

---

**Dernière mise à jour:** Version avec corrections JSON et timeouts optimisés
