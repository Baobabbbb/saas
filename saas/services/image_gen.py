from openai import OpenAI
from config import OPENAI_API_KEY, IMAGE_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_images(scenario):
    scenes = scenario["scenes"]
    base_seed = scenario.get("seed")  # peut être None si non défini
    images = []

    for index, scene in enumerate(scenes):
        # On varie légèrement la seed par scène, mais garde la cohérence globale
        scene_seed = base_seed + index if base_seed is not None else None

        generation_args = {
            "model": IMAGE_MODEL,
            "prompt": scene["description"],
            "size": "1024x1024",
            "quality": "standard",
            "n": 1,
        }

        if scene_seed is not None:
            generation_args["seed"] = scene_seed

        response = client.images.generate(**generation_args)
        image_url = response.data[0].url
        images.append(image_url)

    return images
