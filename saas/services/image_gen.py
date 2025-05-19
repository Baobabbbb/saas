import os
import requests
import base64
from config import STABILITY_API_KEY

ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/core"

HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Accept": "application/json"
}

STYLE_MAP = {
    "space": "futuristic",
    "ocean": "digital-art",
    "dinosaur": "cinematic",
    "fairy": "fantasy-art",
    "superhero": "comic-book",
    "jungle": "analog-film"
}

async def generate_images(scenario):
    scenes = scenario["scenes"]
    base_seed = scenario.get("seed")
    story_type = scenario.get("story_type")  # ← tu peux passer ça depuis main.py
    style = STYLE_MAP.get(story_type)

    images = []

    for index, scene in enumerate(scenes):
        prompt = scene["description"]
        scene_seed = base_seed + index if base_seed is not None else None

        form_data = {
            "prompt": str(prompt),
            "output_format": "png",
            "seed": str(scene_seed) if scene_seed is not None else "0",
            "steps": "30",
            "cfg_scale": "7",
            "aspect_ratio": "1:1"
        }

        if style:
            form_data["style_preset"] = style

        print(f"📤 Génération image scène {index + 1} avec seed {scene_seed}, style {style}")
        response = requests.post(ENDPOINT, headers=HEADERS, files=form_data)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(f"❌ Erreur Stability AI scène {index + 1} :", response.text)
            raise

        result = response.json()
        b64_image = result["image"]

        image_path = f"static/scene_{index + 1}.png"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(b64_image))

        images.append(image_path)

    return images
