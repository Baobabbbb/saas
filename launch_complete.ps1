# SEEDANCE - Lanceur Complet PowerShell
# Lance le backend et le frontend automatiquement

param(
    [switch]$SkipDependencies,
    [switch]$NoOpenBrowser,
    [int]$BackendPort = 8004,
    [int]$FrontendPort = 5173
)

# Configuration des couleurs
$Host.UI.RawUI.WindowTitle = "SEEDANCE - Lanceur Complet"

# Fonctions utilitaires
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green "✅ $args" }
function Write-Error { Write-ColorOutput Red "❌ $args" }
function Write-Warning { Write-ColorOutput Yellow "⚠️ $args" }
function Write-Info { Write-ColorOutput Cyan "ℹ️ $args" }
function Write-Step { Write-ColorOutput Magenta "🔧 $args" }

# Variables globales
$Script:BackendProcess = $null
$Script:FrontendProcess = $null
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SaasDir = Join-Path $BaseDir "saas"
$FrontendDir = Join-Path $BaseDir "frontend"

# Fonction de nettoyage
function Stop-SeedanceServices {
    Write-Step "Arrêt des services SEEDANCE..."
    
    if ($Script:BackendProcess -and !$Script:BackendProcess.HasExited) {
        Write-Info "Arrêt du backend..."
        $Script:BackendProcess.Kill()
    }
    
    if ($Script:FrontendProcess -and !$Script:FrontendProcess.HasExited) {
        Write-Info "Arrêt du frontend..."
        $Script:FrontendProcess.Kill()
    }
    
    # Tuer les processus sur les ports spécifiques
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Info "Arrêt du processus $($process.Name) sur le port $BackendPort"
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Info "Arrêt du processus $($process.Name) sur le port $FrontendPort"
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
}

# Gestionnaire de signaux
try {
    [Console]::TreatControlCAsInput = $false
    [Console]::CancelKeyPress += {
        param($sender, $e)
        $e.Cancel = $true
        Stop-SeedanceServices
        exit 0
    }
} catch {
    # Fallback pour anciennes versions de PowerShell
}

function Test-Prerequisites {
    Write-Step "Vérification des prérequis..."
    
    # Vérifier Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python trouvé: $pythonVersion"
    } catch {
        Write-Error "Python non trouvé. Veuillez installer Python."
        return $false
    }
    
    # Vérifier Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js trouvé: $nodeVersion"
    } catch {
        Write-Error "Node.js non trouvé. Veuillez installer Node.js."
        return $false
    }
    
    # Vérifier les répertoires
    if (-not (Test-Path $SaasDir)) {
        Write-Error "Répertoire backend non trouvé: $SaasDir"
        return $false
    }
    
    if (-not (Test-Path $FrontendDir)) {
        Write-Error "Répertoire frontend non trouvé: $FrontendDir"
        return $false
    }
    
    # Vérifier les fichiers essentiels
    if (-not (Test-Path (Join-Path $SaasDir "main.py"))) {
        Write-Error "Fichier main.py non trouvé dans $SaasDir"
        return $false
    }
    
    if (-not (Test-Path (Join-Path $FrontendDir "package.json"))) {
        Write-Error "Fichier package.json non trouvé dans $FrontendDir"
        return $false
    }
    
    Write-Success "Tous les prérequis sont satisfaits"
    return $true
}

function Install-Dependencies {
    if ($SkipDependencies) {
        Write-Info "Installation des dépendances ignorée (--SkipDependencies)"
        return
    }
    
    Write-Step "Installation des dépendances..."
    
    # Backend Python
    $requirementsFile = Join-Path $SaasDir "requirements.txt"
    if (Test-Path $requirementsFile) {
        Write-Info "Installation des dépendances Python..."
        Push-Location $SaasDir
        try {
            python -m pip install -r requirements.txt
            Write-Success "Dépendances Python installées"
        } catch {
            Write-Warning "Erreur lors de l'installation des dépendances Python: $_"
        }
        Pop-Location
    }
    
    # Frontend Node.js
    Write-Info "Installation des dépendances Node.js..."
    Push-Location $FrontendDir
    try {
        npm install
        Write-Success "Dépendances Node.js installées"
    } catch {
        Write-Warning "Erreur lors de l'installation des dépendances Node.js: $_"
    }
    Pop-Location
}

