#!/usr/bin/env python3
"""
Test des bulles de dialogue réalistes pour les BD
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from saas.services.stable_diffusion_generator import StableDiffusionGenerator
from PIL import Image, ImageDraw
import tempfile

def test_comic_bubbles():
    """Test des différents types de bulles de dialogue"""
    
    # Créer une image de test
    img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Dessiner un fond simple
    draw.rectangle([50, 50, 750, 550], fill='white', outline='black', width=2)
    draw.text((400, 300), "Test BD", fill='black', anchor='mm')
    
    # Créer le générateur
    generator = StableDiffusionGenerator()
    
    # Créer des dialogues de test
    test_dialogues = [
        {
            "character": "Héros",
            "text": "Bonjour ! Je suis le héros de cette histoire !",
            "type": "speech"
        },
        {
            "character": "Héros",
            "text": "Qu'est-ce qui va m'arriver ?",
            "type": "thought"
        },
        {
            "character": "Héros",
            "text": "ATTENTION ! Un danger approche !",
            "type": "shout"
        },
        {
            "character": "Ami",
            "text": "Chut... Il faut être discret...",
            "type": "whisper"
        }
    ]
    
    # Positions pour les bulles
    positions = [
        (100, 100, 180, 80),   # speech
        (450, 120, 200, 100),  # thought
        (150, 350, 220, 90),   # shout
        (500, 380, 190, 70),   # whisper
    ]
    
    # Dessiner chaque type de bulle
    for i, (dialogue, pos) in enumerate(zip(test_dialogues, positions)):
        x, y, w, h = pos
        
        print(f"🎨 Dessin bulle {i+1}: {dialogue['type']} - '{dialogue['text'][:30]}...'")
        
        if dialogue['type'] == 'speech':
            generator._draw_speech_bubble(draw, x, y, w, h)
        elif dialogue['type'] == 'thought':
            generator._draw_thought_bubble(draw, x, y, w, h)
        elif dialogue['type'] == 'shout':
            generator._draw_shout_bubble(draw, x, y, w, h)
        elif dialogue['type'] == 'whisper':
            generator._draw_whisper_bubble(draw, x, y, w, h)
        
        # Ajouter le texte
        generator._draw_bubble_text(draw, x, y, w, h, dialogue['text'])
    
    # Sauvegarder l'image de test
    test_path = Path("test_comic_bubbles.png")
    img.save(test_path)
    
    print(f"✅ Test terminé ! Image sauvegardée : {test_path}")
    print("🎨 L'image contient 4 types de bulles :")
    print("   - Bulle de dialogue classique (ovale avec queue)")
    print("   - Bulle de pensée (forme nuage)")
    print("   - Bulle de cri (forme explosive)")
    print("   - Bulle de chuchotement (pointillés)")
    
    return test_path

if __name__ == "__main__":
    test_comic_bubbles()
