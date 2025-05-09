from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os
from services.layout import compose_comic_page

FONT_PATH = "C:/Windows/Fonts/arial.ttf"

def draw_speech_bubble(draw, text, x, y, max_width, font):
    text_lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            line = test_line
        else:
            text_lines.append(line)
            line = word
    if line:
        text_lines.append(line)

    bubble_width = max([
        draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
        for line in text_lines
    ]) + 20
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
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, size=20)
    except:
        font = ImageFont.load_default()

    x, y = 50, 30
    for dialog in dialogues:
        if "character" not in dialog or "text" not in dialog:
            print("❌ Dialogue mal formé, ignoré :", dialog)
            continue
        speaker = dialog["character"]
        text = dialog["text"]
        full_text = f"{speaker} : {text}"
        draw_speech_bubble(draw, full_text, x, y, img.width - 100, font)
        y += 100

    img.save(output_path)
    return output_path

async def compose_pages(layout_data):
    scene_images = []

    # S'assurer que le dossier 'static/' existe
    os.makedirs("static", exist_ok=True)

    for idx, scene in enumerate(layout_data["scenes"]):
        output = f"static/scene_{idx + 1}.png"
        compose_image_with_bubbles(
            image_url=scene["image"],
            dialogues=scene["dialogues"],
            output_path=output
        )
        scene_images.append(output)

    final_page_path = "static/final_page.png"
    compose_comic_page(scene_images, final_page_path)
    return [final_page_path]
