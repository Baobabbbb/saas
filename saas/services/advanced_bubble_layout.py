"""
Service de layout avancé pour les bandes dessinées améliorées par CrewAI
Gère le placement intelligent des bulles selon les métadonnées CrewAI
"""

from PIL import Image, ImageDraw, ImageFont
import math
import json
from typing import Dict, List, Tuple, Optional

class AdvancedBubbleLayout:
    """
    Gestionnaire avancé de layout pour les bulles de BD
    Utilise les métadonnées CrewAI pour un placement optimal
    """
    
    # Types de bulles selon les standards BD
    BUBBLE_TYPES = {
        'speech': {
            'fill': (255, 255, 255, 220),
            'outline': 'black',
            'outline_width': 2,
            'tail_style': 'normal'
        },
        'thought': {
            'fill': (240, 248, 255, 200),
            'outline': 'gray',
            'outline_width': 1,
            'tail_style': 'bubbles'
        },
        'shout': {
            'fill': (255, 255, 255, 240),
            'outline': 'black',
            'outline_width': 4,
            'tail_style': 'jagged'
        },
        'whisper': {
            'fill': (250, 250, 250, 180),
            'outline': 'lightgray',
            'outline_width': 1,
            'tail_style': 'dashed'
        }
    }
    
    def __init__(self, font_path: str = "C:/Windows/Fonts/arial.ttf"):
        self.font_path = font_path
        self.base_font_size = 18
        
    def _get_font(self, size: int = None) -> ImageFont.FreeTypeFont:
        """Obtient la police avec la taille spécifiée"""
        try:
            return ImageFont.truetype(self.font_path, size or self.base_font_size)
        except:
            return ImageFont.load_default()
    
    def calculate_optimal_bubble_size(self, text: str, font: ImageFont.FreeTypeFont, max_width: int = 300) -> Tuple[int, int]:
        """
        Calcule la taille optimale d'une bulle selon le texte
        
        Returns:
            Tuple[int, int]: (width, height) optimaux
        """
        # Divise le texte en lignes optimales
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.getlength(test_line) <= max_width - 40:  # Marge intérieure
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Calcule les dimensions
        if not lines:
            return 100, 60
            
        max_line_width = max(font.getlength(line) for line in lines)
        width = int(max_line_width + 40)  # Marges
        height = int(len(lines) * (font.size + 4) + 30)  # Espacement + marges
        
        return width, height
    
    def _find_optimal_position(self, img_width: int, img_height: int, 
                             bubble_width: int, bubble_height: int,
                             character_position: Tuple[int, int],
                             existing_bubbles: List[Dict],
                             reading_order: int) -> Tuple[int, int]:
        """
        Trouve la position optimale pour une bulle en évitant les collisions
        et en respectant l'ordre de lecture
        """
        char_x, char_y = character_position
        
        # Zones préférentielles selon l'ordre de lecture
        if reading_order == 0:  # Première bulle - en haut à gauche
            preferred_zones = [
                (int(img_width * 0.1), int(img_height * 0.05)),
                (int(img_width * 0.05), int(img_height * 0.15)),
                (int(img_width * 0.2), int(img_height * 0.1))
            ]
        elif reading_order == 1:  # Deuxième bulle - en haut à droite
            preferred_zones = [
                (int(img_width * 0.6), int(img_height * 0.05)),
                (int(img_width * 0.7), int(img_height * 0.15)),
                (int(img_width * 0.5), int(img_height * 0.1))
            ]
        else:  # Bulles suivantes - adaptatives
            preferred_zones = [
                (int(img_width * 0.3), int(img_height * 0.25)),
                (int(img_width * 0.1), int(img_height * 0.35)),
                (int(img_width * 0.6), int(img_height * 0.3))
            ]
        
        # Teste chaque zone préférentielle
        for x, y in preferred_zones:
            # Vérifie que la bulle reste dans l'image
            if (x + bubble_width <= img_width - 10 and 
                y + bubble_height <= img_height - 10 and
                x >= 10 and y >= 10):
                
                # Vérifie les collisions avec les bulles existantes
                bubble_rect = (x, y, x + bubble_width, y + bubble_height)
                collision = False
                
                for existing in existing_bubbles:
                    existing_rect = (
                        existing['x'], existing['y'],
                        existing['x'] + existing['width'],
                        existing['y'] + existing['height']
                    )
                    if self._rectangles_overlap(bubble_rect, existing_rect):
                        collision = True
                        break
                
                if not collision:
                    return x, y
        
        # Si aucune position optimale trouvée, utilise une position de fallback
        return self._fallback_position(img_width, img_height, bubble_width, bubble_height, existing_bubbles)
    
    def _rectangles_overlap(self, rect1: Tuple[int, int, int, int], rect2: Tuple[int, int, int, int]) -> bool:
        """Vérifie si deux rectangles se chevauchent"""
        x1, y1, x2, y2 = rect1
        x3, y3, x4, y4 = rect2
        
        return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1)
    
    def _fallback_position(self, img_width: int, img_height: int,
                          bubble_width: int, bubble_height: int,
                          existing_bubbles: List[Dict]) -> Tuple[int, int]:
        """Position de fallback si aucune position optimale trouvée"""
        # Grille de positions possibles
        grid_x = 3
        grid_y = 3
        
        for y_step in range(grid_y):
            for x_step in range(grid_x):
                x = int((img_width - bubble_width) * x_step / (grid_x - 1))
                y = int((img_height - bubble_height) * y_step / (grid_y - 1))
                
                # Assure que c'est dans les limites
                x = max(10, min(x, img_width - bubble_width - 10))
                y = max(10, min(y, img_height - bubble_height - 10))
                
                bubble_rect = (x, y, x + bubble_width, y + bubble_height)
                collision = False
                
                for existing in existing_bubbles:
                    existing_rect = (
                        existing['x'], existing['y'],
                        existing['x'] + existing['width'],
                        existing['y'] + existing['height']
                    )
                    if self._rectangles_overlap(bubble_rect, existing_rect):
                        collision = True
                        break
                
                if not collision:
                    return x, y
        
        # Position absolue de fallback
        return 10, 10
    
    def draw_advanced_bubble(self, draw: ImageDraw.Draw, text: str, 
                           bubble_type: str, position: Tuple[int, int],
                           size: Tuple[int, int], character_pos: Tuple[int, int],
                           font: ImageFont.FreeTypeFont):
        """
        Dessine une bulle avancée selon son type et les spécifications CrewAI
        """
        x, y = position
        width, height = size
        char_x, char_y = character_pos
        
        bubble_config = self.BUBBLE_TYPES.get(bubble_type, self.BUBBLE_TYPES['speech'])
        
        # Dessine la bulle principale
        bubble_rect = [x, y, x + width, y + height]
        
        if bubble_type == 'thought':
            # Bulle de pensée avec forme plus arrondie
            draw.ellipse(bubble_rect, 
                        fill=bubble_config['fill'],
                        outline=bubble_config['outline'],
                        width=bubble_config['outline_width'])
        elif bubble_type == 'shout':
            # Bulle de cri avec forme dentelée
            self._draw_jagged_bubble(draw, bubble_rect, bubble_config)
        else:
            # Bulle normale arrondie
            draw.rounded_rectangle(bubble_rect, 
                                 radius=15,
                                 fill=bubble_config['fill'],
                                 outline=bubble_config['outline'],
                                 width=bubble_config['outline_width'])
        
        # Dessine la queue selon le type
        self._draw_bubble_tail(draw, bubble_type, x, y, width, height, char_x, char_y, bubble_config)
        
        # Dessine le texte
        self._draw_bubble_text(draw, text, x, y, width, height, font, bubble_type)
    
    def _draw_jagged_bubble(self, draw: ImageDraw.Draw, rect: List[int], config: Dict):
        """Dessine une bulle dentelée pour les cris"""
        x1, y1, x2, y2 = rect
        
        # Crée des points dentelés sur le contour
        points = []
        steps = 20
        
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            radius_base = min((x2-x1)/2, (y2-y1)/2)
            radius_variation = radius_base * 0.1 * (1 if i % 2 == 0 else -1)
            radius = radius_base + radius_variation
            
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        
        draw.polygon(points, fill=config['fill'], outline=config['outline'])
    
    def _draw_bubble_tail(self, draw: ImageDraw.Draw, bubble_type: str,
                         x: int, y: int, width: int, height: int,
                         char_x: int, char_y: int, config: Dict):
        """Dessine la queue de la bulle selon son type"""
        
        # Position de départ de la queue (bord de la bulle)
        bubble_center_x = x + width // 2
        bubble_bottom = y + height
        
        # Direction vers le personnage
        dx = char_x - bubble_center_x
        tail_start_x = bubble_center_x + (dx // 3)  # Point sur le bord
        tail_start_x = max(x + 10, min(tail_start_x, x + width - 10))
        
        if bubble_type == 'thought':
            # Queue avec petites bulles pour les pensées
            self._draw_thought_bubbles(draw, tail_start_x, bubble_bottom, char_x, char_y, config)
        elif bubble_type == 'whisper':
            # Queue pointillée pour les chuchotements
            self._draw_dashed_tail(draw, tail_start_x, bubble_bottom, char_x, char_y, config)
        else:
            # Queue normale triangulaire
            self._draw_normal_tail(draw, tail_start_x, bubble_bottom, char_x, char_y, config)
    
    def _draw_thought_bubbles(self, draw: ImageDraw.Draw, start_x: int, start_y: int,
                            char_x: int, char_y: int, config: Dict):
        """Dessine des petites bulles pour les pensées"""
        # Trois petites bulles décroissantes
        sizes = [8, 6, 4]
        
        dx = (char_x - start_x) / 4
        dy = (char_y - start_y) / 4
        
        for i, size in enumerate(sizes):
            bubble_x = start_x + dx * (i + 1) - size // 2
            bubble_y = start_y + dy * (i + 1) - size // 2
            
            draw.ellipse([bubble_x, bubble_y, bubble_x + size, bubble_y + size],
                        fill=config['fill'], outline=config['outline'])
    
    def _draw_dashed_tail(self, draw: ImageDraw.Draw, start_x: int, start_y: int,
                         char_x: int, char_y: int, config: Dict):
        """Dessine une queue pointillée"""
        # Ligne pointillée vers le personnage
        segments = 5
        dx = (char_x - start_x) / segments
        dy = (char_y - start_y) / segments
        
        for i in range(0, segments, 2):  # Segments alternés
            x1 = start_x + dx * i
            y1 = start_y + dy * i
            x2 = start_x + dx * (i + 1)
            y2 = start_y + dy * (i + 1)
            
            draw.line([(x1, y1), (x2, y2)], fill=config['outline'], width=2)
    
    def _draw_normal_tail(self, draw: ImageDraw.Draw, start_x: int, start_y: int,
                         char_x: int, char_y: int, config: Dict):
        """Dessine une queue triangulaire normale"""
        # Triangle pointant vers le personnage
        tail_width = 20
        tail_length = min(40, abs(char_y - start_y) // 2)
        
        # Points du triangle
        left_x = start_x - tail_width // 2
        right_x = start_x + tail_width // 2
        tip_x = start_x + (char_x - start_x) // 3
        tip_y = start_y + tail_length
        
        # Assure que la pointe ne dépasse pas trop
        tip_y = min(tip_y, char_y - 10)
        
        triangle_points = [
            (left_x, start_y),
            (right_x, start_y),
            (tip_x, tip_y)
        ]
        
        draw.polygon(triangle_points, 
                    fill=config['fill'], 
                    outline=config['outline'])
    
    def _draw_bubble_text(self, draw: ImageDraw.Draw, text: str,
                         x: int, y: int, width: int, height: int,
                         font: ImageFont.FreeTypeFont, bubble_type: str):
        """Dessine le texte dans la bulle avec un alignement optimal"""
        
        # Divise le texte en lignes
        words = text.split()
        lines = []
        current_line = ""
        max_line_width = width - 20  # Marges
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.getlength(test_line) <= max_line_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Calcule la position verticale centré
        total_text_height = len(lines) * font.size
        start_y = y + (height - total_text_height) // 2
        
        # Couleur du texte selon le type de bulle
        text_color = "black"
        if bubble_type == 'shout':
            text_color = "black"
        elif bubble_type == 'whisper':
            text_color = "gray"
        
        # Dessine chaque ligne centrée
        for i, line in enumerate(lines):
            line_width = font.getlength(line)
            line_x = x + (width - line_width) // 2
            line_y = start_y + i * font.size
            
            draw.text((line_x, line_y), line, fill=text_color, font=font)

# Instance globale
advanced_bubble_layout = AdvancedBubbleLayout()
