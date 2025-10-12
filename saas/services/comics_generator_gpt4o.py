"""
Générateur de bandes dessinées avec gpt-4o-mini + gpt-image-1
Architecture: gpt-4o-mini crée le scénario détaillé, gpt-image-1 génère les planches
"""

import openai
from openai import AsyncOpenAI
import json
import os
import uuid
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()


class ComicsGeneratorGPT4o:
    """Générateur de bandes dessinées avec GPT-4o-mini (scénario) + gpt-image-1 (images)"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY manquante dans les variables d'environnement")
        
        self.client = AsyncOpenAI(api_key=self.openai_key)
        self.cache_dir = Path("static/cache/comics")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Styles artistiques disponibles
        self.art_styles = {
            "cartoon": {
                "name": "Cartoon",
                "description": "Style cartoon coloré et enfantin avec traits simples",
                "prompt_modifier": "cartoon style, colorful, child-friendly, simple lines, bright colors, rounded shapes, Disney-style"
            },
            "manga": {
                "name": "Manga",
                "description": "Style manga japonais avec grands yeux expressifs",
                "prompt_modifier": "manga style, anime, Japanese comic art, expressive large eyes, dynamic poses, black and white with screentones"
            },
            "comics": {
                "name": "Comics Marvel",
                "description": "Style comics américain avec couleurs vives",
                "prompt_modifier": "american comic book style, Marvel/DC style, bold colors, dynamic shading, superhero aesthetic, action poses"
            },
            "realistic": {
                "name": "Réaliste",
                "description": "Style réaliste détaillé",
                "prompt_modifier": "realistic illustration, detailed, photorealistic style, cinematic lighting, high quality"
            },
            "watercolor": {
                "name": "Aquarelle",
                "description": "Style aquarelle doux et artistique",
                "prompt_modifier": "watercolor painting style, soft colors, artistic brush strokes, dreamy atmosphere, painted texture"
            }
        }
        
        # Thèmes prédéfinis
        self.themes = {
            "espace": {
                "name": "Espace",
                "description": "Aventures spatiales avec fusées et planètes",
                "keywords": "space, planets, rockets, astronauts, stars, galaxy"
            },
            "pirates": {
                "name": "Pirates",
                "description": "Aventures de pirates sur les mers",
                "keywords": "pirates, treasure, ships, ocean, islands, adventure"
            },
            "princesses": {
                "name": "Princesses",
                "description": "Histoires de princesses et châteaux",
                "keywords": "princesses, castles, fairy tales, magic, kingdoms"
            },
            "dinosaures": {
                "name": "Dinosaures",
                "description": "Aventures avec des dinosaures",
                "keywords": "dinosaurs, prehistoric, adventure, jungle"
            },
            "animaux": {
                "name": "Animaux",
                "description": "Histoires avec des animaux mignons",
                "keywords": "cute animals, forest, friendship, nature"
            },
            "superheros": {
                "name": "Super-héros",
                "description": "Aventures de super-héros",
                "keywords": "superheroes, powers, action, city, rescue"
            },
            "foret": {
                "name": "Forêt Magique",
                "description": "Aventures dans une forêt enchantée",
                "keywords": "magic forest, fairy, creatures, trees, adventure"
            },
            "ecole": {
                "name": "École",
                "description": "Aventures à l'école",
                "keywords": "school, friends, classroom, learning, fun"
            }
        }
    
    async def generate_comic_story(
        self,
        theme: str,
        num_pages: int,
        art_style: str,
        custom_prompt: Optional[str] = None,
        character_photo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère le scénario complet de la BD avec gpt-4o-mini
        Retourne un JSON avec les détails de chaque planche
        """
        
        print(f"📝 Génération scénario BD: thème={theme}, pages={num_pages}, style={art_style}")
        
        # Récupérer les informations du thème
        theme_info = self.themes.get(theme, {
            "name": theme.title(),
            "description": f"Histoire sur le thème {theme}",
            "keywords": theme
        })
        
        # Récupérer le style artistique
        style_info = self.art_styles.get(art_style, self.art_styles["cartoon"])
        
        # Analyser la photo du personnage si fournie
        character_description = None
        if character_photo_path:
            character_description = await self._analyze_character_photo(character_photo_path)
        
        # Construire le prompt pour gpt-4o-mini
        prompt = f"""Tu es un scénariste expert en bandes dessinées pour enfants de 6-10 ans.

MISSION: Créer une histoire complète en {num_pages} planches de bande dessinée.

THÈME: {theme_info['name']}
Description: {theme_info['description']}
Mots-clés: {theme_info['keywords']}

STYLE ARTISTIQUE: {style_info['name']}
{style_info['description']}

{"DEMANDE PERSONNALISÉE: " + custom_prompt if custom_prompt else ""}

{"PERSONNAGE PRINCIPAL À INTÉGRER: " + character_description if character_description else ""}

CONSIGNES IMPORTANTES:
1. Chaque planche contient EXACTEMENT 4 CASES disposées en grille 2×2
2. L'histoire doit être cohérente, captivante et adaptée aux enfants
3. Chaque case doit avoir:
   - Une description visuelle ULTRA DÉTAILLÉE (pour gpt-image-1)
   - Des dialogues dans des bulles (maximum 2 bulles par case)
   - Une indication de l'action ou l'émotion

4. IMPORTANT pour les BULLES DE DIALOGUE:
   - Les bulles doivent contenir le texte EXACT à afficher
   - Le texte doit être COURT (maximum 10-12 mots par bulle)
   - Les bulles doivent être positionnées pour ne pas cacher les personnages
   - Précise la position suggérée de chaque bulle (haut-gauche, haut-droite, bas-gauche, bas-droite)

5. DESCRIPTIONS VISUELLES ULTRA DÉTAILLÉES:
   Pour chaque case, décris TOUT en détail pour que gpt-image-1 puisse générer l'image parfaite:
   - Les personnages: âge, vêtements, couleurs, positions, expressions faciales
   - Le décor: lieu précis, objets visibles, couleurs, ambiance
   - L'action: ce qui se passe exactement dans cette case
   - Le cadrage: plan large, gros plan, plan américain, etc.
   - La lumière et l'ambiance: jour/nuit, lumineux/sombre, etc.
   
   EXEMPLE DE BONNE DESCRIPTION:
   "Comic book panel showing an 8-year-old girl with long brown hair wearing a yellow t-shirt and blue jeans, 
   standing in her colorful bedroom with toys on shelves behind her. She looks surprised with wide eyes and 
   open mouth, pointing at a glowing magic wand on her bed. Bright sunlight comes through the window. 
   {style_info['prompt_modifier']}. The panel has a speech bubble in the top-right corner saying 'Wow! A magic wand!'"

FORMAT JSON REQUIS:
{{
  "title": "Titre accrocheur de la BD (5-8 mots)",
  "synopsis": "Résumé de l'histoire en 2-3 phrases",
  "total_pages": {num_pages},
  "pages": [
    {{
      "page_number": 1,
      "panels": [
        {{
          "panel_number": 1,
          "visual_description": "Description ULTRA détaillée en anglais pour gpt-image-1 (minimum 40 mots)",
          "action": "Ce qui se passe dans cette case",
          "dialogue_bubbles": [
            {{
              "character": "Nom du personnage",
              "text": "Texte court et percutant",
              "position": "haut-gauche|haut-droite|bas-gauche|bas-droite",
              "emotion": "joyeux|surpris|inquiet|etc"
            }}
          ]
        }},
        {{
          "panel_number": 2,
          "visual_description": "...",
          "action": "...",
          "dialogue_bubbles": [...]
        }},
        {{
          "panel_number": 3,
          "visual_description": "...",
          "action": "...",
          "dialogue_bubbles": [...]
        }},
        {{
          "panel_number": 4,
          "visual_description": "...",
          "action": "...",
          "dialogue_bubbles": [...]
        }}
      ]
    }}
  ]
}}

RÈGLES STRICTES:
- CHAQUE planche a EXACTEMENT 4 cases
- Les descriptions visuelles sont en ANGLAIS (pour gpt-image-1)
- Les dialogues sont en FRANÇAIS (pour les enfants)
- L'histoire doit avoir un début, un milieu et une fin satisfaisante
- Ton positif et adapté aux enfants (pas de violence, pas de peur excessive)

Génère maintenant le scénario complet en JSON:"""

        try:
            print("🤖 Appel gpt-4o-mini pour le scénario...")
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un scénariste expert en bandes dessinées pour enfants. Tu génères des scénarios détaillés en JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000  # Augmenté pour permettre des descriptions détaillées
            )
            
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON (enlever les balises markdown si présentes)
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parser le JSON
            story_data = json.loads(content)
            
            print(f"✅ Scénario généré: '{story_data['title']}' - {len(story_data['pages'])} planches")
            
            return story_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"Contenu reçu: {content[:500]}...")
            raise Exception(f"Erreur de format du scénario: {e}")
        except Exception as e:
            print(f"❌ Erreur génération scénario: {e}")
            raise Exception(f"Erreur lors de la génération du scénario: {e}")
    
    async def _analyze_character_photo(self, photo_path: str) -> str:
        """Analyse une photo de personnage avec gpt-4o-mini pour l'intégrer dans l'histoire"""
        try:
            print(f"📸 Analyse de la photo personnage: {photo_path}")
            
            # Charger et encoder l'image en base64
            with open(photo_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Convertir en base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Déterminer le type MIME
            image_path_obj = Path(photo_path)
            ext = image_path_obj.suffix.lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(ext, 'image/jpeg')
            
            # Analyser avec gpt-4o-mini (vision)
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyse cette photo et décris le personnage en détail pour l'intégrer dans une bande dessinée pour enfants.
                                
Décris:
- Âge approximatif
- Genre
- Couleur et style des cheveux
- Couleur des yeux
- Vêtements portés
- Traits distinctifs
- Expression générale

Réponds en 2-3 phrases maximum, de manière factuelle et descriptive."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            description = response.choices[0].message.content.strip()
            print(f"✅ Personnage analysé: {description[:100]}...")
            
            return description
            
        except Exception as e:
            print(f"⚠️ Erreur analyse photo: {e}")
            return None
    
    async def generate_comic_pages(
        self,
        story_data: Dict[str, Any],
        art_style: str
    ) -> List[Dict[str, Any]]:
        """
        Génère toutes les planches de BD avec gpt-image-1
        Chaque planche est une image unique contenant 4 cases + bulles + texte
        """
        
        print(f"🎨 Génération des planches avec gpt-image-1...")
        
        style_info = self.art_styles.get(art_style, self.art_styles["cartoon"])
        comic_id = str(uuid.uuid4())
        comic_dir = self.cache_dir / comic_id
        comic_dir.mkdir(parents=True, exist_ok=True)
        
        generated_pages = []
        
        for page_data in story_data["pages"]:
            page_num = page_data["page_number"]
            
            try:
                print(f"📄 Génération planche {page_num}/{story_data['total_pages']}...")
                
                # Construire le prompt complet pour gpt-image-1
                # Ce prompt décrit UNE SEULE IMAGE contenant 4 cases de BD
                page_prompt = self._build_page_prompt(page_data, style_info)
                
                print(f"   Prompt: {page_prompt[:200]}...")
                
                # Générer l'image avec gpt-image-1
                image_path = await self._generate_page_with_gpt_image_1(
                    page_prompt,
                    comic_dir,
                    page_num
                )
                
                # Construire la réponse (format compatible avec le reste de l'app)
                page_info = {
                    "page_number": page_num,
                    "image_url": f"/static/cache/comics/{comic_id}/page_{page_num}.png",
                    "image_path": str(image_path),
                    "panels_count": len(page_data["panels"]),
                    "description": f"Planche {page_num} de {story_data['title']}"
                }
                
                generated_pages.append(page_info)
                print(f"✅ Planche {page_num} générée: {image_path}")
                
            except Exception as e:
                print(f"❌ Erreur génération planche {page_num}: {e}")
                raise Exception(f"Erreur génération planche {page_num}: {e}")
        
        # Sauvegarder les métadonnées
        metadata = {
            "comic_id": comic_id,
            "title": story_data["title"],
            "synopsis": story_data["synopsis"],
            "total_pages": len(generated_pages),
            "art_style": art_style,
            "creation_date": datetime.now().isoformat()
        }
        
        metadata_path = comic_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return generated_pages, comic_id
    
    def _build_page_prompt(self, page_data: Dict, style_info: Dict) -> str:
        """Construit le prompt pour gpt-image-1 pour générer UNE planche complète"""
        
        panels = page_data["panels"]
        
        # Construire la description de la planche complète
        prompt = f"""A single comic book page with 4 panels arranged in a 2x2 grid layout. 
{style_info['prompt_modifier']}.

The page shows:

PANEL 1 (Top-Left):
{panels[0]['visual_description']}
Speech bubbles: {self._format_bubbles_for_prompt(panels[0].get('dialogue_bubbles', []))}

PANEL 2 (Top-Right):
{panels[1]['visual_description']}
Speech bubbles: {self._format_bubbles_for_prompt(panels[1].get('dialogue_bubbles', []))}

PANEL 3 (Bottom-Left):
{panels[2]['visual_description']}
Speech bubbles: {self._format_bubbles_for_prompt(panels[2].get('dialogue_bubbles', []))}

PANEL 4 (Bottom-Right):
{panels[3]['visual_description']}
Speech bubbles: {self._format_bubbles_for_prompt(panels[3].get('dialogue_bubbles', []))}

IMPORTANT REQUIREMENTS:
- Clear 2x2 grid layout with black panel borders
- Each panel tells part of the story
- {style_info['prompt_modifier']}
- Include ALL speech bubbles with the EXACT text shown above
- Bubbles should be positioned as indicated (top-left, top-right, etc.)
- Consistent character designs across all 4 panels
- Professional comic book quality
- High resolution, vibrant colors
- No text outside the speech bubbles"""
        
        return prompt
    
    def _format_bubbles_for_prompt(self, bubbles: List[Dict]) -> str:
        """Formate les bulles de dialogue pour le prompt"""
        if not bubbles:
            return "No dialogue"
        
        bubble_texts = []
        for bubble in bubbles:
            position = bubble.get('position', 'center')
            text = bubble.get('text', '')
            bubble_texts.append(f"[{position}] \"{text}\"")
        
        return " | ".join(bubble_texts)
    
    async def _generate_page_with_gpt_image_1(
        self,
        prompt: str,
        output_dir: Path,
        page_num: int
    ) -> Path:
        """Génère une planche de BD avec gpt-image-1"""
        
        try:
            print(f"   🎨 Appel gpt-image-1...")
            
            # Générer l'image avec gpt-image-1
            # Note: gpt-image-1 retourne base64 par défaut (comme dans coloring_generator_gpt4o.py)
            # Ne PAS spécifier response_format, juste récupérer b64_json directement
            response = await self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1536",  # Format portrait pour une planche BD 2x2 (plus de hauteur)
                quality="high",  # Haute qualité pour les BD
                n=1
            )
            
            print(f"   [RESPONSE] Réponse reçue de gpt-image-1")
            
            # gpt-image-1 retourne base64 directement (comme pour les coloriages)
            if hasattr(response, 'data') and len(response.data) > 0:
                image_b64 = response.data[0].b64_json
                print(f"   [OK] Image reçue (base64: {len(image_b64)} caractères)")
                
                # Décoder l'image
                image_data = base64.b64decode(image_b64)
                
                # Vérifier les dimensions réelles de l'image générée
                img = Image.open(io.BytesIO(image_data))
                actual_width, actual_height = img.size
                print(f"   [DIMENSIONS] Image générée: {actual_width}x{actual_height}")
                
                # Sauvegarder
                output_path = output_dir / f"page_{page_num}.png"
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                print(f"   ✅ Planche sauvegardée: {output_path.name} ({len(image_data)} bytes, {actual_width}x{actual_height})")
                return output_path
            else:
                print(f"   [ERROR] Format de réponse inattendu")
                raise Exception("Format de réponse gpt-image-1 inattendu")
            
        except Exception as e:
            print(f"   ❌ Erreur gpt-image-1: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Erreur génération image: {e}")
    
    async def create_complete_comic(
        self,
        theme: str,
        num_pages: int,
        art_style: str,
        custom_prompt: Optional[str] = None,
        character_photo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crée une bande dessinée complète
        1. Génère le scénario avec gpt-4o-mini
        2. Génère les planches avec gpt-image-1
        """
        
        start_time = datetime.now()
        
        try:
            # 1. Générer le scénario
            print("📝 Étape 1: Génération du scénario...")
            story_data = await self.generate_comic_story(
                theme=theme,
                num_pages=num_pages,
                art_style=art_style,
                custom_prompt=custom_prompt,
                character_photo_path=character_photo_path
            )
            
            # 2. Générer les images
            print("🎨 Étape 2: Génération des planches...")
            pages, comic_id = await self.generate_comic_pages(
                story_data=story_data,
                art_style=art_style
            )
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "comic_id": comic_id,
                "title": story_data["title"],
                "synopsis": story_data["synopsis"],
                "pages": pages,
                "total_pages": len(pages),
                "theme": theme,
                "art_style": art_style,
                "generation_time": generation_time
            }
            
            print(f"✅ BD complète générée en {generation_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur création BD: {e}")
            return {
                "success": False,
                "error": str(e),
                "comic_id": None,
                "title": "Erreur",
                "pages": [],
                "total_pages": 0
            }

