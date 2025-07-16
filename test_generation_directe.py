#!/usr/bin/env python3
"""
🔧 Test de génération directe sans passer par l'API
Pour identifier exactement où le pipeline plante
"""

import sys
import os
import asyncio
from pathlib import Path

# Ajouter saas au path
sys.path.insert(0, str(Path(__file__).parent / "saas"))

async def test_generation_directe():
    """Test de génération complète en direct"""
    print("🎬 TEST GÉNÉRATION DIRECTE")
    print("=" * 50)
    
    try:
        # Charger la configuration
        from dotenv import load_dotenv
        load_dotenv()
        
        # Importer la fonction principale
        from services.pipeline_dessin_anime_v2 import creer_dessin_anime
        
        # Test avec une histoire simple
        histoire = "Un petit chat découvre un jardin magique avec des fleurs qui brillent."
        
        print(f"📖 Histoire: {histoire}")
        print("🚀 Début de génération...")
        
        result = await creer_dessin_anime(
            histoire=histoire,
            duree=30,
            openai_key=os.getenv("OPENAI_API_KEY"),
            stability_key=os.getenv("STABILITY_API_KEY"),
            mode="demo"
        )
        
        print("✅ GÉNÉRATION RÉUSSIE!")
        print(f"   Status: {result.get('status')}")
        print(f"   Scènes: {len(result.get('scenes', []))}")
        print(f"   Clips: {len(result.get('clips', []))}")
        print(f"   Durée: {result.get('duree_totale')}s")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        print("\n📋 TRACEBACK COMPLET:")
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        success = loop.run_until_complete(test_generation_directe())
        if success:
            print("\n🎉 Le pipeline fonctionne en direct!")
            print("   → Le problème vient de l'API web, pas du pipeline")
        else:
            print("\n❌ Le pipeline a des erreurs internes")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
