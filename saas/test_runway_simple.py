"""
Test rapide du service Runway simplifié
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour importer les services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.runway_simple import runway_simple_service

async def test_simple_generation():
    """Test de génération simple"""
    
    print("🧪 Test du service Runway simplifié")
    
    # Données de test minimales
    test_data = {
        "style": "cartoon",
        "theme": "adventure", 
        "orientation": "landscape",
        "prompt": "héros aventurier dans une forêt magique",
        "title": "Test Animation"
    }
    
    try:
        print("⏳ Lancement de la génération de test...")
        result = await runway_simple_service.generate_animation(test_data)
        
        print("✅ Test réussi !")
        print(f"📊 Résultat: {result}")
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        import traceback
        print(f"📊 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_simple_generation())
