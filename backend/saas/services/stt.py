import os
import openai
from config import OPENAI_API_KEY, STT_MODEL

openai.api_key = OPENAI_API_KEY

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model=STT_MODEL,
            file=audio_file
        )
        return response["text"]
