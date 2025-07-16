# SEEDANCE - Lancement Express PowerShell
# Script de démarrage rapide sans vérifications poussées

$Host.UI.RawUI.WindowTitle = "SEEDANCE - Lancement Express"

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   🚀 SEEDANCE - LANCEMENT EXPRESS" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Démarrage rapide sans vérifications poussées
Write-Host "🎬 Démarrage des services SEEDANCE..." -ForegroundColor Cyan
Write-Host ""

# Variables
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SaasDir = Join-Path $BaseDir "saas"
$FrontendDir = Join-Path $BaseDir "frontend"

# Backend
Write-Host "🔥 Lancement du backend..." -ForegroundColor Green
$backendCmd = "python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$SaasDir'; $backendCmd" -WindowStyle Normal

# Attendre un peu
Start-Sleep -Seconds 3

# Frontend
Write-Host "🎨 Lancement du frontend..." -ForegroundColor Magenta
$frontendCmd = "npm run dev"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; $frontendCmd" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Services lancés!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Backend: http://localhost:8004" -ForegroundColor Cyan
Write-Host "🎨 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

# Ouvrir le navigateur après 10 secondes
Write-Host "⏳ Ouverture du navigateur dans 10 secondes..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    Start-Process "http://localhost:5173"
    Write-Host "🌐 Navigateur ouvert sur l'interface principale" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible d'ouvrir le navigateur automatiquement" -ForegroundColor Yellow
    Write-Host "Ouvrez manuellement: http://localhost:5173" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "💡 Fermez cette fenêtre ou les fenêtres des services pour arrêter" -ForegroundColor Yellow
Write-Host ""
Read-Host "Appuyez sur Entrée pour fermer cette fenêtre"
