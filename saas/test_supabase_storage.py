#!/usr/bin/env python3
"""
Script de test pour vérifier que Supabase Storage fonctionne correctement
"""

import os
import sys
import asyncio
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les services
sys.path.append(str(Path(__file__).parent))

from services.supabase_storage import get_storage_service
from services.tts import generate_speech

async def test_storage_service():
    """Test du service Supabase Storage"""
    print("🧪 Test du service Supabase Storage...")

    try:
        service = get_storage_service()

        # Créer un fichier de test
        test_file = "/tmp/test_upload.txt"
        with open(test_file, "w") as f:
            f.write("Ceci est un fichier de test pour Supabase Storage")

        # Tester l'upload
        result = await service.upload_file(
            file_path=test_file,
            user_id="test_user",
            content_type="audio",
            custom_filename="test_file.txt"
        )

        print(f"📤 Résultat upload: {result}")

        if result["success"]:
            print("✅ Upload réussi!")
            print(f"   - URL publique: {result['public_url']}")
            print(f"   - URL signée: {result['signed_url']}")
        else:
            print(f"❌ Upload échoué: {result.get('error', 'Erreur inconnue')}")

        # Nettoyer
        os.remove(test_file)

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

async def test_tts_upload():
    """Test de génération audio avec upload vers Supabase Storage"""
    print("\n🎵 Test génération audio avec upload...")

    try:
        # Générer un très court audio de test
        audio_url = await generate_speech(
            text="Bonjour, ceci est un test d'upload vers Supabase Storage.",
            voice="male",
            filename="test_audio.mp3"
        )

        print(f"🎵 Résultat TTS: {audio_url}")

        if audio_url and audio_url.startswith("http"):
            print("✅ Audio uploadé vers Supabase Storage!")
            print(f"   - URL: {audio_url}")
        else:
            print("❌ Échec upload audio")

    except Exception as e:
        print(f"❌ Erreur lors du test TTS: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Fonction principale"""
    print("🚀 Test Supabase Storage pour Herbbie")
    print("=" * 50)

    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()

    # Vérifier les variables d'environnement
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Variables d'environnement manquantes!")
        print("   SUPABASE_URL:", "✅" if supabase_url else "❌")
        print("   SUPABASE_SERVICE_ROLE_KEY:", "✅" if supabase_key else "❌")
        return

    print("✅ Variables d'environnement OK")

    # Tester le service de stockage
    await test_storage_service()

    # Tester la génération audio (commenté pour éviter les coûts)
    # await test_tts_upload()

    print("\n🎉 Tests terminés!")

if __name__ == "__main__":
    asyncio.run(main())




