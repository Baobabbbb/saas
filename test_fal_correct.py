"""
Test correct de l'API Fal AI avec la bonne authentification
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Charger le .env depuis le dossier saas
load_dotenv("saas/.env")

async def test_fal_correct():
    """Test avec la bonne authentification Fal AI"""
    api_key = os.getenv("FAL_API_KEY")
    
    print("🔧 Test correct de l'API Fal AI")
    print(f"   🔑 API Key: {api_key[:10]}...")
    
    # Authentification correcte pour Fal AI
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test avec un modèle simple et disponible
    payload = {
        "prompt": "gentle children's music, magical sounds",
        "duration": 5
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test avec l'endpoint correct
            async with session.post(
                "https://queue.fal.run/fal-ai/stable-audio",
                headers=headers,
                json=payload
            ) as response:
                
                response_text = await response.text()
                print(f"   📡 Réponse [{response.status}]: {response_text}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print(f"   ✅ Succès: {result}")
                        return True
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON invalide")
                        return False
                else:
                    print(f"   ❌ Erreur HTTP")
                    return False
                
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

async def test_fal_models():
    """Test des modèles disponibles"""
    api_key = os.getenv("FAL_API_KEY")
    
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    
    models_to_test = [
        "fal-ai/stable-audio",
        "fal-ai/mmaudio",
        "fal-ai/mmaudio-v2"
    ]
    
    for model in models_to_test:
        print(f"\n🧪 Test modèle: {model}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://queue.fal.run/{model}",
                    headers=headers,
                    json={"prompt": "test", "duration": 3}
                ) as response:
                    
                    print(f"   📊 Status: {response.status}")
                    if response.status != 404:
                        text = await response.text()
                        print(f"   📄 Réponse: {text[:200]}...")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

async def main():
    """Test principal"""
    print("🚀 Test correct de Fal AI")
    print("=" * 50)
    
    # Test basique
    success = await test_fal_correct()
    print(f"   🎵 Test basique: {'✅ OK' if success else '❌ ERREUR'}")
    
    print("\n" + "=" * 50)
    
    # Test modèles
    await test_fal_models()

if __name__ == "__main__":
    asyncio.run(main())
