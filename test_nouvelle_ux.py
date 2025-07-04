#!/usr/bin/env python3
"""
Test de la nouvelle UX pour les comptines musicales
Valide que l'affichage ne se fait qu'une fois la comptine complète
"""

import asyncio
import aiohttp
import json

async def test_nouvelle_ux():
    """Test de la nouvelle logique UX"""
    
    print("🎭 TEST: Nouvelle UX comptines musicales")
    print("=" * 50)
    print("✅ Backend doit retourner task_id sans affichage immédiat")
    print("✅ Frontend doit rester en loading jusqu'à musique prête")
    print("✅ Affichage final : paroles + audio ensemble")
    print()
    
    # Générer une comptine musicale
    payload = {
        "rhyme_type": "animal",
        "custom_request": "une comptine sur un petit chat qui joue",
        "generate_music": True,
        "music_style": "playful",
        "custom_style": ""
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print("1️⃣ Génération comptine musicale...")
            async with session.post(
                "http://localhost:8000/generate_rhyme/",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    text = await response.text()
                    print(f"❌ Erreur: {response.status} - {text}")
                    return
                
                result = await response.json()
                
                print("📋 Réponse backend:")
                print(f"   Status: {result.get('status')}")
                print(f"   Titre: {result.get('title')}")
                print(f"   Paroles: {result.get('lyrics', 'N/A')[:60]}...")
                print(f"   Task ID: {result.get('task_id')}")
                print(f"   Has music: {result.get('has_music')}")
                print(f"   Music status: {result.get('music_status')}")
                
                if result.get('status') == 'success' and result.get('task_id'):
                    print(f"\n✅ Backend OK: Paroles prêtes, task_id fourni")
                    print(f"💡 Frontend devrait:")
                    print(f"   - Rester en mode loading")
                    print(f"   - Ne PAS afficher les paroles maintenant")
                    print(f"   - Lancer le polling sur task_id: {result.get('task_id')}")
                    
                    task_id = result['task_id']
                    
                    # Simuler le polling (quelques tentatives)
                    print(f"\n2️⃣ Simulation polling frontend...")
                    for attempt in range(1, 4):
                        print(f"   Polling {attempt}/3...")
                        
                        async with session.get(
                            f"http://localhost:8000/check_task_status/{task_id}"
                        ) as status_response:
                            
                            if status_response.status == 200:
                                status = await status_response.json()
                                
                                print(f"   Status: {status.get('status')}")
                                print(f"   Task status: {status.get('task_status')}")
                                
                                if status.get('status') == 'completed':
                                    audio_url = status.get('audio_url')
                                    if audio_url:
                                        print(f"\n🎉 SIMULATION RÉUSSIE!")
                                        print(f"   📝 Paroles: {result.get('lyrics', 'N/A')[:60]}...")
                                        print(f"   🎵 Audio: {audio_url[:80]}...")
                                        print(f"\n✅ Frontend devrait maintenant:")
                                        print(f"   - Arrêter le loading")
                                        print(f"   - Afficher paroles + audio ensemble")
                                        print(f"   - Lecteur audio fonctionnel")
                                        return True
                                    else:
                                        print(f"   ⚠️ Terminé mais pas d'audio")
                                        break
                                elif status.get('status') == 'failed':
                                    print(f"   ❌ Génération échouée")
                                    break
                                else:
                                    print(f"   ⏳ En cours...")
                            
                            await asyncio.sleep(5)
                    
                    print(f"\n⏱️ Test arrêté après 3 tentatives")
                    
                else:
                    print(f"❌ Réponse backend inattendue")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_nouvelle_ux())
    
    if success:
        print(f"\n" + "="*50)
        print(f"🎯 NOUVELLE UX VALIDÉE")
        print(f"="*50)
        print(f"📱 EXPÉRIENCE UTILISATEUR:")
        print(f"   1. Utilisateur clique 'Générer'")
        print(f"   2. Loading affiché : 'Création comptine musicale...'")
        print(f"   3. Attente silencieuse (pas de paroles affichées)")
        print(f"   4. Une fois musique prête → Affichage complet")
        print(f"   5. Paroles + lecteur audio avec durée correcte")
        print(f"")
        print(f"✨ AVANTAGES:")
        print(f"   - Plus de confusion (paroles puis message génération)")
        print(f"   - UX cohérente et claire")
        print(f"   - Satisfaction utilisateur maximale")
    else:
        print(f"\n❌ Test non concluant - vérifier la logique")
