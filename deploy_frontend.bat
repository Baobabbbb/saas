@echo off
echo ========================================
echo   DEPLOIEMENT FRONTEND VERS RAILWAY
echo ========================================
echo.

REM Vérifier si on est dans le bon dossier
if not exist "frontend\package.json" (
    echo ERREUR: frontend/package.json introuvable
    echo Lancez ce script depuis backend/
    pause
    exit /b 1
)

echo [1/4] Build du frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ERREUR: Build du frontend echoue
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [2/4] Copie vers saas/static/...
xcopy /E /I /Y frontend\dist saas\static
if errorlevel 1 (
    echo ERREUR: Copie vers static/ echouee
    pause
    exit /b 1
)

echo.
echo [3/4] Commit des changements...
git add frontend/dist saas/static
git status

echo.
set /p COMMIT_MSG="Message de commit (ou Enter pour message par defaut): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=feat: Update frontend build and deploy to Railway

git commit -m "%COMMIT_MSG%"

echo.
echo [4/4] Push vers Railway...
set /p DO_PUSH="Pusher vers Railway maintenant? (o/n): "
if /i "%DO_PUSH%"=="o" (
    git push origin main
    echo.
    echo ========================================
    echo   DEPLOIEMENT TERMINE !
    echo ========================================
    echo.
    echo Le frontend sera deploye sur Railway dans 2-3 minutes
    echo URL: https://herbbie.com
) else (
    echo.
    echo Push annule. Executez manuellement: git push origin main
)

echo.
pause

