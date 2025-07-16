#!/usr/bin/env python3
"""
Script de diagnostic pour SEEDANCE
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_seedance_requirements():
    """Vérifie les prérequis pour SEEDANCE"""
    
    print("🔍 Diagnostic SEEDANCE")
    print("=" * 50)
    
    # Vérifier le répertoire
    saas_dir = Path("saas")
    if not saas_dir.exists():
        print("❌ Répertoire 'saas' introuvable")
        return False
    
    print(f"✅ Répertoire saas: {saas_dir.absolute()}")
    
    # Charger les variables d'environnement
    env_file = saas_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Fichier .env trouvé: {env_file}")
    else:
        print(f"⚠️  Fichier .env manquant: {env_file}")
    
    # Vérifier les clés API
    required_env_vars = [
        "OPENAI_API_KEY",
        "WAVESPEED_API_KEY", 
        "FAL_API_KEY"
    ]
    
    print("\n🔑 Variables d'environnement:")
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"❌ {var}: MANQUANT")
    
    # Vérifier les dépendances Python
    print("\n📦 Dépendances Python:")
    required_packages = [
        "fastapi",
        "uvicorn", 
        "aiohttp",
        "openai",
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}: MANQUANT")
            missing_packages.append(package)
    
    # Vérifier les répertoires de cache
    print("\n📁 Répertoires de cache:")
    cache_dirs = [
        Path("cache"),
        Path("cache/seedance")
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"✅ {cache_dir}")
        else:
            print(f"⚠️  {cache_dir}: Sera créé automatiquement")
    
    # Vérifier les fichiers principaux
    print("\n📄 Fichiers principaux:")
    main_files = [
        saas_dir / "main.py",
        saas_dir / "services" / "seedance_service.py"
    ]
    
    for file_path in main_files:
        if file_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: MANQUANT")
    
    print("\n" + "=" * 50)
    
    if missing_packages:
        print(f"⚠️  Pour installer les packages manquants:")
        print(f"pip install {' '.join(missing_packages)}")
    
    print("🚀 Pour démarrer SEEDANCE:")
    print("python start_seedance_server.py")
    print("ou")
    print("start_seedance.bat")
    
    return len(missing_packages) == 0

if __name__ == "__main__":
    check_seedance_requirements()
