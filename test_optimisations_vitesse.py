#!/usr/bin/env python3
"""
Test des optimisations de vitesse pour les comptines musicales
"""

import requests
import json
import time

def test_fast_mode():
    """Test du mode rapide vs mode complet"""
    
    print("🚀 === Test des optimisations de vitesse ===")
    
    # Test 1: Mode rapide
    print("\n⚡ Test 1: Mode RAPIDE")
    fast_payload = {
        'rhyme_type': 'animal',
        'custom_request': 'comptine sur les chats',
        'generate_music': True,
        'custom_style': 'simple et rapide',
        'fast_mode': True
    }
    
    start_time = time.time()
    try:
        response = requests.post('http://localhost:8000/generate_rhyme/', json=fast_payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            generation_time = time.time() - start_time
            
            print(f"✅ Génération réussie en {generation_time:.2f}s")
            print(f"📝 Titre: {data.get('title')}")
            print(f"📏 Longueur des paroles: {len(data.get('lyrics', '').split())} mots")
            print(f"🎵 Task ID: {data.get('task_id')}")
            
            # Test rapide du polling (2 tentatives)
            task_id = data.get('task_id')
            if task_id:
                print("\\n🔄 Test polling rapide...")
                for i in range(2):
                    poll_response = requests.get(f'http://localhost:8000/check_task_status/{task_id}')
                    if poll_response.status_code == 200:
                        poll_data = poll_response.json()
                        print(f"   Poll {i+1}: {poll_data.get('status')} ({poll_data.get('task_status')})")
                        time.sleep(3)
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur mode rapide: {e}")
    
    # Test 2: Mode complet (pour comparaison)
    print("\\n🎭 Test 2: Mode COMPLET")
    complete_payload = {
        'rhyme_type': 'animal',
        'custom_request': 'comptine sur les chats',
        'generate_music': True,
        'custom_style': 'élaboré et détaillé',
        'fast_mode': False
    }
    
    start_time = time.time()
    try:
        response = requests.post('http://localhost:8000/generate_rhyme/', json=complete_payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            generation_time = time.time() - start_time
            
            print(f"✅ Génération réussie en {generation_time:.2f}s")
            print(f"📝 Titre: {data.get('title')}")
            print(f"📏 Longueur des paroles: {len(data.get('lyrics', '').split())} mots")
            print(f"🎵 Task ID: {data.get('task_id')}")
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur mode complet: {e}")
    
    print("\\n🔧 Optimisations implémentées:")
    print("   ⚡ Mode rapide: Paroles plus courtes, tokens réduits")
    print("   🎵 GoAPI optimisé: Durée courte, qualité 'fast'")
    print("   🔄 Polling: Intervalle réduit de 8s → 6s")
    print("   🎯 Styles simplifiés: Moins de complexité")
    print("   📱 Interface: Toggle mode rapide/complet")

if __name__ == "__main__":
    test_fast_mode()
