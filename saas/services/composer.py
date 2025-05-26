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
            x = int(img_width * 0.45)
    else:
        x = int(img_width * 0.5)

    y = int(img_height * 0.55)
    return x, y

def draw_speech_bubble(draw, text, font, img_width, img_height, target_x, target_y, bubble_index=0):
    text += " " + random.choice(["Hein ?", "Incroyable !", "C’est fou !", "C’est trop bien !", "Haha !", "On y va !"])

    max_bubble_width = img_width - 40

    # Largeur initiale
    wrapped = textwrap.wrap(text, width=32)
    bubble_width = max(draw.textlength(line, font=font) for line in wrapped) + 40

    # Si trop large, on adapte dynamiquement
    while bubble_width > max_bubble_width and len(wrapped) < 50:
        wrapped = textwrap.wrap(text, width=len(wrapped[0]) - 2)
        bubble_width = max(draw.textlength(line, font=font) for line in wrapped) + 40

    bubble_height = len(wrapped) * (font.size + 6) + 30

    # Position X : centrée sur le personnage, sans dépasser
    x = max(20, min(target_x - bubble_width // 2, img_width - bubble_width - 20))

    # Position Y : empile les bulles dans le haut de l'image sans superposition
    y = int(img_height * 0.08) + bubble_index * (bubble_height + 20)

    bubble_box = [x, y, x + bubble_width, y + bubble_height]
    draw.rounded_rectangle(bubble_box, radius=20, fill=(255, 255, 255, 180), outline="black", width=2)

    base = ((x + bubble_width // 2), y + bubble_height)
    point1 = (base[0] - 10, base[1])
    point2 = (base[0] + 10, base[1])
    tip = (base[0], base[1] + 20)
    draw.polygon([point1, point2, tip], fill=(255, 255, 255, 180), outline="black")

    text_y = y + 15
    for line in wrapped:
        draw.text((x + 20, text_y), line, fill="black", font=font)
        text_y += font.size + 6

def compose_image_with_bubbles(image_url, dialogues, description, output_path):
    try:
        if image_url.startswith("http://") or image_url.startswith("https://"):
            print(f"🌐 Téléchargement de l'image : {image_url}")
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            local_path = os.path.normpath(image_url.replace("/static/", "static/"))
            print(f"📁 Chargement image locale : {local_path}")
            img = Image.open(local_path).convert("RGBA")

        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype(FONT_PATH, size=22)
        except:
            font = ImageFont.load_default()

        for dialog in dialogues:
            character = dialog["character"]
            text = f"{character} : {dialog['text']}"
            target_x, target_y = estimate_character_position(description, character, img.width, img.height)
            draw_speech_bubble(draw, text, font, img.width, img.height, target_x, target_y)

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

        image_url = os.path.join("static", image.replace("/static/", "").replace("\\", "/"))
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
