"""
Test de santé pour le service CrewAI V3 - Vérification rapide
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Ajouter le chemin pour importer les modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

from services.crewai_comic_complete_v3 import CrewAIComicCompleteV3, ComicSpecification

async def test_crewai_v3_health():
    """Test de sanité rapide pour CrewAI V3"""
    
    print("🏥 TEST DE SANTÉ CREWAI V3")
    print("=" * 40)
    
    # Test avec différents paramètres
    test_cases = [
        {
            "style": "manga",
            "hero_name": "Luna",
            "story_type": "adventure",
            "custom_request": "A magical adventure",
            "num_images": 2
        },
        {
            "style": "cartoon",
            "hero_name": "Max",
            "story_type": "comedy",
            "custom_request": "A funny story",
            "num_images": 1
        }
    ]
    
    service = CrewAIComicCompleteV3()
    success_count = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {test_case['hero_name']} - {test_case['story_type']}")
        
        try:
            # Créer les spécifications
            spec = ComicSpecification(**test_case)
            
            # Tester la génération (courte)
            print(f"   📋 Specs: ✅")
            print(f"   🎯 Style: {spec.style}")
            print(f"   👤 Héros: {spec.hero_name}")
            print(f"   📖 Type: {spec.story_type}")
            print(f"   🖼️ Images: {spec.num_images}")
            
            # Test de création d'équipe (sans exécution complète pour rapidité)
            crew = service.create_comic_crew()
            print(f"   🎭 Crew: ✅ ({len(crew.agents)} agents)")
            
            success_count += 1
            print(f"   ✅ Test {i+1} : SUCCÈS")
            
        except Exception as e:
            print(f"   ❌ Test {i+1} : ÉCHEC - {e}")
    
    print(f"\n📊 RÉSULTATS:")
    print(f"   Tests réussis: {success_count}/{len(test_cases)}")
    
    if success_count == len(test_cases):
        print("   🎉 TOUS LES TESTS DE SANTÉ SONT OK!")
        return True
    else:
        print("   ⚠️ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_crewai_v3_health())
    print(f"\n{'✅ SERVICE EN BONNE SANTÉ' if result else '❌ SERVICE DÉFAILLANT'}")
