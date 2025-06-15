"""
Service de génération de coloriages (line art noir et blanc) avec Stable Diffusion
"""
import os
import requests
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import base64
from dotenv import load_dotenv

load_dotenv()

class ColoringGenerator:
    """Générateur de coloriages avec Stable Diffusion 3"""
    
    def __init__(self):
        self.output_dir = Path("static/coloring")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stability_key = os.getenv("STABILITY_API_KEY")
        
    async def generate_coloring_pages(self, theme: str) -> Dict[str, Any]:
        """
        Génère des pages de coloriage basées sur un thème
        """
        try:
            print(f"🎨 Génération de coloriages pour le thème: {theme}")
              # Créer un ID unique pour cette série de coloriages
            coloring_id = f"coloring_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            coloring_dir = self.output_dir / coloring_id
            coloring_dir.mkdir(exist_ok=True)
            
            # Générer le prompt pour une seule image de coloriage
            prompt = self._create_single_coloring_prompt(theme)
            
            # Générer l'image
            images = []
            
            try:
                print(f"🖼️ Génération du coloriage: {prompt[:50]}...")
                image_path = await self._generate_coloring_image(prompt, coloring_dir, 1)
                if image_path:
                    images.append({
                        "image_url": f"http://localhost:8000/static/coloring/{coloring_id}/coloring_1_lineart.png",
                        "prompt": prompt,
                        "index": 1
                    })
            except Exception as e:
                print(f"❌ Erreur génération image: {e}")
            
            # Sauvegarder les métadonnées
            metadata = {
                "coloring_id": coloring_id,
                "theme": theme,
                "created_at": datetime.now().isoformat(),
                "total_images": len(images),
                "prompt": prompt
            }
            
            metadata_path = coloring_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"🎉 Coloriages générés avec succès: {len(images)} images dans {coloring_dir}")
            
            return {
                "success": True,
                "coloring_id": coloring_id,
                "theme": theme,
                "images": images,
                "total_images": len(images),
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"❌ Erreur génération coloriages: {e}")
            return {                "success": False,
                "error": str(e),
                "images": []
            }
    
    def _create_coloring_prompts(self, theme: str) -> List[str]:
        """Créer les prompts pour les coloriages selon le thème"""
        
        # Prompts de base par thème
        theme_prompts = {
            'animals': [
                "A cute {animal} sitting in a meadow with flowers",
                "A family of {animal}s playing together",
                "A magical {animal} with wings in a fairy tale forest",
                "A {animal} wearing a crown in a royal garden"
            ],
            'space': [
                "An astronaut floating among stars and planets",
                "A rocket ship flying through space with comets",
                "Friendly aliens having a picnic on the moon",
                "A space station with Earth in the background"
            ],
            'fairies': [
                "A fairy with butterfly wings sitting on a mushroom",
                "A fairy castle with towers and magical gardens",
                "Fairies dancing around a magic tree",
                "A fairy riding a unicorn through clouds"
            ],
            'superheroes': [
                "A superhero flying through the city",
                "A superhero with a cape saving the day",
                "A superhero team standing together",
                "A superhero with special powers and costume"
            ],
            'nature': [
                "Beautiful flowers in a sunny garden",
                "A tree with birds and butterflies",
                "A peaceful lake with ducks and fish",
                "Mountains with a rainbow and clouds"
            ],
            'vehicles': [
                "A race car speeding on a track",
                "An airplane flying through clouds",
                "A sailboat on calm ocean waves",
                "A train traveling through countryside"
            ],
            'princess': [
                "A princess in a beautiful ball gown",
                "A princess's castle with towers and flags",
                "A princess with a crown and jewelry",
                "A princess riding in a royal carriage"
            ],
            'dinosaurs': [
                "A friendly T-Rex in a prehistoric forest",
                "A Triceratops eating plants by a lake",
                "Baby dinosaurs playing together",
                "A Brontosaurus with a long neck reaching for leaves"
            ]
        }        
        # Obtenir les prompts de base pour le thème
        base_prompts = theme_prompts.get(theme, theme_prompts['animals'])
        
        # Créer les prompts pour le line art
        prompts = []
        for prompt in base_prompts:
            # Utiliser des animaux génériques
            if '{animal}' in prompt:
                prompt = prompt.replace('{animal}', 'cat')
            
            # Ajouter les instructions pour le line art
            coloring_prompt = f"Simple black and white line art coloring page, {prompt}, clean outlines, no shading, no fill, white background, suitable for children to color, cartoon style"
            
            prompts.append(coloring_prompt)
        
        return prompts[:4]  # Limiter à 4 images max
    
    def _create_single_coloring_prompt(self, theme: str) -> str:
        """Créer un seul prompt pour le coloriage selon le thème"""
        
        # Prompts par thème (un seul par thème)
        theme_prompts = {
            'animals': "A cute cat sitting in a meadow with flowers",
            'space': "An astronaut floating among stars and planets",
            'fairies': "A fairy with butterfly wings sitting on a mushroom",
            'superheroes': "A superhero flying through the city",
            'nature': "Beautiful flowers in a sunny garden",
            'vehicles': "A race car speeding on a track",
            'princess': "A princess in a beautiful ball gown",
            'dinosaurs': "A friendly T-Rex in a prehistoric forest"
        }
        
        # Obtenir le prompt de base pour le thème
        base_prompt = theme_prompts.get(theme, theme_prompts['animals'])          # Créer le prompt pour l'image de coloriage (line art)
        coloring_prompt = f"Simple black and white line art coloring page, {base_prompt}, clean outlines, no shading, no fill, white background, suitable for children to color, cartoon style"
        
        return coloring_prompt
        
    async def _generate_coloring_image(self, prompt: str, coloring_dir: Path, image_number: int) -> Optional[Path]:
        """Générer une image de coloriage avec Stable Diffusion"""
        
        try:            # Utiliser Stability AI si disponible
            if self.stability_key:
                image_path = await self._generate_with_stability(prompt, coloring_dir, image_number)
                if image_path:
                    return await self._convert_to_line_art(image_path, coloring_dir, image_number)
            
            # Fallback vers une image générée localement
            return await self._create_fallback_coloring(coloring_dir, image_number, prompt)
            
        except Exception as e:
            print(f"❌ Erreur génération image {image_number}: {e}")
            return await self._create_fallback_coloring(coloring_dir, image_number, prompt)
    
    async def _generate_with_stability(self, prompt: str, coloring_dir: Path, image_number: int) -> Optional[Path]:
        """Générer avec l'API Stability AI"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Accept": "application/json"
            }
            
            data = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 20,
                "style_preset": "line-art"  # Style spécialement pour le line art
            }
            
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                image_data = base64.b64decode(response_data["artifacts"][0]["base64"])
                
                image_path = coloring_dir / f"coloring_{image_number}_original.png"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                return image_path
            else:
                print(f"❌ Erreur Stability AI: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur API Stability: {e}")
            return None
    
    async def _convert_to_line_art(self, image_path: Path, coloring_dir: Path, image_number: int) -> Path:
        """Convertir une image en line art noir et blanc"""
        
        try:
            # Ouvrir l'image
            with Image.open(image_path) as img:
                # Convertir en niveaux de gris
                gray_img = img.convert('L')
                
                # Appliquer un filtre de détection de contours
                edges = gray_img.filter(ImageFilter.FIND_EDGES)
                
                # Inverser les couleurs (noir sur blanc)
                edges = ImageOps.invert(edges)
                
                # Ajuster le contraste pour avoir des lignes plus nettes
                edges = ImageOps.autocontrast(edges)
                
                # Convertir en noir et blanc pur
                threshold = 200
                edges = edges.point(lambda x: 255 if x > threshold else 0, mode='1')
                
                # Sauvegarder le line art
                lineart_path = coloring_dir / f"coloring_{image_number}_lineart.png"
                edges.save(lineart_path)
                
                return lineart_path
                
        except Exception as e:
            print(f"❌ Erreur conversion line art: {e}")
            return await self._create_fallback_coloring(coloring_dir, image_number, "Simple coloring page")
    
    async def _create_fallback_coloring(self, coloring_dir: Path, image_number: int, description: str) -> Path:
        """Créer une image de coloriage de fallback simple"""
        
        # Créer une image simple avec du texte et des formes
        img = Image.new('RGB', (1024, 1024), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Utiliser une police par défaut
            font = ImageFont.load_default()
        except:
            font = None
        
        # Dessiner des formes simples pour le coloriage
        # Cercle central
        draw.ellipse([300, 300, 700, 700], outline='black', width=3)
        
        # Étoiles autour
        star_points = [
            (500, 200), (520, 260), (580, 260), (540, 300),
            (560, 360), (500, 330), (440, 360), (460, 300),
            (420, 260), (480, 260)
        ]
        draw.polygon(star_points, outline='black', width=2)
        
        # Texte
        if font:
            draw.text((400, 500), "Coloriage", fill='black', font=font)
            draw.text((350, 530), f"Image {image_number}", fill='black', font=font)
        
        # Sauvegarder
        fallback_path = coloring_dir / f"coloring_{image_number}_lineart.png"
        img.save(fallback_path)
        
        return fallback_path

# Instance globale
coloring_generator = ColoringGenerator()
