import asyncio
import requests
import json

# Test de l'endpoint generate_comic_enhanced
async def test_endpoint():
    url = "http://127.0.0.1:8000/generate_comic_enhanced/"
    
    # Données en format form-data
    data = {
        "style": "pixel",
        "hero_name": "Julie",
        "story_type": "ocean",
        "custom_request": "",
        "num_images": 2,
        "use_crewai": True
    }
    
    print("🧪 Test de l'endpoint generate_comic_enhanced")
    print(f"📋 Données: {data}")
    
    try:
        # Utiliser data= au lieu de json= pour form-data
        response = requests.post(url, data=data)
        print(f"📈 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            print(f"📄 Nombre de pages: {len(result.get('pages', []))}")
            print(f"📝 Métadonnées: {result.get('comic_metadata', {})}")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"💬 Message: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
