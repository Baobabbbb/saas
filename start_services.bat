@echo off
:: 🎵 Script de démarrage rapide - Comptines Musicales (Windows)
:: Ce script démarre automatiquement le backend et le frontend

title Comptines Musicales - Services
echo 🚀 Démarrage des services - Comptines Musicales
echo ================================================

:: Configuration
set BACKEND_DIR=saas
set FRONTEND_DIR=frontend
set BACKEND_PORT=8000
set FRONTEND_PORT=5174

:: Vérification des prérequis
echo 🔍 Vérification des prérequis...

:: Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

:: Vérifier Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

:: Vérifier npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

echo ✅ Prérequis validés

:: Démarrage du backend
echo.
echo 🔧 Démarrage du backend...
cd %BACKEND_DIR%

:: Vérifier le fichier requirements
if not exist "requirements_new.txt" (
    echo ❌ Fichier requirements_new.txt non trouvé
    pause
    exit /b 1
)

:: Démarrer le backend en arrière-plan
echo 🚀 Lancement du serveur backend sur le port %BACKEND_PORT%...
start "Backend Server" cmd /c "python main_new.py"

:: Attendre que le backend soit prêt
echo ⏳ Attente du démarrage du backend...
timeout /t 10 /nobreak >nul

:: Démarrage du frontend
echo.
echo 🎨 Démarrage du frontend...
cd ..\%FRONTEND_DIR%

:: Vérifier package.json
if not exist "package.json" (
    echo ❌ Fichier package.json non trouvé
    pause
    exit /b 1
)

:: Démarrer le frontend
echo 🚀 Lancement du serveur frontend...
start "Frontend Server" cmd /c "npm run dev"

:: Attendre que le frontend soit prêt
echo ⏳ Attente du démarrage du frontend...
timeout /t 15 /nobreak >nul

:: Services prêts
echo.
echo 🎉 SERVICES DÉMARRÉS AVEC SUCCÈS!
echo ==================================
echo 🔧 Backend:    http://localhost:%BACKEND_PORT%
echo 📚 API Docs:   http://localhost:%BACKEND_PORT%/docs
echo 🎨 Frontend:   http://localhost:%FRONTEND_PORT%
echo.
echo 🎵 La fonctionnalité Comptines Musicales est prête!
echo.
echo 💡 Pour tester:
echo    1. Ouvrez http://localhost:%FRONTEND_PORT%
echo    2. Sélectionnez 'Comptine musicale'
echo    3. Choisissez un style et faites votre demande
echo.
echo 🌐 Ouverture automatique du navigateur...

:: Ouvrir automatiquement le frontend dans le navigateur
start http://localhost:%FRONTEND_PORT%

echo.
echo 🛑 Fermez cette fenêtre pour arrêter les services
echo    (Les serveurs continueront à fonctionner en arrière-plan)
pause
