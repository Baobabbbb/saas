import requests
import os

STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY")
STABILITY_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

async def generate_images(scenario, init_image_path=None):
    images = []
    # --------- TEST MINIMAL UNIQUEMENT IMAGE-TO-IMAGE ----------
    # Prompt très simple et image obligatoire
    prompt = "A dog in space"
    # Enlève tout ce qui concerne le seed, le style, etc.

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json",
    }

    files = {
        "prompt": (None, prompt),
        "mode": (None, "image-to-image"),
        "strength": (None, "0.65"),
        "output_format": (None, "png"),
    }

    # Met une image PNG toute simple dans init_image_path pour ce test !
    if init_image_path:
        with open(init_image_path, "rb") as img_file:
            files["image"] = ("image.png", img_file, "image/png")
            response = requests.post(
                STABILITY_ENDPOINT,
                headers=headers,
                files=files,
                timeout=90
            )
    else:
        raise Exception("init_image_path est requis pour ce test image-to-image.")

    # Gestion d'erreur simple
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Erreur Stability AI :", e, "→", response.text)
        raise

    result = response.json()
    if "artifacts" in result and result["artifacts"]:
        img_b64 = result["artifacts"][0]["base64"]
        images.append(img_b64)
    else:
        raise ValueError(f"Aucune image retournée par Stability AI: {result}")

    return images
