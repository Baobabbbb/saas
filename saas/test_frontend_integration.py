#!/usr/bin/env python3
"""
Test end-to-end de l'interface frontend améliorée
"""
import asyncio
import aiohttp
import json
from pathlib import Path

async def test_frontend_integration():
    """Test complet de l'intégration frontend-backend"""
    
    print("🎬 Test d'intégration Frontend-Backend")
    print("=" * 50)
    
    # URL de l'API
    base_url = "http://127.0.0.1:8000"
    
    # Cas de test avec les nouveaux paramètres
    test_cases = [
        {
            "name": "Test Cartoon + Magie",
            "data": {
                "story": "Un petit chat orange découvre un jardin magique où les fleurs chantent des mélodies douces et les papillons dansent dans les rayons de soleil.",
                "style_preferences": {
                    "style": "cartoon",
                    "theme": "magic", 
                    "mood": "joyful",
                    "target_age": "3-8 ans"
                }
            }
        },
        {
            "name": "Test Anime + Espace",
            "data": {
                "story": "Luna, une jeune exploratrice, voyage vers une planète lointaine peuplée de créatures lumineuses qui lui enseignent les secrets de l'univers.",
                "style_preferences": {
                    "style": "anime",
                    "theme": "space",
                    "mood": "adventurous", 
                    "target_age": "3-8 ans"
                }
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['name']}")
            print("-" * 30)
            
            try:
                # Test de l'endpoint generate-story
                url = f"{base_url}/api/animations/generate-story"
                
                async with session.post(url, json=test_case["data"]) as response:
                    print(f"📡 Status HTTP: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Statut: {result.get('status', 'unknown')}")
                        print(f"📹 Scènes générées: {result.get('scenes_count', 0)}")
                        print(f"⏱️  Temps de génération: {result.get('generation_time', 0):.2f}s")
                        
                        if result.get('video_url'):
                            print(f"🎬 Vidéo disponible: {result['video_url']}")
                        
                        # Vérifier les détails des scènes
                        scenes = result.get('scenes_details', [])
                        for j, scene in enumerate(scenes):
                            status = scene.get('status', 'unknown')
                            print(f"   Scène {j+1}: {status}")
                            
                    else:
                        error_data = await response.json()
                        print(f"❌ Erreur: {error_data}")
                        
            except Exception as e:
                print(f"💥 Exception: {str(e)}")
    
    # Test de l'endpoint test-crewai
    print(f"\n🔬 Test du pipeline CrewAI")
    print("-" * 30)
    
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{base_url}/api/animations/test-crewai"
            test_data = {
                "story": "Un petit robot aide ses amis à résoudre une énigme dans la ville du futur."
            }
            
            async with session.post(url, json=test_data) as response:
                print(f"📡 Status HTTP: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Test CrewAI: {result.get('status', 'unknown')}")
                    
                    if 'result' in result:
                        crew_result = result['result']
                        print(f"👥 Agents: {crew_result.get('agents_count', 0)}")
                        print(f"📋 Tâches: {crew_result.get('tasks_count', 0)}")
                        print(f"⏱️  Temps: {crew_result.get('execution_time', 0):.2f}s")
                else:
                    error_data = await response.json()
                    print(f"❌ Erreur test CrewAI: {error_data}")
                    
        except Exception as e:
            print(f"💥 Exception test CrewAI: {str(e)}")
    
    print(f"\n🏁 Tests d'intégration terminés")

if __name__ == "__main__":
    asyncio.run(test_frontend_integration())
