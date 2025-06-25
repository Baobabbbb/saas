#!/usr/bin/env python3
"""
Test des paramètres frontend compatibles Stable Diffusion/Runway
"""
import asyncio
import json
import aiohttp
from pathlib import Path
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from services.crewai_animation import CrewAIAnimationService

async def test_frontend_parameters():
    """Test que tous les paramètres frontend sont compatibles"""
    
    print("🎬 Test des paramètres frontend compatibles Stable Diffusion/Runway")
    print("=" * 60)
    
    # Paramètres de test basés sur le frontend
    test_cases = [
        {
            "name": "Cartoon + Aventure + Joyeux",
            "story": "Un petit chat orange explore un jardin magique rempli de fleurs colorées.",
            "style": "cartoon",
            "theme": "adventure", 
            "mood": "joyful"
        },
        {
            "name": "Anime + Espace + Magique",
            "story": "Luna voyage vers une planète mystérieuse peuplée de créatures lumineuses.",
            "style": "anime",
            "theme": "space",
            "mood": "magical"
        },
        {
            "name": "Aquarelle + Forêt + Paisible",
            "story": "Une petite fée aide les animaux de la forêt enchantée à retrouver leur chemin.",
            "style": "watercolor",
            "theme": "forest",
            "mood": "peaceful"
        },
        {
            "name": "Pixel Art + Ville + Ludique",
            "story": "Un robot coloré aide les habitants de la ville futuriste à résoudre des énigmes.",
            "style": "pixel_art",
            "theme": "city",
            "mood": "playful"
        },
        {
            "name": "Pâte à modeler + Animaux + Aventureux",
            "story": "Un groupe d'animaux part en expédition pour découvrir un trésor caché.",
            "style": "claymation",
            "theme": "animals",
            "mood": "adventurous"
        }
    ]
    
    # Initialiser le service CrewAI
    service = CrewAIAnimationService()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎭 Test {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Créer les paramètres de style
            style_preferences = {
                "style": test_case["style"],
                "theme": test_case["theme"], 
                "mood": test_case["mood"],
                "target_age": "3-8 ans"
            }
            
            print(f"📝 Histoire: {test_case['story'][:50]}...")
            print(f"🎨 Style: {style_preferences['style']}")
            print(f"🌍 Thème: {style_preferences['theme']}")
            print(f"😊 Ambiance: {style_preferences['mood']}")
            
            # Test de la génération des prompts
            result = await service.generate_crew_animation(
                story=test_case["story"],
                style_preferences=style_preferences
            )
            
            if result.get("status") == "success":
                print("✅ Paramètres validés avec succès")
                
                # Vérifier que les paramètres sont présents dans les prompts
                scenes = result.get("scenes", [])
                prompts_valid = True
                
                for scene in scenes:
                    prompt = scene.get("prompt", "").lower()
                    if not any(keyword in prompt for keyword in [
                        test_case["style"], 
                        test_case["theme"], 
                        test_case["mood"]
                    ]):
                        prompts_valid = False
                        break
                
                if prompts_valid:
                    print("✅ Prompts générés correctement avec les paramètres")
                else:
                    print("⚠️  Paramètres partiellement intégrés dans les prompts")
                    
                results.append({
                    "test": test_case["name"],
                    "status": "success",
                    "scenes_count": len(scenes),
                    "prompts_valid": prompts_valid
                })
                
            else:
                print(f"❌ Échec: {result.get('error', 'Erreur inconnue')}")
                results.append({
                    "test": test_case["name"],
                    "status": "failed",
                    "error": result.get('error', 'Erreur inconnue')
                })
                
        except Exception as e:
            print(f"❌ Erreur d'exécution: {str(e)}")
            results.append({
                "test": test_case["name"],
                "status": "error",
                "error": str(e)
            })
    
    # Résumé des résultats
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    success_count = len([r for r in results if r["status"] == "success"])
    total_count = len(results)
    
    print(f"✅ Tests réussis: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 Tous les paramètres frontend sont compatibles avec Stable Diffusion/Runway!")
    else:
        print("⚠️  Certains paramètres nécessitent des ajustements")
        
        # Afficher les échecs
        for result in results:
            if result["status"] != "success":
                print(f"❌ {result['test']}: {result.get('error', 'Échec')}")
    
    # Sauvegarder les résultats
    with open("test_frontend_parameters_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés dans test_frontend_parameters_results.json")
    
    return success_count == total_count

async def main():
    """Fonction principale"""
    try:
        success = await test_frontend_parameters()
        exit_code = 0 if success else 1
        
        print(f"\n🏁 Test terminé avec le code de sortie: {exit_code}")
        return exit_code
        
    except Exception as e:
        print(f"\n💥 Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
