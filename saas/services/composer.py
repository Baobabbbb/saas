from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os
import random
import textwrap
from services.layout import compose_comic_pages

FONT_PATH = "C:/Windows/Fonts/arial.ttf"  # à adapter si besoin

def draw_speech_bubble(draw, text, img_width, img_height, font):
    # 💬 Ajout de variété de styles
    text += " " + random.choice(["Hein ?", "Incroyable !", "C’est fou !", "C’est trop bien !", "Haha !", "On y va !"])

    # 💬 Calcul taille du texte
    max_bubble_width = int(img_width * 0.7)
    wrapped = textwrap.wrap(text, width=30)
    bubble_width = max(draw.textlength(line, font=font) for line in wrapped) + 40
    bubble_height = len(wrapped) * (font.size + 6) + 30

    # 🎯 Position aléatoire en haut de l'image
    x = random.randint(30, img_width - bubble_width - 30)
    y = random.randint(20, int(img_height * 0.4))

    # 🗯️ Dessin de la bulle (transparente avec arrondis)
    bubble_box = [x, y, x + bubble_width, y + bubble_height]
    draw.rounded_rectangle(bubble_box, radius=20, fill=(255, 255, 255, 230), outline="black", width=2)

    # 🕳️ Pointe orientée vers un point plausible
    base = ((x + bubble_width // 2), y + bubble_height)
    point1 = (base[0] - 10, base[1])
    point2 = (base[0] + 10, base[1])
    tip = (base[0], base[1] + 20)
    draw.polygon([point1, point2, tip], fill=(255, 255, 255, 230), outline="black")

    # ✍️ Texte
    text_y = y + 15
    for line in wrapped:
        draw.text((x + 20, text_y), line, fill="black", font=font)
        text_y += font.size + 6

def compose_image_with_bubbles(image_url, dialogues, output_path):
    try:
        # 🖼️ Charge l'image
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
            draw_speech_bubble(draw, text, img.width, img.height, font)

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

        compose_image_with_bubbles(
            image_url=image_url,
            dialogues=scene["dialogues"],
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

    # Nettoyage des scènes temporaires
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
