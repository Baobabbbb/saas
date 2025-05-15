import os
import requests
from config import OPENAI_API_KEY, TTS_MODEL

VOICE_MAP = {
    "grandpa": "onyx",
    "grandma": "fable",
    "child": "nova",
    "woman": "shimmer",
    "man": "echo"
}

def generate_speech(text, voice=None):
    from datetime import datetime
    import openai

    filename = f"output_audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    path = f"static/{filename}"

    input_text = text[:4096]  # limite imposée par OpenAI TTS
    voice_id = VOICE_MAP.get(voice, "nova")

    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice_id,
        input=input_text
    )

    with open(path, "wb") as f:
        f.write(response.content)

    return path