# LANCEMENT COMPLET FRIDAY SEEDANCE - VERSION FONCTIONNELLE POWERSHELL
# Ce script lance le backend sur 8004 et le frontend sur 5173

Write-Host "🚀 FRIDAY SEEDANCE - LANCEMENT COMPLET" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Variables globales
$BackendProcess = $null
$FrontendProcess = $null
$BaseDir = Get-Location
$BackendDir = Join-Path $BaseDir "saas"
$FrontendDir = Join-Path $BaseDir "frontend"

# Fonction de nettoyage
function Cleanup {
    Write-Host ""
    Write-Host "🛑 Arrêt des services..." -ForegroundColor Red
    
    if ($BackendProcess -and !$BackendProcess.HasExited) {
        try {
            $BackendProcess.Kill()
            Write-Host "   ✅ Backend arrêté" -ForegroundColor Green
        } catch {
            Write-Host "   ⚠️ Erreur arrêt backend" -ForegroundColor Yellow
        }
    }
    
    if ($FrontendProcess -and !$FrontendProcess.HasExited) {
        try {
            $FrontendProcess.Kill()
            Write-Host "   ✅ Frontend arrêté" -ForegroundColor Green
        } catch {
            Write-Host "   ⚠️ Erreur arrêt frontend" -ForegroundColor Yellow
        }
    }
    
    # Nettoyer les ports
    try {
        Get-Process -Id (Get-NetTCPConnection -LocalPort 8004 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Get-Process -Id (Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    } catch {
        # Ignorer les erreurs de nettoyage
    }
    
    exit 0
}

# Capturer Ctrl+C
try {
    Write-Host "📁 Répertoires:" -ForegroundColor Cyan
    Write-Host "   Base: $BaseDir" -ForegroundColor Blue
    Write-Host "   Backend: $BackendDir" -ForegroundColor Blue
    Write-Host "   Frontend: $FrontendDir" -ForegroundColor Blue

    # 1. VÉRIFICATIONS RAPIDES
    Write-Host ""
    Write-Host "🔍 Vérifications rapides..." -ForegroundColor Cyan

    # Vérifier Python
    try {
        $pythonVersion = python --version 2>$null
        Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python non trouvé. Installez Python d'abord." -ForegroundColor Red
        exit 1
    }

    # Vérifier Node.js
    try {
        $nodeVersion = node --version 2>$null
        Write-Host "   ✅ Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Node.js non trouvé. Installez Node.js d'abord." -ForegroundColor Red
        exit 1
    }

    # Vérifier npm
    try {
        $npmVersion = npm --version 2>$null
        Write-Host "   ✅ npm: $npmVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ npm non trouvé. Installez npm d'abord." -ForegroundColor Red
        exit 1
    }

    # Vérifier les répertoires et fichiers
    if (!(Test-Path $BackendDir)) {
        Write-Host "❌ Répertoire backend '$BackendDir' non trouvé" -ForegroundColor Red
        exit 1
    }

    if (!(Test-Path $FrontendDir)) {
        Write-Host "❌ Répertoire frontend '$FrontendDir' non trouvé" -ForegroundColor Red
        exit 1
    }

    if (!(Test-Path (Join-Path $BackendDir ".env"))) {
        Write-Host "❌ Fichier .env non trouvé dans $BackendDir" -ForegroundColor Red
        Write-Host "   Créez le fichier $BackendDir\.env avec vos clés API" -ForegroundColor Yellow
        exit 1
    }

    if (!(Test-Path (Join-Path $BackendDir "main.py"))) {
        Write-Host "❌ Fichier main.py non trouvé dans $BackendDir" -ForegroundColor Red
        exit 1
    }

    if (!(Test-Path (Join-Path $FrontendDir "package.json"))) {
        Write-Host "❌ Fichier package.json non trouvé dans $FrontendDir" -ForegroundColor Red
        exit 1
    }

    Write-Host "   ✅ Structure des fichiers OK" -ForegroundColor Green

    # 2. NETTOYAGE DES PROCESSUS EXISTANTS
    Write-Host ""
    Write-Host "🧹 Nettoyage des processus existants..." -ForegroundColor Cyan

    try {
        # Tuer les processus sur les ports 8004 et 5173
        Get-Process -Id (Get-NetTCPConnection -LocalPort 8004 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Get-Process -Id (Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Ports nettoyés" -ForegroundColor Green
    } catch {
        Write-Host "   ✅ Aucun processus à nettoyer" -ForegroundColor Green
    }

    # 3. INSTALLATION DES DÉPENDANCES
    Write-Host ""
    Write-Host "📦 Installation des dépendances..." -ForegroundColor Cyan

    # Backend Python
    Write-Host "   🐍 Dépendances Python..." -ForegroundColor Blue
    Set-Location $BackendDir
    
    if (Test-Path "requirements.txt") {
        try {
            python -m pip install -r requirements.txt --quiet --disable-pip-version-check
            Write-Host "   ✅ Dépendances Python installées" -ForegroundColor Green
        } catch {
            Write-Host "   ⚠️ Erreur installation Python (continuons quand même)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️ requirements.txt non trouvé" -ForegroundColor Yellow
    }

    # Frontend Node.js
    Set-Location $FrontendDir
    Write-Host "   📦 Dépendances Node.js..." -ForegroundColor Blue
    
    if (!(Test-Path "node_modules") -or !(Test-Path "node_modules\.package-lock.json")) {
        try {
            npm install --silent
            Write-Host "   ✅ Dépendances Node.js installées" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ Erreur installation Node.js" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "   ✅ Dépendances Node.js déjà installées" -ForegroundColor Green
    }

    Set-Location $BaseDir

    # 4. DÉMARRAGE DU BACKEND
    Write-Host ""
    Write-Host "🖥️ Démarrage du backend..." -ForegroundColor Cyan
    Set-Location $BackendDir

    # Lancer le backend avec uvicorn
    $BackendProcess = Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004", "--reload" -PassThru
    
    Write-Host "   📍 Backend PID: $($BackendProcess.Id)" -ForegroundColor Blue
    Write-Host "   🌐 URL Backend: http://localhost:8004" -ForegroundColor Blue

    # Attendre que le backend soit prêt
    Write-Host "   ⏳ Attente du backend..." -ForegroundColor Yellow
    for ($i = 1; $i -le 20; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8004/docs" -TimeoutSec 2 -ErrorAction Stop
            Write-Host "   ✅ Backend opérationnel!" -ForegroundColor Green
            break
        } catch {
            if ($BackendProcess.HasExited) {
                Write-Host "   ❌ Le backend s'est arrêté de manière inattendue" -ForegroundColor Red
                exit 1
            }
            Start-Sleep 2
            if ($i -eq 20) {
                Write-Host "   ⚠️ Backend lent à démarrer mais on continue..." -ForegroundColor Yellow
            }
        }
    }

    Set-Location $BaseDir

    # 5. DÉMARRAGE DU FRONTEND
    Write-Host ""
    Write-Host "🌐 Démarrage du frontend..." -ForegroundColor Cyan
    Set-Location $FrontendDir

    # Lancer le frontend avec Vite
    $FrontendProcess = Start-Process npm -ArgumentList "run", "dev" -PassThru

    Write-Host "   📍 Frontend PID: $($FrontendProcess.Id)" -ForegroundColor Blue
    Write-Host "   🌐 URL Frontend: http://localhost:5173" -ForegroundColor Blue

    # Attendre que le frontend soit prêt
    Write-Host "   ⏳ Attente du frontend..." -ForegroundColor Yellow
    for ($i = 1; $i -le 15; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -ErrorAction Stop
            Write-Host "   ✅ Frontend opérationnel!" -ForegroundColor Green
            break
        } catch {
            if ($FrontendProcess.HasExited) {
                Write-Host "   ❌ Le frontend s'est arrêté de manière inattendue" -ForegroundColor Red
                Cleanup
                exit 1
            }
            Start-Sleep 2
            if ($i -eq 15) {
                Write-Host "   ⚠️ Frontend lent à démarrer mais on continue..." -ForegroundColor Yellow
            }
        }
    }

    Set-Location $BaseDir

    # 6. TEST DE CONNECTIVITÉ
    Write-Host ""
    Write-Host "🔗 Test de connectivité..." -ForegroundColor Cyan

    # Test backend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8004/docs" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "   ✅ Backend accessible sur http://localhost:8004" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Backend non accessible (démarrage en cours...)" -ForegroundColor Yellow
    }

    # Test frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "   ✅ Frontend accessible sur http://localhost:5173" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Frontend non accessible (démarrage en cours...)" -ForegroundColor Yellow
    }

    # 7. SUCCÈS - AFFICHAGE DES INFOS
    Write-Host ""
    Write-Host "🎉 LANCEMENT RÉUSSI!" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URLS D'ACCÈS:" -ForegroundColor Cyan
    Write-Host "   Frontend:     http://localhost:5173" -ForegroundColor White
    Write-Host "   Backend API:  http://localhost:8004" -ForegroundColor White
    Write-Host "   API Docs:     http://localhost:8004/docs" -ForegroundColor White
    Write-Host "   Diagnostic:   http://localhost:8004/diagnostic" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 SERVICES ACTIFS:" -ForegroundColor Cyan
    Write-Host "   Backend PID:  $($BackendProcess.Id)" -ForegroundColor White
    Write-Host "   Frontend PID: $($FrontendProcess.Id)" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 CONSEILS:" -ForegroundColor Yellow
    Write-Host "   • L'interface est maintenant accessible" -ForegroundColor White
    Write-Host "   • Laissez cette fenêtre PowerShell ouverte" -ForegroundColor White
    Write-Host "   • Appuyez sur Ctrl+C pour tout arrêter" -ForegroundColor White
    Write-Host "   • En cas de problème, relancez ce script" -ForegroundColor White
    Write-Host ""

    # Ouvrir le navigateur automatiquement après 5 secondes
    Write-Host "🌐 Ouverture automatique du navigateur dans 5 secondes..." -ForegroundColor Cyan
    Start-Sleep 5

    try {
        Start-Process "http://localhost:5173"
        Write-Host "   ✅ Navigateur ouvert" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Ouvrez manuellement: http://localhost:5173" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "🔄 Services en cours d'exécution..." -ForegroundColor Green
    Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow

    # Monitoring des processus
    while ($true) {
        Start-Sleep 5
        
        # Vérifier que les processus sont toujours actifs
        if ($BackendProcess.HasExited) {
            Write-Host ""
            Write-Host "❌ Backend arrêté de manière inattendue" -ForegroundColor Red
            Cleanup
            exit 1
        }
        
        if ($FrontendProcess.HasExited) {
            Write-Host ""
            Write-Host "❌ Frontend arrêté de manière inattendue" -ForegroundColor Red
            Cleanup
            exit 1
        }
    }

} catch {
    Write-Host ""
    Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    Cleanup
} finally {
    # Au cas où
}

# Fonction pour gérer l'interruption
Register-EngineEvent PowerShell.Exiting -Action { Cleanup }
