#!/usr/bin/env python3
"""
Script de lancement complet pour SEEDANCE
Lance automatiquement le backend et le frontend
"""

import os
import sys
import subprocess
import threading
import time
import signal
import psutil
from pathlib import Path

class LauncherSeedance:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        self.saas_dir = self.base_dir / "saas"
        self.frontend_dir = self.base_dir / "frontend"
        self.running = True
        
    def check_port_available(self, port):
        """Vérifie si un port est disponible"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return False
            return True
        except:
            return True
    
    def kill_port(self, port):
        """Tue les processus utilisant un port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if conn.laddr.port == port:
                            print(f"🔫 Arrêt du processus {proc.info['name']} (PID: {proc.info['pid']}) sur le port {port}")
                            proc.kill()
                            time.sleep(1)
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Erreur lors de l'arrêt du port {port}: {e}")

    def setup_environment(self):
        """Configuration de l'environnement"""
        print("🔧 Configuration de l'environnement...")
        
        # Vérifier les répertoires
        if not self.saas_dir.exists():
            print(f"❌ Répertoire backend non trouvé: {self.saas_dir}")
            return False
            
        if not self.frontend_dir.exists():
            print(f"❌ Répertoire frontend non trouvé: {self.frontend_dir}")
            return False
            
        # Vérifier main.py
        main_file = self.saas_dir / "main.py"
        if not main_file.exists():
            print(f"❌ Fichier main.py non trouvé: {main_file}")
            return False
            
        print("✅ Environnement vérifié")
        return True

    def install_dependencies(self):
        """Installation des dépendances"""
        print("\n📦 Vérification des dépendances...")
        
        # Backend Python
        requirements_file = self.saas_dir / "requirements.txt"
        if requirements_file.exists():
            print("🐍 Installation des dépendances Python...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, cwd=str(self.saas_dir))
                print("✅ Dépendances Python installées")
            except subprocess.CalledProcessError:
                print("⚠️ Erreur lors de l'installation des dépendances Python")
        
        # Frontend Node.js
        package_json = self.frontend_dir / "package.json"
        if package_json.exists():
            print("📦 Installation des dépendances Node.js...")
            try:
                subprocess.run([
                    "npm", "install"
                ], check=True, cwd=str(self.frontend_dir))
                print("✅ Dépendances Node.js installées")
            except subprocess.CalledProcessError:
                print("⚠️ Erreur lors de l'installation des dépendances Node.js")

    def start_backend(self):
        """Démarre le serveur backend"""
        print("\n🚀 Démarrage du backend...")
        
        # Libérer le port si nécessaire
        if not self.check_port_available(8004):
            print("🔄 Port 8004 occupé, libération...")
            self.kill_port(8004)
            time.sleep(2)
        
        try:
            # Commande pour démarrer le backend
            cmd = [
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8004",
                "--reload",
                "--log-level", "info"
            ]
            
            print(f"🔧 Commande backend: {' '.join(cmd)}")
            print(f"📁 Répertoire: {self.saas_dir}")
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=str(self.saas_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre un peu pour voir si le serveur démarre
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend démarré avec succès")
                print("🌐 API disponible sur: http://localhost:8004")
                print("📚 Documentation: http://localhost:8004/docs")
                return True
            else:
                stderr = self.backend_process.stderr.read()
                print(f"❌ Erreur lors du démarrage du backend: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du backend: {e}")
            return False

    def start_frontend(self):
        """Démarre le serveur frontend"""
        print("\n🎨 Démarrage du frontend...")
        
        # Libérer le port si nécessaire
        if not self.check_port_available(5173):
            print("🔄 Port 5173 occupé, libération...")
            self.kill_port(5173)
            time.sleep(2)
        
        try:
            # Commande pour démarrer le frontend Vite
            cmd = ["npm", "run", "dev"]
            
            print(f"🔧 Commande frontend: {' '.join(cmd)}")
            print(f"📁 Répertoire: {self.frontend_dir}")
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre un peu pour voir si le serveur démarre
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend démarré avec succès")
                print("🌐 Interface disponible sur: http://localhost:5173")
                return True
            else:
                stderr = self.frontend_process.stderr.read()
                print(f"❌ Erreur lors du démarrage du frontend: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du frontend: {e}")
            return False

    def monitor_processes(self):
        """Surveille les processus"""
        print("\n👀 Surveillance des processus...")
        
        while self.running:
            try:
                # Vérifier le backend
                if self.backend_process and self.backend_process.poll() is not None:
                    print("⚠️ Backend arrêté de manière inattendue")
                    break
                
                # Vérifier le frontend
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("⚠️ Frontend arrêté de manière inattendue")
                    break
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                break

    def stop_services(self):
        """Arrête tous les services"""
        print("\n🛑 Arrêt des services...")
        self.running = False
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("✅ Backend arrêté")
            except:
                self.backend_process.kill()
                print("🔫 Backend forcé à s'arrêter")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend arrêté")
            except:
                self.frontend_process.kill()
                print("🔫 Frontend forcé à s'arrêter")

    def run(self):
        """Lance l'application complète"""
        print("=" * 60)
        print("🎬 SEEDANCE - LANCEUR COMPLET")
        print("=" * 60)
        
        try:
            # Configuration
            if not self.setup_environment():
                return False
            
            # Installation des dépendances
            self.install_dependencies()
            
            # Démarrage du backend
            if not self.start_backend():
                print("❌ Impossible de démarrer le backend")
                return False
            
            # Démarrage du frontend
            if not self.start_frontend():
                print("❌ Impossible de démarrer le frontend")
                self.stop_services()
                return False
            
            print("\n" + "=" * 60)
            print("🎉 SEEDANCE LANCÉ AVEC SUCCÈS!")
            print("=" * 60)
            print("🌐 Backend API: http://localhost:8004")
            print("📚 Documentation: http://localhost:8004/docs")
            print("🎨 Frontend: http://localhost:5173")
            print("=" * 60)
            print("\n💡 Appuyez sur Ctrl+C pour arrêter tous les services")
            
            # Surveillance
            self.monitor_processes()
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
        finally:
            self.stop_services()

def main():
    """Point d'entrée principal"""
    launcher = LauncherSeedance()
    
    # Gestionnaire de signal pour arrêt propre
    def signal_handler(signum, frame):
        launcher.stop_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return launcher.run()

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
