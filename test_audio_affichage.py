#!/usr/bin/env python3
"""
Test de l'affichage audio pour les comptines Udio
Vérifie que l'URL audio complète est bien retournée et utilisable dans le frontend
"""

import asyncio
import aiohttp
import json

async def test_audio_display():
    """Test complet de génération de comptine et affichage audio"""
    
    print("🎵 TEST: Affichage audio des comptines Udio")
    print("=" * 50)
    
    # Étape 1: Générer une comptine musicale
    print("\n1️⃣ Génération d'une comptine musicale...")
    payload = {
        "rhyme_type": "lullaby",
        "custom_request": "une berceuse sur les étoiles",
        "generate_music": True,
        "music_style": "gentle",
        "custom_style": ""
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Appel API pour générer la comptine
            async with session.post(
                "http://localhost:8000/generate_rhyme/",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    text = await response.text()
                    print(f"❌ Erreur génération: {response.status} - {text}")
                    return
                
                result = await response.json()
                print(f"✅ Comptine générée:")
                print(f"   Titre: {result.get('title')}")
                print(f"   Paroles: {result.get('lyrics', 'N/A')[:100]}...")
                print(f"   Task ID: {result.get('task_id')}")
                print(f"   Statut musique: {result.get('music_status')}")
                
                if not result.get('task_id'):
                    print("❌ Pas de task_id, impossible de continuer")
                    return
                
                task_id = result['task_id']
                
                # Étape 2: Polling pour attendre la musique
                print(f"\n2️⃣ Polling pour la musique (task_id: {task_id})...")
                max_attempts = 10  # 100 secondes max pour le test
                
                for attempt in range(1, max_attempts + 1):
                    print(f"   Tentative {attempt}/{max_attempts}...")
                    
                    async with session.get(
                        f"http://localhost:8000/check_task_status/{task_id}"
                    ) as status_response:
                        
                        if status_response.status != 200:
                            print(f"   ⚠️ Erreur statut: {status_response.status}")
                            await asyncio.sleep(10)
                            continue
                        
                        status = await status_response.json()
                        
                        print(f"   Statut: {status.get('status')}")
                        print(f"   Task status: {status.get('task_status')}")
                        
                        # Vérifier si terminé
                        if status.get('status') == 'completed' or status.get('task_status') == 'completed':
                            audio_url = status.get('audio_url') or status.get('audio_path')
                            
                            if audio_url:
                                print(f"✅ Audio prêt!")
                                print(f"   URL: {audio_url}")
                                
                                # Étape 3: Vérifier que l'URL est accessible
                                print(f"\n3️⃣ Vérification de l'accessibilité de l'URL...")
                                
                                async with session.head(audio_url) as head_response:
                                    if head_response.status == 200:
                                        print(f"✅ URL audio accessible (HTTP {head_response.status})")
                                        print(f"   Content-Type: {head_response.headers.get('content-type', 'N/A')}")
                                        print(f"   Content-Length: {head_response.headers.get('content-length', 'N/A')} bytes")
                                        
                                        # Étape 4: Simulation de ce que ferait le frontend
                                        print(f"\n4️⃣ Simulation frontend...")
                                        
                                        # Avant (incorrect)
                                        old_way = f"http://localhost:8000/{audio_url}"
                                        print(f"❌ Ancienne méthode (incorrecte): {old_way}")
                                        
                                        # Après (correct)
                                        new_way = audio_url
                                        print(f"✅ Nouvelle méthode (correcte): {new_way}")
                                        
                                        print(f"\n🎉 TEST RÉUSSI!")
                                        print(f"   - La comptine est générée ✅")
                                        print(f"   - L'URL audio est extraite ✅")
                                        print(f"   - L'URL est accessible ✅") 
                                        print(f"   - Le frontend utilisera l'URL directement ✅")
                                        
                                        return
                                    else:
                                        print(f"❌ URL audio non accessible: HTTP {head_response.status}")
                                        return
                            else:
                                print(f"⚠️ Tâche terminée mais pas d'URL audio")
                                return
                        
                        elif status.get('status') == 'failed':
                            print(f"❌ Génération musicale échouée: {status.get('error')}")
                            return
                        
                        # Continuer le polling
                        await asyncio.sleep(10)
                
                print(f"⏱️ Timeout atteint après {max_attempts} tentatives")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(test_audio_display())
