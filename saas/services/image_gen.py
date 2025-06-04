import requests
import base64
import os

from utils.image_resize import resize_image_if_needed

STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY")
STABILITY_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

async def generate_images(scenario, init_image_path=None):
    images = []
    for idx, scene in enumerate(scenario["scenes"]):
        prompt = f"{scene['description']} --style comic-book"
        seed = scenario.get("seed", None)

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        data = {
            "prompt": prompt,
            "output_format": "png",
            "mode": "image-to-image" if init_image_path else "text-to-image"
        }

        if seed is not None:
            data["seed"] = seed

        if init_image_path:
            resized_image_path = resize_image_if_needed(init_image_path)
            image_base64 = encode_image_to_base64(resized_image_path)
            data["image"] = image_base64
            data["strength"] = 0.65  # Ajustez selon vos besoins

        response = requests.post(
            STABILITY_ENDPOINT,
            headers=headers,
            json=data
        )
        response.raise_for_status()

        result = response.json()
        if "artifacts" in result and result["artifacts"]:
            img_b64 = result["artifacts"][0]["base64"]
            images.append(img_b64)
        else:
            raise ValueError("Aucune image retournée par Stability : " + str(result))

    return images
