#!/usr/bin/env python3
"""Script pour créer une image placeholder pour les erreurs de BD"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image():
    # Créer le répertoire static s'il n'existe pas
    os.makedirs('static', exist_ok=True)
    
    # Créer une image 1024x768 avec fond bleu clair
    img = Image.new('RGB', (1024, 768), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Essayer de charger une police, sinon utiliser la police par défaut
    try:
        # Pour Windows
        font_title = ImageFont.truetype("arial.ttf", 48)
        font_text = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            # Pour macOS/Linux
            font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            font_text = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            # Police par défaut
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
    
    # Dessiner le titre
    title = "Page de BD"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = bbox[2] - bbox[0]
    title_height = bbox[3] - bbox[1]
    x = (1024 - title_width) // 2
    y = (768 - title_height) // 2 - 50
    draw.text((x, y), title, fill='darkblue', font=font_title)
    
    # Dessiner le sous-texte
    subtitle = "Erreur de génération - Placeholder"
    bbox = draw.textbbox((0, 0), subtitle, font=font_text)
    subtitle_width = bbox[2] - bbox[0]
    x = (1024 - subtitle_width) // 2
    y = y + title_height + 20
    draw.text((x, y), subtitle, fill='navy', font=font_text)
    
    # Dessiner un cadre décoratif
    draw.rectangle([50, 50, 1024-50, 768-50], outline='darkblue', width=5)
    draw.rectangle([80, 80, 1024-80, 768-80], outline='blue', width=2)
    
    # Sauvegarder l'image
    img.save('static/placeholder_comic.png')
    print("✅ Image placeholder créée: static/placeholder_comic.png")

if __name__ == "__main__":
    create_placeholder_image()
