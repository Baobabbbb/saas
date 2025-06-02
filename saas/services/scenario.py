import os
import json
import random
import re
from openai import OpenAI
from config import OPENAI_API_KEY, TEXT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_json_from_response(text: str) -> str:
    """
    Extrait un bloc JSON valide à partir d'un texte qui peut contenir du Markdown ou d'autres éléments parasites.
    """
    try:
        # Recherche de bloc ```json ... ```
        match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        # Sinon on tente un fallback brut
        return text.strip()
    except Exception as e:
        raise ValueError("Impossible d'extraire du JSON proprement.") from e

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
    print(repr(raw_text))

    if not raw_text or not raw_text.strip():
        raise ValueError("❌ Le modèle n'a rien renvoyé (réponse vide)")

    try:
        clean_text = extract_json_from_response(raw_text)
        scenario = json.loads(clean_text)
    except json.JSONDecodeError as e:
        print("❌ Erreur JSON : contenu reçu non valide")
        print(raw_text)
        raise ValueError("La réponse du modèle n'est pas un JSON valide") from e

    if "seed" not in scenario or not isinstance(scenario["seed"], int):
        scenario["seed"] = random.randint(0, 2_147_483_647)
        print(f"🔢 Seed générée automatiquement : {scenario['seed']}")
    else:
        print(f"🎯 Seed déjà présente dans la réponse : {scenario['seed']}")

    if style:
        scenario["style"] = style
        print(f"🎨 Style injecté dans le scénario : {style}")

    return scenario
