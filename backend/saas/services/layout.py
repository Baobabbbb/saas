from PIL import Image
import os
import math

def compose_comic_pages(images, output_prefix="static/page"):
    padding = 20
    vignette_width = 800
    vignette_height = 600
    cols = 2
    rows = 2
    per_page = cols * rows
    pages = []

    total_pages = math.ceil(len(images) / per_page)

    for page_num in range(total_pages):
        page_images = images[page_num * per_page : (page_num + 1) * per_page]
        page_width = cols * vignette_width + (cols + 1) * padding
        page_height = rows * vignette_height + (rows + 1) * padding
        page = Image.new("RGB", (page_width, page_height), "white")

        for i, img_path in enumerate(page_images):
            img = Image.open(img_path).resize((vignette_width, vignette_height))
            x = padding + (i % cols) * (vignette_width + padding)
            y = padding + (i // cols) * (vignette_height + padding)
            page.paste(img, (x, y))

        output_path = f"{output_prefix}_{page_num + 1}.png"
        page.save(output_path)
        pages.append(output_path)

    return pages
