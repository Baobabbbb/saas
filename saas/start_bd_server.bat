@echo off
echo 🎨 Démarrage FRIDAY BD avec IA
echo ==============================

echo 📋 Vérification configuration...
cd /d "%~dp0"

python test_config.py

echo.
echo 🚀 Démarrage du serveur...
echo ℹ️ Appuyez sur Ctrl+C pour arrêter

python main.py

pause