function Start-Backend {
    Write-Step "Démarrage du backend..."
    
    Push-Location $SaasDir
    
    try {
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = "python"
        $startInfo.Arguments = "-m uvicorn main:app --host 0.0.0.0 --port $BackendPort --reload"
        $startInfo.WorkingDirectory = $SaasDir
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $false
        
        $Script:BackendProcess = [System.Diagnostics.Process]::Start($startInfo)
        
        Write-Success "Backend démarré (PID: $($Script:BackendProcess.Id))"
        Write-Info "🌐 API disponible sur: http://localhost:$BackendPort"
        Write-Info "📚 Documentation: http://localhost:$BackendPort/docs"
        
        return $true
    } catch {
        Write-Error "Erreur lors du démarrage du backend: $_"
        return $false
    } finally {
        Pop-Location
    }
}

function Start-Frontend {
    Write-Step "Démarrage du frontend..."
    
    Push-Location $FrontendDir
    
    try {
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = "npm"
        $startInfo.Arguments = "run dev"
        $startInfo.WorkingDirectory = $FrontendDir
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $false
        
        $Script:FrontendProcess = [System.Diagnostics.Process]::Start($startInfo)
        
        Write-Success "Frontend démarré (PID: $($Script:FrontendProcess.Id))"
        Write-Info "🎨 Interface disponible sur: http://localhost:$FrontendPort"
        
        return $true
    } catch {
        Write-Error "Erreur lors du démarrage du frontend: $_"
        return $false
    } finally {
        Pop-Location
    }
}

function Open-Browser {
    if ($NoOpenBrowser) {
        Write-Info "Ouverture du navigateur ignorée (--NoOpenBrowser)"
        return
    }
    
    Write-Step "Ouverture du navigateur..."
    Start-Sleep -Seconds 5
    
    try {
        Start-Process "http://localhost:$FrontendPort"
        Start-Process "http://localhost:$BackendPort/docs"
        Write-Success "Navigateur ouvert"
    } catch {
        Write-Warning "Impossible d'ouvrir le navigateur automatiquement"
        Write-Info "Ouvrez manuellement: http://localhost:$FrontendPort"
    }
}

function Wait-ForServices {
    Write-Step "Surveillance des services (Ctrl+C pour arrêter)..."
    
    try {
        while ($true) {
            if ($Script:BackendProcess.HasExited) {
                Write-Error "Le backend s'est arrêté de manière inattendue"
                break
            }
            
            if ($Script:FrontendProcess.HasExited) {
                Write-Error "Le frontend s'est arrêté de manière inattendue"
                break
            }
            
            Start-Sleep -Seconds 5
        }
    } catch [System.OperationCanceledException] {
        Write-Info "Arrêt demandé par l'utilisateur"
    }
}

# Script principal
function Main {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "   🎬 SEEDANCE - LANCEUR COMPLET POWERSHELL" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Info "📁 Répertoire de base: $BaseDir"
    Write-Info "📁 Backend: $SaasDir"
    Write-Info "📁 Frontend: $FrontendDir"
    Write-Info "🌐 Ports: Backend=$BackendPort, Frontend=$FrontendPort"
    Write-Host ""
    
    try {
        # Vérifications
        if (-not (Test-Prerequisites)) {
            return $false
        }
        
        # Installation des dépendances
        Install-Dependencies
        
        # Démarrage du backend
        if (-not (Start-Backend)) {
            Write-Error "Impossible de démarrer le backend"
            return $false
        }
        
        Start-Sleep -Seconds 3
        
        # Démarrage du frontend
        if (-not (Start-Frontend)) {
            Write-Error "Impossible de démarrer le frontend"
            Stop-SeedanceServices
            return $false
        }
        
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "   🎉 SEEDANCE LANCÉ AVEC SUCCÈS!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Backend API: http://localhost:$BackendPort" -ForegroundColor Cyan
        Write-Host "📚 Documentation: http://localhost:$BackendPort/docs" -ForegroundColor Cyan
        Write-Host "🎨 Frontend: http://localhost:$FrontendPort" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "💡 Appuyez sur Ctrl+C pour arrêter tous les services" -ForegroundColor Yellow
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        
        # Ouvrir le navigateur
        Open-Browser
        
        # Attendre
        Wait-ForServices
        
        return $true
        
    } catch {
        Write-Error "Erreur inattendue: $_"
        return $false
    } finally {
        Stop-SeedanceServices
    }
}

# Exécution
$success = Main
exit $(if ($success) { 0 } else { 1 })
