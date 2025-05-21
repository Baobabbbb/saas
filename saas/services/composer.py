from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os
from services.layout import compose_comic_pages

FONT_PATH = "C:/Windows/Fonts/arial.ttf"  # adapte si besoin

def get_text_size(draw, text, font):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height
    except:
        return draw.textsize(text, font=font)

def draw_speech_bubble(draw, text, x, y, max_width, font):
    text_lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        w, _ = get_text_size(draw, test_line, font)
        if w <= max_width:
            line = test_line
        else:
            text_lines.append(line)
            line = word
    if line:
        text_lines.append(line)

    bubble_width = max(get_text_size(draw, line, font)[0] for line in text_lines) + 20
    bubble_height = len(text_lines) * (font.size + 4) + 20

    draw.rounded_rectangle(
        (x, y, x + bubble_width, y + bubble_height),
        radius=10,
        fill="white",
        outline="black"
    )

    text_y = y + 10
    for line in text_lines:
        draw.text((x + 10, text_y), line, fill="black", font=font)
        text_y += font.size + 4

def compose_image_with_bubbles(image_url, dialogues, output_path):
    try:
        if image_url.startswith("http://") or image_url.startswith("https://"):
            print(f"🌐 Téléchargement de l'image : {image_url}")
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            local_path = os.path.normpath(image_url.replace("/static/", "static/"))
            print(f"📁 Chargement image locale : {local_path}")
            img = Image.open(local_path).convert("RGB")

        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT_PATH, size=20)
        except:
            font = ImageFont.load_default()

        x, y = 50, 30
        for dialog in dialogues:
            speaker = dialog["character"]
            text = f"{speaker} : {dialog['text']}"
            draw_speech_bubble(draw, text, x, y, img.width - 100, font)
            y += 100

        img.save(output_path)
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

    # Génération des pages finales
    try:
        print("🛠️ Lancement de compose_comic_pages avec :", scene_images)
        final_image_paths = compose_comic_pages(scene_images)
        print(f"🖼️ Pages finales générées :", final_image_paths)
    except Exception as e:
        print("❌ Erreur dans compose_comic_pages :", e)
        raise

    # Nettoyage des images intermédiaires (scene_*.png)
    for path in scene_images:
        try:
            os.remove(path)
        except Exception as e:
            print(f"⚠️ Impossible de supprimer {path} :", e)

    # Formatage pour le frontend
    return {
        "final_pages": [
            f"/{p.replace(os.sep, '/')}" for p in final_image_paths
        ],
        "title": layout_data.get("title", "Bande dessinée")
    }
