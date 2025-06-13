#!/usr/bin/env python3
"""
Test avec plus d'images pour forcer la création de plusieurs pages
"""

import requests
import json

def test_endpoint_multiple_pages():
    """Test l'endpoint FastAPI avec plus d'images"""
    
    url = "http://localhost:8000/generate_comic/"
    
    # Test avec 6 images pour avoir 2 pages (4 images par page)
    data = {
        "style": "manga",
        "hero_name": "Akira",
        "story_type": "science-fiction", 
        "custom_request": "Une longue aventure dans un Tokyo futuriste avec des robots, des néons, des combats, des découvertes, de l'amitié et des mystères",
        "num_images": 6,  # 6 images devraient faire 2 pages
        "avatar_type": "emoji",
        "emoji": "👦"
    }
    
    print("🧪 Test avec plusieurs pages")
    print("=" * 50)
    print(f"📊 Nombre d'images demandées: {data['num_images']}")
    print(f"📄 Pages attendues: {(data['num_images'] + 3) // 4}")  # ceil(n/4)
    print()
    
    try:
        print("🚀 Envoi de la requête...")
        response = requests.post(url, data=data, timeout=300)
        
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
                
            # Vérification de la logique
            expected_pages = (data['num_images'] + 3) // 4
            actual_pages = len(result.get('pages', []))
            
            if actual_pages == expected_pages:
                print(f"✅ Nombre de pages correct: {actual_pages}/{expected_pages}")
            else:
                print(f"❌ Nombre de pages incorrect: {actual_pages}/{expected_pages}")
                
            return result
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📄 Message: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

if __name__ == "__main__":
    test_endpoint_multiple_pages()
