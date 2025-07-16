@echo off
title Serveur SEEDANCE
color 0A

echo.
echo =========================================
echo   🚀 DEMARRAGE SERVEUR SEEDANCE
echo =========================================
echo.

cd /d "c:\Users\Admin\Documents\saas\saas"
echo 📁 Repertoire: %CD%

echo 🔍 Verification de Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python non trouve
    pause
    exit /b 1
)

echo 🔍 Test d'import FastAPI...
python -c "import fastapi; print('✅ FastAPI OK')"
if %errorlevel% neq 0 (
    echo ❌ FastAPI manquant
    echo 📦 Installation...
    pip install fastapi uvicorn
)

echo.
echo 🚀 Lancement du serveur sur http://localhost:8004
echo 💡 Appuyez sur Ctrl+C pour arreter
echo.

python -m uvicorn main:app --host 127.0.0.1 --port 8004 --reload

echo.
echo 🛑 Serveur arrete
pause
