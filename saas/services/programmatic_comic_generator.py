#!/usr/bin/env python3
"""
Générateur d'images de BD programmées - Solution temporaire
"""

from PIL import Image, ImageDraw, ImageFont
import random
from pathlib import Path
import json

class ProgrammaticComicGenerator:
    """Génère des images de BD programmées qui ressemblent à de vraies scènes"""
    
    def __init__(self):
        self.colors = {
            'sky': ['#87CEEB', '#87CEFA', '#B0E0E6', '#ADD8E6'],
            'grass': ['#90EE90', '#98FB98', '#9ACD32', '#32CD32'],
            'trees': ['#228B22', '#32CD32', '#006400', '#008000'],
            'characters': ['#FFB6C1', '#FFA07A', '#F0E68C', '#DDA0DD'],
            'clothes': ['#FF6347', '#4682B4', '#9370DB', '#20B2AA']
        }
        
        self.art_styles = {
            'cartoon': {
                'line_width': 3,
                'saturation': 1.2,
                'roundness': 0.8
            },
            'realistic': {
                'line_width': 1,
                'saturation': 0.9,
                'roundness': 0.3
            },
            'manga': {
                'line_width': 2,
                'saturation': 0.7,
                'roundness': 0.5
            },
            'comics': {
                'line_width': 4,
                'saturation': 1.5,
                'roundness': 0.2
            },
            'watercolor': {
                'line_width': 1,
                'saturation': 0.8,
                'roundness': 0.9
            }
        }
    
    def generate_scene(self, prompt: str, art_style: str, seed: int, output_path: Path) -> Path:
        """Génère une scène de BD basée sur le prompt et le style"""
        
        # Utiliser la seed pour avoir des résultats déterministes
        random.seed(seed)
        
        # Créer l'image
        img = Image.new('RGB', (1024, 768), color='white')
        draw = ImageDraw.Draw(img)
        
        style_config = self.art_styles.get(art_style, self.art_styles['cartoon'])
        
        # Analyser le prompt pour déterminer les éléments à dessiner
        elements = self._analyze_prompt(prompt)
        
        # Dessiner l'arrière-plan
        self._draw_background(draw, elements, style_config)
        
        # Dessiner les personnages
        self._draw_characters(draw, elements, style_config)
        
        # Dessiner les objets
        self._draw_objects(draw, elements, style_config)
        
        # Ajouter la bordure de case BD
        self._draw_comic_border(draw, style_config)
        
        # Ajouter le style artistique
        self._apply_art_style(img, art_style)
        
        # Sauvegarder
        img.save(output_path)
        print(f"🎨 Image programmée générée: {output_path} (style: {art_style}, seed: {seed})")
        
        return output_path
    
    def _analyze_prompt(self, prompt: str) -> dict:
        """Analyse le prompt pour extraire les éléments à dessiner"""
        prompt_lower = prompt.lower()
        
        elements = {
            'setting': 'outdoor',
            'characters': [],
            'objects': [],
            'mood': 'happy'
        }
        
        # Détecter l'environnement
        if any(word in prompt_lower for word in ['forest', 'tree', 'jungle', 'wood']):
            elements['setting'] = 'forest'
        elif any(word in prompt_lower for word in ['space', 'planet', 'star', 'rocket']):
            elements['setting'] = 'space'
        elif any(word in prompt_lower for word in ['ocean', 'sea', 'beach', 'water']):
            elements['setting'] = 'ocean'
        elif any(word in prompt_lower for word in ['castle', 'kingdom', 'palace']):
            elements['setting'] = 'castle'
        
        # Détecter les personnages
        if any(word in prompt_lower for word in ['child', 'kid', 'boy', 'girl']):
            elements['characters'].append('child')
        if any(word in prompt_lower for word in ['animal', 'cat', 'dog', 'rabbit', 'lion']):
            elements['characters'].append('animal')
        if any(word in prompt_lower for word in ['wizard', 'magic', 'fairy']):
            elements['characters'].append('magical')
        
        # Si pas de personnages détectés, ajouter un personnage par défaut
        if not elements['characters']:
            elements['characters'].append('child')
        
        return elements
    
    def _draw_background(self, draw, elements, style_config):
        """Dessine l'arrière-plan selon l'environnement"""
        setting = elements['setting']
        
        if setting == 'forest':
            # Ciel
            draw.rectangle([0, 0, 1024, 300], fill=random.choice(self.colors['sky']))
            # Sol
            draw.rectangle([0, 300, 1024, 768], fill=random.choice(self.colors['grass']))
            # Arbres
            for i in range(5):
                x = random.randint(50, 950)
                self._draw_tree(draw, x, 250, style_config)
                
        elif setting == 'space':
            # Espace noir avec étoiles
            draw.rectangle([0, 0, 1024, 768], fill='#0B0B2F')
            for _ in range(20):
                x, y = random.randint(0, 1024), random.randint(0, 400)
                draw.ellipse([x, y, x+3, y+3], fill='white')
            # Planète
            draw.ellipse([700, 100, 900, 300], fill='#FF6B6B')
            
        elif setting == 'ocean':
            # Ciel
            draw.rectangle([0, 0, 1024, 400], fill='#87CEEB')
            # Mer
            draw.rectangle([0, 400, 1024, 768], fill='#4682B4')
            # Vagues
            for i in range(3):
                y = 420 + i * 30
                draw.ellipse([0, y, 1024, y + 40], fill='#5F9EA0')
                
        else:  # outdoor par défaut
            # Ciel
            draw.rectangle([0, 0, 1024, 350], fill=random.choice(self.colors['sky']))
            # Sol
            draw.rectangle([0, 350, 1024, 768], fill=random.choice(self.colors['grass']))
            # Soleil
            draw.ellipse([800, 50, 900, 150], fill='#FFD700')
    
    def _draw_tree(self, draw, x, y, style_config):
        """Dessine un arbre"""
        # Tronc
        trunk_width = 15 + random.randint(-5, 5)
        draw.rectangle([x, y, x + trunk_width, y + 100], fill='#8B4513')
        
        # Feuillage
        foliage_color = random.choice(self.colors['trees'])
        size = 60 + random.randint(-20, 20)
        draw.ellipse([x - size//2, y - size//2, x + size//2 + trunk_width, y + size//2], fill=foliage_color)
    
    def _draw_characters(self, draw, elements, style_config):
        """Dessine les personnages"""
        char_count = len(elements['characters'])
        spacing = 1024 // (char_count + 1)
        
        for i, char_type in enumerate(elements['characters']):
            x = spacing * (i + 1)
            y = 400
            self._draw_character(draw, char_type, x, y, style_config)
    
    def _draw_character(self, draw, char_type, x, y, style_config):
        """Dessine un personnage"""
        colors = random.choice(self.colors['characters'])
        clothes_color = random.choice(self.colors['clothes'])
        
        if char_type == 'child':
            # Tête
            draw.ellipse([x-30, y-60, x+30, y], fill=colors)
            # Corps
            draw.rectangle([x-20, y, x+20, y+80], fill=clothes_color)
            # Bras
            draw.rectangle([x-40, y+10, x-20, y+50], fill=colors)
            draw.rectangle([x+20, y+10, x+40, y+50], fill=colors)
            # Jambes
            draw.rectangle([x-15, y+80, x-5, y+140], fill='#0000FF')
            draw.rectangle([x+5, y+80, x+15, y+140], fill='#0000FF')
            
        elif char_type == 'animal':
            # Corps d'animal simple
            draw.ellipse([x-25, y-20, x+25, y+20], fill=colors)
            # Tête
            draw.ellipse([x-20, y-40, x+20, y], fill=colors)
            # Pattes
            for dx in [-15, -5, 5, 15]:
                draw.rectangle([x+dx, y+15, x+dx+5, y+35], fill=colors)
    
    def _draw_objects(self, draw, elements, style_config):
        """Dessine des objets selon le contexte"""
        # Ajouter quelques objets décoratifs
        pass
    
    def _draw_comic_border(self, draw, style_config):
        """Dessine la bordure de case de BD"""
        border_width = max(2, int(style_config['line_width'] * 2))
        color = '#000000'
        
        # Bordures
        draw.rectangle([0, 0, 1024, border_width], fill=color)
        draw.rectangle([0, 768-border_width, 1024, 768], fill=color)
        draw.rectangle([0, 0, border_width, 768], fill=color)
        draw.rectangle([1024-border_width, 0, 1024, 768], fill=color)
    
    def _apply_art_style(self, img, art_style):
        """Applique des effets selon le style artistique"""
        # Pour l'instant, juste les bordures et couleurs de base
        # Ici on pourrait ajouter des filtres, des textures, etc.
        pass

# Instance globale
programmatic_generator = ProgrammaticComicGenerator()
