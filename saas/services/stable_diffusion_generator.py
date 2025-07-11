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
from .comic_ai_enhancer import ComicAIEnhancer
from .sd3_bubble_integrator_v2 import SD3BubbleIntegratorAdvanced

load_dotenv()

class StableDiffusionGenerator:
    """Générateur d'images réalistes avec l'API Stable Diffusion"""
    
    def __init__(self):
        self.output_dir = Path("static/generated_comics")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration pour différents services d'IA
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        self.stability_key = os.getenv("STABILITY_API_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        
        # Initialiser l'enhancer IA pour les bulles
        self.ai_enhancer = ComicAIEnhancer() if os.getenv("ENABLE_AI_BUBBLES", "false").lower() == "true" else None
        
        # Nouveau système SD3 V2.0 pour intégration de bulles ultra-réalistes
        self.sd3_integrator = SD3BubbleIntegratorAdvanced() if os.getenv("ENABLE_SD3_BUBBLES", "true").lower() == "true" else None
        
    async def generate_comic_images(self, comic_data: Dict[str, Any], spec) -> List[Dict[str, Any]]:
        """
        Génère des images réalistes pour une BD et sauvegarde les fichiers
        """
        try:
            print("🎨 Génération d'images RÉALISTES pour la BD avec Stable Diffusion...")
            
            # Stocker les informations du spec pour l'IA
            self.hero_name = spec.hero_name
            self.story_type = spec.story_type
            self.style = spec.style
            
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
                    
                    # Générer l'image SANS bulles avec Stable Diffusion
                    base_image_path = await self._generate_sd_image(prompt, comic_dir, i+1, spec.style)
                    
                    # Créer les spécifications de dialogue
                    dialogues = self._create_page_dialogues(chapter, spec, i+1)
                    
                    # Créer les données temporaires de la page pour le traitement SD3
                    temp_page_data = {
                        "page_number": i + 1,
                        "description": self._extract_scene_description(chapter, prompt),
                        "image_path": str(base_image_path),
                        "dialogues": dialogues,
                        "metadata": {
                            "prompt": prompt,
                            "style": spec.style,
                            "generation_time": datetime.now().isoformat()
                        }
                    }
                    
                    # NOUVEAU SYSTÈME V2.0 : Intégrer les bulles avec SD3 Ultra-Réalistes
                    if self.sd3_integrator and dialogues:
                        print(f"🚀 Application du système SD3 V2.0 pour bulles ultra-réalistes - page {i+1}")
                        enhanced_page = await self.sd3_integrator._process_single_page_advanced(temp_page_data, i+1)
                        final_image_path = Path(enhanced_page["image_path"])
                    else:
                        # Fallback vers l'ancien système si SD3 V2.0 non disponible
                        print(f"⚠️ Fallback vers l'ancien système de bulles pour la page {i+1}")
                        final_image_path = await self._add_dialogue_bubbles(base_image_path, dialogues, comic_dir, i+1)
                    
                    # Créer les données finales de la page
                    page_data = {
                        "page_number": i + 1,
                        "description": temp_page_data["description"],
                        "image_path": str(final_image_path),
                        "image_url": f"/static/generated_comics/{comic_id}/{final_image_path.name}",
                        "dialogues": dialogues,
                        "bubble_system": "sd3_advanced_integrated_v2" if self.sd3_integrator and dialogues else "classic_overlay",
                        "metadata": temp_page_data["metadata"]
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
        
        prompt += f", {style_desc}, vibrant colors, professional comic book art, dynamic composition, clear background areas"
        
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
                "width": 1024,
                "height": 1024
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
            "height": 1024,
            "width": 1024,
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
        """Crée des dialogues variés pour une page avec différents types de bulles"""
        dialogues = []
        
        # Types de dialogues possibles
        dialogue_types = ["speech", "thought", "shout", "whisper"]
        
        # Extraire les dialogues du chapitre si disponibles
        if isinstance(chapter, dict) and "dialogues" in chapter:
            for dialogue in chapter["dialogues"]:
                dialogues.append({
                    "character": dialogue.get("character", spec.hero_name),
                    "text": dialogue.get("text", f"Dialogue page {page_number}"),
                    "type": dialogue.get("type", "speech"),
                    "position": dialogue.get("position", {"x": 0.1, "y": 0.1})
                })
        else:
            # Créer des dialogues variés selon le numéro de page
            if page_number == 1:
                # Page d'ouverture - dialogue d'introduction
                dialogues.append({
                    "character": spec.hero_name,
                    "text": "Bonjour ! Je m'appelle " + spec.hero_name + " et voici mon histoire !",
                    "type": "speech",
                    "position": {"x": 0.15, "y": 0.10}
                })
                if len(spec.characters) > 1:
                    dialogues.append({
                        "character": spec.characters[1] if len(spec.characters) > 1 else "Ami",
                        "text": "Quelle aventure nous attend ?",
                        "type": "speech",
                        "position": {"x": 0.60, "y": 0.70}
                    })
            elif page_number == 2:
                # Page d'action - dialogue plus dynamique
                dialogues.append({
                    "character": spec.hero_name,
                    "text": "Wow ! C'est incroyable !",
                    "type": "shout",
                    "position": {"x": 0.20, "y": 0.15}
                })
                dialogues.append({
                    "character": spec.hero_name,
                    "text": "Je me demande ce qui va se passer...",
                    "type": "thought",
                    "position": {"x": 0.55, "y": 0.65}
                })
            elif page_number == 3:
                # Page de mystère - chuchotement
                dialogues.append({
                    "character": spec.hero_name,
                    "text": "Chut... Il faut être discret...",
                    "type": "whisper",
                    "position": {"x": 0.10, "y": 0.60}
                })
                dialogues.append({
                    "character": "Narrateur",
                    "text": "L'aventure devient mystérieuse...",
                    "type": "thought",
                    "position": {"x": 0.50, "y": 0.20}
                })
            elif page_number >= 4:
                # Pages suivantes - mélange de types
                import random
                
                # Dialogue principal
                main_texts = [
                    "Cette aventure est fantastique !",
                    "Je n'ai jamais vu quelque chose comme ça !",
                    "Il faut que je raconte ça à mes amis !",
                    "Quelle découverte extraordinaire !",
                    "C'est le plus beau jour de ma vie !",
                    "Je me sens comme un vrai héros !",
                    "Cette histoire va être légendaire !",
                    "J'ai hâte de voir la suite !",
                ]
                
                dialogues.append({
                    "character": spec.hero_name,
                    "text": random.choice(main_texts),
                    "type": random.choice(["speech", "shout"]),
                    "position": {"x": 0.15, "y": 0.10}
                })
                
                # Dialogue de pensée
                thought_texts = [
                    "Qu'est-ce qui m'attend maintenant ?",
                    "J'espère que tout va bien se passer...",
                    "Cette aventure me rappelle mes rêves...",
                    "Je me sens plus fort qu'avant !",
                    "Il faut que je reste courageux !",
                ]
                
                dialogues.append({
                    "character": spec.hero_name,
                    "text": random.choice(thought_texts),
                    "type": "thought",
                    "position": {"x": 0.55, "y": 0.65}
                })
        
        # Limiter à 2-3 dialogues par page pour éviter la surcharge
        return dialogues[:3]
    
    async def _add_dialogue_bubbles(self, image_path: Path, dialogues: List[Dict[str, Any]], 
                                  comic_dir: Path, page_number: int) -> Path:
        """Ajoute les bulles de dialogue à l'image avec IA ou fallback classique"""
        try:
            # Si l'enhancer IA est activé, l'utiliser
            if self.ai_enhancer:
                print(f"🤖 Utilisation de l'IA pour les bulles de la page {page_number}")
                
                # Créer le contexte de l'histoire pour l'IA
                story_context = {
                    "page_number": page_number,
                    "hero_name": getattr(self, 'hero_name', 'Héros'),
                    "story_type": getattr(self, 'story_type', 'adventure'),
                    "style": getattr(self, 'style', 'cartoon')
                }
                
                # Utiliser l'IA pour analyser et améliorer l'image
                final_image_path = await self.ai_enhancer.enhance_comic_page(
                    image_path, 
                    story_context, 
                    comic_dir, 
                    page_number
                )
                
                if final_image_path:
                    print(f"✅ Bulles IA ajoutées avec succès: {final_image_path}")
                    return final_image_path
                else:
                    print("⚠️ Fallback vers la méthode classique")
            
            # Fallback classique si IA désactivée ou en erreur
            return await self._add_dialogue_bubbles_classic(image_path, dialogues, comic_dir, page_number)
            
        except Exception as e:
            print(f"❌ Erreur ajout bulles: {e}")
            # En cas d'erreur, retourner l'image originale
            final_path = comic_dir / f"page_{page_number}_final.png"
            img = Image.open(image_path)
            img.save(final_path, 'PNG')
            return final_path
    
    async def _add_dialogue_bubbles_classic(self, image_path: Path, dialogues: List[Dict[str, Any]], 
                                          comic_dir: Path, page_number: int) -> Path:
        """Méthode classique pour ajouter les bulles de dialogue"""
        try:
            # Charger l'image
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Positions prédéfinies pour les bulles (éviter les chevauchements)
            bubble_positions = [
                (0.15, 0.10),  # Haut gauche
                (0.60, 0.15),  # Haut droite
                (0.10, 0.60),  # Bas gauche
                (0.65, 0.65),  # Bas droite
                (0.35, 0.25),  # Centre haut
                (0.25, 0.80),  # Centre bas
            ]
            
            # Ajouter chaque bulle de dialogue
            for i, dialogue in enumerate(dialogues):
                text = dialogue.get("text", "")
                if not text:
                    continue
                    
                # Déterminer le type de bulle
                dialogue_type = dialogue.get("type", "speech")
                character = dialogue.get("character", "")
                
                # Position de la bulle
                pos_index = i % len(bubble_positions)
                x_ratio, y_ratio = bubble_positions[pos_index]
                
                # Calculer la taille de la bulle basée sur le texte
                words = text.split()
                char_count = len(text)
                
                # Taille dynamique
                bubble_width = min(max(200, char_count * 6), int(img.width * 0.35))
                bubble_height = min(max(80, len(words) * 12), int(img.height * 0.25))
                
                # Position finale
                x = int(img.width * x_ratio)
                y = int(img.height * y_ratio)
                
                # S'assurer que la bulle reste dans l'image
                if x + bubble_width > img.width:
                    x = img.width - bubble_width - 10
                if y + bubble_height > img.height:
                    y = img.height - bubble_height - 10
                
                # Dessiner la bulle selon le type
                if dialogue_type == "thought":
                    # Bulle de pensée (nuage avec des petites bulles)
                    self._draw_thought_bubble(draw, x, y, bubble_width, bubble_height)
                elif dialogue_type == "shout":
                    # Bulle de cri (forme explosive)
                    self._draw_shout_bubble(draw, x, y, bubble_width, bubble_height)
                elif dialogue_type == "whisper":
                    # Bulle de chuchotement (pointillés)
                    self._draw_whisper_bubble(draw, x, y, bubble_width, bubble_height)
                else:
                    # Bulle de dialogue normale
                    self._draw_speech_bubble(draw, x, y, bubble_width, bubble_height)
                
                # Ajouter le texte
                self._draw_bubble_text(draw, x, y, bubble_width, bubble_height, text)
            
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
    
    def _draw_speech_bubble(self, draw, x, y, width, height):
        """Dessine une bulle de dialogue classique avec queue"""
        # Bulle principale (ellipse)
        draw.ellipse([x, y, x + width, y + height], fill="white", outline="black", width=3)
        
        # Queue de la bulle (triangle pointant vers le personnage)
        queue_x = x + width // 4
        queue_y = y + height
        points = [
            (queue_x, queue_y),
            (queue_x + 15, queue_y + 20),
            (queue_x + 30, queue_y),
        ]
        draw.polygon(points, fill="white", outline="black")
        
        # Ligne pour fermer la queue
        draw.line([(queue_x, queue_y), (queue_x + 30, queue_y)], fill="white", width=2)
    
    def _draw_thought_bubble(self, draw, x, y, width, height):
        """Dessine une bulle de pensée avec des petites bulles"""
        # Bulle principale (forme nuage avec des cercles)
        # Créer plusieurs cercles qui se chevauchent pour former un nuage
        circles = [
            (x + 10, y + 10, 25),
            (x + 35, y + 5, 30),
            (x + 65, y + 8, 28),
            (x + 90, y + 12, 25),
            (x + 15, y + 35, 30),
            (x + 45, y + 30, 35),
            (x + 75, y + 32, 30),
            (x + 20, y + 60, 25),
            (x + 50, y + 58, 28),
            (x + 80, y + 55, 25),
        ]
        
        # Ajuster les cercles à la taille de la bulle
        scale_x = width / 120
        scale_y = height / 80
        
        for cx, cy, radius in circles:
            scaled_cx = x + int((cx - x) * scale_x)
            scaled_cy = y + int((cy - y) * scale_y)
            scaled_radius = int(radius * min(scale_x, scale_y))
            
            if scaled_cx + scaled_radius <= x + width and scaled_cy + scaled_radius <= y + height:
                draw.ellipse([scaled_cx - scaled_radius, scaled_cy - scaled_radius,
                             scaled_cx + scaled_radius, scaled_cy + scaled_radius], 
                           fill="white", outline="black", width=2)
        
        # Petites bulles de pensée
        small_bubbles = [
            (x + width // 4, y + height + 10, 8),
            (x + width // 4 - 10, y + height + 25, 5),
            (x + width // 4 - 15, y + height + 35, 3),
        ]
        
        for bx, by, radius in small_bubbles:
            draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], 
                       fill="white", outline="black", width=2)
    
    def _draw_shout_bubble(self, draw, x, y, width, height):
        """Dessine une bulle de cri avec des bords explosifs"""
        # Créer une forme en étoile/explosion
        center_x = x + width // 2
        center_y = y + height // 2
        
        # Points pour créer une forme explosive
        points = []
        import math
        
        for i in range(16):  # 16 points pour une forme complexe
            angle = i * math.pi / 8
            if i % 2 == 0:
                # Points extérieurs (pics)
                radius = min(width, height) // 2 + 15
            else:
                # Points intérieurs (creux)
                radius = min(width, height) // 2 - 5
            
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        
        # Dessiner la forme explosive
        draw.polygon(points, fill="white", outline="black", width=4)
    
    def _draw_whisper_bubble(self, draw, x, y, width, height):
        """Dessine une bulle de chuchotement avec des pointillés"""
        # Bulle principale avec contour en pointillés
        # Simuler les pointillés avec des petites lignes
        import math
        
        # Ellipse en pointillés
        for angle in range(0, 360, 10):
            angle_rad = math.radians(angle)
            x1 = x + width // 2 + (width // 2) * math.cos(angle_rad)
            y1 = y + height // 2 + (height // 2) * math.sin(angle_rad)
            x2 = x + width // 2 + (width // 2 + 5) * math.cos(angle_rad)
            y2 = y + height // 2 + (height // 2 + 5) * math.sin(angle_rad)
            
            if angle % 20 == 0:  # Créer l'effet pointillé
                draw.line([(x1, y1), (x2, y2)], fill="black", width=2)
        
        # Remplir l'intérieur
        draw.ellipse([x + 3, y + 3, x + width - 3, y + height - 3], fill="white")
        
        # Queue en pointillés
        queue_x = x + width // 4
        queue_y = y + height
        for i in range(0, 20, 4):
            draw.line([(queue_x + i, queue_y + i), (queue_x + i + 2, queue_y + i + 2)], 
                     fill="black", width=2)
    
    def _draw_bubble_text(self, draw, x, y, width, height, text):
        """Dessine le texte dans la bulle avec un meilleur formatting"""
        try:
            # Essayer de charger une police plus grande
            font = ImageFont.load_default()
            # Si on a PIL avec truetype, on peut essayer une police système
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", 14)
                except:
                    pass  # Garder la police par défaut
        except:
            font = None
        
        # Diviser le texte en lignes intelligemment
        words = text.split()
        lines = []
        current_line = ""
        max_chars_per_line = max(12, width // 10)  # Ajuster selon la largeur
        
        for word in words:
            if len(current_line + word) < max_chars_per_line:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        # Centrer le texte dans la bulle
        line_height = 16
        total_text_height = len(lines) * line_height
        start_y = y + (height - total_text_height) // 2
        
        # Dessiner chaque ligne centrée
        for i, line in enumerate(lines[:4]):  # Max 4 lignes
            # Calculer la largeur du texte pour le centrer
            if font:
                try:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                except:
                    text_width = len(line) * 8
            else:
                text_width = len(line) * 8
            
            text_x = x + (width - text_width) // 2
            text_y = start_y + i * line_height
            
            # Dessiner le texte avec une petite ombre pour plus de lisibilité
            draw.text((text_x + 1, text_y + 1), line, fill="gray", font=font)
            draw.text((text_x, text_y), line, fill="black", font=font)
        
    def _extract_scene_description(self, chapter: Dict[str, Any], prompt: str) -> str:
        """Extrait une description claire de la scène pour l'analyse SD3"""
        
        # Essayer d'extraire depuis le chapitre d'abord
        if isinstance(chapter, dict):
            # Recherche dans différents champs possibles
            description_fields = ["description", "scene_description", "action_description", "scene", "summary"]
            
            for field in description_fields:
                if field in chapter and chapter[field]:
                    desc = str(chapter[field])
                    if len(desc) > 20:  # Description suffisamment détaillée
                        return desc
        
        # Fallback : extraire depuis le prompt
        # Supprimer les éléments techniques du prompt
        clean_prompt = prompt.replace("Comic book illustration featuring", "")
        clean_prompt = clean_prompt.replace("cartoon style", "").replace("vibrant colors", "")
        clean_prompt = clean_prompt.replace("professional comic book art", "")
        clean_prompt = clean_prompt.replace("dynamic composition", "")
        clean_prompt = clean_prompt.replace("clear background areas", "")
        
        # Nettoyer et retourner
        clean_prompt = clean_prompt.strip().rstrip(",").strip()
        
        # Si la description est encore trop technique, créer une description générique
        if len(clean_prompt) < 20 or "illustration" in clean_prompt.lower():
            return f"Scène d'aventure avec {getattr(self, 'hero_name', 'le héros')} dans un environnement {getattr(self, 'style', 'cartoon')}"
        
        return clean_prompt
