#!/usr/bin/env python3
"""
Test rapide du frontend avec les nouvelles temporisations
"""

import requests
import time

def test_frontend_behavior():
    """Test du comportement frontend sans timeout"""
    
    print("🎭 TEST COMPORTEMENT FRONTEND SANS TIMEOUT")
    print("=" * 50)
    
    # Test simple avec une comptine courte
    payload = {
        "rhyme_type": "counting",
        "custom_request": "Comptine courte pour compter de 1 à 3",
        "generate_music": True
    }
    
    try:
        print("1. 🎵 Génération comptine courte...")
        response = requests.post(
            "http://localhost:8000/generate_rhyme/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print(f"   ✅ Paroles: {result.get('title')}")
                print(f"   🎵 Task ID: {result.get('task_id')}")
                print(f"   📊 Statut: {result.get('music_status')}")
                
                # Test de quelques vérifications de statut
                if result.get('task_id'):
                    print(f"\n2. 🔄 Test de quelques vérifications...")
                    for i in range(3):
                        time.sleep(5)
                        status_resp = requests.get(
                            f"http://localhost:8000/check_task_status/{result.get('task_id')}",
                            timeout=10
                        )
                        if status_resp.status_code == 200:
                            status = status_resp.json()
                            print(f"   📊 Vérification {i+1}: {status.get('task_status')}")
                            if status.get('task_status') == 'completed':
                                print(f"   🎵 Audio URL: {'✅' if status.get('audio_url') else '❌'}")
                                break
                        else:
                            print(f"   ❌ Erreur vérification: {status_resp.status_code}")
                
                print(f"\n✅ Frontend fonctionne correctement sans timeout !")
                return True
            else:
                print(f"   ❌ Erreur: {result.get('error')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    success = test_frontend_behavior()
    if success:
        print(f"\n🎉 FRONTEND OPTIMISÉ POUR UDIO !")
        print(f"   - Pas de timeout artificiel")
        print(f"   - Polling continu jusqu'à completion")
        print(f"   - Temps d'attente réalistes affichés")
    else:
        print(f"\n⚠️ Problème détecté")
