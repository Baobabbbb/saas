#!/usr/bin/env python3
"""
Script robuste pour démarrer le serveur SEEDANCE
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Vérifier les prérequis"""
    try:
        import fastapi
        import uvicorn
        import aiohttp
        import openai
        from dotenv import load_dotenv
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False

def start_seedance_server():
    """Démarrer le serveur SEEDANCE"""
    
    print("🚀 Démarrage du serveur SEEDANCE")
    print("=" * 50)
    
    # Se placer dans le bon répertoire
    script_dir = Path(__file__).parent
    saas_dir = script_dir / "saas"
    
    if not saas_dir.exists():
        print(f"❌ Répertoire non trouvé: {saas_dir}")
        return False
    
    os.chdir(saas_dir)
    print(f"📁 Répertoire de travail: {saas_dir.absolute()}")
    
    # Vérifier les prérequis
    if not check_requirements():
        print("❌ Veuillez installer les dépendances manquantes")
        return False
    
    # Vérifier le fichier main.py
    main_file = saas_dir / "main.py"
    if not main_file.exists():
        print(f"❌ Fichier main.py non trouvé: {main_file}")
        return False
    
    print("🌐 Serveur sera accessible sur: http://localhost:8004")
    print("🎬 Endpoint SEEDANCE: http://localhost:8004/api/seedance/generate")
    print("📚 Documentation API: http://localhost:8004/docs")
    print("-" * 50)
    
    try:
        # Démarrer uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8004",
            "--reload",
            "--log-level", "info"
        ]
        
        print(f"🔧 Commande: {' '.join(cmd)}")
        print("🚀 Démarrage en cours...")
        print("💡 Appuyez sur Ctrl+C pour arrêter")
        print("-" * 50)
        
        # Démarrer le serveur
        process = subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = start_seedance_server()
    if not success:
        print("\n❌ Échec du démarrage du serveur")
        input("Appuyez sur Entrée pour continuer...")
        sys.exit(1)
