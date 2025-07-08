"""
Module d'amélioration IA pour les bulles de bande dessinée
Utilise GPT-4o pour l'analyse d'images et GPT-4o-mini pour les dialogues
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import openai
import base64
import json
import os
import math
import asyncio
from typing import Dict, List, Tuple, Any
from pathlib import Path
from dotenv import load_dotenv


class ComicAIEnhancer:
    def __init__(self):
        """Initialise le module IA pour l'amélioration des BD"""
        load_dotenv()
        
        # Configuration OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-test-"):
            print("⚠️ Clé API OpenAI manquante ou factice - Mode test activé")
            self.openai_client = None
            self.test_mode = True
        else:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=api_key)
            self.test_mode = False
        
        # Configuration des modèles
        self.vision_model = os.getenv("COMIC_VISION_MODEL", "gpt-4o")
        self.text_model = os.getenv("COMIC_TEXT_MODEL", "gpt-4o-mini")
        self.enabled = os.getenv("ENABLE_AI_BUBBLES", "true").lower() == "true"
        
    async def enhance_comic_page(self, 
                                image_path: str, 
                                story_context: Dict[str, Any],
                                comic_dir: Path,
                                page_number: int) -> Path:
        """
        Analyse l'image et génère des bulles cohérentes avec IA
        Retourne le chemin de l'image améliorée
        """
        if not self.enabled:
            # Si l'IA est désactivée, retourner l'image originale
            print("⚠️ IA désactivée - retour image originale")
            final_path = comic_dir / f"page_{page_number}_final.png"
            img = Image.open(image_path)
            img.save(final_path, 'PNG')
            return final_path
        
        try:
            print(f"🤖 Amélioration IA de la page {page_number}...")
            
            # 1. Analyser l'image pour détecter les personnages
            character_positions = await self._detect_characters(image_path)
            
            # 2. Générer des dialogues cohérents avec l'histoire
            characters = [story_context.get("hero_name", "Héros")]
            dialogues = await self._generate_contextual_dialogues(
                story_context, page_number, characters, character_positions
            )
            
            # 3. Optimiser le placement des bulles
            optimized_bubbles = self._optimize_bubble_placement(
                dialogues, character_positions
            )
            
            # 4. Appliquer les bulles sur l'image et sauvegarder
            final_path = await self._apply_ai_bubbles(
                image_path, optimized_bubbles, comic_dir, page_number
            )
            
            print(f"✅ Page {page_number} améliorée avec {len(dialogues)} bulles")
            
            return final_path
            
        except Exception as e:
            print(f"⚠️ Erreur lors de l'amélioration IA de la page {page_number}: {e}")
            # Fallback : retourner l'image originale
            final_path = comic_dir / f"page_{page_number}_final.png"
            img = Image.open(image_path)
            img.save(final_path, 'PNG')
            return final_path
    
    async def _detect_characters(self, image_path: str) -> Dict[str, Any]:
        """
        Utilise GPT-4o pour détecter les personnages dans l'image
        """
        if self.test_mode:
            print("🧪 Mode test: génération de données factices pour la détection de personnages")
            return {
                "characters": [
                    {
                        "name": "Héros principal",
                        "position": {"x": 0.3, "y": 0.6},
                        "description": "Personnage principal au centre de l'image"
                    }
                ],
                "free_zones": [
                    {"x": 0.1, "y": 0.1, "width": 0.25, "height": 0.15},
                    {"x": 0.65, "y": 0.05, "width": 0.3, "height": 0.2}
                ]
            }
        
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = await self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyse cette image de bande dessinée et détecte :
                                1. Position des personnages (x,y en pourcentage 0.0-1.0)
                                2. Leur orientation (left/right/front)
                                3. Leur expression (happy/sad/angry/neutral/surprised/excited)
                                4. Zones libres pour bulles de dialogue
                                
                                Réponds UNIQUEMENT en JSON valide :
                                {
                                    "characters": [
                                        {
                                            "position": {"x": 0.3, "y": 0.6},
                                            "orientation": "right",
                                            "expression": "happy",
                                            "size": {"width": 0.2, "height": 0.4}
                                        }
                                    ],
                                    "free_zones": [
                                        {"x": 0.1, "y": 0.1, "width": 0.3, "height": 0.2}
                                    ]
                                }"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"⚠️ Erreur détection personnages: {e}")
            # Fallback basique
            return {
                "characters": [
                    {
                        "position": {"x": 0.5, "y": 0.6},
                        "orientation": "front",
                        "expression": "neutral",
                        "size": {"width": 0.2, "height": 0.3}
                    }
                ],
                "free_zones": [
                    {"x": 0.1, "y": 0.1, "width": 0.3, "height": 0.2},
                    {"x": 0.6, "y": 0.1, "width": 0.3, "height": 0.2}
                ]
            }
    
    async def _generate_contextual_dialogues(self, 
                                           story_context: str,
                                           page_number: int,
                                           characters: List[str],
                                           character_positions: Dict) -> List[Dict[str, Any]]:
        """
        Génère des dialogues cohérents avec GPT-4o-mini
        """
        if self.test_mode:
            print("🧪 Mode test: génération de dialogues factices")
            return [
                {
                    "text": "Quelle aventure nous attend ?",
                    "character": "Héros principal",
                    "type": "speech",
                    "emotion": "curious"
                },
                {
                    "text": "Je sens un mystère...",
                    "character": "Héros principal",
                    "type": "thought",
                    "emotion": "mysterious"
                }
            ]
        
        try:
            detected_chars = character_positions.get("characters", [])
            num_chars = min(len(detected_chars), 2)  # Max 2 dialogues par page
            
            if num_chars == 0:
                return []
            
            # Analyser les expressions pour adapter les dialogues
            expressions = [char.get("expression", "neutral") for char in detected_chars]
            
            # Convertir les caractères en chaînes
            character_names = []
            for char in characters:
                if isinstance(char, dict):
                    character_names.append(char.get("name", "Personnage"))
                else:
                    character_names.append(str(char))
            
            prompt = f"""Tu es un scénariste BD expert. Génère {num_chars} dialogues courts (5-12 mots max) pour cette page.

Contexte : {story_context}
Page : {page_number}
Personnages : {', '.join(character_names)}
Expressions détectées : {expressions}

Règles :
- Dialogues courts et impactants
- Cohérents avec l'histoire et les expressions
- Types selon l'émotion :
  * "speech" : dialogue normal
  * "thought" : pensée interne
  * "shout" : exclamation/cri
  * "whisper" : chuchotement

Réponds en JSON valide :
{{
    "dialogues": [
        {{
            "character_index": 0,
            "text": "Dialogue court",
            "type": "speech",
            "emotion": "happy"
        }}
    ]
}}"""
            
            response = await self.openai_client.chat.completions.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("dialogues", [])
            
        except Exception as e:
            print(f"⚠️ Erreur génération dialogues: {e}")
            # Fallback avec dialogues génériques
            return [
                {
                    "character_index": 0,
                    "text": f"Quelle aventure page {page_number} !",
                    "type": "speech",
                    "emotion": "excited"
                }
            ]
    
    def _optimize_bubble_placement(self, 
                                 dialogues: List[Dict],
                                 character_positions: Dict) -> List[Dict[str, Any]]:
        """
        Optimise le placement des bulles pour pointer vers les personnages
        """
        bubbles = []
        detected_chars = character_positions.get("characters", [])
        free_zones = character_positions.get("free_zones", [])
        
        for dialogue in dialogues:
            char_idx = dialogue.get("character_index", 0)
            
            if char_idx < len(detected_chars):
                char_pos = detected_chars[char_idx]
                
                # Calculer position optimale de la bulle
                bubble_pos = self._calculate_optimal_bubble_position(
                    char_pos, dialogue["text"], dialogue["type"], free_zones
                )
                
                # Calculer la queue pointant vers le personnage
                tail_pos = self._calculate_tail_position(char_pos, bubble_pos)
                
                bubbles.append({
                    "dialogue": dialogue,
                    "character_position": char_pos,
                    "bubble_position": bubble_pos,
                    "tail_position": tail_pos
                })
        
        return bubbles
    
    def _calculate_optimal_bubble_position(self, 
                                         char_pos: Dict,
                                         text: str,
                                         bubble_type: str,
                                         free_zones: List[Dict]) -> Dict[str, float]:
        """
        Calcule la position optimale de la bulle
        """
        # Taille basée sur le texte
        text_length = len(text)
        bubble_width = min(0.35, 0.15 + text_length * 0.008)
        bubble_height = 0.08 + (text_length // 25) * 0.02
        
        char_x = char_pos["position"]["x"]
        char_y = char_pos["position"]["y"]
        
        # Essayer de placer la bulle au-dessus du personnage
        bubble_x = char_x - bubble_width / 2
        bubble_y = char_y - bubble_height - 0.15
        
        # Ajuster si la bulle sort de l'image
        bubble_x = max(0.05, min(0.95 - bubble_width, bubble_x))
        bubble_y = max(0.05, bubble_y)
        
        # Si la bulle est trop basse, essayer à côté
        if bubble_y > 0.7:
            if char_x < 0.5:
                # Personnage à gauche, bulle à droite
                bubble_x = min(0.95 - bubble_width, char_x + 0.1)
            else:
                # Personnage à droite, bulle à gauche
                bubble_x = max(0.05, char_x - bubble_width - 0.1)
            bubble_y = char_y - bubble_height / 2
        
        return {
            "x": bubble_x,
            "y": bubble_y,
            "width": bubble_width,
            "height": bubble_height
        }
    
    def _calculate_tail_position(self, 
                               char_pos: Dict,
                               bubble_pos: Dict) -> Dict[str, Any]:
        """
        Calcule la position de la queue pour pointer vers le personnage
        """
        char_x = char_pos["position"]["x"]
        char_y = char_pos["position"]["y"]
        
        bubble_center_x = bubble_pos["x"] + bubble_pos["width"] / 2
        bubble_center_y = bubble_pos["y"] + bubble_pos["height"] / 2
        
        # Point de départ sur le bord de la bulle le plus proche du personnage
        if char_y > bubble_center_y:
            # Personnage en bas, queue part du bas de la bulle
            tail_start_x = bubble_center_x
            tail_start_y = bubble_pos["y"] + bubble_pos["height"]
        else:
            # Personnage en haut, queue part du haut de la bulle
            tail_start_x = bubble_center_x
            tail_start_y = bubble_pos["y"]
        
        # Point d'arrivée vers le personnage (légèrement au-dessus)
        tail_end_x = char_x
        tail_end_y = char_y - 0.05
        
        return {
            "start": {"x": tail_start_x, "y": tail_start_y},
            "end": {"x": tail_end_x, "y": tail_end_y}
        }
    
    async def _apply_ai_bubbles(self, 
                              image_path: str,
                              bubbles: List[Dict],
                              comic_dir: Path,
                              page_number: int) -> Path:
        """
        Applique les bulles optimisées sur l'image et sauvegarde
        """
        try:
            # Charger l'image
            image = Image.open(image_path).convert("RGBA")
            overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Charger une police
            try:
                font = ImageFont.truetype("arial.ttf", 16)
                font_small = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()
                font_small = font
            
            img_width, img_height = image.size
            
            for bubble_data in bubbles:
                dialogue = bubble_data["dialogue"]
                bubble_pos = bubble_data["bubble_position"]
                tail_pos = bubble_data["tail_position"]
                
                # Convertir coordonnées relatives en pixels
                bubble_x = int(bubble_pos["x"] * img_width)
                bubble_y = int(bubble_pos["y"] * img_height)
                bubble_w = int(bubble_pos["width"] * img_width)
                bubble_h = int(bubble_pos["height"] * img_height)
                
                # Dessiner la bulle selon le type
                bubble_type = dialogue.get("type", "speech")
                if bubble_type == "thought":
                    self._draw_thought_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h)
                elif bubble_type == "shout":
                    self._draw_shout_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h)
                elif bubble_type == "whisper":
                    self._draw_whisper_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h)
                else:
                    self._draw_speech_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h)
                
                # Dessiner la queue pointant vers le personnage
                self._draw_smart_tail(draw, tail_pos, img_width, img_height, bubble_type)
                
                # Ajouter le texte centré
                self._draw_centered_text(draw, dialogue["text"], bubble_x, bubble_y, bubble_w, bubble_h, font)
            
            # Fusionner avec l'image originale
            enhanced_image = Image.alpha_composite(image, overlay)
            
            # Sauvegarder l'image améliorée
            final_path = comic_dir / f"page_{page_number}_final.png"
            enhanced_image.convert("RGB").save(final_path, "PNG")
            
            return final_path
            
        except Exception as e:
            print(f"❌ Erreur lors de l'application des bulles: {e}")
            # Fallback: copier l'image originale
            final_path = comic_dir / f"page_{page_number}_final.png"
            img = Image.open(image_path)
            img.save(final_path, 'PNG')
            return final_path
            
        except Exception as e:
            print(f"⚠️ Erreur application bulles: {e}")
            return image_path  # Retourner l'original en cas d'erreur
    
    def _draw_speech_bubble(self, draw, x, y, width, height):
        """Bulle de dialogue classique"""
        draw.ellipse([x, y, x + width, y + height], fill="white", outline="black", width=3)
    
    def _draw_thought_bubble(self, draw, x, y, width, height):
        """Bulle de pensée (nuage)"""
        # Créer un nuage avec plusieurs cercles
        circles = []
        for i in range(8):
            cx = x + (i % 4) * width // 4 + width // 8
            cy = y + (i // 4) * height // 2 + height // 4
            radius = width // 12 + (i % 3) * 5
            circles.append((cx, cy, radius))
        
        for cx, cy, radius in circles:
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                        fill="white", outline="black", width=2)
    
    def _draw_shout_bubble(self, draw, x, y, width, height):
        """Bulle de cri (forme explosive)"""
        center_x = x + width // 2
        center_y = y + height // 2
        
        # Créer une forme en étoile
        points = []
        for i in range(16):
            angle = i * math.pi / 8
            if i % 2 == 0:
                radius = min(width, height) // 2
            else:
                radius = min(width, height) // 3
            
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        
        draw.polygon(points, fill="white", outline="black", width=4)
    
    def _draw_whisper_bubble(self, draw, x, y, width, height):
        """Bulle de chuchotement (pointillés)"""
        # Contour en pointillés
        for angle in range(0, 360, 15):
            angle_rad = math.radians(angle)
            x1 = x + width // 2 + (width // 2) * math.cos(angle_rad)
            y1 = y + height // 2 + (height // 2) * math.sin(angle_rad)
            
            if angle % 30 == 0:
                draw.ellipse([x1-2, y1-2, x1+2, y1+2], fill="black")
        
        # Remplir l'intérieur
        draw.ellipse([x + 5, y + 5, x + width - 5, y + height - 5], fill="white")
    
    def _draw_smart_tail(self, draw, tail_pos, img_width, img_height, bubble_type):
        """Dessine une queue intelligente pointant vers le personnage"""
        start_x = int(tail_pos["start"]["x"] * img_width)
        start_y = int(tail_pos["start"]["y"] * img_height)
        end_x = int(tail_pos["end"]["x"] * img_width)
        end_y = int(tail_pos["end"]["y"] * img_height)
        
        if bubble_type == "thought":
            # Petites bulles pour les pensées
            for i in range(3):
                bx = start_x + (end_x - start_x) * (i + 1) / 4
                by = start_y + (end_y - start_y) * (i + 1) / 4
                radius = 8 - i * 2
                draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], 
                           fill="white", outline="black", width=2)
        elif bubble_type == "whisper":
            # Queue en pointillés
            for i in range(0, 20, 4):
                progress = i / 20
                px = start_x + (end_x - start_x) * progress
                py = start_y + (end_y - start_y) * progress
                draw.ellipse([px-1, py-1, px+1, py+1], fill="black")
        else:
            # Queue triangulaire classique
            # Calculer les points du triangle
            dx = end_x - start_x
            dy = end_y - start_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                # Normaliser et créer les points du triangle
                ux = dx / length
                uy = dy / length
                
                # Points perpendiculaires pour la base du triangle
                px = -uy * 10
                py = ux * 10
                
                points = [
                    (start_x + px, start_y + py),
                    (start_x - px, start_y - py),
                    (end_x, end_y)
                ]
                
                draw.polygon(points, fill="white", outline="black", width=2)
    
    def _draw_centered_text(self, draw, text, x, y, width, height, font):
        """Dessine le texte centré dans la bulle"""
        # Découper le texte en lignes
        words = text.split()
        lines = []
        current_line = ""
        max_chars_per_line = max(10, width // 12)
        
        for word in words:
            if len(current_line + word) < max_chars_per_line:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        # Centrer verticalement
        line_height = 18
        total_height = len(lines) * line_height
        start_y = y + (height - total_height) // 2
        
        # Dessiner chaque ligne centrée
        for i, line in enumerate(lines[:3]):  # Max 3 lignes
            # Calculer largeur pour centrer horizontalement
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * 8
            
            text_x = x + (width - text_width) // 2
            text_y = start_y + i * line_height
            
            # Ombre pour lisibilité
            draw.text((text_x + 1, text_y + 1), line, fill="gray", font=font)
            draw.text((text_x, text_y), line, fill="black", font=font)


# Test du module
if __name__ == "__main__":
    import asyncio
    from pathlib import Path
    
    async def test_module():
        try:
            enhancer = ComicAIEnhancer()
            print("✅ Module ComicAIEnhancer initialisé avec succès")
            
            # Test avec une image factice
            test_image = Path("test_image.png")
            if test_image.exists():
                context = {
                    "page_number": 1,
                    "hero_name": "Luna",
                    "story_type": "adventure",
                    "style": "cartoon"
                }
                
                result = await enhancer.enhance_comic_page(
                    test_image,
                    context,
                    test_image.parent,
                    1
                )
                
                if result:
                    print(f"✅ Test réussi: {result}")
                else:
                    print("⚠️ Test échoué")
            else:
                print("⚠️ Image de test non trouvée")
                
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
    
    asyncio.run(test_module())
