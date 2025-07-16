@echo off
echo 🔄 Redémarrage complet du serveur SEEDANCE...
echo =============================================

echo 🛑 Arrêt des anciens processus Python...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak > nul

echo 🔍 Vérification du port 8004...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8004"') do (
    echo 🛑 Arrêt du processus %%a...
    taskkill /f /pid %%a 2>nul
)

echo 📁 Accès au répertoire du serveur...
cd /d "c:\Users\Admin\Documents\saas\saas"

echo 🚀 Démarrage du nouveau serveur...
echo ℹ️ Serveur démarré avec les corrections de cache
echo ℹ️ Appuyez sur Ctrl+C pour arrêter
echo.

python main.py
