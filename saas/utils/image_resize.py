from PIL import Image
import os

# Seuil minimal recommandé par Stability SD3 : 512x512
MIN_SIZE = 512

def resize_image_if_needed(image_path, min_size=MIN_SIZE):
    """
    Prend le chemin d'une image, redimensionne si besoin pour SD3 (minimum 512x512),
    sauvegarde une copie "_resized" dans le même dossier et retourne le chemin du fichier.
    Si pas besoin de redimensionner, retourne le chemin d'origine.
    """
    # Génère le nom de fichier pour la copie redimensionnée
    base, ext = os.path.splitext(image_path)
    resized_path = f"{base}_resized{ext}"

    try:
        with Image.open(image_path) as img:
            width, height = img.size

            # Si l'image est déjà assez grande, pas besoin de resize
            if width >= min_size and height >= min_size:
                return image_path

            # Sinon, calcule les nouvelles dimensions (conserve le ratio)
            scale = max(min_size / width, min_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)

            # Sauvegarde la nouvelle image
            img_resized.save(resized_path, format="PNG")
            print(f"🖼 Image redimensionnée à {new_width}x{new_height} → {resized_path}")
            return resized_path
    except Exception as e:
        print(f"❌ Erreur resize image : {e}")
        # Si souci, retourne l'original, mais log l'erreur
        return image_path
