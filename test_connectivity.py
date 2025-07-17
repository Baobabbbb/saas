#!/usr/bin/env python3
"""
Script de test de connectivité API - simule ce que fait le frontend
"""

import asyncio
import aiohttp
import json

async def test_backend_connectivity():
    """Test la connectivité avec le backend comme le ferait le frontend"""
    print("🌐 Test de connectivité Backend/Frontend")
    print("=" * 50)
    
    base_url = "http://localhost:8004"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Diagnostic API
            print("1. 🔍 Test diagnostic des clés API...")
            async with session.get(f"{base_url}/diagnostic") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Diagnostic: {response.status}")
                    print(f"   OpenAI: {'✅' if data.get('openai_configured') else '❌'}")
                    print(f"   Stability: {'✅' if data.get('stability_configured') else '❌'}")
                    print(f"   FAL: {'✅' if data.get('fal_configured') else '❌'}")
                else:
                    print(f"   ❌ Erreur diagnostic: {response.status}")
                    return False
            
            # Test 2: Génération d'histoire
            print("\n2. 📚 Test génération d'histoire...")
            story_data = {
                "theme": "space",
                "age_target": "3-6 ans", 
                "custom_request": "avec des robots sympathiques"
            }
            async with session.post(
                f"{base_url}/generate-story",
                json=story_data
            ) as response:
                if response.status == 200:
                    story_result = await response.json()
                    print(f"   ✅ Histoire générée: {response.status}")
                    print(f"   Contenu: {story_result.get('story', '')[:100]}...")
                else:
                    print(f"   ❌ Erreur histoire: {response.status}")
                    error_text = await response.text()
                    print(f"   Détails: {error_text[:200]}...")
                    return False
            
            # Test 3: Animation SEEDANCE (test court)
            print("\n3. 🎬 Test animation SEEDANCE...")
            animation_data = {
                "story": story_result.get('story', 'Une histoire spatiale avec des robots'),
                "theme": "space",
                "age_target": "3-6 ans",
                "duration": 15,  # Court pour le test
                "style": "cartoon",
                "pipeline": "seedance"
            }
            
            print("   📡 Envoi de la requête d'animation...")
            async with session.post(
                f"{base_url}/generate",
                json=animation_data,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes max
            ) as response:
                if response.status == 200:
                    animation_result = await response.json()
                    if animation_result.get('status') == 'success':
                        print(f"   ✅ Animation générée: {response.status}")
                        print(f"   ID: {animation_result.get('animation_id')}")
                        print(f"   URL: {animation_result.get('video_url')}")
                        print(f"   Durée: {animation_result.get('actual_duration')}s")
                        print(f"   Temps: {animation_result.get('generation_time')}s")
                    else:
                        print(f"   ⚠️ Animation échouée: {animation_result.get('error', 'Erreur inconnue')}")
                        print(f"   Type: {animation_result.get('error_type', 'Inconnu')}")
                        print(f"   Solution: {animation_result.get('solution', 'Aucune')}")
                        return False
                else:
                    print(f"   ❌ Erreur requête: {response.status}")
                    error_text = await response.text()
                    print(f"   Détails: {error_text[:300]}...")
                    return False
            
            print("\n✅ Tous les tests de connectivité réussis!")
            return True
            
    except aiohttp.ClientError as e:
        print(f"❌ Erreur de connexion: {e}")
        print("   🔧 Vérifiez que le backend est démarré sur http://localhost:8004")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de connectivité API Backend/Frontend")
    print("\n⚠️ Assurez-vous que le backend est démarré avant de lancer ce test!")
    print("   Commande: cd saas/saas && python -m uvicorn main:app --host 0.0.0.0 --port 8004")
    
    input("\nAppuyez sur Entrée pour continuer...")
    
    success = asyncio.run(test_backend_connectivity())
    
    if success:
        print("\n🎉 Connectivité parfaite! Le frontend devrait fonctionner correctement.")
    else:
        print("\n⚠️ Problèmes détectés. Corrigez les erreurs avant d'utiliser le frontend.")
