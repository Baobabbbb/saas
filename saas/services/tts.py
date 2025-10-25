import os
import requests
from datetime import datetime
from unidecode import unidecode  # ✅ Ajout pour nettoyer les accents
import openai  # Import OpenAI en fallback

# Mapping des voix pour Runway eleven_multilingual_v2
# Utilisation de voix spécifiques de haute qualité pour Herbbie
VOICE_MAP = {
    "female": "Maya",        # Voix féminine douce et chaleureuse, parfaite pour les histoires d'enfants
    "male": "Arjun",         # Voix masculine claire et engageante, idéale pour la narration
    # Anciens mappings pour compatibilité - utilisent les nouvelles voix
    "grand-pere": "Arjun",   # Voix masculine mature
    "grand-mere": "Maya",    # Voix féminine douce et rassurante
    "pere": "Arjun",         # Voix masculine paternelle
    "mere": "Maya",          # Voix féminine maternelle
    "petit-garcon": "Arjun", # Voix masculine jeune
    "petite-fille": "Maya"   # Voix féminine jeune
}

def generate_speech_openai_fallback(text, voice=None, filename=None):
    """Fallback vers OpenAI TTS si Runway échoue"""
    print(f"🔄 TTS: Fallback vers OpenAI TTS - voice={voice}, filename={filename}")

    try:
        # Configuration OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not available for fallback")

        # Mapping des voix OpenAI
        openai_voice_map = {
            "Maya": "shimmer",      # Féminin doux
            "Arjun": "echo",        # Masculin clair
            "female": "shimmer",
            "male": "echo",
            "grand-pere": "echo",
            "grand-mere": "shimmer",
            "pere": "echo",
            "mere": "shimmer",
            "petit-garcon": "echo",
            "petite-fille": "nova"
        }

        voice_id = openai_voice_map.get(voice, "nova")
        input_text = text[:4096]  # Limite OpenAI

        # Si aucun nom de fichier fourni, générer un nom avec timestamp
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.mp3"
        else:
            filename = unidecode(filename).lower().replace(" ", "_").replace("'", "").replace("’", "").replace(",", "")
            if not filename.endswith(".mp3"):
                filename += ".mp3"

        path = f"static/{filename}"

        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=input_text
        )

        with open(path, "wb") as f:
            f.write(response.content)

        print(f"✅ TTS: Fallback OpenAI réussi: {path}")
        return path

    except Exception as e:
        print(f"❌ TTS: Échec du fallback OpenAI: {e}")
        raise

