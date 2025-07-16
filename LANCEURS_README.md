# 🎬 SEEDANCE - Lanceurs Complets

Ce répertoire contient plusieurs scripts pour lancer automatiquement le backend et le frontend de SEEDANCE.

## 📋 Scripts Disponibles

### 1. `launch_complete.bat` (Windows)
Script batch simple pour Windows.

**Utilisation :**
```cmd
launch_complete.bat
```

**Fonctionnalités :**
- ✅ Vérification automatique des prérequis
- 📦 Installation automatique des dépendances
- 🚀 Lancement du backend (port 8004)
- 🎨 Lancement du frontend (port 5173)
- 🌐 Ouverture automatique du navigateur
- 🪟 Fenêtres séparées pour backend et frontend

### 2. `launch_complete.ps1` (PowerShell)
Script PowerShell avancé avec options.

**Utilisation :**
```powershell
# Lancement standard
.\launch_complete.ps1

# Avec options
.\launch_complete.ps1 -SkipDependencies -NoOpenBrowser -BackendPort 8080 -FrontendPort 3000
```

**Options :**
- `-SkipDependencies` : Ignore l'installation des dépendances
- `-NoOpenBrowser` : N'ouvre pas le navigateur automatiquement
- `-BackendPort <port>` : Port personnalisé pour le backend (défaut: 8004)
- `-FrontendPort <port>` : Port personnalisé pour le frontend (défaut: 5173)

### 3. `launch_complete.sh` (Linux/macOS)
Script bash pour systèmes Unix.

**Utilisation :**
```bash
# Rendre le script exécutable
chmod +x launch_complete.sh

# Lancement standard
./launch_complete.sh

# Avec options
./launch_complete.sh --skip-deps --no-browser --backend-port 8080 --frontend-port 3000
```

**Options :**
- `--skip-deps` : Ignore l'installation des dépendances
- `--no-browser` : N'ouvre pas le navigateur automatiquement
- `--backend-port <port>` : Port personnalisé pour le backend
- `--frontend-port <port>` : Port personnalisé pour le frontend
- `--help` : Affiche l'aide

### 4. `launch_complete.py` (Python)
Script Python multiplateforme avec surveillance avancée.

**Utilisation :**
```bash
python launch_complete.py
```

**Fonctionnalités :**
- 🔍 Vérification avancée des ports
- 🔫 Arrêt automatique des processus conflictuels
- 👀 Surveillance continue des processus
- 🛡️ Gestion robuste des erreurs
- 🧹 Nettoyage automatique à l'arrêt

## 🔧 Prérequis

### Backend (Python)
- Python 3.8+
- pip
- Les dépendances dans `saas/requirements.txt`

### Frontend (Node.js)
- Node.js 16+
- npm
- Les dépendances dans `frontend/package.json`

## 🌐 URLs par Défaut

Après le lancement, les services seront disponibles sur :

- **Backend API :** http://localhost:8004
- **Documentation API :** http://localhost:8004/docs
- **Frontend Interface :** http://localhost:5173

## 🚀 Démarrage Rapide

### Windows
1. Double-cliquer sur `launch_complete.bat`
2. Attendre que les services démarrent
3. Le navigateur s'ouvrira automatiquement

### PowerShell
```powershell
.\launch_complete.ps1
```

### Linux/macOS
```bash
chmod +x launch_complete.sh
./launch_complete.sh
```

### Python (multiplateforme)
```bash
python launch_complete.py
```

## 🛑 Arrêt des Services

### Méthode 1 : Ctrl+C
Appuyez sur `Ctrl+C` dans le terminal pour arrêter proprement tous les services.

### Méthode 2 : Fermeture des fenêtres
Pour les scripts batch, fermez simplement les fenêtres du backend et frontend.

### Méthode 3 : Arrêt manuel des ports
```bash
# Linux/macOS
lsof -ti:8004 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8004).OwningProcess | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process -Force
```

## 🔍 Dépannage

### Port déjà utilisé
Les scripts détectent automatiquement les ports occupés et les libèrent.

### Dépendances manquantes
Les scripts installent automatiquement les dépendances. Pour ignorer :
- Batch : Modifier le script
- PowerShell : `-SkipDependencies`
- Bash : `--skip-deps`

### Python non trouvé
Vérifiez que Python est installé et dans le PATH :
```bash
python --version
# ou
python3 --version
```

### Node.js non trouvé
Vérifiez que Node.js est installé :
```bash
node --version
npm --version
```

### Erreurs de permissions (Linux/macOS)
```bash
chmod +x launch_complete.sh
sudo ./launch_complete.sh  # Si nécessaire
```

## 📝 Logs

### Localisation des logs
- **Windows Batch :** Affiché dans les fenêtres de terminal
- **PowerShell :** Sortie standard
- **Bash :** `/tmp/seedance_backend.log` et `/tmp/seedance_frontend.log`
- **Python :** Sortie standard avec code couleur

### Visualiser les logs en temps réel
```bash
# Backend
tail -f /tmp/seedance_backend.log

# Frontend
tail -f /tmp/seedance_frontend.log
```

## 🎯 Recommandations

### Pour le développement
Utilisez le script Python ou PowerShell pour une surveillance avancée.

### Pour la production
Configurez des services système appropriés plutôt que ces scripts de développement.

### Pour les démonstrations
Le script batch Windows est le plus simple pour les présentations.

## 🆘 Support

En cas de problème :

1. Vérifiez les prérequis
2. Consultez les logs
3. Vérifiez que les ports ne sont pas utilisés
4. Redémarrez avec les dépendances fraîches
5. Contactez l'équipe de développement

## 📄 Licence

Ces scripts font partie du projet SEEDANCE et suivent la même licence.
