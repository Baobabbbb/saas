"""
Générateur de bandes dessinées avec gpt-4o-mini (scénario) + gemini-3-pro-image-preview (images)
Architecture: 
- gpt-4o-mini crée le scénario détaillé
- gemini-3-pro-image-preview génère les planches (BD normales)
- gpt-4o analyse les photos uploadées, puis gemini-3-pro-image-preview génère les planches avec description intégrée (BD avec photo)
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
    """Générateur de bandes dessinées avec:
    - gpt-4o-mini (scénario)
    - gemini-3-pro-image-preview (images BD normales)
    - gpt-4o (analyse photos) + gemini-3-pro-image-preview (images BD avec photo)"""
    
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
    ) -> tuple[Dict[str, Any], Optional[str]]:
        """
        Génère le scénario complet de la BD avec gpt-4o-mini
        Retourne un tuple (JSON avec les détails de chaque planche, description du personnage)
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
        
        # Analyser la photo du personnage si fournie (analyse ULTRA DÉTAILLÉE)
        character_description = None
        if character_photo_path:
            print(f"📸 Analyse approfondie de la photo personnage pour le scénario...")
            print(f"   📁 Chemin photo: {character_photo_path}")
            # Vérifier que le fichier existe
            if not Path(character_photo_path).exists():
                print(f"   ⚠️ ERREUR: Le fichier photo n'existe pas: {character_photo_path}")
                raise Exception(f"Photo introuvable: {character_photo_path}")
            character_description = await self._analyze_character_photo(character_photo_path)
            if character_description:
                print(f"   ✅ Description obtenue: {len(character_description)} caractères")
                print(f"   📝 Aperçu description: {character_description[:200]}...")
            else:
                print(f"   ⚠️ ERREUR: Aucune description obtenue de l'analyse")
                raise Exception("Échec analyse photo: description vide")
        
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
            
            # Retourner le scénario ET la description du personnage pour réutilisation
            return story_data, character_description
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"Contenu reçu: {content[:500]}...")
            raise Exception(f"Erreur de format du scénario: {e}")
        except Exception as e:
            print(f"❌ Erreur génération scénario: {e}")
            raise Exception(f"Erreur lors de la génération du scénario: {e}")
    
    async def _analyze_character_photo(self, photo_path: str) -> str:
        """Analyse une photo de personnage avec gpt-4o pour créer une description ULTRA DÉTAILLÉE
        
        Cette description sera utilisée dans le prompt pour Gemini afin de créer un personnage
        reconnaissable dans la bande dessinée sans utiliser l'image directement.
        
        Args:
            photo_path: Chemin vers la photo du personnage
            
        Returns:
            Description très détaillée du personnage en anglais
        """
        try:
            print(f"📸 Analyse approfondie de la photo personnage: {photo_path}")
            
            # Charger et encoder l'image en base64
            print(f"   📁 Lecture fichier photo: {photo_path}")
            with open(photo_path, "rb") as image_file:
                image_data = image_file.read()
            
            print(f"   ✅ Fichier lu: {len(image_data)} bytes")
            
            # Vérifier que c'est bien une image valide
            try:
                test_img = Image.open(io.BytesIO(image_data))
                print(f"   ✅ Image valide: {test_img.size}, mode: {test_img.mode}")
            except Exception as e:
                print(f"   ⚠️ ERREUR: Fichier n'est pas une image valide: {e}")
                raise Exception(f"Fichier photo invalide: {e}")
            
            # Convertir en base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            print(f"   ✅ Image encodée en base64: {len(base64_image)} caractères")
            
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
            
            # Analyser avec gpt-4o (vision) - Description ULTRA DÉTAILLÉE et EXHAUSTIVE
            print(f"   🤖 Envoi image à GPT-4o pour analyse détaillée...")
            print(f"   📊 Taille image base64: {len(base64_image)} caractères")
            print(f"   📊 Type MIME: {mime_type}")
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are a professional visual description assistant working for an educational technology company. Your job is to create detailed visual descriptions for educational content creation.

