@echo off
echo 🚀 Demarrage du serveur SEEDANCE...
echo 📁 Repertoire de travail: %CD%
echo 🌐 URL: http://localhost:8004
echo 🎬 Endpoint: http://localhost:8004/api/seedance/generate
echo.
echo ===============================================
echo Verifiez que votre frontend pointe vers http://localhost:8004
echo ===============================================
echo.

cd /d "c:\Users\Admin\Documents\saas\saas"
echo 📂 Repertoire courant: %CD%

REM Tester si Python est accessible
python --version
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas accessible
    pause
    exit /b 1
)

REM Tester les imports essentiels
python -c "import fastapi, uvicorn; print('✅ FastAPI et Uvicorn sont disponibles')"
if %errorlevel% neq 0 (
    echo ❌ FastAPI ou Uvicorn manquant
    echo Installation...
    pip install fastapi uvicorn python-dotenv
)

echo.
echo 🚀 Lancement d'Uvicorn...
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload --log-level info

echo.
echo ❌ Le serveur s'est arrete
pause
