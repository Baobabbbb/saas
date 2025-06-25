"""
Test du service Runway Story pour vrais dessins animés
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour importer les services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.runway_story import runway_story_service

async def test_story_generation():
    """Test de génération de vrai dessin animé narratif"""
    
    print("🎬 Test du service Runway Story - Vrais dessins animés")
    
    # Données de test pour un vrai dessin animé
    test_data = {
        "style": "cartoon",
        "theme": "adventure", 
        "orientation": "landscape",
        "prompt": "Un jeune héros courageux part à l'aventure dans une forêt magique pour sauver ses amis",
        "title": "La Grande Aventure"
    }
    
    try:
        print("⏳ Lancement de la génération de dessin animé narratif...")
        result = await runway_story_service.generate_animation(test_data)
        
        print("✅ Dessin animé généré avec succès !")
        print(f"🎬 Titre: {result['title']}")
        print(f"📖 Histoire: {result['story'][:200]}...")
        print(f"🎥 Vidéo: {result['video_url']}")
        print(f"⏱️ Durée: {result['duration']} secondes")
        print(f"📚 Type de production: {result['narrative_type']}")
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        import traceback
        print(f"📊 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_story_generation())
