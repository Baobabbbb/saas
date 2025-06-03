import os
import requests
import random
from config import STABILITY_API_KEY
from utils.translate import translate_text
from utils.image_resize import resize_image_if_needed
from PIL import Image
import io

STATIC_DIR = "static/comics"
os.makedirs(STATIC_DIR, exist_ok=True)

STYLE_PRESETS = {
    "cartoon": "comic-book",
    "manga": "anime",
    "watercolor": "digital-art",
    "pixel": "pixel-art"
}

STABILITY_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

async def generate_images(scenario, init_image_path=None):
    scenes = scenario["scenes"]
    seed = scenario.get("seed", random.randint(0, 2_147_483_647))
    style_id = scenario.get("style", "cartoon")
    style_preset = STYLE_PRESETS.get(style_id, "comic-book")

    print(f"🎨 Style injecté dans Stability : {style_id} → {style_preset}")
    print(f"📡 Endpoint utilisé : {STABILITY_ENDPOINT}")
    images = []

    for idx, scene in enumerate(scenes):
        original_prompt = scene["description"]
        translated_prompt = translate_text(original_prompt)
        prompt = f"{translated_prompt} --style {style_preset}"

        print(f"📄 Génération image scène {idx + 1} avec seed {seed + idx}, style {style_preset}")
        print(f"🔤 Prompt traduit : {prompt}")

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
        }

        files = None
        data = {
            "prompt": prompt,
            "seed": str(seed + idx),
        }

        # --- Gestion de l'image personnalisée ---
        if init_image_path and os.path.exists(init_image_path):
            print(f"🖼 Image personnalisée trouvée : {init_image_path}")

            with Image.open(init_image_path) as img:
                img = resize_image_if_needed(img)
                image_bytes = io.BytesIO()
                img.save(image_bytes, format="PNG")
                image_bytes.seek(0)

            files = {
                "image": ("init.png", image_bytes, "image/png"),
            }

        # --- Envoi à Stability ---
        response = requests.post(
            STABILITY_ENDPOINT,
            headers=headers,
            data=data,
            files=files,
        )

        if response.status_code != 200:
            print(f"❌ Erreur Stability AI scène {idx + 1} : {response.text}")
            response.raise_for_status()

        # --- Sauvegarde de l'image ---
        filename = f"scene_{seed + idx}.png"
        filepath = os.path.join(STATIC_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(response.content)

        images.append(f"comics/{filename}")

    # --- Suppression de l'image personnalisée après usage ---
    if init_image_path and os.path.exists(init_image_path):
        try:
            os.remove(init_image_path)
            print(f"🧽 Image personnalisée supprimée : {init_image_path}")
        except Exception as e:
            print(f"⚠️ Impossible de supprimer l'image : {e}")

    return images
