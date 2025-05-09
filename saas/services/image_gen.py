from openai import OpenAI
from config import OPENAI_API_KEY, IMAGE_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_images(scenario):
    scenes = scenario["scenes"]
    images = []

    for scene in scenes:
        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=scene["description"],
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        images.append(image_url)

    return images