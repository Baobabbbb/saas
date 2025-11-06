#!/usr/bin/env python3
"""
Test d'intégration Sora 2 - Vérification complète du système
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from services.sora2_generator import Sora2Generator
from config import SORA2_PLATFORMS, SORA2_CONFIG

async def test_sora2_integration():
    """Test complet de l'intégration Sora 2"""
    print("🚀 Test d'intégration Sora 2 - HERBBIE")
    print("=" * 50)

    # 1. Test de l'initialisation
    print("1️⃣ Test d'initialisation du générateur...")
    try:
        generator = Sora2Generator()
        print(f"✅ Générateur initialisé: {generator.selected_platform}")

        # Vérifier les plateformes disponibles
        available = generator.get_available_platforms()
        print(f"📋 Plateformes disponibles: {available}")

        if not generator.is_available():
            print("⚠️ Aucune plateforme Sora 2 disponible")
            print("💡 Configurez au moins une clé API Sora 2 dans .env")
            return False

    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return False

    # 2. Test de génération d'idée
    print("\n2️⃣ Test de génération d'idée créative...")
    try:
        idea_data = await generator.generate_animation_idea("space", 30)
        print(f"✅ Idée générée: {idea_data['idea'][:50]}...")
        print(f"📝 Environnement: {idea_data['environment'][:50]}...")
        print(f"🎵 Sons: {idea_data['sound'][:50]}...")
        print(f"🎬 Scènes: {len(idea_data['scenes'])} scènes")

    except Exception as e:
        print(f"❌ Erreur génération idée: {e}")
        return False

    # 3. Test de génération vidéo (simulation)
    print("\n3️⃣ Test de génération vidéo Sora 2 (simulation)...")
    try:
        # Prendre la première scène pour le test
        test_scene = idea_data['scenes'][0]
        video_url = await generator.generate_sora2_video(
            test_scene,
            idea_data['idea'],
            idea_data['environment'],
            10  # durée de 10s
        )
        print(f"✅ Vidéo générée (simulation): {video_url[:50]}...")

    except Exception as e:
        print(f"❌ Erreur génération vidéo: {e}")
        return False

    # 4. Test de génération complète
    print("\n4️⃣ Test de génération complète...")
    try:
        result = await generator.generate_complete_animation("ocean", 30)
        print(f"✅ Animation complète générée: {result['status']}")
        print(f"🎬 Titre: {result['title']}")
        print(f"⏱️ Durée: {result['duration']}s")
        print(f"🏷️ Type: {result['type']}")
        print(f"🌐 Plateforme: {result['platform']}")

    except Exception as e:
        print(f"❌ Erreur génération complète: {e}")
        return False

    # 5. Test de configuration
    print("\n5️⃣ Vérification de la configuration...")
    print(f"✅ Configuration Sora 2 chargée")
    print(f"📊 Durée max: {SORA2_CONFIG['max_duration']}s")
    print(f"🎨 Style: {SORA2_CONFIG['style'][:50]}...")
    print(f"🎯 Audience: {SORA2_CONFIG['target_audience']}")

    print("\n🎉 Tous les tests Sora 2 ont réussi!")
    print("✅ Intégration Sora 2 fonctionnelle dans HERBBIE")
    return True

if __name__ == "__main__":
    # Configuration du logging
    import logging
    logging.basicConfig(level=logging.INFO)

    # Exécuter les tests
    success = asyncio.run(test_sora2_integration())

    if success:
        print("\n🎯 Résultat: Intégration Sora 2 PRÊTE POUR PRODUCTION")
        sys.exit(0)
    else:
        print("\n❌ Résultat: Problèmes détectés - Vérifiez la configuration")
        sys.exit(1)
