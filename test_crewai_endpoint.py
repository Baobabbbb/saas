#!/usr/bin/env python3
"""
Test simple de l'endpoint CrewAI
"""

import requests
import json

def test_crewai_endpoint():
    url = "http://localhost:8000/api/animations/generate-cohesive"
    
    payload = {
        "story": "Une petite souris courageuse découvre un fromage magique dans une grotte mystérieuse.",
        "style": "cartoon",
        "theme": "custom", 
        "mode": "fast",
        "duration": 30,
        "orientation": "landscape"
    }
    
    print("🧪 Test endpoint CrewAI...")
    print(f"📍 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès !")
            print(f"📹 Résultat: {json.dumps(result, indent=2)}")
        else:
            print("❌ Erreur:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur connexion: {e}")

if __name__ == "__main__":
    test_crewai_endpoint()
