import os
import requests
import random
from config import STABILITY_API_KEY
from utils.translate import translate_to_english

# Dossier où les images générées seront sauvegardées
STATIC_DIR = "static/comics"
os.makedirs(STATIC_DIR, exist_ok=True)

# Endpoint de l’API Stability AI (v2beta)
STABILITY_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/core"

# Entêtes avec la clé API Stability
HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Accept": "image/png"
}

# Mapping des styles frontend → style_preset Stability AI
STYLE_PRESETS = {
    "cartoon": "comic-book",
    "manga": "anime",
    "watercolor": "digital-art",
    "pixel": "pixel-art"
}

async def generate_images(scenario):
    scenes = scenario["scenes"]
    seed = scenario.get("seed", random.randint(0, 2_147_483_647))
    style_id = scenario.get("style", "cartoon")
    style_preset = STYLE_PRESETS.get(style_id, "comic-book")

    print(f"🎨 Style injecté dans Stability : {style_id} → {style_preset}")
    images = []

    for idx, scene in enumerate(scenes):
        original_prompt = scene["description"]
        prompt = translate_to_english(original_prompt)
        scene_seed = seed + idx

        print(f"📤 Génération image scène {idx + 1} avec seed {scene_seed}, style {style_preset}")
        print(f"🔤 Prompt traduit : {prompt}")

        files = {
            "prompt": (None, prompt),
            "output_format": (None, "png"),
            "aspect_ratio": (None, "1:1"),
            "style_preset": (None, style_preset),
            "seed": (None, str(scene_seed))
        }

        response = requests.post(STABILITY_ENDPOINT, headers=HEADERS, files=files)

        if response.status_code != 200:
            print(f"❌ Erreur Stability AI scène {idx + 1} : {response.text}")
            response.raise_for_status()

        filename = f"scene_{scene_seed}.png"
        filepath = os.path.join(STATIC_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        images.append(f"/static/comics/{filename}")

    return images
