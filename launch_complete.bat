@echo off
title SEEDANCE - Lanceur Complet
color 0A
chcp 65001 >nul

echo.
echo ================================================================
echo   🎬 SEEDANCE - LANCEUR COMPLET BACKEND + FRONTEND
echo ================================================================
echo.

REM Définir les répertoires
set "BASE_DIR=%~dp0"
set "SAAS_DIR=%BASE_DIR%saas"
set "FRONTEND_DIR=%BASE_DIR%frontend"

echo 📁 Répertoire de base: %BASE_DIR%
echo 📁 Backend: %SAAS_DIR%
echo 📁 Frontend: %FRONTEND_DIR%
echo.

REM Vérifications préliminaires
echo 🔍 Vérifications préliminaires...

if not exist "%SAAS_DIR%" (
    echo ❌ Répertoire backend non trouvé: %SAAS_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ❌ Répertoire frontend non trouvé: %FRONTEND_DIR%
    pause
    exit /b 1
)

if not exist "%SAAS_DIR%\main.py" (
    echo ❌ Fichier main.py non trouvé dans %SAAS_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo ❌ Fichier package.json non trouvé dans %FRONTEND_DIR%
    pause
    exit /b 1
)

echo ✅ Tous les fichiers nécessaires sont présents
echo.

REM Installation des dépendances
echo 📦 Vérification des dépendances...
echo.

REM Backend Python
if exist "%SAAS_DIR%\requirements.txt" (
    echo 🐍 Installation des dépendances Python...
    cd /d "%SAAS_DIR%"
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ⚠️ Erreur lors de l'installation des dépendances Python
    ) else (
        echo ✅ Dépendances Python installées
    )
    echo.
)

REM Frontend Node.js
echo 📦 Installation des dépendances Node.js...
cd /d "%FRONTEND_DIR%"
call npm install
if errorlevel 1 (
    echo ⚠️ Erreur lors de l'installation des dépendances Node.js
) else (
    echo ✅ Dépendances Node.js installées
)
echo.

REM Démarrage des services
echo ================================================================
echo   🚀 DÉMARRAGE DES SERVICES
echo ================================================================
echo.

REM Créer les fichiers de démarrage temporaires
set "BACKEND_BAT=%TEMP%\seedance_backend.bat"
set "FRONTEND_BAT=%TEMP%\seedance_frontend.bat"

REM Script backend
echo @echo off > "%BACKEND_BAT%"
echo title SEEDANCE Backend ^(Port 8004^) >> "%BACKEND_BAT%"
echo color 0B >> "%BACKEND_BAT%"
echo cd /d "%SAAS_DIR%" >> "%BACKEND_BAT%"
echo echo 🚀 Démarrage du backend SEEDANCE... >> "%BACKEND_BAT%"
echo echo 🌐 API: http://localhost:8004 >> "%BACKEND_BAT%"
echo echo 📚 Docs: http://localhost:8004/docs >> "%BACKEND_BAT%"
echo echo. >> "%BACKEND_BAT%"
echo python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload >> "%BACKEND_BAT%"
echo pause >> "%BACKEND_BAT%"

REM Script frontend
echo @echo off > "%FRONTEND_BAT%"
echo title SEEDANCE Frontend ^(Port 5173^) >> "%FRONTEND_BAT%"
echo color 0D >> "%FRONTEND_BAT%"
echo cd /d "%FRONTEND_DIR%" >> "%FRONTEND_BAT%"
echo echo 🎨 Démarrage du frontend SEEDANCE... >> "%FRONTEND_BAT%"
echo echo 🌐 Interface: http://localhost:5173 >> "%FRONTEND_BAT%"
echo echo. >> "%FRONTEND_BAT%"
echo npm run dev >> "%FRONTEND_BAT%"
echo pause >> "%FRONTEND_BAT%"

REM Lancement en parallèle
echo 🚀 Lancement du backend...
start "SEEDANCE Backend" "%BACKEND_BAT%"

echo ⏳ Attente 5 secondes avant le frontend...
timeout /t 5 /nobreak >nul

echo 🎨 Lancement du frontend...
start "SEEDANCE Frontend" "%FRONTEND_BAT%"

echo.
echo ================================================================
echo   🎉 SEEDANCE LANCÉ AVEC SUCCÈS!
echo ================================================================
echo.
echo 🌐 Backend API: http://localhost:8004
echo 📚 Documentation: http://localhost:8004/docs
echo 🎨 Frontend Interface: http://localhost:5173
echo.
echo 💡 Deux nouvelles fenêtres se sont ouvertes pour:
echo    - Backend (fenêtre bleue)
echo    - Frontend (fenêtre violette)
echo.
echo 🛑 Pour arrêter: Fermez les fenêtres ou appuyez Ctrl+C dans chacune
echo.
echo ================================================================

REM Attendre quelques secondes puis ouvrir le navigateur
echo ⏳ Ouverture automatique du navigateur dans 10 secondes...
timeout /t 10 /nobreak >nul

REM Ouvrir les URLs dans le navigateur
start http://localhost:5173
start http://localhost:8004/docs

echo.
echo 🌐 Navigateur ouvert sur l'interface principale
echo 📚 Documentation API également ouverte
echo.
echo ✨ SEEDANCE est maintenant prêt à l'emploi!
echo.

pause

REM Nettoyage des fichiers temporaires
del "%BACKEND_BAT%" 2>nul
del "%FRONTEND_BAT%" 2>nul
