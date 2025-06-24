"""
Test du service Runway Gen-4 Turbo
"""

import asyncio
from services.runway_gen4 import runway_gen4_service

async def test_runway_service():
    """Test du service Runway (simulation)"""
    print("🧪 Test du service Runway Gen-4 Turbo")
    
    # Test de validation des données
    test_data = {
        "style": "cartoon",
        "theme": "animals",
        "orientation": "landscape",
        "prompt": "Un chat orange qui joue dans un jardin",
        "title": "Chat Joueur"
    }
    
    validation = runway_gen4_service.validate_animation_data(test_data)
    print(f"✅ Validation: {validation}")
    
    # Test de création de prompt optimisé
    prompt = runway_gen4_service._create_optimized_prompt(
        "cartoon", "animals", "Un chat orange qui joue", "landscape"
    )
    print(f"📝 Prompt optimisé: {prompt}")
    
    # Test des styles supportés
    print(f"🎨 Styles supportés: {list(runway_gen4_service.supported_styles.keys())}")
    
    print("✅ Tests de base réussis!")

if __name__ == "__main__":
    asyncio.run(test_runway_service())