def generate_speech(text, voice=None, filename=None):
    print(f"🎵 TTS: Tentative génération audio avec Runway - voice={voice}, filename={filename}")

    # Limite de caractères pour Runway (basé sur la tarification: 1 crédit / 50 caractères)
    input_text = text[:2500]  # Limite conservatrice pour éviter les coûts élevés
    voice_model = VOICE_MAP.get(voice, "Maya")  # Default to Maya if no voice specified
    print(f"🎵 TTS: Voice mappée: {voice} -> {voice_model}")

    # Configuration de l'API Runway
    runway_api_key = os.getenv("RUNWAY_API_KEY")
    if not runway_api_key:
        print("⚠️ RUNWAY_API_KEY non configurée, utilisation du fallback OpenAI")
        return generate_speech_openai_fallback(text, voice, filename)

    # Validation basique de la clé API
    if not runway_api_key.startswith("key_"):
        print(f"⚠️ RUNWAY_API_KEY format invalide, utilisation du fallback OpenAI (clé: {runway_api_key[:10]}...)")
        return generate_speech_openai_fallback(text, voice, filename)

    print(f"🔑 RUNWAY_API_KEY détectée et valide: {runway_api_key[:10]}...")

    # Si aucun nom de fichier fourni, générer un nom avec timestamp
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}.mp3"

    # Sinon, nettoyer le nom
    else:
        filename = unidecode(filename)  # ✅ Supprime les accents
        filename = (
            filename.lower()
            .replace(" ", "_")
            .replace("'", "")
            .replace("’", "")
            .replace(",", "")
        )
        if not filename.endswith(".mp3"):
            filename += ".mp3"

    path = f"static/{filename}"

    # Préparation de la requête Runway API
    url = "https://api.runwayml.com/v1/text_to_speech"
    headers = {
        "Authorization": f"Bearer {runway_api_key}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06"
    }

    payload = {
        "model": "eleven_multilingual_v2",
        "text": input_text,
        "voice": {
            "type": "runway-preset",
            "presetId": voice_model
        }
    }

    try:
        print(f"🎵 TTS: Lancement de la tâche Runway text-to-speech...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Runway retourne un task_id pour suivre la génération
        result = response.json()
        task_id = result.get("id")

        if not task_id:
            raise ValueError("No task ID returned from Runway API")

        print(f"🎵 TTS: Tâche créée avec ID: {task_id}")

        # Attendre que la tâche soit terminée (polling)
        max_attempts = 30  # Maximum 30 tentatives (environ 2-3 minutes)
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            task_url = f"https://api.runwayml.com/v1/tasks/{task_id}"

            try:
                task_response = requests.get(task_url, headers={
                    "Authorization": f"Bearer {runway_api_key}",
                    "X-Runway-Version": "2024-11-06"
                })
                task_response.raise_for_status()

                task_data = task_response.json()
                status = task_data.get("status")

                print(f"🎵 TTS: Tentative {attempt}/{max_attempts} - Statut: {status}")

                if status == "SUCCEEDED":
                    # Tâche terminée avec succès
                    output = task_data.get("output", {})
                    audio_url = output.get("audio_url")

                    if not audio_url:
                        raise ValueError("No audio URL in task output")

                    print(f"🎵 TTS: Tâche réussie ! Téléchargement depuis: {audio_url}")

                    # Télécharger le fichier audio
                    audio_response = requests.get(audio_url)
                    audio_response.raise_for_status()

                    with open(path, "wb") as f:
                        f.write(audio_response.content)

                    print(f"🎵 TTS: Fichier audio créé: {path} (taille: {len(audio_response.content)} bytes)")
                    return path

                elif status == "FAILED":
                    error_msg = task_data.get("failure_reason", "Unknown failure")
                    raise ValueError(f"Task failed: {error_msg}")

                elif status in ["PENDING", "RUNNING"]:
                    # Attendre avant la prochaine vérification
                    import time
                    time.sleep(5)  # Attendre 5 secondes
                    continue

                else:
                    raise ValueError(f"Unknown task status: {status}")

            except requests.exceptions.RequestException as task_error:
                print(f"⚠️ Erreur lors de la vérification de tâche (tentative {attempt}): {task_error}")
                if attempt < max_attempts:
                    import time
                    time.sleep(5)
                    continue
                else:
                    raise

        # Timeout atteint
        raise TimeoutError(f"Task {task_id} did not complete within {max_attempts * 5} seconds")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur API Runway: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"❌ Code HTTP: {e.response.status_code}")
            print(f"❌ Détails erreur: {e.response.text}")

            # Si c'est une erreur 401 (Unauthorized), utiliser le fallback OpenAI
            if e.response.status_code == 401:
                print("🔄 Erreur 401 Runway - Tentative fallback vers OpenAI TTS")
                return generate_speech_openai_fallback(text, voice, filename)
        raise
    except Exception as e:
        print(f"❌ Erreur inattendue Runway: {e}")
        # En cas d'erreur inattendue, essayer le fallback OpenAI
        print("🔄 Erreur inattendue Runway - Tentative fallback vers OpenAI TTS")
        try:
            return generate_speech_openai_fallback(text, voice, filename)
        except Exception as fallback_error:
            print(f"❌ Échec du fallback OpenAI: {fallback_error}")
            raise
