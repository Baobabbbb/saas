from PIL import Image
import os

MIN_SIZE = 512

def resize_image_if_needed(image_path, min_size=MIN_SIZE):
    """
    Redimensionne si besoin pour min 512x512, conserve le ratio, force format PNG,
    renvoie le chemin du fichier à utiliser (copie si redimensionnement, sinon chemin original).
    """
    base, _ = os.path.splitext(image_path)
    resized_path = f"{base}_resized.png"

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width >= min_size and height >= min_size:
                return image_path

            scale = max(min_size / width, min_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            img_resized.save(resized_path, format="PNG")
            print(f"🖼 Image redimensionnée à {new_width}x{new_height} → {resized_path}")
            return resized_path
    except Exception as e:
        print(f"❌ Erreur resize image : {e}")
        return image_path
