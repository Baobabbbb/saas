import os
from datetime import datetime
from unidecode import unidecode
import openai

# Mapping des voix OpenAI TTS-1 pour différenciation homme/femme
# Versions premium : alloy (féminin claire/professionnelle) + onyx (masculin profonde)
VOICE_MAP = {
    "female": "alloy",    # Voix féminine claire et professionnelle (meilleure qualité)
    "male": "onyx",       # Voix masculine profonde et autoritaire
}

# Utilisation OpenAI TTS-1

def generate_speech(text, voice=None, filename=None):
    """Génération audio avec OpenAI TTS-1"""
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

        path = f"static/{filename}"

        # Génération audio avec OpenAI TTS-1 (modèle standard, voix plus douces)
        response = openai.audio.speech.create(
            model="tts-1",  # Modèle standard (plus rapide et moins cher que HD)
            voice=voice_id,
            input=input_text,
            response_format="mp3"
        )

        # Sauvegarde du fichier audio
        with open(path, "wb") as f:
            f.write(response.content)

        return path

    except Exception as e:
        raise
