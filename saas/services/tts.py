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

# Fonctions Runway supprimées - utilisation OpenAI TTS-1 avec voix douces

def generate_speech(text, voice=None, filename=None):
    """Génération audio avec OpenAI TTS-1 (meilleures voix douces)"""
    print(f"🎵 TTS: Génération audio OpenAI TTS-1 - voice={voice}, filename={filename}")

    try:
        # Configuration OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # Utilisation du mapping des voix (versions plus douces)
        voice_id = VOICE_MAP.get(voice, "shimmer")  # Default to shimmer (female)

        # OpenAI TTS-1 permet jusqu'à 4096 caractères
        input_text = text[:4096]  # Limite OpenAI TTS-1

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

        file_size = len(response.content)
        # Convertir en minutes:secondes pour plus de lisibilité
        duration_estimate = file_size / (128 * 1024 / 8)  # Estimation basée sur 128kbps
        minutes = int(duration_estimate // 60)
        seconds = int(duration_estimate % 60)

        print(f"✅ Audio généré avec succès: {path} ({file_size} bytes)")
        print(f"🎵 Durée estimée: {minutes}min{seconds}s | Modèle: TTS-1 | Voix: {voice_id}")

        return path

    except Exception as e:
        print(f"❌ Erreur génération audio OpenAI: {e}")
        raise
