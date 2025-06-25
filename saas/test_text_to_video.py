"""
Test direct de text-to-video avec Runway
"""

import asyncio
import httpx
import os

async def test_text_to_video():
    api_key = os.getenv("RUNWAY_API_KEY")
    base_url = "https://api.dev.runwayml.com"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06"
    }
    
    # Test simple de text-to-video
    payload = {
        "model": "gen4_turbo",
        "promptText": "Cartoon style animated scene: A young hero walking through a magical forest, colorful trees, friendly creatures, adventure atmosphere, Disney-style animation",
        "duration": 10,
        "ratio": "1280:720"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("🧪 Test de l'endpoint text-to-video...")
            response = await client.post(
                f"{base_url}/v1/text_to_video",
                headers=headers,
                json=payload
            )
            
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Succès ! Task ID: {result.get('id')}")
            else:
                print(f"❌ Erreur: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_text_to_video())
