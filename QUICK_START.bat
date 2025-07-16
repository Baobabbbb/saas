@echo off
title SEEDANCE - Lancement Express
color 0E

echo.
echo ========================================
echo   🚀 SEEDANCE - LANCEMENT EXPRESS
echo ========================================
echo.

REM Démarrage rapide sans vérifications poussées
echo 🎬 Démarrage des services SEEDANCE...
echo.

REM Backend
echo 🔥 Lancement du backend...
start "SEEDANCE Backend" cmd /k "cd /d %~dp0saas && python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload"

REM Attendre un peu
timeout /t 3 /nobreak >nul

REM Frontend
echo 🎨 Lancement du frontend...
start "SEEDANCE Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ✅ Services lancés!
echo.
echo 🌐 Backend: http://localhost:8004
echo 🎨 Frontend: http://localhost:5173
echo.

REM Ouvrir le navigateur après 10 secondes
timeout /t 10 /nobreak >nul
start http://localhost:5173

echo 🌐 Navigateur ouvert sur l'interface principale
echo.
echo 💡 Fermez cette fenêtre ou les fenêtres des services pour arrêter
pause
