"""
Test avec caractères français pour vérifier l'encodage UTF-8
"""

import requests
import json

# Test avec caractères français
data = {
    "style": "cartoon",
    "theme": "adventure",
    "orientation": "landscape", 
    "prompt": "petit héros dans une forêt magique avec des créatures fantastiques"
}

try:
    response = requests.post(
        "http://localhost:8000/api/animations/generate",
        json=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Succès ! Animation générée")
        print(f"🎬 Titre: {result.get('title')}")
        print(f"📝 Description: {result.get('description')}")
        print(f"🎥 Vidéo: {result.get('video_url')}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(f"📄 Réponse: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
