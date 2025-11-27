#!/usr/bin/env python3
"""
Script de migration pour régénérer les fichiers audio manquants
et les uploader vers Supabase Storage
"""

import os
import asyncio
from pathlib import Path
from supabase import create_client, Client
from services.supabase_storage import get_storage_service
from services.tts import generate_speech

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xfbmdeuzuyixpmouhqcv.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

async def migrate_audio_files():
    """Migre les anciens fichiers audio vers Supabase Storage"""

    if not SUPABASE_SERVICE_KEY:
        print("❌ SUPABASE_SERVICE_KEY manquante")
        return

    # Initialiser Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    print("🔄 Migration des fichiers audio vers Supabase Storage...")
    print("=" * 60)

    # Récupérer les créations avec audio_path local
    try:
        result = supabase.table('creations').select('id, user_id, title, data').execute()
        creations = result.data

        migrated_count = 0
        error_count = 0

        for creation in creations:
            data = creation.get('data', {})
            audio_path = data.get('audio_path')

            # Vérifier si c'est un chemin local (pas une URL)
            if audio_path and not audio_path.startswith('http') and audio_path.startswith('static/'):
                print(f"📝 Traitement: {creation['title']}")
                print(f"   Ancien chemin: {audio_path}")

                try:
                    # Récupérer le contenu texte
                    content = data.get('content', '')
                    if not content:
                        print("   ⚠️ Pas de contenu texte - ignoré")
                        continue

                    # Générer un nouveau nom de fichier
                    filename = audio_path.replace('static/', '').replace('.mp3', '_migrated.mp3')

                    # Régénérer l'audio
                    print("   🎵 Régénération de l'audio...")
                    new_audio_url = await generate_speech(
                        text=content[:4000],  # Limiter la taille
                        voice="female",  # Voix par défaut
                        filename=filename,
                        user_id=creation.get('user_id')  # Utiliser le user_id de la création
                    )

                    if new_audio_url and new_audio_url.startswith('http'):
                        # Mettre à jour la base de données
                        new_data = data.copy()
                        new_data['audio_path'] = new_audio_url

                        supabase.table('creations').update({
                            'data': new_data
                        }).eq('id', creation['id']).execute()

                        print(f"   ✅ Migré: {new_audio_url}")
                        migrated_count += 1
                    else:
                        print("   ❌ Échec génération audio")
                        error_count += 1

                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
                    error_count += 1

                print()

        print("=" * 60)
        print(f"📊 Résumé migration:")
        print(f"   ✅ Migrés: {migrated_count}")
        print(f"   ❌ Erreurs: {error_count}")
        print(f"   🔄 Total traité: {migrated_count + error_count}")

    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(migrate_audio_files())




