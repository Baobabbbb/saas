import os
from datetime import datetime
from unidecode import unidecode
import openai

# Mapping des voix OpenAI TTS-1-HD pour différenciation homme/femme
VOICE_MAP = {
    "female": "alloy",   # Voix féminine claire et professionnelle
    "male": "echo",      # Voix masculine profonde et naturelle
}

# Fonctions Runway supprimées - retour à OpenAI TTS-1-HD

def generate_speech(text, voice=None, filename=None):
    """Génération audio avec OpenAI TTS-1-HD"""
    print(f"🎵 TTS: Génération audio OpenAI TTS-1-HD - voice={voice}, filename={filename}")

    try:
        # Configuration OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # Utilisation du mapping des voix
        voice_id = VOICE_MAP.get(voice, "alloy")  # Default to alloy (female)

        # OpenAI TTS-1-HD permet jusqu'à 4096 caractères (plus long que Runway)
        input_text = text[:4096]  # Limite OpenAI TTS-1-HD

        print(f"🎤 Voix sélectionnée: {voice_id}")
        print(f"📝 Longueur texte: {len(text)} → {len(input_text)} caractères utilisés")

        # Nettoyer le nom de fichier
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.mp3"
        else:
            filename = unidecode(filename).lower().replace(" ", "_").replace("'", "").replace("’", "").replace(",", "")
            if not filename.endswith(".mp3"):
                filename += ".mp3"

        path = f"static/{filename}"

        # Génération audio avec OpenAI TTS-1-HD
        response = openai.audio.speech.create(
            model="tts-1-hd",  # Modèle HD de haute qualité
            voice=voice_id,
            input=input_text,
            response_format="mp3"
        )

        # Sauvegarde du fichier audio
        with open(path, "wb") as f:
            f.write(response.content)

        file_size = len(response.content)
        print(f"✅ Audio généré avec succès: {path} ({file_size} bytes)")
        print(f"🎵 Modèle utilisé: TTS-1-HD | Voix: {voice_id}")

        return path

    except Exception as e:
        print(f"❌ Erreur génération audio OpenAI: {e}")
        raise
