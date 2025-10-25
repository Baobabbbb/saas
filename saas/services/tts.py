import os
from datetime import datetime
from unidecode import unidecode
import openai

# Mapping des voix OpenAI pour différenciation homme/femme
VOICE_MAP = {
    "female": "shimmer",      # Voix féminine douce et chaleureuse
    "male": "echo",          # Voix masculine claire et engageante
    # Anciens mappings pour compatibilité
    "grand-pere": "echo",    # Voix masculine mature
    "grand-mere": "shimmer", # Voix féminine douce et rassurante
    "pere": "echo",          # Voix masculine paternelle
    "mere": "shimmer",       # Voix féminine maternelle
    "petit-garcon": "echo",  # Voix masculine jeune
    "petite-fille": "nova"   # Voix féminine jeune
}

def generate_speech(text, voice=None, filename=None):
    """Génération audio avec OpenAI TTS"""
    print(f"🎵 TTS: Génération audio OpenAI - voice={voice}, filename={filename}")

    try:
        # Configuration OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # Utilisation du mapping des voix défini globalement
        voice_id = VOICE_MAP.get(voice, "shimmer")  # Default to shimmer (female)
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

        print(f"✅ TTS: Audio généré avec succès: {path}")
        return path

    except Exception as e:
        print(f"❌ TTS: Erreur génération audio: {e}")
        raise
