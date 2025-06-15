"""
Service de génération d'images réelles pour les BD
"""
import os
import json
import requests
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import base64
import io

class ComicImageGenerator:
    """Générateur d'images pour BD avec création de fichiers réels"""
    
    def __init__(self):
        self.output_dir = Path("C:/Users/freda/Desktop/backend/saas/static/generated_comics")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_comic_images(self, comic_data: Dict[str, Any], spec) -> List[Dict[str, Any]]:
        """
        Génère des images réelles pour une BD et sauvegarde les fichiers
        """
        try:
            print("🎨 Génération d'images réelles pour la BD...")
            
            # Créer un dossier pour cette BD
            comic_id = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            comic_dir = self.output_dir / comic_id
            comic_dir.mkdir(exist_ok=True)
            
            pages = []
            
            # Extraire les prompts du résultat CrewAI
            prompts = self._extract_prompts_from_crewai(comic_data)
            
            for i in range(spec.num_images):
                try:
                    print(f"🖼️ Génération image {i+1}/{spec.num_images}")
                    
                    # Utiliser le prompt correspondant ou créer un fallback
                    if i < len(prompts):
                        prompt = prompts[i]
                    else:
                        prompt = self._create_fallback_prompt(spec, i)
                    
                    # Générer l'image
                    image_path = await self._generate_image_from_prompt(prompt, comic_dir, i+1, spec.style)
                    
                    # Créer les spécifications de dialogue
                    dialogues = self._create_page_dialogues(spec, i+1)
                    
                    # Appliquer les bulles de dialogue
                    final_image_path = await self._add_dialogue_bubbles(image_path, dialogues, comic_dir, i+1)
                    
                    # Créer les données de la page
                    page_data = {
                        "page_number": i + 1,
                        "description": f"Page {i+1} - {prompt[:100]}...",
                        "image_path": str(final_image_path),
                        "image_url": f"/static/generated_comics/{comic_id}/page_{i+1}_final.png",
                        "dialogues": dialogues,
                        "metadata": {
                            "prompt": prompt,
                            "style": spec.style,
                            "generation_time": datetime.now().isoformat()
                        }
                    }
                    
                    pages.append(page_data)
                    print(f"✅ Image {i+1} générée et sauvegardée: {final_image_path}")
                    
                except Exception as e:
                    print(f"❌ Erreur génération image {i+1}: {e}")
                    continue
            
            # Sauvegarder les métadonnées de la BD
            metadata_path = comic_dir / "comic_metadata.json"
            metadata = {
                "comic_id": comic_id,
                "title": f"Aventure de {spec.hero_name}",
                "style": spec.style,
                "creation_date": datetime.now().isoformat(),
                "pages": len(pages),
                "crewai_data": comic_data
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"🎉 BD générée avec succès: {len(pages)} pages dans {comic_dir}")
            
            return pages
            
        except Exception as e:
            print(f"❌ Erreur génération BD: {e}")
            raise
    
    def _extract_prompts_from_crewai(self, comic_data: Dict[str, Any]) -> List[str]:
        """Extrait les prompts du résultat CrewAI"""
        try:
            # Le résultat CrewAI est dans comic_data["result"] sous forme de string JSON
            if "result" in comic_data:
                result_str = comic_data["result"]
                if isinstance(result_str, str):
                    result_data = json.loads(result_str)
                else:
                    result_data = result_str
                
                # Extraire les prompts
                prompts_data = result_data.get("prompts", [])
                prompts = []
                
                for prompt_info in prompts_data:
                    if isinstance(prompt_info, dict):
                        description = prompt_info.get("description", "")
                        style = prompt_info.get("style", "")
                        full_prompt = f"{description}, art style: {style}"
                        prompts.append(full_prompt)
                    else:
                        prompts.append(str(prompt_info))
                
                return prompts
                
        except Exception as e:
            print(f"⚠️ Erreur extraction prompts: {e}")
        
        return []
    
    def _create_fallback_prompt(self, spec, page_number: int) -> str:
        """Crée un prompt de fallback"""
        return (f"Comic book illustration featuring {spec.hero_name} in a {spec.story_type} adventure, "
                f"page {page_number}, {spec.style} art style, vibrant colors, professional comic book art, "
                f"dynamic composition, space for dialogue bubbles")
    
    async def _generate_image_from_prompt(self, prompt: str, comic_dir: Path, page_number: int, style: str) -> Path:
        """
        Génère une image à partir d'un prompt
        Pour le moment, crée une image de placeholder colorée
        """
        try:
            # Créer une image de base (800x600)
            width, height = 800, 600
            
            # Couleurs selon le style
            color_schemes = {
                "pixel": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
                "cartoon": ["#FD79A8", "#6C5CE7", "#00B894", "#FDCB6E", "#E17055"],
                "realistic": ["#2D3436", "#636E72", "#DDD", "#74B9FF", "#00CEC9"],
                "manga": ["#2D3436", "#FFF", "#FF7675", "#74B9FF", "#FD79A8"],
                "watercolor": ["#E17055", "#00CEC9", "#FDCB6E", "#6C5CE7", "#FD79A8"]
            }
            
            colors = color_schemes.get(style, color_schemes["cartoon"])
            
            # Créer l'image
            img = Image.new('RGB', (width, height), colors[0])
            draw = ImageDraw.Draw(img)
            
            # Ajouter des formes géométriques pour simuler une composition
            import random
            random.seed(page_number)  # Pour avoir des résultats reproductibles
            
            # Fond dégradé simulé
            for i in range(0, height, 10):
                opacity = int(255 * (1 - i / height))
                color = (*[int(c) for c in bytes.fromhex(colors[1][1:])], opacity)
                draw.rectangle([0, i, width, i+10], fill=color[:3])
            
            # Formes géométriques pour simuler personnages/objets
            for i in range(3):
                x = random.randint(50, width-150)
                y = random.randint(50, height-150)
                w = random.randint(80, 150)
                h = random.randint(80, 150)
                color = colors[random.randint(2, len(colors)-1)]
                draw.ellipse([x, y, x+w, y+h], fill=color)
            
            # Ajouter du texte pour identifier l'image
            try:
                # Utiliser une police par défaut
                font = ImageFont.load_default()
            except:
                font = None
            
            # Texte d'information
            info_text = f"Page {page_number} - Style: {style}"
            text_bbox = draw.textbbox((0, 0), info_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = (width - text_width) // 2
            text_y = height - text_height - 20
            
            # Fond pour le texte
            draw.rectangle([text_x-10, text_y-5, text_x+text_width+10, text_y+text_height+5], fill='white')
            draw.text((text_x, text_y), info_text, fill='black', font=font)
            
            # Sauvegarder l'image
            image_path = comic_dir / f"page_{page_number}_base.png"
            img.save(image_path, 'PNG')
            
            print(f"📸 Image de base créée: {image_path}")
            return image_path
            
        except Exception as e:
            print(f"❌ Erreur création image: {e}")
            raise
    
    def _create_page_dialogues(self, spec, page_number: int) -> List[Dict[str, Any]]:
        """Crée des dialogues pour une page"""
        dialogues = [
            {
                "character": spec.hero_name,
                "text": f"Voici ma première aventure sur la page {page_number}!",
                "type": "speech",
                "position": {"x": 0.1, "y": 0.1}
            }
        ]
        
        if page_number > 1:
            dialogues.append({
                "character": "Narrateur",
                "text": f"L'aventure continue dans {spec.story_type}...",
                "type": "narration",
                "position": {"x": 0.5, "y": 0.8}
            })
        
        return dialogues
    
    async def _add_dialogue_bubbles(self, image_path: Path, dialogues: List[Dict[str, Any]], 
                                   comic_dir: Path, page_number: int) -> Path:
        """Ajoute les bulles de dialogue à l'image"""
        try:
            # Charger l'image de base
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Utiliser une police par défaut
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Ajouter chaque bulle de dialogue
            for i, dialogue in enumerate(dialogues):
                text = dialogue.get("text", "")
                char = dialogue.get("character", "")
                pos = dialogue.get("position", {"x": 0.1 + i*0.3, "y": 0.1 + i*0.2})
                
                # Calculer la position en pixels
                x = int(pos["x"] * img.width)
                y = int(pos["y"] * img.height)
                
                # Calculer la taille du texte
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Définir les dimensions de la bulle
                bubble_width = max(text_width + 20, 150)
                bubble_height = max(text_height + 20, 50)
                
                # S'assurer que la bulle reste dans l'image
                if x + bubble_width > img.width:
                    x = img.width - bubble_width - 10
                if y + bubble_height > img.height:
                    y = img.height - bubble_height - 10
                
                # Dessiner la bulle (ellipse blanche avec bordure noire)
                bubble_coords = [x, y, x + bubble_width, y + bubble_height]
                draw.ellipse(bubble_coords, fill='white', outline='black', width=2)
                
                # Dessiner le texte centré dans la bulle
                text_x = x + (bubble_width - text_width) // 2
                text_y = y + (bubble_height - text_height) // 2
                draw.text((text_x, text_y), text, fill='black', font=font)
                
                # Ajouter le nom du personnage si disponible
                if char and char != "Narrateur":
                    char_bbox = draw.textbbox((0, 0), char, font=font)
                    char_width = char_bbox[2] - char_bbox[0]
                    char_x = x + (bubble_width - char_width) // 2
                    char_y = y - 25
                    if char_y > 0:
                        draw.text((char_x, char_y), char, fill='darkblue', font=font)
            
            # Sauvegarder l'image finale
            final_path = comic_dir / f"page_{page_number}_final.png"
            img.save(final_path, 'PNG')
            
            print(f"💬 Bulles ajoutées à la page {page_number}")
            return final_path
            
        except Exception as e:
            print(f"❌ Erreur ajout bulles: {e}")
            raise

# Instance globale
comic_image_generator = ComicImageGenerator()
