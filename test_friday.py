"""
Test rapide de la pipeline FRIDAY
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire saas au path et changer le répertoire de travail
saas_path = str(Path(__file__).parent / "saas")
sys.path.insert(0, saas_path)
os.chdir(saas_path)

def test_imports():
    """Test des imports principaux"""
    print("Test des imports FRIDAY...")
    
    try:
        # Test configuration
        import os
        from dotenv import load_dotenv
        load_dotenv("saas/.env")
        
        openai_ok = bool(os.getenv("OPENAI_API_KEY"))
        stability_ok = bool(os.getenv("STABILITY_API_KEY"))
        
        print(f"OpenAI API: {'OK' if openai_ok else 'MANQUANT'}")
        print(f"Stability API: {'OK' if stability_ok else 'MANQUANT'}")
        
        # Test pipeline
        from services.animation_pipeline import animation_pipeline
        print("Pipeline animation: OK")
        
        # Test app
        from main_new import app
        print("Application FastAPI: OK")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    print(f"\nResultat: {'SUCCESS' if success else 'FAILED'}")
