from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os
from services.layout import compose_comic_pages

FONT_PATH = "C:/Windows/Fonts/arial.ttf"

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

    bubble_width = max([get_text_size(draw, line, font)[0] for line in text_lines]) + 20
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
            print(f"📁 Chargement image locale : {image_url}")
            img = Image.open(image_url).convert("RGB")

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
        print("🧩 SCENE :", scene)

        image = scene.get("image")
        if not image:
            raise ValueError(f"❌ La scène {idx + 1} n'a pas d'image")

        if image.startswith("http://") or image.startswith("https://"):
            image_url = image
        else:
            image_url = f"/static/{image}"

        output = f"static/scene_{idx + 1}.png"

        compose_image_with_bubbles(
            image_url=image_url,
            dialogues=scene["dialogues"],
            output_path=output
        )

        scene_images.append(f"static/scene_{idx + 1}.png")

    # 🔍 Log de debug avant génération de la BD finale
    try:
        print("🛠️ Lancement de compose_comic_pages avec :", scene_images)
        final_image_path = compose_comic_pages(scene_images)
        print(f"🖼️ Final page générée dans : {final_image_path}")
    except Exception as e:
        print("❌ Erreur dans compose_comic_pages :", e)
        raise

    # Préparation des pages scène par scène
    pages = []
    for i, filename in enumerate(scene_images):
        pages.append({
            "text": "\n".join(
                f'{d["character"]}: {d["text"]}' for d in layout_data["scenes"][i]["dialogues"]
            ),
            "image_url": f"static/{filename}"
        })

    return pages
