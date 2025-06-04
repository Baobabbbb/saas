import os
import requests
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

STABILITY_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

async def generate_images(scenario, init_image_path=None):
    scenes = scenario["scenes"]
    seed = scenario.get("seed", 42)
    style_id = scenario.get("style", "cartoon")
    style_preset = STYLE_PRESETS.get(style_id, "comic-book")
    images = []

    use_image_to_image = init_image_path is not None and os.path.exists(init_image_path)
    resized_path = None
    if use_image_to_image:
        resized_path = resize_image_if_needed(init_image_path)
        print(f"🖼 Image personnalisée trouvée et redimensionnée : {resized_path}")

    for idx, scene in enumerate(scenes):
        original_prompt = scene["description"]
        translated_prompt = translate_text(original_prompt)
        prompt = f"{translated_prompt} --style {style_preset}"

        print(f"📄 Génération image scène {idx + 1} avec seed {seed + idx}, style {style_preset}")
        print(f"🔤 Prompt traduit : {prompt}")

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "image/*",
        }

        files = {
            "prompt": (None, prompt),
            "seed": (None, str(seed + idx)),
            "output_format": (None, "png"),
        }

        if use_image_to_image and resized_path:
            files["image"] = (os.path.basename(resized_path), open(resized_path, "rb"), "image/png")
            files["mode"] = (None, "image-to-image")
            files["strength"] = (None, "0.6")  # <-- OBLIGATOIRE en mode image-to-image

        response = requests.post(
            STABILITY_ENDPOINT,
            headers=headers,
            files=files,
        )

        if use_image_to_image and resized_path:
            files["image"][1].close()

        if response.status_code != 200:
            print(f"❌ Erreur Stability AI scène {idx + 1} : {response.text}")
            response.raise_for_status()

        filename = f"scene_{seed + idx}.png"
        filepath = os.path.join(STATIC_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(response.content)
        images.append(f"comics/{filename}")

    if resized_path and os.path.exists(resized_path):
        try:
            os.remove(resized_path)
            print(f"🧽 Image redimensionnée supprimée : {resized_path}")
        except Exception as e:
            print(f"⚠️ Impossible de supprimer l'image : {e}")

    return images
