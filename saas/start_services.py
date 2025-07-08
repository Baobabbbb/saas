#!/usr/bin/env python3
"""
Script pour démarrer tous les services nécessaires
"""
import asyncio
import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Démarre le backend Python"""
    print("🚀 Démarrage du backend...")
    backend_path = Path(__file__).parent
    
    # Démarrer le serveur backend
    cmd = [
        sys.executable, "main.py"
    ]
    
    print(f"Commande: {' '.join(cmd)}")
    print(f"Répertoire: {backend_path}")
    
    try:
        process = subprocess.Popen(
            cmd, 
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("✅ Backend démarré!")
        print("📝 Logs du backend:")
        
        # Lire et afficher les logs
        for line in iter(process.stdout.readline, ''):
            print(f"[BACKEND] {line.rstrip()}")
            
    except Exception as e:
        print(f"❌ Erreur démarrage backend: {e}")

def start_frontend():
    """Démarre le frontend React"""
    print("🎨 Démarrage du frontend...")
    frontend_path = Path(__file__).parent.parent / "frontend"
    
    if not frontend_path.exists():
        print("❌ Dossier frontend non trouvé")
        return
    
    # Démarrer le serveur frontend
    cmd = ["npm", "start"]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        print("✅ Frontend démarré!")
        print("🌐 Accès: http://localhost:3000")
        
    except Exception as e:
        print(f"❌ Erreur démarrage frontend: {e}")

async def main():
    """Fonction principale"""
    print("🏁 Démarrage des services FRIDAY BD")
    print("=" * 50)
    
    # Vérifier la configuration
    print("🔍 Vérification de la configuration...")
    
    # Variables requises
    required_vars = ["OPENAI_API_KEY", "ENABLE_AI_BUBBLES"]
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ Variable manquante: {var}")
            return
        else:
            print(f"✅ {var}: OK")
    
    print()
    
    # Proposer les options
    print("🎯 Options de démarrage:")
    print("1. Backend seulement")
    print("2. Frontend seulement")
    print("3. Backend et Frontend")
    print("4. Test de génération BD")
    
    choice = input("\nChoisissez une option (1-4): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
    elif choice == "3":
        print("🔄 Démarrage des deux services...")
        # TODO: Démarrer les deux en parallèle
        print("ℹ️ Démarrez le backend dans un terminal et le frontend dans un autre")
    elif choice == "4":
        print("🧪 Lancement du test de génération BD...")
        # Importer et tester le générateur
        try:
            from services.stable_diffusion_generator import StableDiffusionGenerator
            
            # Créer un spec de test
            class TestSpec:
                def __init__(self):
                    self.hero_name = "Luna"
                    self.story_type = "adventure"
                    self.style = "cartoon"
                    self.num_images = 1
            
            # Données de test
            comic_data = {
                "chapters": [{
                    "scene": 1,
                    "description": "Luna découvre un monde magique",
                    "action_description": "Une jeune fille regarde un paysage fantastique"
                }]
            }
            
            generator = StableDiffusionGenerator()
            spec = TestSpec()
            
            print("🎨 Génération d'une page de test...")
            pages = await generator.generate_comic_images(comic_data, spec)
            
            if pages:
                print(f"✅ Page générée: {pages[0]['image_url']}")
                print("🎉 Test réussi!")
            else:
                print("❌ Échec de la génération")
                
        except Exception as e:
            print(f"❌ Erreur test: {e}")
    else:
        print("❌ Option invalide")

if __name__ == "__main__":
    asyncio.run(main())
