from PIL import Image
import os

# Les tailles minimales requises par Stability AI pour SD3 : >= 512x512 (et généralement <= 1536)
MIN_SIZE = 512
MAX_SIZE = 1536

def resize_image_if_needed(image_path):
    """
    Vérifie et redimensionne l'image pour être carrée, >= 512x512, <= 1536x1536.
    Renvoie le chemin du fichier redimensionné (si redimensionné) ou l'original sinon.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as img:
        width, height = img.size

        # Détermine la taille de base carrée
        new_side = min(max(width, height, MIN_SIZE), MAX_SIZE)

        if width == height and MIN_SIZE <= width <= MAX_SIZE:
            return image_path  # Déjà correct

        # Nouvelle image blanche carrée
        new_img = Image.new("RGBA", (new_side, new_side), (255, 255, 255, 0))
        left = (new_side - width) // 2
        top = (new_side - height) // 2
        new_img.paste(img, (left, top))

        # Enregistre la nouvelle image redimensionnée dans le même dossier
        dirpath, fname = os.path.split(image_path)
        base, ext = os.path.splitext(fname)
        resized_path = os.path.join(dirpath, f"{base}_resized.png")
        new_img.save(resized_path, "PNG")
        print(f"🖼 Image redimensionnée à {new_side}x{new_side} → {resized_path}")
        return resized_path
