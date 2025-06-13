#!/usr/bin/env python3
"""
Test direct de l'endpoint pour vérifier le nombre de scènes générées
"""

import requests
import json

def test_endpoint_crewai():
    """Test l'endpoint FastAPI avec CrewAI"""
    
    url = "http://localhost:8000/generate_comic/"
    
    # Préparation des données de test
    data = {
        "style": "manga",
        "hero_name": "Akira",
        "story_type": "science-fiction", 
        "custom_request": "Une histoire dans un Tokyo futuriste avec des robots et des néons",
        "num_images": 3,
        "avatar_type": "emoji",
        "emoji": "👦"
    }
    
    print("🧪 Test de l'endpoint FastAPI")
    print("=" * 50)
    print(f"📊 Données envoyées: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print()
    
    try:
        print("🚀 Envoi de la requête...")
        response = requests.post(url, data=data, timeout=180)
        
        print(f"📈 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Réponse reçue avec succès!")
            print(f"📚 Titre: {result.get('title', 'N/A')}")
            print(f"📄 Nombre de pages: {len(result.get('pages', []))}")
            print(f"🤖 Amélioré par CrewAI: {result.get('enhanced_by_crewai', False)}")
            
            print("📖 Pages générées:")
            for i, page in enumerate(result.get('pages', [])):
                print(f"  Page {i+1}: {page}")
                
            return result
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📄 Message: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

if __name__ == "__main__":
    test_endpoint_crewai()
