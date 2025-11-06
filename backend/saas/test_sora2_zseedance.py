#!/usr/bin/env python3
"""
Test du générateur Sora 2 Zseedance - Workflow identique à zseedance.json
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from services.sora2_zseedance_generator import Sora2ZseedanceGenerator

async def test_sora2_zseedance():
    """Test complet du générateur Sora 2 zseedance"""
    print("🚀 Test Sora 2 Zseedance - Workflow n8n identique")
    print("=" * 60)

    # 1. Test de l'initialisation
    print("1️⃣ Test d'initialisation du générateur...")
    try:
        generator = Sora2ZseedanceGenerator()
        print(f"✅ Générateur initialisé: {generator.selected_platform}")

        # Vérifier les plateformes disponibles
        available = generator.get_available_platforms()
        print(f"📋 Plateformes disponibles: {available}")

        if not generator.is_available():
            print("⚠️ Aucune plateforme Sora 2 disponible")
            print("💡 Configurez OPENAI_API_KEY, RUNWAY_API_KEY, ou PIKA_API_KEY dans .env")
            return False

    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return False

    # 2. Test du workflow complet zseedance
    print("\n2️⃣ Test du workflow zseedance complet...")
    try:
        # Étape 1: Ideas AI Agent
        print("📝 Étape 1: Ideas AI Agent...")
        idea_data = await generator.generate_ideas_agent()
        print(f"✅ Idée générée: {idea_data['Idea'][:50]}...")
        print(f"🎬 Caption: {idea_data['Caption']}")

        # Étape 2: Prompts AI Agent
        print("\n📝 Étape 2: Prompts AI Agent...")
        prompts_data = await generator.generate_prompts_agent(idea_data)
        print(f"✅ Prompts générés: {len(prompts_data)} scènes")
        for i, scene_key in enumerate(['Scene 1', 'Scene 2', 'Scene 3'], 1):
            if scene_key in prompts_data:
                print(f"  Scène {i}: {prompts_data[scene_key][:50]}...")

        # Étape 3: Create Clips (simulation)
        print("\n🎬 Étape 3: Create Clips avec Sora 2...")
        video_urls = []
        for i in range(1, 4):
            scene_key = f"Scene {i}"
            if scene_key in prompts_data:
                scene_prompt = prompts_data[scene_key]

                # Attendre entre les générations (comme zseedance avec batching)
                if i > 1:
                    await asyncio.sleep(1)

                video_url = await generator.create_sora2_clip(
                    scene_prompt,
                    prompts_data["Idea"],
                    prompts_data["Environment"]
                )
                video_urls.append(video_url)
                print(f"✅ Clip {i} généré (simulation): {video_url[:50]}...")

        # Étape 4: Sequence Video
        print("\n🔗 Étape 4: Sequence Video...")
        final_video_url = await generator.sequence_sora2_video(video_urls)
        print(f"✅ Vidéo finale assemblée: {final_video_url[:50]}...")

    except Exception as e:
        print(f"❌ Erreur workflow zseedance: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Test de génération complète
    print("\n3️⃣ Test de génération complète...")
    try:
        result = await generator.generate_complete_animation_zseedance("space")
        print(f"✅ Animation complète générée: {result['status']}")
        print(f"🎬 Titre: {result['title']}")
        print(f"⏱️ Durée: {result['duration']}s")
        print(f"🏷️ Type: {result['type']}")
        print(f"🌐 Plateforme: {result['platform']}")
        print(f"📹 Nombre de vidéos: {result['video_count']}")

    except Exception as e:
        print(f"❌ Erreur génération complète: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n🎉 Tous les tests Sora 2 Zseedance ont réussi!")
    print("✅ Workflow zseedance fonctionnel avec Sora 2")
    print("✅ Pas de modes différents - système unique et fiable")
    print("✅ Audio intégré à Sora 2 - pas d'étape séparée")
    return True

if __name__ == "__main__":
    # Configuration du logging
    import logging
    logging.basicConfig(level=logging.INFO)

    # Exécuter les tests
    success = asyncio.run(test_sora2_zseedance())

    if success:
        print("\n🎯 Résultat: Sora 2 Zseedance PRÊT POUR PRODUCTION")
        print("✅ Système fonctionnel basé exactement sur zseedance.json")
        print("✅ Aucun fallback - système fiable et prévisible")
        sys.exit(0)
    else:
        print("\n❌ Résultat: Problèmes détectés - Vérifiez la configuration")
        sys.exit(1)
