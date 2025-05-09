import os
import json
from openai import OpenAI
from config import OPENAI_API_KEY, TEXT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_scenario(prompt: str):
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un scénariste de bande dessinée. Génère une histoire courte divisée en scènes. "
                    "Pour chaque scène, donne une description visuelle + des dialogues. "
                    "Réponds uniquement avec un JSON structuré comme suit : "
                    "{ 'title': str, 'scenes': [ { 'description': str, 'dialogues': [ { 'character': str, 'text': str } ] } ] }"
                )
            },
            {
                "role": "user",
                "content": f"Crée une bande dessinée à partir de ce thème : {prompt}"
            }
        ],
        temperature=0.8
    )
    raw_text = response.choices[0].message.content
    return json.loads(raw_text)
