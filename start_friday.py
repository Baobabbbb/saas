#!/usr/bin/env python3
"""
🤖 FRIDAY - Démarrage du serveur principal
Utilise la nouvelle pipeline sans CrewAI (GPT-4o-mini + SD3-Turbo)
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire saas au path
saas_path = str(Path(__file__).parent / "saas")
if saas_path not in sys.path:
    sys.path.insert(0, saas_path)

# Changer le répertoire de travail
os.chdir(saas_path)

def check_environment():
    """Vérifier la configuration de l'environnement"""
    print("🔧 Vérification de l'environnement...")
    
    from dotenv import load_dotenv
    load_dotenv("saas/.env")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    stability_key = os.getenv("STABILITY_API_KEY")
    
    issues = []
    
    if not openai_key or openai_key.startswith("sk-votre"):
        issues.append("❌ Clé API OpenAI manquante ou invalide")
    else:
        print(f"✅ OpenAI configuré: {openai_key[:10]}...")
    
    if not stability_key or stability_key.startswith("sk-votre"):
        issues.append("❌ Clé API Stability AI manquante ou invalide")
    else:
        print(f"✅ Stability AI configuré: {stability_key[:10]}...")
    
    # Vérifier les dépendances
    try:
        import fastapi
        import openai
        import aiohttp
        print("✅ Dépendances principales installées")
    except ImportError as e:
        issues.append(f"❌ Dépendance manquante: {e}")
    
    # Vérifier les répertoires
    cache_dir = Path("saas/cache")
    static_dir = Path("saas/static")
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    
    print("✅ Répertoires créés")
    
    if issues:
        print("\n⚠️ PROBLÈMES DÉTECTÉS:")
        for issue in issues:
            print(f"   {issue}")
        print("\n🔧 Corrigez ces problèmes avant de continuer.")
        return False
    
    print("✅ Environnement prêt!")
    return True

def start_server(use_new_pipeline=True):
    """Démarrer le serveur FRIDAY"""
    
    if not check_environment():
        print("❌ Impossible de démarrer le serveur")
        return
    
    print(f"\n🚀 Démarrage de FRIDAY...")
    
    if use_new_pipeline:
        print("📦 Pipeline: Nouvelle version (GPT-4o-mini + SD3-Turbo)")
        print("📂 Fichier: main_new.py")
        
        # Importer et démarrer la nouvelle version
        try:
            import uvicorn
            
            # Importer depuis le bon répertoire
            import sys
            from pathlib import Path
            saas_dir = Path(__file__).parent / "saas"
            sys.path.insert(0, str(saas_dir))
            os.chdir(str(saas_dir))
            
            import main_new
            app = main_new.app
            
            print(f"\n🌐 Serveur démarré sur: http://localhost:8000")
            print(f"📚 Documentation: http://localhost:8000/docs")
            print(f"🔍 Diagnostic: http://localhost:8000/diagnostic")
            print(f"💚 Santé: http://localhost:8000/health")
            print(f"\n🎬 Endpoint principal: POST /api/animations/generate")
            
            uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
            
        except ImportError as e:
            print(f"❌ Erreur d'importation: {e}")
            print("🔧 Installez uvicorn: pip install uvicorn")
        except Exception as e:
            print(f"❌ Erreur de démarrage: {e}")
    
    else:
        print("📦 Pipeline: Version originale (avec CrewAI)")
        print("📂 Fichier: main.py")
        
        try:
            import uvicorn
            from main import app
            
            uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
            
        except Exception as e:
            print(f"❌ Erreur de démarrage: {e}")

def show_usage():
    """Afficher les instructions d'utilisation"""
    print("""
🤖 FRIDAY - Assistant d'animation IA

UTILISATION:
  python start_friday.py            # Nouvelle pipeline (recommandé)
  python start_friday.py --old      # Ancienne pipeline avec CrewAI

ENDPOINTS PRINCIPAUX:
  POST /api/animations/generate     # Génération complète d'animation
  POST /tts                         # Synthèse vocale
  POST /stt                         # Transcription audio
  GET  /diagnostic                  # Vérification configuration

CONFIGURATION REQUISE:
  - Fichier saas/.env avec:
    • OPENAI_API_KEY=sk-...
    • STABILITY_API_KEY=sk-...
  
PIPELINE NOUVELLE VERSION:
  1. Analyse histoire (GPT-4o-mini)
  2. Style visuel (GPT-4o-mini)  
  3. Prompts vidéo (GPT-4o-mini)
  4. Génération clips (SD3-Turbo)
  5. Assemblage final

EXEMPLE D'UTILISATION:
  curl -X POST http://localhost:8000/api/animations/generate \\
    -H "Content-Type: application/json" \\
    -d '{"story": "Une petite fille sauve la forêt magique", "target_duration": 60}'
""")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 FRIDAY - Serveur d'animation IA")
    parser.add_argument("--old", action="store_true", help="Utiliser l'ancienne pipeline avec CrewAI")
    parser.add_argument("--help-usage", action="store_true", help="Afficher l'aide d'utilisation")
    
    args = parser.parse_args()
    
    if args.help_usage:
        show_usage()
    else:
        use_new = not args.old
        start_server(use_new_pipeline=use_new)
