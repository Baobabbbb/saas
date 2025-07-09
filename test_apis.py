"""
Test direct des APIs Wavespeed et Fal AI
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Charger le .env depuis le dossier saas
load_dotenv("saas/.env")

async def test_wavespeed_api():
    """Test direct de l'API Wavespeed"""
    api_key = os.getenv("WAVESPEED_API_KEY")
    base_url = os.getenv("WAVESPEED_BASE_URL", "https://api.wavespeed.ai/api/v3")
    model = os.getenv("WAVESPEED_MODEL", "bytedance/seedance-v1-pro-t2v-480p")
    
    print("🔧 Test direct de l'API Wavespeed")
    print(f"   🔑 API Key: {api_key[:10] if api_key else 'Non définie'}...")
    print(f"   🌐 Base URL: {base_url}")
    print(f"   🎯 Model: {model}")
    
    payload = {
        "aspect_ratio": "16:9",
        "duration": 10,
        "prompt": "STYLE: 2D cartoon animation, Disney style | SCENE: A cute panda learning to count stars in the sky | QUALITY: high quality animation, smooth movement"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"   📤 Envoi de la requête...")
            async with session.post(
                f"{base_url}/{model}",
                headers=headers,
                json=payload
            ) as response:
                
                response_text = await response.text()
                print(f"   📡 Réponse [{response.status}]:")
                print(f"   📄 Contenu: {response_text}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print(f"   ✅ JSON valide")
                        print(f"   🎬 Résultat: {json.dumps(result, indent=2)}")
                        
                        prediction_id = result.get("data", {}).get("id")
                        if prediction_id:
                            print(f"   🆔 Prediction ID: {prediction_id}")
                            return prediction_id
                        else:
                            print(f"   ❌ Pas de prediction ID")
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON invalide")
                else:
                    print(f"   ❌ Erreur HTTP: {response.status}")
                    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    return None

async def test_fal_ai_api():
    """Test direct de l'API Fal AI"""
    api_key = os.getenv("FAL_API_KEY")
    base_url = os.getenv("FAL_BASE_URL", "https://queue.fal.run")
    model = os.getenv("FAL_AUDIO_MODEL", "fal-ai/mmaudio-v2")
    
    print("🔧 Test direct de l'API Fal AI")
    print(f"   🔑 API Key: {api_key[:10] if api_key else 'Non définie'}...")
    print(f"   🌐 Base URL: {base_url}")
    print(f"   🎯 Model: {model}")
    
    payload = {
        "prompt": "sound effects: gentle children's music, magical sounds, educational atmosphere",
        "duration": 10
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"   📤 Envoi de la requête...")
            async with session.post(
                f"{base_url}/{model}",
                headers=headers,
                json=payload
            ) as response:
                
                response_text = await response.text()
                print(f"   📡 Réponse [{response.status}]:")
                print(f"   📄 Contenu: {response_text}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print(f"   ✅ JSON valide")
                        print(f"   🎵 Résultat: {json.dumps(result, indent=2)}")
                        
                        request_id = result.get("request_id")
                        if request_id:
                            print(f"   🆔 Request ID: {request_id}")
                            return request_id
                        else:
                            print(f"   ❌ Pas de request ID")
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON invalide")
                else:
                    print(f"   ❌ Erreur HTTP: {response.status}")
                    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    return None

async def main():
    """Test principal"""
    print("🚀 Test des APIs externes pour SEEDANCE")
    print("=" * 50)
    
    # Test Wavespeed
    prediction_id = await test_wavespeed_api()
    
    print("\n" + "=" * 50)
    
    # Test Fal AI
    request_id = await test_fal_ai_api()
    
    print("\n" + "=" * 50)
    print("🎯 Résultats des tests:")
    print(f"   📹 Wavespeed: {'✅ OK' if prediction_id else '❌ ERREUR'}")
    print(f"   🎵 Fal AI: {'✅ OK' if request_id else '❌ ERREUR'}")

if __name__ == "__main__":
    asyncio.run(main())
