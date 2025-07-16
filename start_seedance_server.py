#!/usr/bin/env python3
"""
Script pour démarrer le serveur SEEDANCE sur le port 8004
"""

import os
import sys
import subprocess
from pathlib import Path

def start_seedance_server():
    """Démarre le serveur FastAPI avec SEEDANCE sur le port 8004"""
    
    # Se placer dans le bon répertoire
    saas_dir = Path(__file__).parent / "saas"
    os.chdir(saas_dir)
    
    print("🚀 Démarrage du serveur SEEDANCE...")
    print(f"📁 Répertoire: {saas_dir}")
    print("🌐 URL: http://localhost:8004")
    print("🎬 Endpoint SEEDANCE: http://localhost:8004/api/seedance/generate")
    print("-" * 50)
    
    try:
        # Démarrer uvicorn avec le port 8004
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8004",
            "--reload",
            "--log-level", "info"
        ]
        
        print(f"🔧 Commande: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_seedance_server()
