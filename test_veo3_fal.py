#!/usr/bin/env python3
"""
Test d'intégration pour la génération d'animation via fal-ai/Veo3
"""

import asyncio
import httpx
import json
import sys
import os
from dotenv import load_dotenv

# Chargement de l'environnement depuis le dossier saas
load_dotenv('./saas/.env')

# Ajout du dossier saas au path pour importer les services
sys.path.append('./saas')

from services.veo3_fal import veo3_fal_service

BASE_URL = "http://localhost:8000"

async def test_veo3_service_direct():
    """Test direct du service veo3_fal"""
    print("🧪 Test direct du service veo3_fal...")
    
    try:
        result = await veo3_fal_service.generate_video(
            prompt="Un petit chat orange qui joue avec une balle de laine dans un jardin ensoleillé, style cartoon pour enfants",
            aspect_ratio="16:9",
            generate_audio=True
        )
        
        print(f"✅ Test direct réussi!")
        print(f"🎥 URL: {result['video_url']}")
        print(f"📊 Taille: {result.get('file_size', 0) / 1024 / 1024:.1f} MB")
        print(f"⏱️ Temps: {result.get('generation_time', 0):.1f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test direct: {e}")
        return False

async def test_animation_endpoint():
    """Test de l'endpoint FastAPI pour les animations"""
    print("\n🧪 Test endpoint /api/generate-animation...")
    
    payload = {
        "style": "cartoon",
        "theme": "animals", 
        "orientation": "landscape",
        "prompt": "Un petit chat orange qui explore un jardin magique",
        "title": "Le Chat Explorateur"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:            response = await client.post(
                f"{BASE_URL}/api/animations/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Endpoint réussi!")
                print(f"🆔 ID: {result.get('id')}")
                print(f"🎥 URL: {result.get('video_url')}")
                print(f"📊 Status: {result.get('status')}")
                return True
            else:
                print(f"❌ Erreur endpoint: {response.status_code}")
                print(f"📄 Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur requête: {e}")
            return False

async def test_animation_from_comic():
    """Test de génération d'animation à partir d'une BD"""
    print("\n🧪 Test génération animation depuis BD...")
    
    # Données BD de test
    comic_data = {
        "title": "Les Aventures de Luna",
        "scenes": [
            {
                "description": "Luna la petite sorcière dans sa tour magique, entourée de livres volants"
            },
            {
                "description": "Luna lance un sort qui fait apparaître des papillons lumineux"
            },
            {
                "description": "Les papillons emmènent Luna voler au-dessus de la forêt enchantée"
            }
        ],
        "seed": 12345
    }
    
    try:
        result = await veo3_fal_service.generate_animation_from_comic(
            comic_data=comic_data,
            orientation="portrait"
        )
        
        print(f"✅ Animation depuis BD réussie!")
        print(f"🎬 Titre: {result.get('title')}")
        print(f"🎥 URL: {result['video_url']}")
        print(f"📐 Orientation: {result.get('orientation')}")
        print(f"🎭 Scènes: {result.get('scene_count')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur animation BD: {e}")
        return False

async def main():
    """Lance tous les tests"""
    print("🚀 Démarrage des tests fal-ai/Veo3...")
    
    # Vérification des variables d'environnement
    fal_key = os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ FAL_API_KEY manquante dans .env")
        return
    
    print(f"🔑 FAL_API_KEY configurée: {fal_key[:10]}...")
    
    results = []
    
    # Test 1: Service direct
    results.append(await test_veo3_service_direct())
    
    # Test 2: Endpoint FastAPI 
    results.append(await test_animation_endpoint())
    
    # Test 3: Animation depuis BD
    results.append(await test_animation_from_comic())
    
    # Résumé
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Résultats: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 Tous les tests ont réussi!")
    else:
        print("⚠️ Certains tests ont échoué")

if __name__ == "__main__":
    asyncio.run(main())
