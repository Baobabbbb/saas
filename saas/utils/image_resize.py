from PIL import Image
import os

def resize_image_if_needed(image_path, min_pixels=262144):
    with Image.open(image_path) as img:
        width, height = img.size
        if width * height >= min_pixels:
            return image_path  # Pas besoin de redimensionner

        # Calcul de la nouvelle taille proportionnelle
        scale_factor = (min_pixels / (width * height)) ** 0.5
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Chemin de sauvegarde
        base, ext = os.path.splitext(image_path)
        resized_path = f"{base}_resized{ext}"
        resized_img.save(resized_path)

        return resized_path
