import os
import requests
import random
from config import STABILITY_API_KEY
from utils.translate import translate_text
from utils.image_resize import resize_image_if_needed

STATIC_DIR = "static/comics"
os.makedirs(STATIC_DIR, exist_ok=True)

STYLE_PRESETS = {
    "cartoon": "comic-book",
    "manga": "anime",
    "watercolor": "digital-art",
    "pixel": "pixel-art"
}

async def generate_images(scenario, init_image_path=None):
    scenes = scenario["scenes"]
    seed = scenario.get("seed", random.randint(0, 2_147_483_647))
    style_id = scenario.get("style", "cartoon")
    style_preset = STYLE_PRESETS.get(style_id, "comic-book")

    use_image_to_image = init_image_path and os.path.exists(init_image_path)
    endpoint = (
        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024x1024/image-to-image"
        if use_image_to_image else
        "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    )

    print(f"🎨 Style injecté dans Stability : {style_id} → {style_preset}")
    print(f"📡 Endpoint utilisé : {endpoint}")
    images = []

    if use_image_to_image:
        resized_path = resize_image_if_needed(init_image_path)
        image_data = open(resized_path, "rb").read()

    for idx, scene in enumerate(scenes):
        original_prompt = scene["description"]
        translated_prompt = translate_text(original_prompt)

        print(f"📄 Génération image scène {idx + 1} avec seed {seed + idx}, style {style_preset}")
        print(f"🔤 Prompt traduit : {translated_prompt}")

        files = {
            "prompt": (None, translated_prompt),
            "style_preset": (None, style_preset),
            "seed": (None, str(seed + idx))
        }

        if use_image_to_image:
            files["init_image"] = ("image.png", image_data, "image/png")
        else:
            files["output_format"] = (None, "png")
            files["aspect_ratio"] = (None, "1:1")

        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {STABILITY_API_KEY}",
                # Ne pas mettre 'Accept' ici si ça déclenche une erreur ; certains endpoints n’aiment pas 'image/*'
            },
            files=files
        )

        if response.status_code != 200:
            print(f"❌ Erreur Stability AI scène {idx + 1} : {response.text}")
            response.raise_for_status()

        filename = f"scene_{seed + idx}.png"
        filepath = os.path.join(STATIC_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(response.content)

        images.append(f"comics/{filename}")

    if use_image_to_image:
        try:
            os.remove(resized_path)
            print(f"🧽 Image personnalisée temporaire supprimée : {resized_path}")
        except Exception as e:
            print(f"⚠️ Impossible de supprimer l'image : {e}")

    return images
