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
    max_bubble_width = img_width - 40

    # Découpage du texte
    wrapped = textwrap.wrap(text, width=32)
    content_width = max(draw.textlength(line, font=font) for line in wrapped)
    bubble_width = content_width + 40

    # Largeur limitée pour cohérence
    bubble_width = max(180, min(bubble_width, int(img_width * 0.75)))

    # Hauteur en fonction du nombre de lignes
    line_count = len(wrapped)
    line_height = font.size + 6
    bubble_height = line_count * line_height + 30
    bubble_height = max(60, min(bubble_height, 160))  # hauteur cohérente

    # Décalage horizontal pour éviter chevauchement latéral
    horizontal_shift = (bubble_index % 2) * 40 * (-1 if bubble_index % 4 == 1 else 1)
    x = target_x - bubble_width // 2 + horizontal_shift
    x = max(20, min(x, img_width - bubble_width - 20))  # contrainte de bord

    # Position Y : bulle empilée proprement en haut
    base_y = int(img_height * 0.05)
    spacing = bubble_height + 30
    y = base_y + bubble_index * spacing
    if y + bubble_height > img_height * 0.95:
        y = int(img_height * 0.95) - bubble_height

    # Dessin de la bulle
    bubble_box = [x, y, x + bubble_width, y + bubble_height]
    draw.rounded_rectangle(bubble_box, radius=20, fill=(255, 255, 255, 180), outline="black", width=2)

    # Pointe directionnelle en bas
    if horizontal_shift > 0:
        direction = "right"
    elif horizontal_shift < 0:
        direction = "left"
    else:
        direction = "center"

    if direction == "left":
        base_x = x + 20
    elif direction == "right":
        base_x = x + bubble_width - 20
    else:
        base_x = x + bubble_width // 2

    base_y = y + bubble_height
    point1 = (base_x - 10, base_y)
    point2 = (base_x + 10, base_y)
    tip = (base_x, base_y + 20)
    draw.polygon([point1, point2, tip], fill=(255, 255, 255, 180), outline="black")

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
            local_path = os.path.normpath(image_url.replace("/static/", "static/"))
            print(f"📁 Chargement image locale : {local_path}")
            img = Image.open(local_path).convert("RGBA")

        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype(FONT_PATH, size=22)
        except:
            font = ImageFont.load_default()

        for i, dialog in enumerate(dialogues):
            character = dialog["character"]
            text = f"{character} : {dialog['text']}"
            target_x, target_y = estimate_character_position(description, character, img.width, img.height)
            draw_speech_bubble(draw, text, font, img.width, img.height, target_x, target_y, bubble_index=i)


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
