@echo off
echo 🚀 Démarrage HERBBIE avec Sora 2 Zseedance
echo ========================================
echo.

REM Vérifier si on est dans le bon dossier
if not exist "main.py" (
    echo ❌ Erreur: Vous devez exécuter ce script depuis le dossier backend/saas/
    echo.
    echo Utilisation:
    echo   cd backend/saas
    echo   start_sora2.bat
    pause
    exit /b 1
)

echo 📦 Installation des dépendances...
pip install -r requirements.txt > nul 2>&1
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo ✅ Dépendances installées

echo.
echo 🎭 Test du générateur Sora 2 Zseedance...
echo.

REM Exécuter le test
python test_sora2_zseedance.py

REM Vérifier le résultat du test
if errorlevel 1 (
    echo.
    echo ❌ Test échoué - Vérifiez la configuration des clés API
    echo.
    echo 💡 Configurez au moins une de ces variables dans .env:
    echo    OPENAI_API_KEY=sk-your-key
    echo    RUNWAY_API_KEY=your-key
    echo    PIKA_API_KEY=your-key
    echo.
    set /p choice="Voulez-vous continuer malgré tout? (o/n): "
    if /i not "%choice%"=="o" (
        echo ❌ Démarrage annulé
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Démarrage du serveur HERBBIE avec Sora 2...
echo.
echo 🌐 Frontend: http://localhost:8006
echo 📚 Documentation API: http://localhost:8006/docs
echo 🎭 Générateur: Sora 2 Zseedance (workflow n8n)
echo.

REM Démarrer le serveur
python main.py

pause
