@echo off
chcp 65001 >nul
color 0A

echo ========================================
echo 🚀 FRIDAY SEEDANCE - LANCEMENT COMPLET
echo ========================================
echo.

:: Variables
set "BASE_DIR=%~dp0"
set "BACKEND_DIR=%BASE_DIR%"
set "FRONTEND_DIR=%BASE_DIR%..\frontend"

echo 📁 Répertoires:
echo    Base: %BASE_DIR%
echo    Backend: %BACKEND_DIR%
echo    Frontend: %FRONTEND_DIR%
echo.

:: Vérifications rapides
echo 🔍 Vérifications rapides...

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trouvé. Installez Python d'abord.
    pause
    exit /b 1
) else (
    echo    ✅ Python trouvé
)

:: Vérifier Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js non trouvé. Installez Node.js d'abord.
    pause
    exit /b 1
) else (
    echo    ✅ Node.js trouvé
)

:: Vérifier npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm non trouvé. Installez npm d'abord.
    pause
    exit /b 1
) else (
    echo    ✅ npm trouvé
)

:: Vérifier les fichiers
if not exist "%BACKEND_DIR%main.py" (
    echo ❌ Fichier main.py non trouvé dans %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%BACKEND_DIR%.env" (
    echo ❌ Fichier .env non trouvé dans %BACKEND_DIR%
    echo    Créez le fichier .env avec vos clés API
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo ❌ Fichier package.json non trouvé dans %FRONTEND_DIR%
    pause
    exit /b 1
)

echo    ✅ Structure des fichiers OK
echo.

:: Nettoyage des processus existants
echo 🧹 Nettoyage des processus existants...
taskkill /f /im python.exe /t >nul 2>&1
taskkill /f /im node.exe /t >nul 2>&1
timeout /t 2 /nobreak >nul
echo    ✅ Processus nettoyés
echo.

:: Installation des dépendances
echo 📦 Installation des dépendances...
cd /d "%BACKEND_DIR%"

if exist requirements.txt (
    echo    🐍 Dépendances Python...
    python -m pip install -r requirements.txt --quiet --disable-pip-version-check
    echo    ✅ Dépendances Python installées
) else (
    echo    ⚠️ requirements.txt non trouvé
)

cd /d "%FRONTEND_DIR%"
if not exist node_modules (
    echo    📦 Dépendances Node.js...
    npm install --silent
    echo    ✅ Dépendances Node.js installées
) else (
    echo    ✅ Dépendances Node.js déjà installées
)

echo.

:: Démarrage du backend
echo 🖥️ Démarrage du backend...
cd /d "%BACKEND_DIR%"
start "SEEDANCE-Backend" /min cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload"
echo    📍 Backend démarré en arrière-plan
echo    🌐 URL Backend: http://localhost:8004

:: Attendre le backend
echo    ⏳ Attente du backend...
timeout /t 5 /nobreak >nul

:: Démarrage du frontend
echo.
echo 🌐 Démarrage du frontend...
cd /d "%FRONTEND_DIR%"
start "SEEDANCE-Frontend" /min cmd /c "npm run dev"
echo    📍 Frontend démarré en arrière-plan
echo    🌐 URL Frontend: http://localhost:5173

:: Attendre le frontend
echo    ⏳ Attente du frontend...
timeout /t 5 /nobreak >nul

echo.
echo 🎉 LANCEMENT RÉUSSI!
echo ==================
echo.
echo 🌐 URLS D'ACCÈS:
echo    Frontend:     http://localhost:5173
echo    Backend API:  http://localhost:8004
echo    API Docs:     http://localhost:8004/docs
echo    Diagnostic:   http://localhost:8004/diagnostic
echo.
echo 💡 CONSEILS:
echo    • L'interface sera accessible dans quelques secondes
echo    • Les services tournent en arrière-plan
echo    • Fermez les fenêtres noires pour arrêter les services
echo.

:: Ouverture automatique du navigateur
echo 🌐 Ouverture du navigateur dans 5 secondes...
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo ✅ Terminé! Profitez de SEEDANCE!
echo.
pause
