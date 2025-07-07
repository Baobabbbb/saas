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
            
            # Nettoyer le nom du thème pour le nom de fichier
            clean_theme = theme.lower().replace(' ', '_').replace('é', 'e').replace('è', 'e')
            
            # Générer le prompt pour une seule image de coloriage
            prompt = self._create_single_coloring_prompt(theme)
            
            # Générer l'image directement dans le dossier coloring
            images = []
            
            try:
                print(f"🖼️ Génération du coloriage: {prompt[:50]}...")
                image_path = await self._generate_coloring_image(prompt, self.output_dir, clean_theme)
                if image_path:
                    images.append({
                        "image_url": f"http://localhost:8000/static/coloring/coloriage_{clean_theme}.png",
                        "theme": theme
                    })
            except Exception as e:
                print(f"❌ Erreur génération image: {e}")
            
            # Sauvegarder les métadonnées (optionnel, dans un fichier unique)
            metadata = {
                "theme": theme,
                "created_at": datetime.now().isoformat(),
                "total_images": len(images),
                "filename": f"coloriage_{clean_theme}.png"
            }
            
            print(f"🎉 Coloriage généré avec succès: {len(images)} image(s)")
            
            return {
                "success": True,
                "theme": theme,
                "images": images,
                "total_images": len(images),
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"❌ Erreur génération coloriages: {e}")
            return {
                "success": False,
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
        
        # Prompts par thème - Optimisés pour le coloriage
        theme_prompts = {
            'animaux': "A cute friendly cat sitting in a meadow with butterflies and flowers",
            'dinosaures': "A friendly cartoon T-Rex playing with a ball in a forest with palm trees",
            'espace': "An astronaut floating among stars, planets and a rocket ship",
            'fees': "A beautiful fairy with butterfly wings sitting on a large mushroom in an enchanted garden",
            'super-heros': "A superhero with a cape flying above a city with tall buildings",
            'nature': "Beautiful sunflowers and roses in a garden with butterflies and a sun",
            'vehicules': "A racing car with number on it speeding on a track with flags",
            'princesse': "A princess in an elegant ball gown standing in front of a castle",
            'licorne': "A magical unicorn with a horn and mane galloping through a rainbow landscape",
            'ocean': "Friendly dolphins jumping over waves with fish and coral",
            'ferme': "A happy cow, pig and chicken in a farm with a barn and flowers"
        }
        
        # Obtenir le prompt de base pour le thème (avec fallback)
        base_prompt = theme_prompts.get(theme.lower(), f"A cute {theme} scene for children")
        
        # Créer le prompt optimisé pour Stable Diffusion line art
        coloring_prompt = f"Black and white line drawing coloring book page, {base_prompt}, simple clean outlines, no shading, no gradients, no fill, thick black lines, white background, cartoon style, suitable for children ages 4-10, high contrast, clear details"
        
        return coloring_prompt
    
    def _get_theme_seed(self, theme: str) -> int:
        """Générer une seed déterministe basée sur le thème pour la cohérence"""
        
        # Seeds fixes par thème pour garantir la cohérence
        theme_seeds = {
            'animaux': 123456,
            'dinosaures': 234567,
            'espace': 345678,
            'fees': 456789,
            'super-heros': 567890,
            'nature': 678901,
            'vehicules': 789012,
            'princesse': 890123,
            'licorne': 901234,
            'ocean': 12345,
            'ferme': 112233
        }
        
        # Utiliser seed prédéfinie ou générer à partir du hash du thème
        seed = theme_seeds.get(theme.lower(), abs(hash(theme.lower())) % 999999)
        print(f"🎲 Seed coloriage pour thème '{theme}': {seed}")
        return seed
    
    async def _generate_coloring_image(self, prompt: str, coloring_dir: Path, theme_name: str) -> Optional[Path]:
        """Générer une image de coloriage avec Stable Diffusion et seed pour cohérence"""
        
        try:
            print(f"🎨 Génération coloriage pour '{theme_name}' avec prompt: {prompt[:100]}...")
            
            # Obtenir la seed pour le thème
            theme_seed = self._get_theme_seed(theme_name)
            
            # Utiliser Stability AI si disponible
            if self.stability_key and self.stability_key != "your_stability_key_here":
                print(f"🔑 Utilisation de Stability AI avec seed {theme_seed}...")
                image_path = await self._generate_with_stability(prompt, coloring_dir, theme_name, theme_seed)
                if image_path:
                    print("✅ Génération Stability AI réussie")
                    return await self._convert_to_line_art(image_path, coloring_dir, theme_name)
                else:
                    print("❌ Échec Stability AI, passage au fallback")
            else:
                print("⚠️ Clé Stability AI manquante ou invalide, utilisation du fallback")
            
            # Fallback vers une image générée localement
            return await self._create_fallback_coloring(coloring_dir, theme_name, prompt)
            
        except Exception as e:
            print(f"❌ Erreur génération image {theme_name}: {e}")
            return await self._create_fallback_coloring(coloring_dir, theme_name, prompt)
    
    async def _generate_with_stability(self, prompt: str, coloring_dir: Path, theme_name: str, seed: int) -> Optional[Path]:
        """Générer avec l'API Stability AI avec seed pour cohérence"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Accept": "application/json"
            }
            
            data = {
                "text_prompts": [
                    {"text": prompt, "weight": 1.0},
                    {"text": "colored, shaded, filled, gradients, complex details, realistic, photographic, blurry", "weight": -0.8}
                ],
                "cfg_scale": 10,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
                "seed": seed,  # ✅ AJOUT DE LA SEED POUR COHÉRENCE
                "style_preset": "line-art",  # Style spécialement pour le line art
                "sampler": "K_DPM_2_ANCESTRAL"
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
                
                image_path = coloring_dir / f"coloriage_{theme_name}.png"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                return image_path
            else:
                print(f"❌ Erreur Stability AI: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur API Stability: {e}")
            return None
    
    async def _convert_to_line_art(self, image_path: Path, coloring_dir: Path, theme_name: str) -> Path:
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
                
                # Convertir en noir et blanc pur avec seuillage
                threshold = 200
                lut = []
                for i in range(256):
                    if i > threshold:
                        lut.append(255)
                    else:
                        lut.append(0)
                edges = edges.point(lut, mode='1')
                
                # Sauvegarder le line art
                lineart_path = coloring_dir / f"coloriage_{theme_name}.png"
                edges.save(lineart_path)
                
                return lineart_path
                
        except Exception as e:
            print(f"❌ Erreur conversion line art: {e}")
            return await self._create_fallback_coloring(coloring_dir, theme_name, "Simple coloring page")
    
    async def _create_fallback_coloring(self, coloring_dir: Path, theme_name: str, description: str) -> Path:
        """Créer une image de coloriage de fallback plus élaborée"""
        
        # Créer une image avec des formes adaptées au thème
        img = Image.new('RGB', (1024, 1024), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Utiliser une police par défaut plus grande
            font = ImageFont.load_default()
        except:
            font = None
        
        # Dessiner des formes selon le thème
        if 'animaux' in theme_name.lower() or 'cat' in theme_name.lower():
            # Dessiner un chat simple
            # Corps ovale
            draw.ellipse([350, 450, 650, 700], outline='black', width=4)
            # Tête
            draw.ellipse([400, 350, 600, 500], outline='black', width=4)
            # Oreilles
            draw.polygon([(420, 350), (400, 300), (450, 320)], outline='black', width=3)
            draw.polygon([(580, 350), (600, 300), (550, 320)], outline='black', width=3)
            # Yeux
            draw.ellipse([440, 380, 470, 410], outline='black', width=3)
            draw.ellipse([530, 380, 560, 410], outline='black', width=3)
            # Queue
            draw.arc([250, 500, 350, 650], 45, 180, fill='black', width=4)
            
        elif 'fleur' in theme_name.lower() or 'nature' in theme_name.lower():
            # Dessiner une fleur
            center_x, center_y = 500, 500
            # Pétales
            for i in range(8):
                angle = i * 45
                x1 = center_x + 80 * (i % 2 + 1) * 0.7
                y1 = center_y + 80 * (i % 2 + 1) * 0.7
                draw.ellipse([center_x-40, center_y-40, center_x+40, center_y+40], outline='black', width=4)
                if i % 2 == 0:
                    draw.ellipse([center_x-20+60, center_y-60, center_x+20+60, center_y-20], outline='black', width=3)
            # Centre
            draw.ellipse([center_x-30, center_y-30, center_x+30, center_y+30], outline='black', width=4)
            # Tige
            draw.line([center_x, center_y+40, center_x, center_y+200], fill='black', width=6)
            
        else:
            # Forme géométrique générique plus jolie
            # Étoile centrale plus grande
            star_points = [
                (500, 250), (530, 350), (630, 350), (560, 420),
                (590, 520), (500, 470), (410, 520), (440, 420),
                (370, 350), (470, 350)
            ]
            draw.polygon(star_points, outline='black', width=4)
            
            # Cercles décoratifs
            for i, (x, y) in enumerate([(300, 300), (700, 300), (300, 700), (700, 700)]):
                draw.ellipse([x-50, y-50, x+50, y+50], outline='black', width=3)
        
        # Bordure décorative
        draw.rectangle([50, 50, 974, 974], outline='black', width=6)
        
        # Titre plus joli
        if font:
            draw.text((350, 100), f"Coloriage {theme_name.title()}", fill='black', font=font)
        
        # Sauvegarder
        fallback_path = coloring_dir / f"coloriage_{theme_name}.png"
        img.save(fallback_path)
        
        print(f"🎨 Fallback coloriage créé pour {theme_name}")
        return fallback_path

    async def generate_coloring(self, theme: str) -> Dict[str, Any]:
        """
        Méthode de compatibilité avec l'endpoint
        """
        return await self.generate_coloring_pages(theme)

# Instance globale
coloring_generator = ColoringGenerator()
