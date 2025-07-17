# SEEDANCE - Lancement sécurisé PowerShell
# Version Windows avec vérifications complètes

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   🚀 SEEDANCE - LANCEMENT SÉCURISÉ" -ForegroundColor Yellow  
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Variables
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SaasDir = Join-Path $BaseDir "saas"
$FrontendDir = Join-Path $BaseDir "frontend"

# Déterminer la commande Python
$PythonCmd = "python"
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
}

Write-Host "🔍 Vérifications préalables..." -ForegroundColor Cyan

# Vérification 1: Fichier .env
$EnvFile = Join-Path $SaasDir ".env"
if (-Not (Test-Path $EnvFile)) {
    Write-Host "❌ Fichier .env manquant dans $SaasDir" -ForegroundColor Red
    Write-Host "   Créez le fichier .env avec vos clés API" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

# Vérification 2: Clés API essentielles
Write-Host "🔑 Vérification des clés API..." -ForegroundColor Cyan

$EnvContent = Get-Content $EnvFile | Where-Object { $_ -match "^[^#].*=" }
$EnvVars = @{}
foreach ($line in $EnvContent) {
    $parts = $line -split "=", 2
    if ($parts.Length -eq 2) {
        $EnvVars[$parts[0]] = $parts[1]
    }
}

if (-Not $EnvVars["OPENAI_API_KEY"] -or $EnvVars["OPENAI_API_KEY"] -like "sk-votre*") {
    Write-Host "❌ Clé OpenAI manquante ou invalide" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

if (-Not $EnvVars["WAVESPEED_API_KEY"] -or $EnvVars["WAVESPEED_API_KEY"] -like "votre_*") {
    Write-Host "❌ Clé Wavespeed manquante ou invalide" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

if (-Not $EnvVars["FAL_API_KEY"] -or $EnvVars["FAL_API_KEY"] -like "votre_*") {
    Write-Host "❌ Clé Fal AI manquante ou invalide" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host "✅ Toutes les clés API sont configurées" -ForegroundColor Green

# Vérification 3: Dependencies Python
Write-Host "📦 Vérification des dépendances Python..." -ForegroundColor Cyan
Set-Location $SaasDir

$TestImport = & $PythonCmd -c "import fastapi, uvicorn, aiohttp" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Installation des dépendances Python..." -ForegroundColor Yellow
    & $PythonCmd -m pip install -r requirements.txt
}

# Vérification 4: Node.js pour le frontend  
Write-Host "🎨 Vérification du frontend..." -ForegroundColor Cyan
Set-Location $FrontendDir

if (-Not (Test-Path "node_modules")) {
    Write-Host "⚠️ Installation des dépendances Node.js..." -ForegroundColor Yellow
    npm install
}

Write-Host "✅ Toutes les vérifications passées!" -ForegroundColor Green
Write-Host ""

# Lancement du backend
Write-Host "🔥 Lancement du backend SEEDANCE..." -ForegroundColor Green
Set-Location $SaasDir

$BackendCmd = "$PythonCmd -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Write-Host '🚀 Démarrage du backend SEEDANCE...' -ForegroundColor Green;
    $BackendCmd;
    Write-Host 'Backend arrêté. Appuyez sur Entrée pour fermer.' -ForegroundColor Yellow;
    Read-Host
" -WindowStyle Normal

# Attendre que le backend soit prêt
Write-Host "⏳ Attente du démarrage backend..." -ForegroundColor Cyan
Start-Sleep -Seconds 8

# Test de connectivité
Write-Host "🔍 Test de connectivité backend..." -ForegroundColor Cyan
try {
    $Response = Invoke-WebRequest -Uri "http://localhost:8004/diagnostic" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend non accessible" -ForegroundColor Red
    Write-Host "   Attendez quelques secondes et vérifiez la fenêtre backend" -ForegroundColor Yellow
}

# Lancement du frontend
Write-Host "🎨 Lancement du frontend..." -ForegroundColor Magenta
Set-Location $FrontendDir

Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Write-Host '🎨 Démarrage du frontend SEEDANCE...' -ForegroundColor Magenta;
    npm run dev;
    Write-Host 'Frontend arrêté. Appuyez sur Entrée pour fermer.' -ForegroundColor Yellow;
    Read-Host
" -WindowStyle Normal

Write-Host ""
Write-Host "🎉 Services SEEDANCE démarrés avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Backend: http://localhost:8004" -ForegroundColor Cyan
Write-Host "🎨 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

# Ouverture automatique du navigateur
Write-Host "⏳ Ouverture du navigateur dans 10 secondes..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    Start-Process "http://localhost:5173"
    Write-Host "🌐 Navigateur ouvert sur l'interface SEEDANCE" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'ouvrir le navigateur automatiquement" -ForegroundColor Yellow
    Write-Host "Ouvrez manuellement: http://localhost:5173" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "💡 Conseils d'utilisation:" -ForegroundColor Yellow
Write-Host "   • Laissez les fenêtres backend/frontend ouvertes" -ForegroundColor Yellow
Write-Host "   • En cas d'erreur, vérifiez les logs dans les fenêtres" -ForegroundColor Yellow
Write-Host "   • Utilisez le diagnostic dans l'interface web" -ForegroundColor Yellow
Write-Host "   • Consultez TROUBLESHOOTING.md en cas de problème" -ForegroundColor Yellow
Write-Host ""

Write-Host "Services lancés dans des fenêtres séparées" -ForegroundColor Green
Write-Host "Fermez les fenêtres PowerShell pour arrêter les services" -ForegroundColor Yellow

Read-Host "Appuyez sur Entrée pour fermer cette fenêtre"
