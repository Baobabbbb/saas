#!/usr/bin/env python3
"""
Test d'intégration CrewAI pour vérifier que tout fonctionne.
"""
import requests
import json
import time

def test_crewai_endpoint():
    """Test l'endpoint CrewAI de génération d'animation."""
    url = "http://localhost:8000/api/animations/generate-fast"
    
    payload = {
        "style": "cartoon",
        "theme": "animals",
        "duration": 10,
        "orientation": "landscape",
        "prompt": "Un petit chat qui joue dans un jardin",
        "title": "Chat dans le jardin"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🎬 Test de génération d'animation CrewAI...")
    print(f"📝 Prompt: {payload['prompt']}")
    print(f"🎨 Style: {payload['style']}")
    print(f"🎭 Theme: {payload['theme']}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Réponse reçue:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ Erreur:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")

def test_simple_status():
    """Test simple de status du serveur."""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"🟢 Serveur accessible: {response.status_code}")
        return True
    except:
        print("🔴 Serveur inaccessible")
        return False

if __name__ == "__main__":
    print("🚀 Test d'intégration CrewAI FRIDAY")
    print("=" * 50)
    
    # Test de status
    if test_simple_status():
        # Test de génération
        test_crewai_endpoint()
    else:
        print("❌ Impossible de tester - serveur non accessible")
