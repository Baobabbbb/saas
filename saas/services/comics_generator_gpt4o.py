"""
Générateur de bandes dessinées avec gpt-4o-mini + gemini-3-pro-image-preview
Architecture: gpt-4o-mini crée le scénario détaillé, gemini-3-pro-image-preview génère les planches
"""

import openai
from openai import AsyncOpenAI
from google import genai
from google.genai import types
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
from services.supabase_storage import get_storage_service

load_dotenv()


class ComicsGeneratorGPT4o:
    """Générateur de bandes dessinées avec GPT-4o-mini (scénario) + gemini-3-pro-image-preview (images)"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY manquante dans les variables d'environnement")
        
        self.client = AsyncOpenAI(api_key=self.openai_key)
        
        # Client Gemini pour la génération d'images
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY manquante dans les variables d'environnement")
        
        self.gemini_client = genai.Client(api_key=self.gemini_api_key)
        self.cache_dir = Path("static/cache/comics")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Styles artistiques disponibles
        self.art_styles = {
            "3d": {
                "name": "3D",
                "description": "Style 3D avec effets de profondeur et relief",
                "prompt_modifier": "3D illustration, three-dimensional, depth effect, volumetric lighting, realistic shadows, modern digital art, CGI style"
            },
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
            },
            "robots": {
                "name": "Robots",
                "description": "Aventures avec des robots et la technologie",
                "keywords": "robots, technology, futuristic, AI, machines, sci-fi"
            },
            "chevaliers": {
                "name": "Chevaliers",
                "description": "Aventures de chevaliers et châteaux",
                "keywords": "knights, castles, medieval, dragons, swords, armor, quest"
            },
            "sports": {
                "name": "Sports",
                "description": "Aventures sportives et compétitions",
                "keywords": "sports, football, basketball, competition, team, victory, games"
            },
            "musique": {
                "name": "Musique",
                "description": "Concerts et aventures musicales",
                "keywords": "music, concerts, instruments, band, songs, rhythm, melody"
            },
            "cirque": {
                "name": "Cirque",
                "description": "Spectacles de cirque et acrobaties",
                "keywords": "circus, acrobats, clowns, trapeze, juggling, entertainment, show"
            },
            "licornes": {
                "name": "Licornes",
                "description": "Aventures avec des licornes magiques",
                "keywords": "unicorns, magic, rainbow, sparkles, fantasy, mystical creatures"
            },
            "vehicules": {
                "name": "Véhicules",
                "description": "Aventures avec voitures et transports",
                "keywords": "cars, vehicles, transportation, race, trucks, bikes, adventure"
            },
            "cuisine": {
                "name": "Cuisine",
                "description": "Recettes et aventures culinaires",
                "keywords": "cooking, recipes, kitchen, food, baking, chef, delicious"
            },
            "jardin": {
                "name": "Jardin",
                "description": "Aventures dans le jardin avec plantes et fleurs",
                "keywords": "garden, plants, flowers, nature, butterflies, bees, growing"
            },
            "voyage_temps": {
                "name": "Voyage dans le temps",
                "description": "Aventures temporelles et voyages dans le passé/futur",
                "keywords": "time travel, past, future, history, adventure, discovery, timeline"
            },
            # Thèmes avec noms anglais pour compatibilité
            "space": {
                "name": "Espace",
                "description": "Aventures spatiales avec fusées et planètes",
                "keywords": "space, planets, rockets, astronauts, stars, galaxy"
            },
            "ocean": {
                "name": "Océan",
                "description": "Aventures sous-marines",
                "keywords": "ocean, underwater, sea creatures, coral reef, diving, marine life"
            },
            "adventure": {
                "name": "Aventure",
                "description": "Exploration et découvertes",
                "keywords": "adventure, exploration, discovery, journey, quest, exciting"
            },
            "animals": {
                "name": "Animaux",
                "description": "Histoires avec des animaux mignons",
                "keywords": "cute animals, forest, friendship, nature"
            },
            "magic": {
                "name": "Magie",
                "description": "Monde magique et sortilèges",
                "keywords": "magic, spells, wizards, enchanted, mystical, fantasy"
            },
            "friendship": {
                "name": "Amitié",
                "description": "Histoires d'amitié",
                "keywords": "friendship, friends, together, support, bond, caring"
            },
            "forest": {
                "name": "Forêt",
                "description": "Mystères de la forêt",
                "keywords": "forest, trees, nature, wildlife, exploration, adventure"
            },
            "dinosaurs": {
                "name": "Dinosaures",
                "description": "L'époque des dinosaures",
                "keywords": "dinosaurs, prehistoric, adventure, jungle, T-Rex, fossils"
            },
            "fairy_tale": {
                "name": "Conte de fées",
                "description": "Contes classiques revisités",
                "keywords": "fairy tale, princess, castle, magic, storybook, classic"
            },
            "superhero": {
                "name": "Super-héros",
                "description": "Aventures héroïques",
                "keywords": "superheroes, powers, action, city, rescue, hero"
            },
            "knights": {
                "name": "Chevaliers",
                "description": "Aventures de chevaliers et châteaux",
                "keywords": "knights, castles, medieval, dragons, swords, armor, quest"
            },
            "unicorns": {
                "name": "Licornes",
                "description": "Aventures avec des licornes magiques",
                "keywords": "unicorns, magic, rainbow, sparkles, fantasy, mystical creatures"
            },
            "vehicles": {
                "name": "Véhicules",
                "description": "Aventures avec voitures et transports",
                "keywords": "cars, vehicles, transportation, race, trucks, bikes, adventure"
            },
            "cooking": {
                "name": "Cuisine",
                "description": "Recettes et aventures culinaires",
                "keywords": "cooking, recipes, kitchen, food, baking, chef, delicious"
            },
            "garden": {
                "name": "Jardin",
                "description": "Aventures dans le jardin avec plantes et fleurs",
                "keywords": "garden, plants, flowers, nature, butterflies, bees, growing"
            },
            "time_travel": {
                "name": "Voyage dans le temps",
                "description": "Aventures temporelles et voyages dans le passé/futur",
                "keywords": "time travel, past, future, history, adventure, discovery, timeline"
            },
            "zoo": {
                "name": "Zoo",
                "description": "Aventures au zoo avec tous les animaux",
                "keywords": "zoo, animals, lions, elephants, giraffes, monkeys, penguins, adventure, visit"
            },
            "fete": {
                "name": "Fête",
                "description": "Anniversaires et célébrations joyeuses",
                "keywords": "party, birthday, celebration, cake, balloons, presents, fun, friends, joy"
            },
            "party": {
                "name": "Fête",
                "description": "Anniversaires et célébrations joyeuses",
                "keywords": "party, birthday, celebration, cake, balloons, presents, fun, friends, joy"
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
        prompt = f"""Tu es un scénariste expert en bandes dessinées pour enfants de 6-10 ans. Tu écris en français impeccable sans aucune faute d'orthographe.

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
{("3. CRITIQUE ABSOLU: Le personnage décrit ci-dessus DOIT être le HÉROS PRINCIPAL et apparaître dans LES 4 CASES de chaque planche. C'est LUI qui fait les actions, c'est LUI le protagoniste. Dans CHAQUE case, commence la description par: 'The main character (the person described above) is...' pour que gpt-image-1-mini sache que c'est ce personnage précis qui doit apparaître: " + character_description) if character_description else ""}
3. Chaque case doit avoir:
   - Une description visuelle ULTRA DÉTAILLÉE (pour gpt-image-1-mini)
   - Des dialogues dans des bulles (maximum 2 bulles par case)
   - Une indication de l'action ou l'émotion

