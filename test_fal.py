"""
Test simple de l'API Fal AI
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Charger le .env depuis le dossier saas
load_dotenv("saas/.env")

async def test_fal_status():
    """Test du statut de l'API Fal AI"""
    api_key = os.getenv("FAL_API_KEY")
    
    print("🔧 Test du statut Fal AI")
    print(f"   🔑 API Key: {api_key[:10] if api_key else 'Non définie'}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test simple avec un modèle de base
            async with session.get(
                "https://queue.fal.run/fal-ai/fast-sdxl/status",
                headers=headers
            ) as response:
                
                response_text = await response.text()
                print(f"   📡 Réponse [{response.status}]: {response_text}")
                
                return response.status == 200
                
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

async def test_fal_simple():
    """Test simple de génération"""
    api_key = os.getenv("FAL_API_KEY")
    
    print("🔧 Test de génération simple Fal AI")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test avec un modèle simple
    payload = {
        "prompt": "test audio generation",
        "sync_mode": True
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://queue.fal.run/fal-ai/stable-audio",
                headers=headers,
                json=payload
            ) as response:
                
                response_text = await response.text()
                print(f"   📡 Réponse [{response.status}]: {response_text}")
                
                return response.status == 200
                
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

async def main():
    """Test principal"""
    print("🚀 Test Fal AI")
    print("=" * 50)
    
    # Test status
    status_ok = await test_fal_status()
    print(f"   📊 Status: {'✅ OK' if status_ok else '❌ ERREUR'}")
    
    print("\n" + "=" * 50)
    
    # Test simple
    simple_ok = await test_fal_simple()
    print(f"   🎵 Simple: {'✅ OK' if simple_ok else '❌ ERREUR'}")

if __name__ == "__main__":
    asyncio.run(main())