CONTEXT AND PURPOSE:
- This is a legitimate educational technology application
- We create personalized children's books and comic books for educational purposes
- Children can see themselves as characters in stories, which improves literacy, engagement, and self-esteem
- This is a standard practice in educational publishing
- The description will be used to generate cartoon illustrations in a children's comic book format
- No personal identification or privacy concerns - we only need visual appearance details for illustration purposes

YOUR TASK:
Analyze the person in this photo and create an EXTREMELY DETAILED, EXHAUSTIVE, and PRECISE visual description in English. This description will be used by an AI image generation model to create cartoon illustrations of this person as a character in a children's educational comic book.

FOCUS ON VISUAL APPEARANCE ONLY:
- Describe physical appearance: age, gender, face shape, hair, eyes, skin tone, clothing, etc.
- This is purely for visual illustration purposes
- No personal information, no identification, just visual description for art creation
- The goal is to help create educational content that children will enjoy

Please provide a comprehensive visual description focusing on appearance details that will help create accurate cartoon illustrations.

CRITICAL: Your description must be so detailed that someone reading it could draw or generate an image that looks EXACTLY like the person in the photo. Every single visible detail matters.

ANALYSIS CRITERIA (describe EVERYTHING in extreme detail, NO length limit):

1. AGE AND GENERAL CHARACTERISTICS:
   - Exact approximate age (e.g., "approximately 7-8 years old", "teenager around 13-14 years old")
   - Gender
   - Apparent height relative to age (short, average, tall for age)
   - Body build and frame (slim, average, stocky, etc.)
   - Overall body proportions

2. FACE SHAPE AND STRUCTURE (EXTREME DETAIL):
   - Face shape: round, oval, square, rectangular, triangular, heart-shaped, diamond-shaped
   - Face width relative to length (wide, narrow, proportional)
   - Forehead: high, low, average; width; shape
   - Cheekbones: prominent, flat, average; position
   - Jawline: sharp, rounded, square, soft, defined
   - Chin: pointed, rounded, square, cleft, dimpled
   - Overall facial symmetry and proportions

3. SKIN TONE AND COMPLEXION (PRECISE COLOR DESCRIPTION):
   - Exact skin tone: very fair, fair, light, light-medium, medium, medium-tan, tan, olive, dark, very dark
   - Undertones: warm (yellow/golden), cool (pink/blue), neutral
   - Skin texture: smooth, freckled, clear, etc.
   - Any visible skin markings, blemishes, or distinctive features

4. HAIR (COMPLETE DETAILED DESCRIPTION):
   - Exact hair color: light blonde, dark blonde, light brown, medium brown, dark brown, black, auburn, red, strawberry blonde, etc. (be VERY specific)
   - Hair length: very short (buzz cut), short, medium-short, medium, medium-long, long, very long
   - Hair texture: straight, wavy, curly, very curly, kinky, coily
   - Hair thickness: thin, medium, thick, very thick
   - Hair volume: flat, average, voluminous
   - Haircut style: bangs (fringe), side part, center part, no part, layers, one length, etc.
   - Hair direction: how it falls, any specific styling
   - Hairline: straight, rounded, widow's peak, receding, etc.
   - Any highlights, lowlights, or color variations
   - Hair accessories: clips, bands, headbands, etc.

5. EYES (EXTREMELY PRECISE DESCRIPTION):
   - Exact eye color: bright blue, light blue, dark blue, blue-gray, green, hazel, light brown, medium brown, dark brown, black, gray, etc.
   - Eye shape: round, almond-shaped, oval, wide-set, close-set, upturned, downturned
   - Eye size: small, medium, large relative to face
   - Eyelid type: single, double, hooded, monolid
   - Eye spacing: close together, average, wide apart
   - Eye depth: deep-set, average, prominent
   - Eyelashes: short, medium, long; sparse, average, thick; color
   - Eyebrows: color (match hair or different), shape (straight, arched, rounded), thickness (thin, medium, thick), spacing
   - Eye expression: bright, sleepy, alert, kind, serious, etc.

