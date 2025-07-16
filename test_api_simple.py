#!/usr/bin/env python3
"""
🔍 Test simple de l'API pour voir l'erreur exacte
"""

import requests
import json

def test_api_simple():
    """Test simple avec gestion d'erreur"""
    
    payload = {
        "story": "Un petit chat",
        "duration": 30,
        "style": "cartoon",
        "mode": "demo"
    }
    
    try:
        print("📤 Test API...")
        response = requests.post(
            "http://localhost:8000/generate_animation/",
            json=payload,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ Erreur!")
            print(f"Text: {response.text}")
            
            # Essayer de parser le JSON d'erreur
            try:
                error_data = response.json()
                print(f"Détails erreur: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("Impossible de parser l'erreur JSON")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api_simple()
