from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os
import random
import textwrap
from services.layout import compose_comic_pages

FONT_PATH = "C:/Windows/Fonts/arial.ttf"  # à adapter si besoin

def estimate_character_position(description: str, character: str, img_width: int, img_height: int):
    desc = description.lower()
    character = character.lower()

    if character in desc:
        if "gauche" in desc:
            x = int(img_width * 0.2)
        elif "droite" in desc:
            x = int(img_width * 0.7)
        else:
            x = int(img_width * 0.5)
    else:
        x = int(img_width * 0.5)
    y = int(img_height * 0.55)
    return x, y

def draw_speech_bubble(draw, text, font, img_width, img_height, target_x, target_y, bubble_index=0, total_bubbles=1):
    wrapped = textwrap.wrap(text, width=32)
    content_width = max(draw.textlength(line, font=font) for line in wrapped)
    bubble_width = max(180, min(content_width + 40, int(img_width * 0.75)))
    line_count = len(wrapped)
    line_height = font.size + 6
    bubble_height = max(60, min(line_count * line_height + 30, 160))

    margin_top = int(img_height * 0.04)
    max_bubbles_area = int(img_height * 0.38)
    spacing = (max_bubbles_area - bubble_height) // max(1, total_bubbles)
    y = margin_top + bubble_index * spacing

    # --- Bulle à gauche/droite si 2 bulles, sinon comme avant
    if total_bubbles == 1:
        x = int((img_width - bubble_width) / 2)
    elif total_bubbles == 2:
        if bubble_index == 0:
            x = int(img_width * 0.08)
        else:
            x = int(img_width * 0.54)
        x = min(x, img_width - bubble_width - 20)
    else:
        x = max(20, min(target_x - bubble_width // 2 + (bubble_index - total_bubbles//2)*30, img_width - bubble_width - 20))

    # --- Dessin bulle ---
    bubble_box = [x, y, x + bubble_width, y + bubble_height]
    # BULLE PLUS TRANSPARENTE (alpha=180)
    draw.rounded_rectangle(bubble_box, radius=20, fill=(255, 255, 255, 180), outline="black", width=3)

    # --- Queue compacte & BD ---
    base_x = x + bubble_width // 2
    base_y = y + bubble_height
    tip_x = target_x
    tip_y = min(target_y, base_y + 32)
    dx = tip_x - base_x
    shift = max(-20, min(20, dx//2))
    left_x = base_x - 13 + shift
    right_x = base_x + 13 + shift
    left_y = right_y = base_y

    # Queue = triangle compact BD-style, même alpha que la bulle
    draw.polygon(
        [(left_x, left_y), (right_x, right_y), (tip_x, tip_y)],
        fill=(255,255,255,180),
        outline="black"
    )
    draw.line([(left_x, left_y), (tip_x, tip_y), (right_x, right_y)], fill="black", width=2)

    # Texte dans la bulle
    text_y = y + 15
    for line in wrapped:
        draw.text((x + 20, text_y), line, fill="black", font=font)
        text_y += line_height

def compose_image_with_bubbles(image_url, dialogues, description, output_path):
    try:
        if image_url.startswith("http://") or image_url.startswith("https://"):
            print(f"🌐 Téléchargement de l'image : {image_url}")
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            local_path = image_url
            if image_url.startswith("/static/"):
                local_path = os.path.normpath(image_url.lstrip("/"))
            else:
                local_path = os.path.normpath(image_url)
            print(f"📁 Chargement image locale : {local_path}")
            img = Image.open(local_path).convert("RGBA")

        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype(FONT_PATH, size=22)
        except:
            font = ImageFont.load_default()

        total_bubbles = len(dialogues)
        for i, dialog in enumerate(dialogues):
            character = dialog["character"]
            text = f"{character} : {dialog['text']}"
            target_x, target_y = estimate_character_position(description, character, img.width, img.height)
            draw_speech_bubble(
                draw, text, font, img.width, img.height,
                target_x, target_y, bubble_index=i, total_bubbles=total_bubbles
            )

        final = Image.alpha_composite(img, overlay).convert("RGB")
        final.save(output_path)
        print(f"✅ Image sauvegardée dans : {output_path}")
        return output_path

    except Exception as e:
        print("❌ Erreur dans compose_image_with_bubbles :", e)
        raise

async def compose_pages(layout_data):
    scene_images = []

    for idx, scene in enumerate(layout_data["scenes"]):
        print("🧩 SCÈNE :", scene)

        image = scene.get("image")
        if not image:
            raise ValueError(f"❌ La scène {idx + 1} n'a pas d'image")

        if image.startswith("/static/"):
            image_url = image
        else:
            image_url = f"/{image}" if not image.startswith("static/") else image

        output = os.path.join("static", f"scene_{idx + 1}.png")
        dialogues = scene.get("dialogues", [])[:random.randint(1, 4)]

        compose_image_with_bubbles(
            image_url=image_url,
            dialogues=dialogues,
            description=scene.get("description", ""),
            output_path=output
        )

        scene_images.append(output)

    try:
        print("🛠️ Lancement de compose_comic_pages avec :", scene_images)
        final_image_paths = compose_comic_pages(scene_images)
        print(f"🖼️ Pages finales générées :", final_image_paths)
    except Exception as e:
        print("❌ Erreur dans compose_comic_pages :", e)
        raise

    for path in scene_images:
        try:
            os.remove(path)
        except Exception as e:
            print(f"⚠️ Impossible de supprimer {path} :", e)

    return {
        "final_pages": [
            f"/{p.replace(os.sep, '/')}" for p in final_image_paths
        ],
        "title": layout_data.get("title", "Bande dessinée")
    }
