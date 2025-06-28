#!/usr/bin/env python3
"""
Script de démarrage simple pour FRIDAY
Démarre directement depuis le répertoire saas
"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    """Démarrer FRIDAY depuis le bon répertoire"""
    
    # Aller dans le répertoire saas
    backend_dir = Path(__file__).parent
    saas_dir = backend_dir / "saas"
    
    if not saas_dir.exists():
        print("❌ Répertoire saas introuvable!")
        return
    
    print("🚀 Démarrage FRIDAY...")
    print(f"📁 Répertoire: {saas_dir}")
    
    try:
        # Changer vers le répertoire saas
        os.chdir(str(saas_dir))
        
        # Démarrer avec uvicorn
        cmd = [sys.executable, "-m", "uvicorn", "main_new:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        
        print("🌐 Démarrage du serveur...")
        print("📱 Backend: http://localhost:8000")
        print("📚 Docs: http://localhost:8000/docs")
        print("🔍 Diagnostic: http://localhost:8000/diagnostic")
        print("\n⏹️ Appuyez sur Ctrl+C pour arrêter")
        
        # Démarrer le serveur
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n✅ Serveur arrêté")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
