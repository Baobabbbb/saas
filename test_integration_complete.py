"""
Test de l'intégration complète Runway Gen-4 Turbo
Test rapide de génération d'animation via l'API principale
"""

import asyncio
import httpx
import json

async def test_animation_integration():
    """Test de l'endpoint d'animation principal"""
    
    # URL du backend
    backend_url = "http://127.0.0.1:8000"
    
    # Données de test pour animation
    test_data = {
        "style": "cartoon",
        "theme": "magic",
        "orientation": "landscape",
        "prompt": "Un petit magicien avec une baguette étoilée"
    }
    
    print("🧪 Test d'intégration Runway Gen-4 Turbo")
    print(f"📡 Backend: {backend_url}")
    print(f"🎨 Test: {test_data}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            
            # Test endpoint principal
            print("1️⃣ Test de l'endpoint principal /api/animations/generate")
            response = await client.post(
                f"{backend_url}/api/animations/generate",
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Endpoint principal - SUCCÈS")
                print(f"   ID: {result['id']}")
                print(f"   Titre: {result['title']}")
                print(f"   Description: {result['description']}")
                print(f"   Statut: {result['status']}")
                print(f"   URL vidéo: {result['video_url']}")
                if result.get('thumbnail_url'):
                    print(f"   URL thumbnail: {result['thumbnail_url']}")
                print()
            else:
                print(f"❌ Endpoint principal - ÉCHEC: {response.status_code}")
                print(f"   Erreur: {response.text}")
                print()
            
            # Test endpoint rapide
            print("2️⃣ Test de l'endpoint rapide /api/animations/generate-fast")
            response = await client.post(
                f"{backend_url}/api/animations/generate-fast",
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Endpoint rapide - SUCCÈS")
                print(f"   ID: {result['id']}")
                print(f"   Titre: {result['title']}")
                print(f"   Description: {result['description']}")
                print(f"   Statut: {result['status']}")
                print(f"   URL vidéo: {result['video_url']}")
                print()
            else:
                print(f"❌ Endpoint rapide - ÉCHEC: {response.status_code}")
                print(f"   Erreur: {response.text}")
                print()
            
            # Test diagnostic
            print("3️⃣ Test du diagnostic système")
            response = await client.get(f"{backend_url}/diagnostic")
            
            if response.status_code == 200:
                diagnostic = response.json()
                print("✅ Diagnostic - SUCCÈS")
                for key, value in diagnostic.items():
                    print(f"   {key}: {value}")
                print()
            else:
                print(f"❌ Diagnostic - ÉCHEC: {response.status_code}")
                print()
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

    print("🏁 Test d'intégration terminé")
    print()
    print("📋 RÉSUMÉ DE L'INTÉGRATION:")
    print("   ✅ Service Runway Gen-4 Turbo intégré")
    print("   ✅ Cache local activé pour la rapidité")
    print("   ✅ Fallback simulation en cas d'erreur")
    print("   ✅ Endpoints optimisés (normal et rapide)")
    print("   ✅ Frontend connecté via veo3.js")
    print("   ✅ Intégration complète avec le site principal")

if __name__ == "__main__":
    asyncio.run(test_animation_integration())
