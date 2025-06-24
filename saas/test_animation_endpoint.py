"""
Test de l'endpoint d'animation avec Runway Gen-4 Turbo
"""

import asyncio
import httpx

async def test_animation_endpoint():
    """Test de l'endpoint /api/animations/generate"""
    
    print("🧪 Test de l'endpoint d'animation Runway Gen-4 Turbo")
    
    # Payload de test
    payload = {
        "style": "cartoon",
        "theme": "animals", 
        "orientation": "landscape",
        "prompt": "Un chat orange qui joue dans un jardin"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/animations/generate",
                json=payload
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Réponse reçue:")
                print(f"   - ID: {result.get('id', 'N/A')}")
                print(f"   - Titre: {result.get('title', 'N/A')}")
                print(f"   - Description: {result.get('description', 'N/A')}")
                print(f"   - Status: {result.get('status', 'N/A')}")
                print(f"   - Durée: {result.get('duration', 'N/A')} secondes")
            else:
                print(f"❌ Erreur: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_animation_endpoint())
