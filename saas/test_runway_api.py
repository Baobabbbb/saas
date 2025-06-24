#!/usr/bin/env python3
"""
Script de test pour vérifier l'API Runway Gen-4
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.runway_gen4_new import runway_gen4_service

async def test_runway_api():
    """Test de l'API Runway Gen-4"""
    
    print("🧪 Test de l'API Runway Gen-4...")
    print("=" * 50)
    
    # Données de test
    test_data = {
        "style": "cartoon",
        "theme": "animals",
        "orientation": "landscape",
        "prompt": "cute cartoon animals playing in a colorful forest",
        "title": "Test Animation",
        "description": "Animation de test"
    }
    
    try:
        print("🚀 Lancement de la génération...")
        result = await runway_gen4_service.generate_animation(test_data)
        
        print("✅ Résultat de la génération:")
        print(f"   ID: {result['id']}")
        print(f"   Titre: {result['title']}")
        print(f"   Statut: {result['status']}")
        print(f"   URL Vidéo: {result.get('video_url', 'N/A')}")
        print(f"   URL Thumbnail: {result.get('thumbnail_url', 'N/A')}")
        
        if result['status'] == 'completed' and result.get('video_url'):
            print("🎉 Génération réussie avec la vraie API Runway !")
        elif result['status'] == 'failed':
            print(f"❌ Génération échouée: {result.get('error', 'Erreur inconnue')}")
        else:
            print("⚠️ Génération en mode simulation")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_runway_api())
