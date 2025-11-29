#!/usr/bin/env python3
"""Test rapide du service Supabase Storage"""

import asyncio
import os
from services.supabase_storage import get_storage_service

async def test_storage():
    """Test rapide de l'upload"""
    print("🧪 Test du service Supabase Storage...")

    service = get_storage_service()
    if not service:
        print("❌ Service non initialisé")
        return

    # Créer un fichier de test
    test_file = "/tmp/test_storage.txt"
    with open(test_file, "w") as f:
        f.write("Test de stockage Supabase")

    try:
        # Tester l'upload
        result = await service.upload_file(
            file_path=test_file,
            user_id="test_user",
            content_type="audio",
            custom_filename="test_audio.txt"
        )

        print(f"📤 Résultat: {result}")

        if result.get("success"):
            print("✅ Upload réussi!")
            print(f"   URL: {result.get('public_url')}")
        else:
            print(f"❌ Échec: {result.get('error')}")

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

    # Nettoyer
    os.remove(test_file)

if __name__ == "__main__":
    asyncio.run(test_storage())





















