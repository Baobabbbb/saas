import os
import json
import random
from openai import OpenAI
from config import OPENAI_API_KEY, TEXT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_scenario(prompt: str, style: str = None):
    """
    Génère un scénario structuré pour une bande dessinée à partir d'un prompt.
    Ajoute une seed et le style utilisé dans la structure retournée.
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

    print("🧪 Texte brut reçu :")
    print(repr(raw_text))  # montre aussi les caractères invisibles

    if not raw_text or not raw_text.strip():
        raise ValueError("❌ Le modèle n'a rien renvoyé (réponse vide)")

    try:
        scenario = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("❌ Erreur JSON : contenu reçu non valide")
        print(raw_text)
        raise ValueError("La réponse du modèle n'est pas un JSON valide") from e

    # Ajout d'une seed si absente
    if "seed" not in scenario or not isinstance(scenario["seed"], int):
        scenario["seed"] = random.randint(0, 2_147_483_647)
        print(f"🔢 Seed générée automatiquement : {scenario['seed']}")
    else:
        print(f"🎯 Seed déjà présente dans la réponse : {scenario['seed']}")

    # Ajout du style si transmis
    if style:
        scenario["style"] = style
        print(f"🎨 Style injecté dans le scénario : {style}")

    return scenario
