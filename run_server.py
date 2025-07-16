import subprocess
import sys
import os
from pathlib import Path

# Se placer dans le bon répertoire
saas_dir = Path("c:/Users/Admin/Documents/saas/saas")
os.chdir(saas_dir)

print(f"🚀 Démarrage du serveur SEEDANCE depuis {saas_dir}")
print("🌐 Serveur accessible sur: http://localhost:8004")

# Commande pour démarrer uvicorn
cmd = [
    sys.executable, "-m", "uvicorn", 
    "main:app", 
    "--host", "127.0.0.1", 
    "--port", "8004",
    "--reload"
]

print(f"🔧 Commande: {' '.join(cmd)}")

try:
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("🛑 Serveur arrêté")
except Exception as e:
    print(f"❌ Erreur: {e}")
    input("Appuyez sur Entrée...")
