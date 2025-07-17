#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement du service SEEDANCE après les corrections
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire saas au path
sys.path.append(str(Path(__file__).parent / "saas"))

from services.seedance_service import SeedanceService

async def test_seedance_service():
    """Test complet du service SEEDANCE"""
    print("🧪 Test du service SEEDANCE après corrections")
    print("=" * 50)
    
    try:
        # Initialisation du service
        print("📦 Initialisation du service...")
        service = SeedanceService()
        print("✅ Service initialisé avec succès")
        
        # Test de génération d'histoire
        print("\n📚 Test de génération d'histoire...")
        story = await service.generate_story_for_theme(
            theme="space",
            age_target="3-6 ans",
            custom_request="avec des robots amicaux"
        )
        print(f"✅ Histoire générée: {story[:100]}...")
        
        # Test de génération d'animation courte
        print("\n🎬 Test de génération d'animation...")
        result = await service.generate_seedance_animation(
            story=story,
            theme="space",
            age_target="3-6 ans",
            duration=15,  # Durée courte pour le test
            style="cartoon"
        )
        
        if result["status"] == "success":
            print("✅ Animation générée avec succès!")
            print(f"   🆔 ID: {result['animation_id']}")
            print(f"   🎞️ URL: {result['video_url']}")
            print(f"   ⏱️ Durée: {result['actual_duration']}s")
            print(f"   🎬 Scènes: {result['scenes_count']}")
            print(f"   ⚡ Temps: {result['generation_time']}s")
        else:
            print("❌ Échec de la génération d'animation")
            print(f"   Erreur: {result.get('error', 'Inconnue')}")
            print(f"   Type: {result.get('error_type', 'Inconnu')}")
            print(f"   Solution: {result.get('solution', 'Aucune')}")
            
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Test terminé!")
    return True

async def test_api_keys():
    """Test de validation des clés API"""
    print("🔑 Test des clés API")
    print("-" * 30)
    
    # Vérification des variables d'environnement
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / "saas" / ".env")
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "WAVESPEED_API_KEY": os.getenv("WAVESPEED_API_KEY"), 
        "FAL_API_KEY": os.getenv("FAL_API_KEY")
    }
    
    for key_name, key_value in api_keys.items():
        if key_value and not key_value.startswith("votre_") and not key_value.startswith("sk-votre"):
            print(f"✅ {key_name}: Configurée ({key_value[:10]}...)")
        else:
            print(f"❌ {key_name}: Manquante ou invalide")
    
    return all(key_value and not key_value.startswith("votre_") and not key_value.startswith("sk-votre") for key_value in api_keys.values())

if __name__ == "__main__":
    print("🚀 SEEDANCE - Test de Fonctionnement")
    print("=" * 50)
    
    # Test des clés API
    keys_ok = asyncio.run(test_api_keys())
    
    if keys_ok:
        # Test du service
        asyncio.run(test_seedance_service())
    else:
        print("\n❌ Les clés API ne sont pas correctement configurées")
        print("   Vérifiez le fichier saas/.env")