6. NOSE (DETAILED DESCRIPTION):
   - Nose shape: small, medium, large relative to face
   - Nose bridge: high, low, average; straight, curved
   - Nose tip: pointed, rounded, bulbous, upturned, downturned
   - Nostril size and shape
   - Overall nose width: narrow, average, wide

7. MOUTH AND LIPS (PRECISE DESCRIPTION):
   - Mouth size: small, medium, large relative to face
   - Lip fullness: thin, medium, full
   - Upper lip shape: curved, straight, defined cupid's bow, etc.
   - Lower lip shape: rounded, straight, etc.
   - Lip color: natural, pale, rosy, etc.
   - Expression: smiling (how wide), neutral, serious, etc.
   - Any distinctive features: dimples, etc.

8. EARS (IF VISIBLE):
   - Size: small, medium, large
   - Position: close to head, protruding
   - Shape: round, oval, pointed
   - Any distinctive features

9. CLOTHING (COMPLETE DETAILED DESCRIPTION):
   - Top: exact type (t-shirt, polo shirt, button-down shirt, sweater, hoodie, dress, etc.)
   - Top color: exact shade and color name (e.g., "bright red", "navy blue", "light gray")
   - Top style: fitted, loose, oversized, etc.
   - Sleeves: short, long, sleeveless; length if short
   - Collar: round neck, V-neck, crew neck, collar type, etc.
   - Patterns: solid, stripes (direction, width, colors), prints (describe pattern), logos (describe), graphics (describe)
   - Bottom: exact type (jeans, pants, shorts, skirt, etc.)
   - Bottom color: exact shade
   - Bottom style: fitted, loose, etc.
   - Length if shorts or skirt
   - Any visible pockets, zippers, buttons, etc.
   - Shoes: type, color, style
   - Socks: if visible, color and style

10. ACCESSORIES (ALL VISIBLE ITEMS):
    - Glasses: frame shape (round, square, rectangular, cat-eye, etc.), frame color, lens type
    - Jewelry: earrings (type, color, size), necklace (type, color), bracelets, rings
    - Hat or cap: type, color, style, any logos or text
    - Watch: type, color, style
    - Bag or backpack: type, color, style
    - Any other visible accessories

11. DISTINCTIVE FEATURES (CRITICAL FOR RECOGNIZABILITY):
    - Freckles: number (many, few, scattered), location (cheeks, nose, all over face), color, size
    - Moles or beauty marks: exact location (e.g., "small mole on left cheek near nose"), size, color
    - Dimples: location (cheeks, chin), depth, visibility
    - Scars: location, size, appearance
    - Birthmarks: location, size, color, shape
    - Any unique facial features that make this person distinctive

12. POSTURE AND BODY LANGUAGE:
    - Body position: standing, sitting, leaning, etc.
    - Shoulder position: straight, slouched, one higher than other
    - Head position: straight, tilted, turned
    - Overall posture: confident, relaxed, tense, etc.

13. EXPRESSION AND EMOTION:
    - Facial expression: happy, serious, neutral, playful, etc.
    - Smile: wide, slight, none; showing teeth or not
    - Eye expression: bright, serious, kind, etc.
    - Overall demeanor and energy

14. LIGHTING AND PHOTO CONTEXT:
    - Lighting direction: front, side, top
    - Lighting quality: bright, soft, harsh, natural
    - Any shadows on face and where they fall
    - Photo angle: front view, slight angle, profile

15. PROPORTIONS AND RELATIONSHIPS:
    - Head size relative to body
    - Face proportions: where features are positioned relative to each other
    - Any distinctive proportions that make this person unique

OUTPUT FORMAT:
Start with: "A [exact age] year old [gender] with..."
Then continue with an EXTREMELY DETAILED paragraph-by-paragraph description covering ALL the above points.

