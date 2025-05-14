import os
import requests
from config import OPENAI_API_KEY, TTS_MODEL

def generate_speech(text, output_path="static/audio.mp3"):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": TTS_MODEL,
        "input": text,
        "voice": "nova",
        "response_format": "mp3"
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path