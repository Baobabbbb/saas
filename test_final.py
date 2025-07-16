#!/usr/bin/env python3
"""
🧪 Test final pour identifier le blocage
"""

import requests
import json

def test_api_8001():
    """Test de l'API simplifiée sur le port 8001"""
    
    payload = {
        "story": "Un petit chat découvre un jardin",
        "duration": 20,
        "mode": "demo"
    }
    
    try:
        print("📤 Test API simplifiée...")
        response = requests.post(
            "http://localhost:8002/generate_animation/",
            json=payload,
            timeout=120  # 2 minutes
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            if 'result' in result:
                r = result['result']
                print(f"Scènes: {len(r.get('scenes', []))}")
                print(f"Clips: {len(r.get('clips', []))}")
        else:
            print("❌ Erreur!")
            try:
                error_data = response.json()
                print(f"Erreur: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Text: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api_8001()