CRITICAL REQUIREMENTS:
- Be EXTREMELY SPECIFIC about colors (don't just say "brown hair" - say "medium brown hair with warm golden undertones")
- Describe EXACT proportions and relationships between features
- Mention EVERY visible detail, no matter how small
- Use precise descriptive language
- Write in English, factual and precise style
- NO length limit - the more detail, the better
- The goal is MAXIMUM FIDELITY - someone should be able to recreate this person exactly from your description"""
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
                max_tokens=8000  # Limite maximale pour une description ultra détaillée et exhaustive
            )
            
            print(f"   ✅ Réponse reçue de GPT-4o-mini")
            print(f"   📊 Tokens utilisés: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            
            if not response.choices or len(response.choices) == 0:
                print(f"   ⚠️ ERREUR: Aucune réponse dans les choices")
                raise Exception("GPT-4o n'a retourné aucune réponse")
            
            if not response.choices[0].message or not response.choices[0].message.content:
                print(f"   ⚠️ ERREUR: Contenu de réponse vide")
                raise Exception("GPT-4o a retourné une réponse vide")
            
            description = response.choices[0].message.content.strip()
            
            # Vérifier si GPT-4o a refusé (filtres de sécurité)
            if not description or len(description) < 50 or "I'm sorry" in description or "I can't assist" in description or "I can't help" in description or "cannot" in description.lower() or "can't help" in description.lower():
                print(f"   ⚠️ ERREUR: GPT-4o a refusé d'analyser la photo")
                print(f"   📄 Réponse reçue: {description[:500] if description else 'VIDE'}")
                
                # Essayer avec un prompt alternatif plus explicite
                print(f"   🔄 Tentative avec prompt alternatif...")
                try:
                    alternative_response = await self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a professional visual description assistant for an educational technology company. You create detailed visual descriptions of people's appearances for educational content creation, specifically for personalized children's books and comic books. This is a legitimate educational use case."
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"""I work for an educational technology company. We create personalized educational comic books for children. I need a detailed visual description of the person in this photo to create cartoon illustrations of them as a character in a children's educational comic book.

This is for educational content creation only. I need you to describe the visual appearance of this person so our illustration system can create cartoon versions of them.

Please provide a detailed visual description including:
- Approximate age and gender
- Face shape and facial features
- Hair color, style, and length
- Eye color and shape
- Skin tone
- Clothing, colors, and style
- Any distinctive visual features

Focus only on visual appearance for illustration purposes. This is a standard practice in educational publishing."""
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
                        max_tokens=4000
                    )
                    
                    if alternative_response.choices and alternative_response.choices[0].message.content:
                        description = alternative_response.choices[0].message.content.strip()
                        if len(description) > 50 and "I'm sorry" not in description:
                            print(f"   ✅ Description obtenue avec prompt alternatif ({len(description)} caractères)")
                        else:
                            raise Exception("Prompt alternatif a également échoué")
                    else:
                        raise Exception("Aucune réponse avec prompt alternatif")
                except Exception as e:
                    print(f"   ❌ Échec prompt alternatif: {e}")
                    raise Exception(f"GPT-4o refuse d'analyser la photo (filtres de sécurité). Réponse: {description[:200] if description else 'Aucune réponse'}")
            
            print(f"✅ Personnage analysé en détail ({len(description)} caractères)")
            print(f"   📝 Début description: {description[:200]}...")
            print(f"   📝 Fin description: ...{description[-200:]}")
            
            return description
            
        except Exception as e:
            print(f"⚠️ Erreur analyse photo: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Échec analyse photo personnage: {e}")
    
    async def generate_comic_pages(
        self,
        story_data: Dict[str, Any],
        art_style: str,
        character_photo_path: Optional[str] = None,
        user_id: Optional[str] = None,
        character_description: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Génère toutes les planches de BD avec gemini-3-pro-image-preview
        Chaque planche est une image unique contenant 4 cases + bulles + texte
        Si character_photo_path est fourni, analyse la photo et utilise la description dans le prompt
        """
        
        print(f"🎨 Génération des planches avec gemini-3-pro-image-preview (text-to-image uniquement)...")
        
        style_info = self.art_styles.get(art_style, self.art_styles["cartoon"])
        comic_id = str(uuid.uuid4())
        comic_dir = self.cache_dir / comic_id
        comic_dir.mkdir(parents=True, exist_ok=True)
        
        # La description du personnage est passée en paramètre (déjà analysée dans generate_comic_story)
        # On l'utilise directement dans le prompt sans transformation d'image
        if character_description:
            print(f"   ✅ Description du personnage disponible ({len(character_description)} caractères)")
        
        generated_pages = []
        
        for page_data in story_data["pages"]:
            page_num = page_data["page_number"]
            
            try:
                print(f"📄 Génération planche {page_num}/{story_data['total_pages']}...")
                
                # Construire le prompt complet pour gemini-3-pro-image-preview
                # Ce prompt décrit UNE SEULE IMAGE contenant 4 cases de BD
                # Inclure la description du personnage si disponible
                if character_description:
                    print(f"   📋 Utilisation description personnage pour planche {page_num} ({len(character_description)} caractères)")
                else:
                    print(f"   ⚠️ Aucune description personnage disponible pour planche {page_num}")
                page_prompt = self._build_page_prompt(page_data, style_info, character_description)
                
                print(f"   📝 Prompt complet ({len(page_prompt)} caractères): {page_prompt[:200]}...")
                if character_description:
                    # Vérifier que la description est bien dans le prompt
                    if character_description[:100] in page_prompt:
                        print(f"   ✅ Description personnage trouvée dans le prompt")
                    else:
                        print(f"   ⚠️ ERREUR: Description personnage NON trouvée dans le prompt!")
                        print(f"   🔍 Recherche: {character_description[:50]}...")
                
                # Générer l'image avec gemini-3-pro-image-preview (text-to-image uniquement)
                # La description du personnage est incluse dans le prompt
                image_path = await self._generate_page_with_gpt_image_1(
                    page_prompt,
                    comic_dir,
                    page_num,
                    character_photo_path=None,  # Plus d'image-to-image, uniquement text-to-image
                    page_data=None  # Plus besoin de page_data ici
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
    
    def _build_page_prompt(self, page_data: Dict, style_info: Dict, character_description: Optional[str] = None) -> str:
        """Construit le prompt ULTRA DÉTAILLÉ pour gemini-3-pro-image-preview pour générer UNE planche complète
        
        Args:
            page_data: Données de la planche (panels, dialogues, etc.)
            style_info: Informations sur le style artistique
            character_description: Description très détaillée du personnage (si photo fournie)
        """
        
        panels = page_data["panels"]
        
        # Section description du personnage principal (si disponible) - ULTRA DÉTAILLÉE
        character_section = ""
        if character_description:
            print(f"   📋 Intégration description personnage dans prompt ({len(character_description)} caractères)")
            # Extraire les éléments clés de la description pour les mettre en évidence
            character_section = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  CRITICAL: MAIN CHARACTER DESCRIPTION - READ THIS FIRST AND FOLLOW EXACTLY  ⚠️  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

THE FOLLOWING DESCRIPTION IS THE EXACT APPEARANCE OF THE MAIN CHARACTER. YOU MUST RECREATE THIS CHARACTER EXACTLY AS DESCRIBED IN ALL 4 PANELS:

{character_description}

╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  ABSOLUTE REQUIREMENTS - THESE ARE MANDATORY, NOT OPTIONAL  ⚠️  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1. MAXIMUM FIDELITY REQUIRED: The main character in ALL 4 panels MUST match the description above with ABSOLUTE PRECISION. Every single detail mentioned (age, gender, face shape, skin tone, hair color/style/length/texture, eye color/shape/size, nose shape/size, mouth shape/size, clothing colors/styles/patterns, accessories, distinctive features like freckles, moles, dimples) MUST be accurately represented in EVERY panel. NO EXCEPTIONS.

2. PERFECT CONSISTENCY: The character must look IDENTICAL across all 4 panels. Same face shape, same hair color and style, same eye color, same skin tone, same clothing, same distinctive features. NO variations, NO changes, NO approximations.

3. INSTANT RECOGNIZABILITY: The character must be INSTANTLY RECOGNIZABLE as the person described above. If someone saw the original photo and then saw the comic, they should immediately recognize it's the same person without any doubt.

4. DETAIL PRESERVATION (MANDATORY):
   - Exact hair color and style must match (if description says "medium brown wavy hair", it MUST be medium brown and wavy)
   - Exact eye color and shape must match (if description says "bright blue almond-shaped eyes", they MUST be bright blue and almond-shaped)
   - Exact skin tone must match (if description says "fair skin with warm undertones", it MUST be fair with warm undertones)
   - Exact clothing colors and styles must match (if description says "bright red t-shirt", it MUST be bright red)
   - All distinctive features (freckles, moles, dimples, etc.) must be present and visible
   - Facial proportions and structure must match exactly

5. CHARACTER AS HERO: This character is the HERO and PROTAGONIST of the story. They appear in ALL 4 panels as the central figure performing the actions described below. The character described above IS the main character.

6. REFERENCE IN PANELS: When describing each panel below, the "main character" refers EXCLUSIVELY to the person described in detail above. Use the specific appearance details from the description above (hair color, eye color, clothing, etc.) when rendering the character in each panel.

7. NO CREATIVE LIBERTY: Do NOT change, modify, approximate, or "interpret" the character description. Follow it EXACTLY as written. Do NOT create a "similar" character - create THE EXACT character described above.

"""
        
        # Construire la description de la planche complète avec TOUS les détails
        prompt = f"""A professional comic book page in square format with 4 panels arranged in a 2x2 grid layout.
{style_info['prompt_modifier']}.
{character_section}
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
        """Génère une planche de BD avec gemini-3-pro-image-preview (text-to-image uniquement)
        
        Le prompt contient déjà toute la description détaillée du personnage (si photo fournie)
        obtenue via l'analyse GPT-4o. On utilise uniquement text-to-image avec gemini-3-pro-image-preview.
        
        Args:
            prompt: Prompt ULTRA DÉTAILLÉ incluant la description du personnage
            output_dir: Répertoire de sortie
            page_num: Numéro de la planche
            character_photo_path: Non utilisé (conservé pour compatibilité)
            page_data: Non utilisé (conservé pour compatibilité)
        """
        
        try:
            print(f"   🎨 Appel gemini-3-pro-image-preview (text-to-image uniquement)...")
            print(f"   📝 Prompt détaillé ({len(prompt)} caractères)")
            
            # Générer l'image avec text-to-image uniquement
            # Le prompt contient déjà toute la description du personnage si une photo a été fournie
            response = self.gemini_client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[prompt]
            )
            
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
            # 1. Générer le scénario (avec analyse de la photo si fournie)
            print("📝 Étape 1: Génération du scénario...")
            story_data, character_description = await self.generate_comic_story(
                theme=theme,
                num_pages=num_pages,
                art_style=art_style,
                custom_prompt=custom_prompt,
                character_photo_path=character_photo_path
            )
            
            # 2. Générer les images (avec description du personnage pour le prompt détaillé)
            print("🎨 Étape 2: Génération des planches...")
            pages, comic_id = await self.generate_comic_pages(
                story_data=story_data,
                art_style=art_style,
                character_photo_path=None,  # Plus besoin de la photo, on utilise la description
                user_id=user_id,  # Passer user_id pour upload Supabase Storage
                character_description=character_description  # Passer la description détaillée
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