4. CRITIQUE pour les BULLES DE DIALOGUE:
   - TOUS les textes doivent être en FRANÇAIS PARFAIT sans faute d'orthographe
   - Les bulles doivent contenir le texte EXACT à afficher dans l'image finale
   - Le texte doit être COURT (maximum 8-10 mots par bulle pour tenir dans la bulle)
   - Langage simple et adapté aux enfants de 6-10 ans
   - Pas de fautes d'orthographe, de grammaire ou de conjugaison
   - Vérifie chaque mot : "tu" au lieu de "t", "c'est" au lieu de "cé", etc.
   - Les bulles doivent être positionnées pour ne pas cacher les personnages
   - Précise la position suggérée de chaque bulle (haut-gauche, haut-droite, bas-gauche, bas-droite)

5. DESCRIPTIONS VISUELLES ULTRA DÉTAILLÉES:
   Pour chaque case, décris TOUT en détail pour que gpt-image-1-mini puisse générer l'image parfaite:
   - Les personnages: âge, vêtements, couleurs, positions, expressions faciales
   - Le décor: lieu précis, objets visibles, couleurs, ambiance
   - L'action: ce qui se passe exactement dans cette case
   - Le cadrage: plan large, gros plan, plan américain, etc.
   - La lumière et l'ambiance: jour/nuit, lumineux/sombre, etc.

   EXEMPLE DE BONNE DESCRIPTION:
   "Comic book panel showing an 8-year-old girl with long brown hair wearing a yellow t-shirt and blue jeans,
   standing in her colorful bedroom with toys on shelves behind her. She looks surprised with wide eyes and
   open mouth, pointing at a glowing magic wand on her bed. Bright sunlight comes through the window.
   {style_info['prompt_modifier']}. The panel has a speech bubble in the top-right corner saying 'Wow ! Une baguette magique !'"

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
          "visual_description": "Description ULTRA détaillée en anglais pour gpt-image-1-mini (minimum 40 mots)",
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
- Les descriptions visuelles sont en ANGLAIS (pour gpt-image-1-mini)
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
    
    async def _transform_photo_to_avatar(self, photo_path: str) -> str:
        """Transforme une photo en avatar cartoon avec OpenAI images.edit pour éviter les blocages Gemini
        
        Args:
            photo_path: Chemin vers la photo originale
            
        Returns:
            Chemin vers l'avatar créé
            
        Raises:
            Exception: Si la transformation échoue
        """
        try:
            print(f"   🎨 Transformation photo en avatar cartoon avec OpenAI...")
            
            # Charger l'image
            input_image = Image.open(photo_path)
            width, height = input_image.size
            
            # Convertir en RGBA (requis par images.edit)
            if input_image.mode != 'RGBA':
                input_image = input_image.convert('RGBA')
            
            # Redimensionner en carré 1024x1024 (requis pour images.edit)
            size = 1024
            square_image = Image.new('RGBA', (size, size), (255, 255, 255, 255))
            
            # Calculer le ratio pour garder les proportions
            ratio = min(size / width, size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            resized_image = input_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Centrer l'image
            x_offset = (size - new_width) // 2
            y_offset = (size - new_height) // 2
            square_image.paste(resized_image, (x_offset, y_offset), resized_image)
            
            # Sauvegarder temporairement en PNG (RGBA)
            temp_input_path = self.cache_dir / f"temp_input_{uuid.uuid4().hex[:8]}.png"
            square_image.save(temp_input_path, 'PNG')
            
            # Créer un masque blanc en RGBA (tout l'image sera modifiée)
            mask_image = Image.new('RGBA', (size, size), (255, 255, 255, 255))
            temp_mask_path = self.cache_dir / f"temp_mask_{uuid.uuid4().hex[:8]}.png"
            mask_image.save(temp_mask_path, 'PNG')
            
            # Prompt pour transformer en avatar cartoon
            avatar_prompt = "Transform this into a friendly cartoon-style avatar character suitable for a children's comic book. Make it clearly a cartoon illustration with recognizable features preserved."
            
            # Utiliser images.edit pour transformer en avatar
            with open(temp_input_path, "rb") as input_file, open(temp_mask_path, "rb") as mask_file:
                response = await self.client.images.edit(
                    image=input_file,
                    mask=mask_file,
                    prompt=avatar_prompt,
                    n=1,
                    size=f"{size}x{size}"
                )
            
            # Récupérer l'URL de l'image générée
            avatar_url = response.data[0].url
            
            # Télécharger l'image
            import httpx
            async with httpx.AsyncClient() as client:
                avatar_response = await client.get(avatar_url)
                avatar_response.raise_for_status()
                avatar_data = avatar_response.content
            
            # Sauvegarder l'avatar
            avatar_path = self.cache_dir / f"avatar_{uuid.uuid4().hex[:8]}.png"
            with open(avatar_path, 'wb') as f:
                f.write(avatar_data)
            
            # Nettoyer les fichiers temporaires
            temp_input_path.unlink(missing_ok=True)
            temp_mask_path.unlink(missing_ok=True)
            
            print(f"   ✅ Avatar cartoon créé: {avatar_path.name}")
            return str(avatar_path)
            
        except Exception as e:
            print(f"   ❌ Erreur création avatar: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Échec transformation photo en avatar: {e}")
    
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
                                "text": """Analyse cette photo et décris le personnage de manière ULTRA DÉTAILLÉE pour que gpt-image-1-mini puisse le recréer EXACTEMENT dans une bande dessinée.

IMPORTANT: La description doit être suffisamment précise pour que le personnage soit PARFAITEMENT RECONNAISSABLE dans la BD.

Décris EN DÉTAIL:
- Âge approximatif (ex: "enfant d'environ 8 ans")
- Genre
- Visage: forme, teint de peau (couleur précise), traits faciaux distinctifs
- Cheveux: couleur exacte, longueur, style, texture (raides/bouclés/ondulés)
- Yeux: couleur exacte, forme, taille
- Nez: forme, taille
- Bouche: forme, expression
- Oreilles: si visibles, forme
- Morphologie: taille, corpulence
- Vêtements: couleurs précises, style, motifs, détails
- Accessoires: lunettes, bijoux, chapeau, etc.
- Traits distinctifs: taches de rousseur, grain de beauté, fossettes, etc.
- Expression générale et posture

Réponds en 5-7 phrases TRÈS DÉTAILLÉES, en anglais (pour gpt-image-1-mini), de manière factuelle et précise. Commence par "A [age] year old [gender] with..."."""
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
                max_tokens=500
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
        art_style: str,
        character_photo_path: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Génère toutes les planches de BD avec gemini-3-pro-image-preview
        Chaque planche est une image unique contenant 4 cases + bulles + texte
        Si character_photo_path est fourni, analyse la photo et utilise la description dans le prompt
        """
        
        print(f"🎨 Génération des planches avec gemini-3-pro-image-preview...")
        
        if character_photo_path:
            print(f"   📸 Photo de personnage fournie, utilisation image-to-image pour fidélité maximale")
        
        style_info = self.art_styles.get(art_style, self.art_styles["cartoon"])
        comic_id = str(uuid.uuid4())
        comic_dir = self.cache_dir / comic_id
        comic_dir.mkdir(parents=True, exist_ok=True)
        
        # Si une photo de personnage est fournie, transformer d'abord en avatar AVANT de générer les planches
        avatar_path = None
        if character_photo_path:
            print(f"   🎨 Transformation photo en avatar cartoon avec OpenAI (OBLIGATOIRE)...")
            avatar_path = await self._transform_photo_to_avatar(character_photo_path)
            print(f"   ✅ Avatar créé: {avatar_path}")
        
        generated_pages = []
        
        for page_data in story_data["pages"]:
            page_num = page_data["page_number"]
            
            try:
                print(f"📄 Génération planche {page_num}/{story_data['total_pages']}...")
                
                # Construire le prompt complet pour gemini-3-pro-image-preview
                # Ce prompt décrit UNE SEULE IMAGE contenant 4 cases de BD
                page_prompt = self._build_page_prompt(page_data, style_info)
                
                print(f"   Prompt: {page_prompt[:200]}...")
                
                # Générer l'image avec gemini-3-pro-image-preview
                # Si avatar_path est fourni, utilise l'avatar (pas la photo originale)
                image_path = await self._generate_page_with_gpt_image_1(
                    page_prompt,
                    comic_dir,
                    page_num,
                    character_photo_path=avatar_path if avatar_path else None,  # Passer l'avatar, pas la photo originale
                    page_data=page_data  # Passer page_data pour extraire les panels
                )
                
                # 📤 Upload OBLIGATOIRE vers Supabase Storage
                storage_service = get_storage_service()
                if not storage_service:
                    raise Exception("Service Supabase Storage non disponible")

                if not user_id:
                    raise Exception("user_id requis pour l'upload Supabase Storage")

                upload_result = await storage_service.upload_file(
                    file_path=str(image_path),
                    user_id=user_id,
                    content_type="comic",
                    creation_id=comic_id,
                    custom_filename=f"page_{page_num}.png"
                )

                if not upload_result["success"]:
                    raise Exception(f"Échec upload Supabase Storage: {upload_result.get('error', 'Erreur inconnue')}")

                # Utiliser l'URL signée Supabase (valide 1 an)
                image_url = upload_result["signed_url"]
                print(f"✅ Image uploadée vers Supabase Storage: {image_url[:50]}...")
                
                # Construire la réponse (format compatible avec le reste de l'app)
                page_info = {
                    "page_number": page_num,
                    "image_url": image_url,
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
        """Construit le prompt pour gemini-3-pro-image-preview pour générer UNE planche complète"""
        
        panels = page_data["panels"]
        
        # Construire la description de la planche complète
        prompt = f"""A professional comic book page in square format with 4 panels arranged in a 2x2 grid layout.
{style_info['prompt_modifier']}.

LAYOUT:
- Square format (1024x1024 pixels)
- 4 equally-sized panels in a clean 2x2 grid
- Generous white margins around the entire grid
- Each panel is smaller with thick black borders and plenty of spacing between them
- Professional comic book page composition with clean gutters

PANEL CONTENT:

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

STYLE REQUIREMENTS:
- {style_info['prompt_modifier']}
- Clear, bold black panel borders with generous spacing between panels
- Each panel should be significantly smaller to leave plenty of white space around them
- Professional comic book page layout with wide gutters (white space between panels)
- CRITICAL: Include ALL speech bubbles with the EXACT text shown above - DO NOT MODIFY, CHANGE, or CORRECT the text in the speech bubbles under any circumstances
- The text in speech bubbles must be COPIED VERBATIM from what is provided - no grammar fixes, no spelling corrections, no rephrasing
- Consistent character designs across all 4 panels
- High quality, professional comic book art
- Vibrant colors and clear composition
- No text outside the speech bubbles
- Clean white background with margins around the entire 2x2 panel grid"""
        
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
        page_num: int,
        character_photo_path: Optional[str] = None,
        page_data: Optional[Dict] = None
    ) -> Path:
        """Génère une planche de BD avec gemini-3-pro-image-preview (avec ou sans photo de référence)
        
        Selon la documentation officielle Gemini:
        - Text-to-image: contents=[prompt]
        - Image-to-image: contents=[prompt, image] où image est un objet PIL Image
        - Réponse: response.parts avec part.as_image() pour obtenir l'image
        """
        
        try:
            print(f"   🎨 Appel gemini-3-pro-image-preview...")
            
            # Si un avatar est fourni (déjà transformé dans generate_comic_pages), l'utiliser avec Gemini
            if character_photo_path:
                print(f"   📸 Avatar cartoon fourni, utilisation avec Gemini: {character_photo_path}")
                
                # Charger l'avatar (déjà transformé en cartoon avec OpenAI)
                input_image = Image.open(character_photo_path)
                print(f"   [DEBUG] Avatar chargé: {input_image.size}, mode: {input_image.mode}")
                
                # Créer un prompt très court et simple pour l'image-to-image
                # Le prompt complet de la BD est trop long et peut déclencher des filtres
                # Utiliser une approche similaire aux coloriages : prompt court et direct
                if page_data and 'panels' in page_data:
                    panels = page_data['panels']
                    # Extraire les descriptions courtes des panels
                    panel_descs = []
                    for i, panel in enumerate(panels[:4]):
                        desc = panel.get('visual_description', '')[:60]  # Limiter à 60 caractères
                        # Nettoyer la description : remplacer les références à "person" ou "main character"
                        desc = desc.replace('main character', 'character')
                        desc = desc.replace('the person', 'the character')
                        desc = desc.replace('this person', 'this character')
                        desc = desc.replace('person', 'character')
                        panel_descs.append(desc)
                    
                    # Prompt très simple pour avatar cartoon (pas "photo")
                    simple_prompt = f"""Create a comic book page with 4 panels in a 2x2 grid. Use the cartoon character from this image as the main character in all panels.

Panel 1: {panel_descs[0] if len(panel_descs) > 0 else 'First scene'}
Panel 2: {panel_descs[1] if len(panel_descs) > 1 else 'Second scene'}
Panel 3: {panel_descs[2] if len(panel_descs) > 2 else 'Third scene'}
Panel 4: {panel_descs[3] if len(panel_descs) > 3 else 'Fourth scene'}

Style: cartoon, colorful, child-friendly."""
                else:
                    # Si pas de page_data, utiliser un prompt très simple
                    simple_prompt = "Create a comic book page with 4 panels in a 2x2 grid. Use the cartoon character from this image as the main character. Cartoon style, colorful, child-friendly."
                
                print(f"   [DEBUG] Prompt image-to-image simplifié ({len(simple_prompt)} chars): {simple_prompt[:200]}...")
                
                # Utiliser exactement la même méthode que les coloriages qui fonctionnent
                response = self.gemini_client.models.generate_content(
                    model="gemini-3-pro-image-preview",
                    contents=[simple_prompt, input_image]  # Prompt d'abord, puis image (comme les coloriages)
                )
                print(f"   [DEBUG] Réponse image-to-image reçue")
                
                # Vérifier prompt_feedback pour voir s'il y a un blocage
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    print(f"   [DEBUG] prompt_feedback: {response.prompt_feedback}")
                    if hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                        print(f"   [WARNING] Block reason: {response.prompt_feedback.block_reason}")
                        if hasattr(response.prompt_feedback, 'block_reason_message') and response.prompt_feedback.block_reason_message:
                            print(f"   [WARNING] Block message: {response.prompt_feedback.block_reason_message}")
            else:
                # Générer l'image normalement sans photo de référence (text-to-image)
                response = self.gemini_client.models.generate_content(
                    model="gemini-3-pro-image-preview",
                    contents=[prompt]
                )
                print(f"   [DEBUG] Réponse text-to-image reçue")
            
            print(f"   [RESPONSE] Réponse reçue de gemini-3-pro-image-preview")
            
            # Vérifier prompt_feedback AVANT d'essayer d'extraire l'image
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                print(f"   [DEBUG] prompt_feedback: {response.prompt_feedback}")
                if hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                    block_reason = response.prompt_feedback.block_reason
                    block_message = getattr(response.prompt_feedback, 'block_reason_message', None)
                    print(f"   [ERROR] Génération bloquée par Gemini! Reason: {block_reason}, Message: {block_message}")
                    raise Exception(f"Génération bloquée par Gemini (sécurité): {block_reason}. Message: {block_message}")
            
            # Inspecter la structure complète de la réponse
            print(f"   [DEBUG] Response type: {type(response)}")
            
            image_data = None
            generated_image = None
            
            # Utiliser la même méthode que les coloriages qui fonctionnent
            # response.candidates[0].content.parts
            if hasattr(response, 'candidates') and response.candidates is not None and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data is not None:
                            # Essayer différentes méthodes d'accès aux données (comme les coloriages)
                            if hasattr(part.inline_data, 'data'):
                                data = part.inline_data.data
                                
                                # Vérifier que data n'est pas None
                                if data is None:
                                    continue
                                
                                # Si c'est une string, c'est probablement du base64
                                if isinstance(data, str):
                                    try:
                                        image_data = base64.b64decode(data)
                                        print(f"   [OK] Image décodée depuis base64 string: {len(image_data)} bytes")
                                        break
                                    except Exception as e:
                                        print(f"   [ERROR] Erreur decode base64: {e}")
                                        continue
                                elif isinstance(data, bytes):
                                    image_data = data
                                    print(f"   [OK] Image déjà en bytes: {len(image_data)} bytes")
                                    break
                                else:
                                    # Essayer de convertir en string puis décoder
                                    try:
                                        data_str = str(data)
                                        image_data = base64.b64decode(data_str)
                                        print(f"   [OK] Image convertie puis décodée: {len(image_data)} bytes")
                                        break
                                    except Exception as e:
                                        print(f"   [ERROR] Impossible de decoder les donnees: {e}")
                                        continue
                                
                                # Vérifier que les données sont valides
                                if image_data:
                                    try:
                                        test_img = Image.open(io.BytesIO(image_data))
                                        print(f"   [OK] Image valide: {test_img.size}")
                                        break
                                    except Exception as e:
                                        print(f"   [ERROR] Donnees decodees ne sont pas une image valide: {e}")
                                        image_data = None
                                        continue
                        elif hasattr(part, 'text') and part.text:
                            print(f"   [TEXT] {part.text[:200]}...")
            
            # Si on a obtenu une image PIL via as_image(), la convertir en bytes
            if generated_image:
                # Convertir l'image PIL en bytes
                img_bytes = io.BytesIO()
                generated_image.save(img_bytes, format='PNG')
                image_data = img_bytes.getvalue()
                print(f"   [OK] Image convertie en bytes: {len(image_data)} bytes")
            
            # Si toujours pas d'image, essayer d'inspecter toute la structure
            if not image_data and not generated_image:
                print(f"   [DEBUG] Aucune image trouvée, inspection complète...")
                try:
                    # Essayer de convertir en dict
                    if hasattr(response, 'model_dump'):
                        response_dict = response.model_dump()
                        print(f"   [DEBUG] Response dict keys: {list(response_dict.keys())}")
                        # Afficher le contenu complet pour debug
                        import json
                        print(f"   [DEBUG] Response dict (first 1000 chars): {str(response_dict)[:1000]}")
                except Exception as e:
                    print(f"   [DEBUG] Erreur inspection: {e}")
            
            if image_data:
                print(f"   [OK] Image reçue ({len(image_data)} bytes)")
                
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
                print(f"   [ERROR] Aucune image trouvée dans la réponse")
                # Logs de debug supplémentaires
                print(f"   [DEBUG] Response type: {type(response)}")
                print(f"   [DEBUG] Response has parts: {hasattr(response, 'parts')}")
                if hasattr(response, 'parts'):
                    print(f"   [DEBUG] Number of parts: {len(response.parts)}")
                raise Exception("Format de réponse gemini-3-pro-image-preview inattendu - aucune image trouvée")
            
        except Exception as e:
            print(f"   ❌ Erreur gemini-3-pro-image-preview: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Erreur génération image: {e}")
    
    async def create_complete_comic(
        self,
        theme: str,
        num_pages: int,
        art_style: str,
        custom_prompt: Optional[str] = None,
        character_photo_path: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crée une bande dessinée complète
        1. Génère le scénario avec gpt-4o-mini
        2. Génère les planches avec gpt-image-1-mini
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
                art_style=art_style,
                character_photo_path=character_photo_path,  # Passer la photo pour images.edit()
                user_id=user_id  # Passer user_id pour upload Supabase Storage
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

