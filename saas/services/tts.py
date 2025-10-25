import os
import openai
from datetime import datetime
from unidecode import unidecode  # ✅ Ajout pour nettoyer les accents

VOICE_MAP = {
    "female": "shimmer",  # Voix féminine douce et chaleureuse (excellente pour enfants)
    "male": "echo",       # Voix masculine expressive et claire (parfaite pour narrateur)
    # Anciens mappings pour compatibilité
    "grand-pere": "fable",    # Voix britannique calme
    "grand-mere": "shimmer", 
    "pere": "echo",
    "mere": "shimmer",
    "petit-garcon": "echo",
    "petite-fille": "nova"    # Voix jeune et énergique
}

def generate_speech(text, voice=None, filename=None):
    print(f"🎵 TTS: Génération audio - voice={voice}, filename={filename}")
    input_text = text[:4096]  # Limite imposée par OpenAI TTS
    voice_id = VOICE_MAP.get(voice, "nova")
    print(f"🎵 TTS: Voice mappée: {voice} -> {voice_id}")

    # Configuration de l'API OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")

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

    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice_id,
        input=input_text
    )

    with open(path, "wb") as f:
        f.write(response.content)

    print(f"🎵 TTS: Fichier audio créé: {path}")
    return path
