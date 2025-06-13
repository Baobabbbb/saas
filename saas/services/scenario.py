import os
import json
import random
import re
from openai import OpenAI
from config import OPENAI_API_KEY, TEXT_MODEL
# Importation du service CrewAI pour l'amélioration des BD
from services.crewai_text_enhancer import get_crewai_comic_enhancer

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

async def generate_scenario(prompt: str, style: str = None, use_crewai: bool = True, num_images: int = 3):
    """
    Génère un scénario structuré pour une bande dessinée à partir d'un prompt.
    Utilise CrewAI pour améliorer la qualité si use_crewai=True.
    """
    # Génération du scénario de base
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"Tu es un scénariste de bande dessinée. Génère une histoire courte divisée en EXACTEMENT {num_images} scènes. "
                    "Pour chaque scène, donne une description visuelle + des dialogues. "
                    "Réponds uniquement avec un JSON structuré comme suit : "
                    "{ 'title': str, 'scenes': [ { 'description': str, 'dialogues': [ { 'character': str, 'text': str } ] } ] }"
                )
            },
            {
                "role": "user",
                "content": f"Crée une bande dessinée de {num_images} scènes à partir de ce thème : {prompt}"
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
        base_scenario = json.loads(clean_text)
    except json.JSONDecodeError as e:
        print("❌ Erreur JSON : contenu reçu non valide")
        print(raw_text)
        raise ValueError("La réponse du modèle n'est pas un JSON valide") from e    # Ajout de la seed si manquante
    if "seed" not in base_scenario or not isinstance(base_scenario["seed"], int):
        base_scenario["seed"] = random.randint(0, 2_147_483_647)
        print(f"🔢 Seed générée automatiquement : {base_scenario['seed']}")
    else:
        print(f"🎯 Seed déjà présente dans la réponse : {base_scenario['seed']}")
    
    if style:
        base_scenario["style"] = style
        print(f"🎨 Style injecté dans le scénario : {style}")
    
    # Amélioration avec CrewAI si activée
    if use_crewai:
        try:
            print("🚀 Amélioration du scénario avec CrewAI...")
            enhancer = get_crewai_comic_enhancer()
            enhanced_scenario = await enhancer.enhance_scenario_text_only(
                base_scenario, prompt, style
            )
            
            # Validation du scénario amélioré
            validation = enhancer.validate_enhanced_scenario(enhanced_scenario)
            
            if validation['is_valid']:
                print("✅ Scénario amélioré par CrewAI avec succès")
                return enhanced_scenario
            else:
                print("⚠️ Scénario CrewAI invalide, utilisation de la version de base")
                print(f"Erreurs: {validation['errors']}")
                return base_scenario
                
        except Exception as e:
            print(f"⚠️ Erreur CrewAI, utilisation du scénario de base: {e}")
            return base_scenario
    else:
        print("📝 Utilisation du scénario de base (CrewAI désactivé)")
        return base_scenario

# Fonction de compatibilité pour l'ancien système
async def generate_scenario_basic(prompt: str, style: str = None, num_images: int = 3):
    """
    Génère un scénario de base sans CrewAI pour la compatibilité
    """
    return await generate_scenario(prompt, style, use_crewai=False, num_images=num_images)
