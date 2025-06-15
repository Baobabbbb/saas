import requests
import os
import base64
import time

from utils.image_resize import resize_image_if_needed
from utils.translate import translate_text  # <== Pour traduire chaque scène

STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY")
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"
STABILITY_ENDPOINT = f"https://api.stability.ai/v1/generation/{ENGINE_ID}/text-to-image"

def get_style_prompt(style):
    """Retourne le prompt adapté selon le style choisi par l'utilisateur"""
    style_prompts = {        'cartoon': 'cartoon style, animated, colorful, family-friendly',
        'realistic': 'realistic style, detailed, photorealistic, high quality',
        'manga': 'manga style, anime art, japanese illustration style',
        'watercolor': 'watercolor painting style, soft colors, artistic',
        'sketch': 'pencil sketch style, hand-drawn, artistic lines'
    }
    return style_prompts.get(style.lower(), 'cartoon style')

async def generate_images(scenario, hero_prompt_en=None, init_image_path=None, style="cartoon"):
    images = []
    
    # Récupère le prompt de style
    style_prompt = get_style_prompt(style)
    
    for idx, scene in enumerate(scenario["scenes"]):
        # Traduction FR -> EN pour la description
        description_fr = scene['description']
        description_en = await translate_text(description_fr)        # Concatène le prompt héros si fourni + amélioration réalisme + style utilisateur
        if hero_prompt_en:
            prompt = f"{hero_prompt_en}. {description_en}. {style_prompt}, professional illustration, highly detailed, realistic shading and lighting, crisp clean lines, vibrant colors"
        else:
            prompt = f"{description_en}. {style_prompt}, professional illustration, highly detailed, realistic shading and lighting, crisp clean lines, vibrant colors"
        print(f"📝 Description FR : {description_fr}\n➡️ Prompt EN : {prompt}")        # Préparation du body JSON avec paramètres optimisés pour réalisme
        body = {
            "text_prompts": [
                {"text": prompt, "weight": 1.0}
            ],
            "cfg_scale": 10,  # Plus élevé pour plus de fidélité au prompt
            "height": 1024,
            "width": 1024,
            "sampler": "K_DPMPP_2M",
            "samples": 1,
            "steps": 40,  # Plus d'étapes pour plus de qualité
            "style_preset": "anime"
        }

        # Headers API REST
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # (L'API REST ne supporte pas image-to-image directement ici)
        response = requests.post(
            STABILITY_ENDPOINT,
            headers=headers,
            json=body,
            timeout=90
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print("❌ Erreur Stability AI :", e, "→", response.text)
            raise

        result = response.json()
        if "artifacts" in result and result["artifacts"]:
            img_b64 = result["artifacts"][0]["base64"]
            os.makedirs("static/uploads", exist_ok=True)
            filename = f"scene_{int(time.time())}_{idx}.png"
            output_path = f"static/uploads/{filename}"
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            images.append(output_path)
        else:
            raise ValueError(f"Aucune image retournée par Stability AI: {result}")

    return images

# --- Génération image héros à partir d'un prompt ---
async def generate_hero_from_prompt(prompt):
    """
    Génère une image de héros via prompt text-to-image (REST API) et l'enregistre dans static/uploads/.
    Retourne le chemin relatif du fichier PNG créé.
    """
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    body = {
        "text_prompts": [
            {"text": prompt, "weight": 1.0}
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "sampler": "K_DPMPP_2M",
        "samples": 1,
        "steps": 30,
        "style_preset": "anime"
    }

    endpoint = f"https://api.stability.ai/v1/generation/{ENGINE_ID}/text-to-image"

    response = requests.post(
        endpoint,
        headers=headers,
        json=body,
        timeout=90
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Erreur Stability AI (generate_hero_from_prompt) :", e, "→", response.text)
        raise

    result = response.json()
    if "artifacts" in result and result["artifacts"]:
        img_b64 = result["artifacts"][0]["base64"]
        os.makedirs("static/uploads", exist_ok=True)
        file_hash = abs(hash(prompt)) % 10**8
        out_path = f"static/uploads/hero_{file_hash}.png"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        return out_path
    else:
        raise ValueError(f"Aucune image retournée par Stability AI: {result}")
