import os
import json
import random
from openai import OpenAI
from config import OPENAI_API_KEY, TEXT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_scenario(prompt: str):
    """
    Génère un scénario structuré pour une bande dessinée à partir d'un prompt.
    Une seed est ajoutée s'il n'y en a pas.
    """
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

    try:
        scenario = json.loads(raw_text)
    except json.JSONDecodeError:
        print("❌ Erreur de parsing JSON dans la réponse OpenAI")
        raise

    # Ajout d'une seed si absente
    if "seed" not in scenario or not isinstance(scenario["seed"], int):
        scenario["seed"] = random.randint(0, 2_147_483_647)
        print(f"🔢 Seed générée automatiquement : {scenario['seed']}")
    else:
        print(f"🎯 Seed déjà présente dans la réponse : {scenario['seed']}")

    return scenario
