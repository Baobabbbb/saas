@echo off
title SEEDANCE Server - DEMARRAGE AUTOMATIQUE
color 0A

echo.
echo ======================================================
echo   🚀 DEMARRAGE AUTOMATIQUE DU SERVEUR SEEDANCE
echo ======================================================
echo.

REM Aller dans le bon repertoire
cd /d "c:\Users\Admin\Documents\saas\saas"

echo 📁 Repertoire actuel: %CD%
echo.

REM Verification rapide
if not exist "main.py" (
    echo ❌ Fichier main.py non trouve dans %CD%
    echo ❌ Verifiez que vous etes dans le bon repertoire
    pause
    exit /b 1
)

echo ✅ Fichier main.py trouve
echo.

REM Test de Python
echo 🐍 Test de Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python non accessible
    pause
    exit /b 1
)

echo ✅ Python OK
echo.

REM Installation des dependances si necessaire
echo 📦 Verification des dependances...
python -c "import fastapi, uvicorn" 2>nul
if %errorlevel% neq 0 (
    echo ⬇️ Installation de FastAPI et Uvicorn...
    pip install fastapi uvicorn python-dotenv aiohttp openai
    if %errorlevel% neq 0 (
        echo ❌ Echec de l'installation
        pause
        exit /b 1
    )
)

echo ✅ Dependances OK
echo.

REM Verifier le port 8004
echo 🔍 Verification du port 8004...
netstat -an | findstr :8004 > nul
if %errorlevel% equ 0 (
    echo ⚠️ Le port 8004 est deja utilise
    echo ⚠️ Tentative d'arret des processus...
    taskkill /f /im python.exe 2>nul
    timeout /t 2 > nul
)

echo.
echo =========================================
echo   🚀 LANCEMENT DU SERVEUR SEEDANCE
echo =========================================
echo.
echo 🌐 URL: http://localhost:8004
echo 📚 Documentation: http://localhost:8004/docs
echo 💡 Appuyez sur Ctrl+C pour arreter
echo.

REM Lancer le serveur
python -m uvicorn main:app --host 127.0.0.1 --port 8004 --reload

echo.
echo 🛑 Serveur arrete
pause
