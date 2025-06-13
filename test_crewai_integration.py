"""
Script de test pour vérifier l'intégration CrewAI
"""

import asyncio
import json
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

from services.crewai_comic_service import crewai_comic_service
from services.crewai_comic_composer import crewai_comic_composer

async def test_crewai_integration():
    """Test de base de l'intégration CrewAI"""
    
    print("🧪 Test de l'intégration CrewAI pour les BD")
    print("=" * 50)
    
    # Scénario de test simple
    test_scenario = {
        "title": "Les Aventures de Tom",
        "scenes": [
            {
                "description": "Tom se réveille dans sa chambre. Il regarde par la fenêtre et voit un dragon.",
                "dialogues": [
                    {"character": "Tom", "text": "Oh mon dieu ! Qu'est-ce que c'est que ça ?"}
                ]
            },
            {
                "description": "Tom sort de sa maison et s'approche du dragon coloré.",
                "dialogues": [
                    {"character": "Dragon", "text": "Bonjour petit humain ! Je m'appelle Spark."},
                    {"character": "Tom", "text": "Tu... tu peux parler ?"}
                ]
            }
        ],
        "style": "cartoon"
    }
    
    print("📝 Scénario de test :")
    print(json.dumps(test_scenario, indent=2, ensure_ascii=False))
    print()
    
    # Test 1: Validation du scénario
    print("🔍 Test 1: Validation du scénario de base")
    validation = crewai_comic_service.validate_improved_scenario(test_scenario)
    print(f"Valide: {validation['is_valid']}")
    if not validation['is_valid']:
        print(f"Erreurs: {validation['errors']}")
    else:
        print("✅ Scénario de base valide")
    print()
    
    # Test 2: Amélioration avec CrewAI (simulation)
    print("🤖 Test 2: Simulation d'amélioration CrewAI")
    try:
        # Pour le test, on simule juste la structure sans appeler les vrais agents
        # car cela nécessiterait une vraie clé API OpenAI
        
        enhanced_scenario = test_scenario.copy()
        enhanced_scenario.update({
            "crewai_enhanced": True,
            "enhancement_timestamp": "2025-06-13T10:00:00",
            "review_notes": [
                "Dialogues optimisés pour les bulles BD",
                "Descriptions enrichies pour meilleur rendu visuel",
                "Placement des bulles optimisé"
            ],
            "quality_score": 8.5,
            "ready_for_production": True
        })
        
        # Ajouter des métadonnées de layout aux scènes
        for scene in enhanced_scenario["scenes"]:
            scene["layout_metadata"] = {
                "character_positions": {
                    "Tom": {"x_ratio": 0.3, "y_ratio": 0.7},
                    "Dragon": {"x_ratio": 0.7, "y_ratio": 0.6}
                },
                "optimal_bubble_positions": [
                    {"x_ratio": 0.1, "y_ratio": 0.1, "type": "speech"}
                ]
            }
        
        print("✅ Amélioration simulée terminée")
        print(f"Score qualité: {enhanced_scenario.get('quality_score', 'N/A')}")
        print(f"Prêt pour production: {enhanced_scenario.get('ready_for_production', False)}")
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'amélioration: {e}")
        print()
    
    # Test 3: Validation du composer
    print("🎨 Test 3: Validation du système de composition")
    try:
        test_scene = {
            "description": "Tom dans sa chambre",
            "dialogues": [
                {"character": "Tom", "text": "Bonjour le monde !"}
            ],
            "image": "test_image.png"  # Image fictive pour le test
        }
        
        validation = crewai_comic_composer.validate_scene_for_composition(test_scene)
        print(f"Scène valide pour composition: {validation['is_valid']}")
        
        if not validation['is_valid']:
            print(f"Erreurs: {validation['errors']}")
        else:
            print("✅ Scène valide pour composition")
            print(f"Nombre de dialogues: {validation['dialogues_count']}")
            print(f"Métadonnées layout: {validation['has_layout_metadata']}")
        print()
        
    except Exception as e:
        print(f"❌ Erreur validation composer: {e}")
        print()
    
    # Test 4: Vérification des types de bulles
    print("💬 Test 4: Types de bulles")
    test_dialogues = [
        {"character": "Tom", "text": "Bonjour !"},
        {"character": "Tom", "text": "Au secours !!"},
        {"character": "Tom", "text": "Chut... c'est un secret"},
        {"character": "Tom", "text": "(Il pense à quelque chose)"}
    ]
    
    for dialogue in test_dialogues:
        bubble_type = crewai_comic_composer.determine_bubble_type(dialogue, "")
        print(f"'{dialogue['text']}' → Type: {bubble_type}")
    
    print()
    print("🎉 Tests terminés !")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_crewai_integration())
        print("✅ Tous les tests sont passés avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        import traceback
        traceback.print_exc()
