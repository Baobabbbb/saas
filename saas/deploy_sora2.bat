@echo off
echo 🎭 Déploiement HERBBIE avec Sora 2
echo =================================
echo.

REM Vérifier si on est dans le bon dossier
if not exist "main.py" (
    echo ❌ Erreur: Vous devez exécuter ce script depuis le dossier backend/saas/
    echo.
    echo Utilisation:
    echo   cd backend/saas
    echo   deploy_sora2.bat
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
echo 🔧 Vérification de la configuration Sora 2...
echo.

REM Vérifier les variables d'environnement Sora 2
echo Vérification des plateformes Sora 2 disponibles:
echo.

set "sora_available=false"

REM Vérifier OpenAI
if defined OPENAI_API_KEY (
    if not "%OPENAI_API_KEY%"=="sk-votre" (
        echo ✅ OpenAI Sora: Configuré
        set "sora_available=true"
    ) else (
        echo ⚠️ OpenAI Sora: Clé par défaut (non configurée)
    )
) else (
    echo ⚠️ OpenAI Sora: Non configuré
)

REM Vérifier Runway ML
if defined RUNWAY_API_KEY (
    if not "%RUNWAY_API_KEY%"=="your-runway-key" (
        echo ✅ Runway ML: Configuré
        set "sora_available=true"
    ) else (
        echo ⚠️ Runway ML: Clé par défaut (non configurée)
    )
) else (
    echo ⚠️ Runway ML: Non configuré
)

REM Vérifier Pika Labs
if defined PIKA_API_KEY (
    if not "%PIKA_API_KEY%"=="your-pika-key" (
        echo ✅ Pika Labs: Configuré
        set "sora_available=true"
    ) else (
        echo ⚠️ Pika Labs: Clé par défaut (non configurée)
    )
) else (
    echo ⚠️ Pika Labs: Non configuré
)

REM Vérifier Luma AI
if defined LUMA_API_KEY (
    if not "%LUMA_API_KEY%"=="your-luma-key" (
        echo ✅ Luma AI: Configuré
        set "sora_available=true"
    ) else (
        echo ⚠️ Luma AI: Clé par défaut (non configurée)
    )
) else (
    echo ⚠️ Luma AI: Non configuré
)

if "%sora_available%"=="false" (
    echo.
    echo ⚠️ ATTENTION: Aucune plateforme Sora 2 n'est configurée
    echo.
    echo 💡 Configurez au moins une plateforme dans votre fichier .env:
    echo    OPENAI_API_KEY=sk-votre-cle-reelle
    echo    RUNWAY_API_KEY=your-runway-key-reel
    echo    PIKA_API_KEY=your-pika-key-reel
    echo    LUMA_API_KEY=your-luma-key-reel
    echo.
    echo 📖 Consultez README_SORA2_INTEGRATION.md pour plus d'informations
    echo.
    set /p choice="Voulez-vous continuer malgré tout? (o/n): "
    if /i not "%choice%"=="o" (
        echo ❌ Déploiement annulé
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Démarrage du serveur HERBBIE avec Sora 2...
echo.
echo 🌐 Frontend: http://localhost:8006
echo 📚 Documentation API: http://localhost:8006/docs
echo 🎭 Mode Sora 2: Activé
echo.

REM Démarrer le serveur
python main.py

pause
