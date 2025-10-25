import os
import openai

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
STT_MODEL = os.getenv("STT_MODEL", "whisper-1")

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model=STT_MODEL,
            file=audio_file
        )
        return response["text"]
