"""
Générateur d'images réalistes avec Stable Diffusion pour les BD
"""
import os
import requests
import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from dotenv import load_dotenv

load_dotenv()

class StableDiffusionGenerator:
    """Générateur d'images réalistes avec l'API Stable Diffusion"""
    
    def __init__(self):
        self.output_dir = Path("C:/Users/freda/Desktop/backend/saas/static/generated_comics")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration pour différents services d'IA
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        self.stability_key = os.getenv("STABILITY_API_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        
    async def generate_comic_images(self, comic_data: Dict[str, Any], spec) -> List[Dict[str, Any]]:
        """
        Génère des images réalistes pour une BD et sauvegarde les fichiers
        """
        try:
            print("🎨 Génération d'images RÉALISTES pour la BD avec Stable Diffusion...")
            
            # Créer un dossier pour cette BD
            comic_id = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            comic_dir = self.output_dir / comic_id
            comic_dir.mkdir(exist_ok=True)
            
            pages = []
            
            # Extraire les chapitres/scènes du scénario CrewAI
            chapters = comic_data.get("chapters", [])
            if not chapters:
                # Fallback : créer une scène basique
                chapters = [{"scene": 1, "description": f"Une aventure de {spec.hero_name} dans un style {spec.style}"}]
            
            # Limiter au nombre d'images demandé
            chapters_to_process = chapters[:spec.num_images]
            
            for i, chapter in enumerate(chapters_to_process):
                try:
                    print(f"🖼️ Génération image {i+1}/{len(chapters_to_process)}")
                    
                    # Créer un prompt détaillé pour Stable Diffusion
                    prompt = self._create_detailed_prompt(chapter, spec, i)
                    print(f"🎯 Prompt: {prompt[:100]}...")
                    
                    # Générer l'image avec Stable Diffusion
                    image_path = await self._generate_sd_image(prompt, comic_dir, i+1, spec.style)
                    
                    # Créer les spécifications de dialogue
                    dialogues = self._create_page_dialogues(chapter, spec, i+1)
                    
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
                    # En cas d'erreur, créer une image de fallback
                    fallback_path = await self._create_fallback_image(comic_dir, i+1, spec.style)
                    pages.append({
                        "page_number": i + 1,
                        "description": f"Page {i+1} - Image de fallback",
                        "image_path": str(fallback_path),
                        "image_url": f"/static/generated_comics/{comic_id}/page_{i+1}_final.png",
                        "dialogues": [],
                        "metadata": {
                            "style": spec.style,
                            "generation_time": datetime.now().isoformat(),
                            "fallback": True
                        }
                    })
                    continue
            
            # Sauvegarder les métadonnées de la BD
            metadata_path = comic_dir / "comic_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "comic_id": comic_id,
                    "creation_date": datetime.now().isoformat(),
                    "total_pages": len(pages),
                    "style": spec.style,
                    "hero_name": spec.hero_name
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✅ BD complète générée: {len(pages)} pages")
            return pages
            
        except Exception as e:
            print(f"❌ Erreur génération BD: {e}")
            raise
    
    def _create_detailed_prompt(self, chapter: Dict[str, Any], spec, page_number: int) -> str:
        """Crée un prompt détaillé pour Stable Diffusion"""
        
        # Descriptions de base selon le style
        style_descriptions = {
            "cartoon": "cartoon style, vibrant colors, expressive characters, clean lines, children's book illustration",
            "manga": "manga style, anime artwork, detailed characters, expressive eyes, black and white or colored",
            "realistic": "realistic art style, detailed illustration, professional artwork, photorealistic",
            "pixel": "pixel art style, retro gaming aesthetic, 16-bit graphics, colorful pixels",
            "watercolor": "watercolor painting style, soft brushstrokes, artistic, flowing colors"
        }
        
        style_desc = style_descriptions.get(spec.style, "cartoon style")
        
        # Extraire la description de la scène
        scene_description = ""
        if isinstance(chapter, dict):
            scene_description = chapter.get("description", "")
            if not scene_description:
                scene_description = chapter.get("scene", "")
            if not scene_description:
                scene_description = chapter.get("action_description", "")
        
        # Construire le prompt
        prompt = f"Comic book illustration featuring {spec.hero_name}"
        
        if scene_description:
            prompt += f", {scene_description}"
        else:
            prompt += f" in a {spec.story_type} adventure, page {page_number-1}"
        
        prompt += f", {style_desc}, vibrant colors, professional comic book art, dynamic composition, space for dialogue bubbles"
        
        # Ajouter des mots-clés selon le type d'histoire
        story_keywords = {
            "adventure": "action scene, dynamic poses, adventure setting",
            "comedy": "humorous situation, expressive faces, comedic timing",
            "fantasy": "magical elements, fantastical creatures, mystical atmosphere",
            "science-fiction": "futuristic setting, sci-fi elements, technology",
            "mystery": "mysterious atmosphere, detective scene, suspenseful mood"
        }
        
        if spec.story_type in story_keywords:
            prompt += f", {story_keywords[spec.story_type]}"
        
        return prompt
    
    async def _generate_sd_image(self, prompt: str, comic_dir: Path, page_number: int, style: str) -> Path:
        """
        Génère une image avec Stable Diffusion
        Utilise plusieurs services en fallback
        """
        
        # Essayer d'abord avec Hugging Face (gratuit)
        if self.huggingface_token:
            try:
                return await self._generate_with_huggingface(prompt, comic_dir, page_number)
            except Exception as e:
                print(f"⚠️ Hugging Face failed: {e}")
        
        # Fallback: Stability AI
        if self.stability_key:
            try:
                return await self._generate_with_stability(prompt, comic_dir, page_number)
            except Exception as e:
                print(f"⚠️ Stability AI failed: {e}")
        
        # Fallback final: image générée localement améliorée
        print("🎨 Utilisation du générateur local amélioré")
        return await self._generate_enhanced_local_image(prompt, comic_dir, page_number, style)
    
    async def _generate_with_huggingface(self, prompt: str, comic_dir: Path, page_number: int) -> Path:
        """Génère avec l'API Hugging Face"""
        url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {self.huggingface_token}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "width": 768,
                "height": 512
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Redimensionner pour BD
                    image = image.resize((800, 600), Image.Resampling.LANCZOS)
                    
                    image_path = comic_dir / f"page_{page_number}_base.png"
                    image.save(image_path, 'PNG')
                    
                    print(f"✅ Image générée avec Hugging Face: {image_path}")
                    return image_path
                else:
                    error_text = await response.text()
                    raise Exception(f"Hugging Face API error: {response.status} - {error_text}")
    
    async def _generate_with_stability(self, prompt: str, comic_dir: Path, page_number: int) -> Path:
        """Génère avec l'API Stability AI"""
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        headers = {
            "Authorization": f"Bearer {self.stability_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 512,
            "width": 768,
            "steps": 20,
            "samples": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    image_data = data["artifacts"][0]["base64"]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    image_path = comic_dir / f"page_{page_number}_base.png"
                    image.save(image_path, 'PNG')
                    
                    print(f"✅ Image générée avec Stability AI: {image_path}")
                    return image_path
                else:
                    error_text = await response.text()
                    raise Exception(f"Stability AI error: {response.status} - {error_text}")
    
    async def _generate_enhanced_local_image(self, prompt: str, comic_dir: Path, page_number: int, style: str) -> Path:
        """Génère une image locale améliorée (fallback)"""
        try:
            # Créer une image plus sophistiquée qu'avant
            width, height = 800, 600
            
            # Couleurs selon le style (plus nuancées)
            color_schemes = {
                "cartoon": {
                    "bg": "#87CEEB",  # Sky blue
                    "ground": "#90EE90",  # Light green
                    "characters": ["#FFB6C1", "#DDA0DD", "#F0E68C", "#98FB98"],
                    "accent": "#FF69B4"
                },
                "manga": {
                    "bg": "#F5F5F5",  # White gray
                    "ground": "#D3D3D3",  # Light gray
                    "characters": ["#FF6347", "#4169E1", "#32CD32", "#FFD700"],
                    "accent": "#000000"
                },
                "realistic": {
                    "bg": "#4682B4",  # Steel blue
                    "ground": "#8FBC8F",  # Dark sea green
                    "characters": ["#CD853F", "#A0522D", "#D2691E", "#BC8F8F"],
                    "accent": "#2F4F4F"
                }
            }
            
            colors = color_schemes.get(style, color_schemes["cartoon"])
            
            # Créer l'image avec un gradient de fond
            img = Image.new('RGB', (width, height), colors["bg"])
            draw = ImageDraw.Draw(img)
            
            # Fond dégradé
            for i in range(height):
                intensity = int(255 * (i / height))
                color = tuple(int(c * (1 - i / height * 0.3)) for c in img.getpixel((0, 0)))
                draw.line([(0, i), (width, i)], fill=color)
            
            # Sol/horizon
            horizon_y = int(height * 0.7)
            draw.rectangle([0, horizon_y, width, height], fill=colors["ground"])
            
            # Personnages simplifiés mais plus réalistes
            import random
            random.seed(hash(prompt) % 1000)  # Seed basé sur le prompt pour cohérence
            
            # Personnage principal (héros)
            char_x = random.randint(100, 300)
            char_y = random.randint(horizon_y - 150, horizon_y - 50)
            char_color = colors["characters"][0]
            
            # Corps (ovale)
            draw.ellipse([char_x, char_y, char_x + 60, char_y + 100], fill=char_color)
            # Tête (cercle)
            draw.ellipse([char_x + 15, char_y - 40, char_x + 45, char_y - 10], fill=char_color)
            # Bras
            draw.ellipse([char_x - 15, char_y + 20, char_x + 15, char_y + 40], fill=char_color)
            draw.ellipse([char_x + 45, char_y + 20, char_x + 75, char_y + 40], fill=char_color)
            
            # Éléments d'arrière-plan selon le style
            if "adventure" in prompt.lower():
                # Montagnes
                draw.polygon([(0, horizon_y), (150, horizon_y - 100), (300, horizon_y)], fill="#708090")
                draw.polygon([(200, horizon_y), (350, horizon_y - 80), (500, horizon_y)], fill="#778899")
            elif "comedy" in prompt.lower():
                # Étoiles comiques
                for _ in range(5):
                    star_x = random.randint(50, width - 50)
                    star_y = random.randint(50, horizon_y - 100)
                    self._draw_star(draw, star_x, star_y, 20, colors["accent"])
            
            # Texte informatif stylisé
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            info_text = f"Page {page_number} - Style: {style}"
            text_bbox = draw.textbbox((0, 0), info_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            text_x = width - text_width - 20
            text_y = height - 30
            
            # Bulle pour le texte
            draw.ellipse([text_x - 15, text_y - 10, text_x + text_width + 15, text_y + 20], 
                        fill="white", outline=colors["accent"], width=2)
            draw.text((text_x, text_y), info_text, fill=colors["accent"], font=font)
            
            # Sauvegarder l'image
            image_path = comic_dir / f"page_{page_number}_base.png"
            img.save(image_path, 'PNG')
            
            print(f"🎨 Image locale améliorée créée: {image_path}")
            return image_path
            
        except Exception as e:
            print(f"❌ Erreur création image locale: {e}")
            raise
    
    def _draw_star(self, draw, cx, cy, size, color):
        """Dessine une étoile"""
        points = []
        for i in range(10):
            angle = i * 3.14159 / 5
            if i % 2 == 0:
                r = size
            else:
                r = size // 2
            x = cx + r * __import__('math').cos(angle)
            y = cy + r * __import__('math').sin(angle)
            points.extend([x, y])
        draw.polygon(points, fill=color)
    
    async def _create_fallback_image(self, comic_dir: Path, page_number: int, style: str) -> Path:
        """Crée une image de fallback simple"""
        return await self._generate_enhanced_local_image("Simple comic page", comic_dir, page_number, style)
    
    def _create_page_dialogues(self, chapter: Dict[str, Any], spec, page_number: int) -> List[Dict[str, Any]]:
        """Crée des dialogues pour une page"""
        dialogues = []
        
        # Extraire les dialogues du chapitre si disponibles
        if isinstance(chapter, dict) and "dialogues" in chapter:
            for dialogue in chapter["dialogues"]:
                dialogues.append({
                    "character": dialogue.get("character", spec.hero_name),
                    "text": dialogue.get("text", f"Dialogue page {page_number}"),
                    "type": "speech",
                    "position": {"x": 0.1, "y": 0.1}
                })
        else:
            # Dialogue par défaut
            dialogues.append({
                "character": spec.hero_name,
                "text": f"Voici ma première aventure sur la page {page_number}!",
                "type": "speech",
                "position": {"x": 0.1, "y": 0.1}
            })
        
        return dialogues
    
    async def _add_dialogue_bubbles(self, image_path: Path, dialogues: List[Dict[str, Any]], 
                                  comic_dir: Path, page_number: int) -> Path:
        """Ajoute les bulles de dialogue à l'image"""
        try:
            # Charger l'image
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Ajouter chaque bulle de dialogue
            for i, dialogue in enumerate(dialogues):
                text = dialogue.get("text", "")
                if text:
                    # Position de la bulle (simplifiée)
                    x = int(img.width * (0.1 + i * 0.3))
                    y = int(img.height * 0.1)
                    
                    # Taille de la bulle
                    bubble_width = min(200, len(text) * 8)
                    bubble_height = 60
                    
                    # Dessiner la bulle
                    draw.ellipse([x, y, x + bubble_width, y + bubble_height], 
                               fill="white", outline="black", width=2)
                    
                    # Ajouter le texte
                    try:
                        font = ImageFont.load_default()
                    except:
                        font = None
                    
                    # Diviser le texte en lignes
                    words = text.split()
                    lines = []
                    current_line = ""
                    
                    for word in words:
                        if len(current_line + word) < 20:  # Max caractères par ligne
                            current_line += word + " "
                        else:
                            lines.append(current_line.strip())
                            current_line = word + " "
                    if current_line:
                        lines.append(current_line.strip())
                    
                    # Dessiner chaque ligne
                    for j, line in enumerate(lines[:3]):  # Max 3 lignes
                        text_y = y + 15 + j * 15
                        draw.text((x + 10, text_y), line, fill="black", font=font)
            
            # Sauvegarder l'image finale
            final_path = comic_dir / f"page_{page_number}_final.png"
            img.save(final_path, 'PNG')
            
            print(f"💬 Bulles ajoutées: {final_path}")
            return final_path
            
        except Exception as e:
            print(f"❌ Erreur ajout bulles: {e}")
            # En cas d'erreur, copier l'image originale
            final_path = comic_dir / f"page_{page_number}_final.png"
            import shutil
            shutil.copy2(image_path, final_path)
            return final_path


# Instance globale
stable_diffusion_generator = StableDiffusionGenerator()
