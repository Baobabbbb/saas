"""
Test du Pipeline d'Animation Intégré CrewAI
Test end-to-end du système de génération d'animation narrative
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.integrated_animation_service import integrated_animation_service

async def test_simple_story():
    """Test avec une histoire simple"""
    
    print("🧪 === TEST PIPELINE ANIMATION CRÉAWAI ===")
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    # Histoire de test
    test_story = """
    Il était une fois un petit chat orange nommé Minou qui vivait dans une maison bleue.
    Un jour, Minou découvrit un jardin secret rempli de fleurs colorées et de papillons magiques.
    Il joua avec les papillons sous le soleil doré.
    Puis il rentra chez lui, heureux de sa belle aventure.
    """
    
    # Préférences de style
    style_preferences = {
        "style": "cartoon coloré et mignon",
        "mood": "joyeux et doux",
        "target_age": "3-6 ans",
        "colors": "couleurs vives et chaleureuses"
    }
    
    print(f"📖 Histoire de test:")
    print(f"   {test_story.strip()}")
    print(f"🎨 Style: {style_preferences}")
    print()
    
    try:
        # Lancer la génération complète
        result = await integrated_animation_service.generate_complete_animation(
            story_text=test_story.strip(),
            style_preferences=style_preferences
        )
        
        print("\n🎬 === RÉSULTATS ===")
        
        if result.get('status') == 'success':
            print("✅ Génération réussie !")
            print(f"🎥 Vidéo: {result.get('video_path')}")
            print(f"📊 Scènes: {result.get('scenes_count')}")
            print(f"⏱️  Durée: {result.get('total_duration')}s")
            print(f"🕒 Temps génération: {result.get('generation_time')}s")
            
            if result.get('scenes_details'):
                print("\n📋 Détails des scènes:")
                for scene in result.get('scenes_details', []):
                    print(f"  Scène {scene['scene_number']}: {scene['description'][:50]}... ({scene['duration']}s)")
            
        else:
            print("❌ Génération échouée")
            print(f"Erreur: {result.get('error')}")
            
        return result
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

async def test_agents_only():
    """Test uniquement la partie agents CrewAI (sans génération vidéo)"""
    
    print("\n🧪 === TEST AGENTS CREWAI SEULEMENT ===")
    
    # Tester la création des agents
    try:
        agents = integrated_animation_service.create_agents()
        print(f"✅ {len(agents)} agents créés:")
        for name, agent in agents.items():
            print(f"  - {name}: {agent.role}")
        
        # Tester la création des tâches
        test_story = "Un petit oiseau apprend à voler dans un jardin fleuri."
        style_prefs = {"style": "cartoon", "mood": "joyeux"}
        
        tasks = integrated_animation_service.create_tasks(test_story, style_prefs, agents)
        print(f"✅ {len(tasks)} tâches créées:")
        for i, task in enumerate(tasks):
            print(f"  - Tâche {i+1}: {task.agent.role}")
        
        return {"status": "success", "agents": len(agents), "tasks": len(tasks)}
        
    except Exception as e:
        print(f"❌ Erreur test agents: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

async def test_api_simulation():
    """Test de l'API Runway en mode simulation"""
    
    print("\n🧪 === TEST API RUNWAY SIMULATION ===")
    
    try:
        # Test appel API en mode simulation
        result = await integrated_animation_service.call_runway_api(
            "cute cartoon cat playing in colorful garden",
            duration=5
        )
        
        print(f"✅ Appel API simulé réussi:")
        print(f"  ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  URL: {result.get('video_url')}")
        print(f"  Durée: {result.get('duration')}s")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return {"status": "error", "error": str(e)}

async def main():
    """Test principal"""
    
    print("🚀 DÉBUT DES TESTS PIPELINE ANIMATION")
    print("=" * 50)
    
    # Test 1: Agents seulement
    print("\n1️⃣ Test création agents et tâches...")
    agents_result = await test_agents_only()
    
    # Test 2: API simulation
    print("\n2️⃣ Test API Runway simulation...")
    api_result = await test_api_simulation()
    
    # Test 3: Pipeline complet (mode test)
    print("\n3️⃣ Test pipeline complet...")
    story_result = await test_simple_story()
    
    # Résumé
    print("\n🎯 === RÉSUMÉ DES TESTS ===")
    print(f"Agents: {'✅' if agents_result.get('status') == 'success' else '❌'}")
    print(f"API: {'✅' if api_result.get('status') == 'success' else '❌'}")
    print(f"Pipeline: {'✅' if story_result.get('status') == 'success' else '❌'}")
    
    print(f"\n⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
