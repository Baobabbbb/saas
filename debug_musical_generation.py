#!/usr/bin/env python3
"""
Script de débogage pour la génération musicale
Teste directement l'API GoAPI DiffRhythm
"""

import requests
import json
import os
import sys
from pathlib import Path

# Ajouter le chemin du module saas
sys.path.append(str(Path(__file__).parent / "saas"))

from config import GOAPI_API_KEY, DIFFRHYTHM_MODEL, DIFFRHYTHM_TASK_TYPE

def test_goapi_connection():
    """Test de connexion direct à l'API GoAPI"""
    print("🔍 Test de connexion à l'API GoAPI DiffRhythm...")
    print(f"🔑 Clé API: {GOAPI_API_KEY[:10]}...{GOAPI_API_KEY[-10:]}")
    print(f"🤖 Modèle: {DIFFRHYTHM_MODEL}")
    print(f"📋 Type de tâche: {DIFFRHYTHM_TASK_TYPE}")
    
    # URLs possibles à tester
    urls_to_test = [
        "https://api.go-api.ai/api/v1/task/async",
        "https://goapi.ai/api/v1/task/async",
        "https://api.goapi.ai/v1/task/async",
        "https://goapi.xyz/api/v1/task/async"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GOAPI_API_KEY}"
    }
    
    # Payload de test simple
    payload = {
        "model": DIFFRHYTHM_MODEL,
        "task_type": DIFFRHYTHM_TASK_TYPE,
        "input": {
            "text": "Petit chat, petit chat, ferme tes yeux, fais dodo",
            "style": "gentle lullaby, soft and soothing, quiet vocals, peaceful melody"
        }
    }
    
    for url in urls_to_test:
        print(f"\n📤 Test de l'URL: {url}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Succès!")
                print(f"📋 Réponse: {json.dumps(result, indent=2)}")
                
                task_id = result.get('task_id')
                if task_id:
                    print(f"🆔 Task ID reçu: {task_id}")
                    return task_id, url
                    
            elif response.status_code == 401:
                print("❌ Erreur d'authentification (401) - Clé API invalide?")
            elif response.status_code == 404:
                print("❌ Endpoint non trouvé (404)")
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                print(f"📋 Réponse: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ Erreur de connexion - URL inaccessible")
        except requests.exceptions.Timeout:
            print("❌ Timeout")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print("\n❌ Aucune URL ne fonctionne")
    return None, None

def check_task_status(task_id):
    """Vérifier le statut d'une tâche"""
    if not task_id:
        return
        
    print(f"\n🔍 Vérification du statut de la tâche {task_id}...")
    
    url = f"https://api.go-api.ai/api/v1/task/{task_id}"
    headers = {
        "Authorization": f"Bearer {GOAPI_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            print(f"📋 Statut: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"📋 Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_backend_endpoint():
    """Test de l'endpoint backend local"""
    print("\n🧪 Test de l'endpoint backend local...")
    
    payload = {
        "rhyme_type": "lullaby",
        "custom_request": "Une berceuse douce pour un bébé",
        "generate_music": True,
        "language": "fr"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/generate_musical_rhyme/",
            json=payload,
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            print(f"📋 Titre: {result.get('title', 'N/A')}")
            print(f"🎵 A de la musique: {result.get('has_music', False)}")
            print(f"📊 Statut musique: {result.get('music_status', 'N/A')}")
            print(f"🆔 Task ID: {result.get('music_task_id', 'N/A')}")
            if result.get('error'):
                print(f"❌ Erreur: {result['error']}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"📋 Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    print("🚀 DÉBOGAGE GÉNÉRATION MUSICALE")
    print("=" * 50)
    
    # Test 1: Connexion directe à GoAPI
    task_id, working_url = test_goapi_connection()
    
    # Test 2: Vérification du statut si task_id obtenu
    if task_id and working_url:
        import time
        time.sleep(2)  # Petite pause
        check_task_status(task_id)
        print(f"\n✅ URL qui fonctionne: {working_url}")
    
    # Test 3: Test de l'endpoint backend
    test_backend_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")

if __name__ == "__main__":
    main()
