#!/usr/bin/env python3
"""
Test simple de FRIDAY depuis le répertoire saas
"""
import os
import sys
from pathlib import Path

def test_friday():
    """Test simple de la configuration FRIDAY"""
    
    print("🔧 Test configuration FRIDAY...")
    
    # Configuration environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    stability_key = os.getenv("STABILITY_API_KEY")
    
    print(f"OpenAI: {'✅' if openai_key else '❌'}")
    print(f"Stability: {'✅' if stability_key else '❌'}")
    
    # Test imports
    try:
        from services.animation_pipeline import animation_pipeline
        print("Pipeline animation: ✅")
    except Exception as e:
        print(f"Pipeline animation: ❌ {e}")
    
    try:
        from main_new import app
        print("Application FastAPI: ✅")
    except Exception as e:
        print(f"Application FastAPI: ❌ {e}")
    
    print("✅ Test terminé")

if __name__ == "__main__":
    # Aller dans le répertoire saas
    script_dir = Path(__file__).parent
    os.chdir(str(script_dir))
    
    test_friday()
