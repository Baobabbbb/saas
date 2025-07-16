#!/usr/bin/env powershell
# Script PowerShell pour démarrer SEEDANCE

Write-Host "🚀 Démarrage du serveur SEEDANCE..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Aller dans le bon répertoire
Set-Location "c:\Users\Admin\Documents\saas\saas"
Write-Host "📁 Répertoire: $(Get-Location)" -ForegroundColor Cyan

# Vérifier que le fichier main.py existe
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Fichier main.py non trouvé" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

Write-Host "✅ Fichier main.py trouvé" -ForegroundColor Green

# Tester Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non accessible" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Installer les dépendances si nécessaire
Write-Host "📦 Vérification des dépendances..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn, aiohttp, openai" 2>$null
    Write-Host "✅ Dépendances OK" -ForegroundColor Green
} catch {
    Write-Host "⬇️ Installation des dépendances..." -ForegroundColor Yellow
    pip install fastapi uvicorn python-dotenv aiohttp openai
}

# Arrêter les processus existants
Write-Host "🔍 Arrêt des processus Python existants..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "🚀 LANCEMENT DU SERVEUR" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "🌐 URL: http://localhost:8004" -ForegroundColor Cyan
Write-Host "📚 Documentation: http://localhost:8004/docs" -ForegroundColor Cyan
Write-Host "💡 Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
Write-Host ""

# Lancer le serveur
try {
    python -m uvicorn main:app --host 127.0.0.1 --port 8004 --reload
} catch {
    Write-Host "❌ Erreur lors du démarrage: $_" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
}

Write-Host "🛑 Serveur arrêté" -ForegroundColor Red
