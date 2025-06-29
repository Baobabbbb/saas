import os
import openai
from config import OPENAI_API_KEY, TTS_MODEL
from datetime import datetime
from unidecode import unidecode  # ✅ Ajout pour nettoyer les accents

VOICE_MAP = {
    "grand-pere": "onyx",
    "grand-mere": "fable", 
    "pere": "echo",
    "mere": "shimmer",
    "petit-garcon": "nova",
    "petite-fille": "alloy"
}

def generate_speech(text, voice=None, filename=None):
    input_text = text[:4096]  # Limite imposée par OpenAI TTS
    voice_id = VOICE_MAP.get(voice, "nova")

    # Si aucun nom de fichier fourni, générer un nom avec timestamp
    if not filename:
        filename = f"{filename or 'audio'}.mp3"

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

    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice_id,
        input=input_text
    )

    with open(path, "wb") as f:
        f.write(response.content)

    return path
