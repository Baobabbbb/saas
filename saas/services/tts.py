import os
from datetime import datetime
from unidecode import unidecode
import openai
from services.supabase_storage import get_storage_service

# Mapping des voix OpenAI TTS-1 pour différenciation homme/femme
# Versions premium : alloy (féminin claire/professionnelle) + onyx (masculin profonde)
VOICE_MAP = {
    "female": "alloy",    # Voix féminine claire et professionnelle (meilleure qualité)
    "male": "onyx",       # Voix masculine profonde et autoritaire
}

# Utilisation OpenAI TTS-1

def generate_speech(text, voice=None, filename=None, user_id=None):
    """Génération audio avec OpenAI TTS-1 et upload vers Supabase Storage"""
    try:
        # Configuration OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # Utilisation du mapping des voix
        voice_id = VOICE_MAP.get(voice, "alloy")

        # OpenAI TTS-1 permet jusqu'à 4096 caractères
        input_text = text[:4096]

        # Nettoyer le nom de fichier
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.mp3"
        else:
            filename = unidecode(filename).lower().replace(" ", "_").replace("'", "").replace("’", "").replace(",", "")
            if not filename.endswith(".mp3"):
                filename += ".mp3"

        # Créer un fichier temporaire pour l'audio
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Génération audio avec OpenAI TTS-1 (modèle standard, voix plus douces)
            response = openai.audio.speech.create(
                model="tts-1",  # Modèle standard (plus rapide et moins cher que HD)
                voice=voice_id,
                input=input_text,
                response_format="mp3"
            )

            # Sauvegarde temporaire du fichier audio
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # Upload vers Supabase Storage si user_id fourni
            print(f"🔍 [TTS] user_id reçu: {user_id} (type: {type(user_id)})")
            if user_id:
                storage_service = get_storage_service()
                if storage_service:
                    # Exécuter la coroutine async dans un contexte synchrone
                    import asyncio
                    try:
                        # Essayer d'obtenir la boucle d'événements existante
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Si la boucle est déjà en cours d'exécution, créer une nouvelle boucle isolée
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            try:
                                upload_result = new_loop.run_until_complete(
                                    storage_service.upload_file(
                                        file_path=temp_path,
                                        user_id=user_id,
                                        content_type="audio",
                                        custom_filename=filename
                                    )
                                )
                            finally:
                                new_loop.close()
                        else:
                            upload_result = loop.run_until_complete(
                                storage_service.upload_file(
                                    file_path=temp_path,
                                    user_id=user_id,
                                    content_type="audio",
                                    custom_filename=filename
                                )
                            )
                    except RuntimeError:
                        # Pas de boucle d'événements, en créer une nouvelle
                        upload_result = asyncio.run(
                            storage_service.upload_file(
                                file_path=temp_path,
                                user_id=user_id,
                                content_type="audio",
                                custom_filename=filename
                            )
                        )

                    if upload_result["success"]:
                        audio_url = upload_result["signed_url"]
                        print(f"✅ Audio uploadé vers Supabase Storage: {audio_url[:50]}...")
                        return audio_url
                    else:
                        print(f"❌ Échec upload Supabase Storage: {upload_result.get('error', 'Erreur inconnue')}")
                        raise Exception(f"Échec upload Supabase Storage: {upload_result.get('error', 'Erreur inconnue')}")
                else:
                    print("❌ Service Supabase Storage non disponible")
                    raise Exception("Service Supabase Storage non disponible")
            else:
                print("❌ user_id requis pour l'upload Supabase Storage")
                raise Exception("user_id requis pour l'upload Supabase Storage")

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        raise
