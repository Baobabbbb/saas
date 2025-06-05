import requests
from PIL import Image
import io
import os

from utils.image_resize import resize_image_if_needed

STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY")
STABILITY_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

async def generate_images(scenario, init_image_path=None):
    images = []
    for idx, scene in enumerate(scenario["scenes"]):
        # Prompt, style & seed
        prompt = f"{scene['description']} --style comic-book"
        seed = scenario.get("seed", None)

        # Headers (l'API veut ce header précis)
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "application/json",
        }

        # Form-data
        files = {
            "prompt": (None, prompt),
            "output_format": (None, "png"),
        }
        if seed is not None:
            files["seed"] = (None, str(seed))

        if init_image_path:
            # Mode image-to-image
            files["mode"] = (None, "image-to-image")
            files["strength"] = (None, "0.65")  # Choisis la force voulue
            img_path = resize_image_if_needed(init_image_path)
            with open(img_path, "rb") as img_file:
                files["image"] = ("image.png", img_file, "image/png")
                # Attention: il faut garder le context manager ouvert le temps de la requête
                response = requests.post(
                    STABILITY_ENDPOINT,
                    headers=headers,
                    files=files,
                    timeout=90
                )
        else:
            # Mode text-to-image
            files["mode"] = (None, "text-to-image")
            response = requests.post(
                STABILITY_ENDPOINT,
                headers=headers,
                files=files,
                timeout=90
            )

        # Gestion des erreurs réseau ou API
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print("❌ Erreur Stability AI :", e, "→", response.text)
            raise

        # Lecture du résultat
        result = response.json()
        if "artifacts" in result and result["artifacts"]:
            img_b64 = result["artifacts"][0]["base64"]
            images.append(img_b64)
        else:
            raise ValueError(f"Aucune image retournée par Stability AI: {result}")

    return images
