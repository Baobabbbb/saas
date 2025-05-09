from PIL import Image
import os

def compose_comic_page(images, output_path):
    padding = 20
    vignette_height = 600
    vignette_width = 800
    total_height = padding + (vignette_height + padding) * len(images)
    total_width = vignette_width + 2 * padding

    page = Image.new("RGB", (total_width, total_height), "white")

    y_offset = padding
    for img_path in images:
        img = Image.open(img_path).resize((vignette_width, vignette_height))
        page.paste(img, (padding, y_offset))
        y_offset += vignette_height + padding

    page.save(output_path)
    return output_path
