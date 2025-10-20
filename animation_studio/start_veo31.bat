@echo off
echo 🚀 Démarrage Animation Studio avec Veo 3.1 Fast
echo ===============================================
echo.

REM Vérifier si on est dans le bon dossier
if not exist "backend\main.py" (
    echo ❌ Erreur: Vous devez exécuter ce script depuis le dossier animation_studio/
    echo.
    echo Utilisation:
    echo   cd backend/animation_studio
    echo   start_veo31.bat
    pause
    exit /b 1
)

cd backend

echo 📦 Installation des dépendances...
pip install -r requirements.txt > nul 2>&1
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo ✅ Dépendances installées

echo.
echo 🎭 Test du générateur Veo 3.1 Fast...
echo.

REM Exécuter le test
python test_veo31.py

REM Vérifier le résultat du test
if errorlevel 1 (
    echo.
    echo ❌ Test échoué - Vérifiez la configuration des clés API
    echo.
    echo 💡 Configurez RUNWAY_API_KEY dans .env:
    echo    RUNWAY_API_KEY=your-runway-api-key
    echo.
    set /p choice="Voulez-vous continuer malgré tout? (o/n): "
    if /i not "%choice%"=="o" (
        echo ❌ Démarrage annulé
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Démarrage du serveur Animation Studio avec Veo 3.1 Fast...
echo.
echo 🌐 Backend: http://localhost:8080
echo 📚 Documentation API: http://localhost:8080/docs
echo 🎭 Générateur: Veo 3.1 Fast (Runway ML)
echo.

REM Démarrer le serveur
python main.py

pause
