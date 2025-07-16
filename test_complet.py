#!/usr/bin/env python3
"""
🧪 Test complet de toutes les fonctionnalités
"""

import requests
import json
import time

def test_all_features():
    """Test de toutes les fonctionnalités du serveur complet"""
    
    base_url = "http://localhost:8003"
    
    print("🧪 TEST COMPLET DE TOUTES LES FONCTIONNALITÉS")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n🏥 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health OK - Version: {data.get('version')}")
            print(f"   Features: {data.get('features_status')}")
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False
    
    # Test 2: Génération d'histoire
    print("\n📖 Test 2: Génération d'Histoire")
    try:
        payload = {
            "story_type": "dragon gentil",
            "voice": "grand-pere",
            "custom_request": "Une histoire courte avec une leçon"
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/generate_story/", json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ Histoire générée en {elapsed:.1f}s")
                print(f"   Titre: {data.get('title', 'N/A')}")
                print(f"   Longueur: {len(data.get('story', ''))} caractères")
            else:
                print(f"❌ Erreur histoire: {data.get('error')}")
                return False
        else:
            print(f"❌ Histoire failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Histoire error: {e}")
        return False
    
    # Test 3: Génération d'animation
    print("\n🎬 Test 3: Génération d'Animation")
    try:
        payload = {
            "story": "Un petit oiseau apprend à voler dans un ciel bleu",
            "duration": 20,
            "mode": "demo",
            "style": "cartoon"
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/generate_animation/", json=payload, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ Animation générée en {elapsed:.1f}s")
                print(f"   Scènes: {len(data.get('scenes', []))}")
                print(f"   Clips: {len(data.get('clips', []))}")
            else:
                print(f"❌ Erreur animation: {data.get('error')}")
                return False
        else:
            print(f"❌ Animation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Animation error: {e}")
        return False
    
    # Test 4: Génération de comptine
    print("\n🎵 Test 4: Génération de Comptine")
    try:
        payload = {
            "rhyme_type": "petite souris",
            "generate_music": True,
            "custom_request": "Quelque chose de mignon"
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/generate_rhyme/", json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ Comptine générée en {elapsed:.1f}s")
                print(f"   Titre: {data.get('title', 'N/A')}")
                print(f"   Musique: {data.get('music_status', 'N/A')}")
            else:
                print(f"❌ Erreur comptine: {data.get('error')}")
                return False
        else:
            print(f"❌ Comptine failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Comptine error: {e}")
        return False
    
    # Test 5: Génération de coloriage
    print("\n🎨 Test 5: Génération de Coloriage")
    try:
        payload = {
            "theme": "jardin fleuri",
            "difficulty": "facile",
            "custom_request": "Avec des papillons"
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/generate_coloring/", json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ Coloriage généré en {elapsed:.1f}s")
                print(f"   Titre: {data.get('title', 'N/A')}")
                print(f"   Difficulté: {data.get('difficulty')}")
            else:
                print(f"❌ Erreur coloriage: {data.get('error')}")
                return False
        else:
            print(f"❌ Coloriage failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Coloriage error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS RÉUSSIS !")
    print("✅ Histoires: Fonctionnel")
    print("✅ Animations: Fonctionnel") 
    print("✅ Comptines: Fonctionnel")
    print("✅ Coloriages: Fonctionnel")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_all_features()
