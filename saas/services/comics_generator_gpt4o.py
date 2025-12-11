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
from PIL import Image, ImageDraw, ImageFont
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
            "ocean_fr": {
                "name": "Océan",
                "description": "Aventures sous-marines",
                "keywords": "ocean, underwater, sea creatures, coral reef, diving, marine life"
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
        
    def _add_watermark(self, image: Image.Image) -> Image.Image:
        """
        Ajoute le watermark "Créé avec HERBBIE" en bas à gauche de l'image
        
        Args:
            image: Image PIL à watermarker
            
        Returns:
            Image avec watermark ajouté
        """
        try:
            print(f"   [WATERMARK] Début ajout watermark, mode image: {image.mode}, taille: {image.size}")
            
            # Convertir l'image en RGBA si nécessaire pour supporter la transparence
            if image.mode != 'RGBA':
                watermarked = image.convert('RGBA')
                print(f"   [WATERMARK] Image convertie en RGBA")
            else:
                watermarked = image.copy()
            
            # Créer un nouveau draw sur l'image
            draw = ImageDraw.Draw(watermarked, 'RGBA')
            
            # Texte du watermark
            text = "Créé avec HERBBIE"
            
            # Taille de l'image
            width, height = watermarked.size
            
            # Taille de police adaptative (environ 4% de la hauteur, minimum 20px pour visibilité)
            font_size = max(20, int(height * 0.04))
            print(f"   [WATERMARK] Taille police calculée: {font_size}px")
            
            # Essayer de charger une police, sinon utiliser la police par défaut
            font = None
            try:
                # Essayer d'utiliser une police système
                font = ImageFont.truetype("arial.ttf", font_size)
                print(f"   [WATERMARK] Police Arial chargée")
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                    print(f"   [WATERMARK] Police DejaVu chargée")
                except:
                    # Police par défaut
                    font = ImageFont.load_default()
                    print(f"   [WATERMARK] Police par défaut utilisée")
            
            # Calculer la taille du texte
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            print(f"   [WATERMARK] Taille texte: {text_width}x{text_height}")
            
            # Position en bas à gauche avec marge (3% de la largeur/hauteur)
            margin_x = max(10, int(width * 0.03))
            margin_y = max(10, int(height * 0.03))
            x = margin_x  # Bas à gauche
            y = height - text_height - margin_y
            
            print(f"   [WATERMARK] Position calculée: ({x}, {y})")
            
            # Dessiner un fond semi-transparent pour la lisibilité (plus opaque)
            padding = 10
            rect_coords = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
            # Fond blanc très opaque avec bordure noire
            draw.rectangle(
                rect_coords,
                fill=(255, 255, 255, 250)  # Blanc presque opaque
            )
            # Bordure noire autour du fond
            draw.rectangle(
                rect_coords,
                outline=(0, 0, 0, 255),
                width=2
            )
            print(f"   [WATERMARK] Rectangle fond dessiné: {rect_coords}")
            
            # Dessiner le texte en noir avec contour blanc pour meilleure visibilité
            # D'abord le contour (blanc)
            for adj in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                draw.text((x + adj[0], y + adj[1]), text, fill=(255, 255, 255, 255), font=font)
            # Puis le texte principal (noir)
            draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)
            print(f"   [WATERMARK] Texte dessiné avec contour: '{text}'")
            
            # Convertir de nouveau en RGB si l'image originale était en RGB (pour compatibilité)
            original_mode = image.mode
            if original_mode == 'RGB':
                watermarked = watermarked.convert('RGB')
                print(f"   [WATERMARK] Image reconvertie en RGB")
            
            print(f"   [WATERMARK] ✅ Watermark ajouté avec succès en bas à gauche: '{text}' à ({x}, {y}), taille police: {font_size}px")
            
            return watermarked
            
        except Exception as e:
            print(f"   [ERROR] Erreur ajout watermark: {e}")
            import traceback
            traceback.print_exc()
            # En cas d'erreur, retourner l'image originale
            print(f"   [WARNING] Retour de l'image originale sans watermark")
            return image
    
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
        
        # Transformer la photo du personnage en illustration de BD si fournie
        character_illustration_path = None
        if character_photo_path:
            print(f"📸 Transformation photo en personnage BD...")
            print(f"   📁 Chemin photo: {character_photo_path}")
            # Vérifier que le fichier existe
            if not Path(character_photo_path).exists():
                print(f"   ⚠️ ERREUR: Le fichier photo n'existe pas: {character_photo_path}")
                raise Exception(f"Photo introuvable: {character_photo_path}")
            character_illustration_path = await self._transform_photo_to_comic_character(character_photo_path)
            if character_illustration_path:
                print(f"   ✅ Illustration personnage créée: {character_illustration_path}")
            else:
                print(f"   ⚠️ ERREUR: Aucune illustration obtenue")
                raise Exception("Échec transformation photo: illustration vide")
        
        # Construire le prompt pour gpt-4o-mini
        prompt = f"""Tu es un scénariste expert en bandes dessinées pour enfants de 6-10 ans. Tu écris en français impeccable sans AUCUNE faute d'orthographe, de grammaire ou de conjugaison.

MISSION: Créer une histoire complète en {num_pages} planches de bande dessinée.

THÈME: {theme_info['name']}
Description: {theme_info['description']}
Mots-clés: {theme_info['keywords']}

STYLE ARTISTIQUE: {style_info['name']}
{style_info['description']}

{"DEMANDE PERSONNALISÉE: " + custom_prompt if custom_prompt else ""}

{"⚠️ PERSONNAGE PRINCIPAL PERSONNALISÉ: Un personnage personnalisé (basé sur une photo uploadée) sera le HÉROS PRINCIPAL de cette histoire. Ce personnage doit apparaître dans TOUTES les cases de TOUTES les planches et être le protagoniste de l'histoire. L'histoire doit être centrée sur ce personnage et ses aventures selon le thème choisi." if character_photo_path else ""}

CONSIGNES IMPORTANTES:
1. Chaque planche contient EXACTEMENT 4 CASES disposées en grille 2×2
2. L'histoire doit être cohérente, captivante et adaptée aux enfants. {"CRITIQUE: L'histoire DOIT être centrée sur le personnage personnalisé uploadé qui est le HÉROS PRINCIPAL. Crée une vraie histoire selon le thème choisi avec ce personnage comme protagoniste." if character_photo_path else ""}
{"3. CRITIQUE: Le personnage personnalisé uploadé DOIT être le HÉROS PRINCIPAL et apparaître dans LES 4 CASES de chaque planche. C'est LUI qui fait les actions, c'est LUI le protagoniste. Dans CHAQUE case, commence la description par: 'The main character (the personalized character from the uploaded photo) is...' pour que le modèle d'image sache que c'est ce personnage précis qui doit apparaître." if character_photo_path else ""}
4. Chaque case doit avoir:
   - Une description visuelle ULTRA DÉTAILLÉE (pour gpt-image-1-mini)
   - Des dialogues dans des bulles (maximum 2 bulles par case)
   - Une indication de l'action ou l'émotion

5. CRITIQUE ABSOLUE pour les BULLES DE DIALOGUE - ORTHOGRAPHE PARFAITE OBLIGATOIRE:
   - TOUS les textes doivent être en FRANÇAIS PARFAIT sans AUCUNE faute d'orthographe, de grammaire ou de conjugaison
   - Les bulles doivent contenir le texte EXACT à afficher dans l'image finale
   - Le texte doit être COURT (maximum 8-10 mots par bulle pour tenir dans la bulle)
   - Langage simple et adapté aux enfants de 6-10 ans
   - ⚠️ VÉRIFICATION ORTHOGRAPHE OBLIGATOIRE pour chaque bulle avant de l'inclure :
     * "tu" (pas "t"), "c'est" (pas "cé" ou "c"), "il y a" (pas "y'a")
     * Accents corrects : "été", "été", "à", "é", "è", "ê", "ô", "û", etc.
     * Conjugaisons correctes : "il fait" (pas "il fai"), "nous allons" (pas "on va" si c'est formel)
     * Pluriels corrects : "les enfants" (pas "les enfant"), "des amis" (pas "des ami")
     * Articles corrects : "le", "la", "les", "un", "une", "des"
     * Pas de mots inventés ou abrégés : "super" (pas "sup"), "génial" (pas "génial")
   - Les bulles doivent être positionnées pour ne pas cacher les personnages
   - Précise la position suggérée de chaque bulle (haut-gauche, haut-droite, bas-gauche, bas-droite)

6. DESCRIPTIONS VISUELLES ULTRA DÉTAILLÉES:
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
                    {"role": "system", "content": "Tu es un scénariste expert en bandes dessinées pour enfants. Tu génères des scénarios détaillés en JSON. CRITIQUE: Tous les textes dans les bulles de dialogue doivent être en français PARFAIT sans AUCUNE faute d'orthographe, de grammaire ou de conjugaison. Vérifie chaque mot avant de l'inclure dans les bulles."},
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
            return story_data, character_illustration_path
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"Contenu reçu: {content[:500]}...")
            raise Exception(f"Erreur de format du scénario: {e}")
        except Exception as e:
            print(f"❌ Erreur génération scénario: {e}")
            raise Exception(f"Erreur lors de la génération du scénario: {e}")
    
    async def _transform_photo_to_comic_character(self, photo_path: str) -> str:
        """Transforme une photo en illustration de personnage de BD avec gpt-image-1
        
        Utilise images.edit pour transformer la photo en illustration de personnage de BD,
        similaire à l'approche utilisée pour les coloriages.
        
        Args:
            photo_path: Chemin vers la photo du personnage
            
        Returns:
            Chemin vers l'illustration de personnage générée
        """
        try:
            print(f"📸 Transformation photo en personnage BD avec gpt-image-1: {photo_path}")
            
            # Charger l'image
            input_image = Image.open(photo_path)
            original_width, original_height = input_image.size
            print(f"   📏 Image originale: {original_width}x{original_height}")
            
            # Convertir en RGBA (requis par images.edit)
            if input_image.mode != 'RGBA':
                input_image = input_image.convert('RGBA')
            
            # Redimensionner en carré 1024x1024 (requis pour images.edit)
            size = 1024
            square_image = Image.new('RGBA', (size, size), (255, 255, 255, 255))
            
            # Calculer le ratio pour garder les proportions
            ratio = min(size / original_width, size / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            resized_image = input_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Centrer l'image
            x_offset = (size - new_width) // 2
            y_offset = (size - new_height) // 2
            square_image.paste(resized_image, (x_offset, y_offset), resized_image)
            
            # Sauvegarder temporairement en PNG (RGBA)
            temp_input_path = self.cache_dir / f"temp_comic_input_{uuid.uuid4().hex[:8]}.png"
            square_image.save(temp_input_path, 'PNG')
            
            # Créer un masque blanc en RGBA (tout l'image sera modifiée)
            mask_image = Image.new('RGBA', (size, size), (255, 255, 255, 255))
            temp_mask_path = self.cache_dir / f"temp_comic_mask_{uuid.uuid4().hex[:8]}.png"
            mask_image.save(temp_mask_path, 'PNG')
            
            # Prompt pour transformer en personnage de BD
            edit_prompt = """Transform this photo into a friendly cartoon-style character illustration suitable for a children's comic book. Make it clearly a cartoon illustration with recognizable features preserved. The character should look like a hero character ready for comic book adventures. Preserve the person's distinctive features like hair color, clothing style, and general appearance, but make it clearly a cartoon illustration."""
            
            print(f"   🎨 Transformation avec gpt-image-1...")
            
            # Utiliser images.edit pour transformer en personnage de BD
            with open(temp_input_path, "rb") as input_file, open(temp_mask_path, "rb") as mask_file:
                response = await self.client.images.edit(
                    image=input_file,
                    mask=mask_file,
                    prompt=edit_prompt,
                    n=1,
                    size=f"{size}x{size}",
                    model="gpt-image-1"
                )
            
            # Vérifier la structure de la réponse
            if not response.data or len(response.data) == 0:
                raise Exception("Aucune image générée par gpt-image-1")
            
            image_result = response.data[0]
            
            # Récupérer l'image (URL ou base64)
            image_data = None
            if hasattr(image_result, 'url') and image_result.url:
                # Télécharger l'image depuis l'URL
                import httpx
                async with httpx.AsyncClient() as client:
                    image_response = await client.get(image_result.url)
                    image_response.raise_for_status()
                    image_data = image_response.content
            elif hasattr(image_result, 'b64_json') and image_result.b64_json:
                # Décoder l'image depuis base64
                image_data = base64.b64decode(image_result.b64_json)
            else:
                raise Exception(f"Format de réponse gpt-image-1 inattendu: pas d'URL ni de b64_json")
            
            if not image_data:
                raise Exception("Impossible de récupérer l'image générée")
            
            # Charger l'image générée
            generated_img = Image.open(io.BytesIO(image_data))
            
            # Sauvegarder l'illustration de personnage
            character_illustration_path = self.cache_dir / f"comic_character_{uuid.uuid4().hex[:8]}.png"
            generated_img.save(character_illustration_path, 'PNG', optimize=True)
            print(f"   ✅ Personnage BD créé: {character_illustration_path.name}")
            
            # Nettoyer les fichiers temporaires
            temp_input_path.unlink(missing_ok=True)
            temp_mask_path.unlink(missing_ok=True)
            
            return str(character_illustration_path)
            
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
        Si character_photo_path est fourni, utilise l'illustration transformée avec Gemini
        """
        
        print(f"🎨 Génération des planches avec gemini-3-pro-image-preview...")
        
        style_info = self.art_styles.get(art_style, self.art_styles["cartoon"])
        comic_id = str(uuid.uuid4())
        comic_dir = self.cache_dir / comic_id
        comic_dir.mkdir(parents=True, exist_ok=True)
        
        # L'illustration du personnage est passée en paramètre (déjà transformée dans generate_comic_story)
        if character_photo_path:
            print(f"   ✅ Illustration personnage disponible: {character_photo_path}")
        
        # Contexte global de cohérence (mêmes personnages / styles sur toutes les pages)
        continuity_notes = self._build_continuity_notes(story_data, style_info)

        generated_pages = []
        
        for page_data in story_data["pages"]:
            page_num = page_data["page_number"]
            
            try:
                print(f"📄 Génération planche {page_num}/{story_data['total_pages']}...")
                
                # Construire le prompt complet pour gemini-3-pro-image-preview
                page_prompt = self._build_page_prompt(
                    page_data=page_data,
                    style_info=style_info,
                    story_title=story_data.get("title"),
                    story_synopsis=story_data.get("synopsis"),
                    total_pages=story_data.get("total_pages", len(story_data.get("pages", []))),
                    current_page=page_num,
                    continuity_notes=continuity_notes,
                    character_description=None  # Conservé pour compatibilité, non utilisé
                )
                
                print(f"   📝 Prompt complet ({len(page_prompt)} caractères): {page_prompt[:200]}...")
                
                # Générer l'image avec gemini-3-pro-image-preview
                # Si character_photo_path est fourni, utiliser image-to-image avec l'illustration transformée
                image_path = await self._generate_page_with_gpt_image_1(
                    page_prompt,
                    comic_dir,
                    page_num,
                    character_photo_path=character_photo_path,  # Utiliser l'illustration transformée
                    page_data=None
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
    
    def _build_page_prompt(
        self,
        page_data: Dict,
        style_info: Dict,
        story_title: Optional[str] = None,
        story_synopsis: Optional[str] = None,
        total_pages: Optional[int] = None,
        current_page: Optional[int] = None,
        continuity_notes: Optional[str] = None,
        character_description: Optional[str] = None
    ) -> str:
        """Construit le prompt détaillé pour gemini-3-pro-image-preview pour générer UNE planche complète
        
        Args:
            page_data: Données de la planche (panels, dialogues, etc.)
            style_info: Informations sur le style artistique
            story_title: Titre global de l'histoire (pour cohérence multi-pages)
            story_synopsis: Synopsis global (pour cohérence multi-pages)
            total_pages: Nombre total de planches dans cette BD (pour cohérence)
            current_page: Numéro de la planche actuelle (pour cohérence)
            continuity_notes: Notes globales de cohérence (personnages, style, accessoires)
            character_description: Non utilisé (conservé pour compatibilité, on utilise l'illustration directement)
        """
        
        panels = page_data["panels"]
        
        # Contexte global pour renforcer la cohérence multi-planches
        title_line = f"COMIC TITLE: {story_title}" if story_title else "COMIC TITLE: A coherent kids comic"
        synopsis_line = f"SYNOPSIS: {story_synopsis}" if story_synopsis else "SYNOPSIS: Keep the same characters and story thread across all pages."
        page_progress = ""
        if total_pages and current_page:
            page_progress = f"THIS IS PAGE {current_page} OF {total_pages}. The style, main characters, outfits, colors, and props MUST stay identical to the previous pages and across all pages."
        else:
            page_progress = "Maintain exactly the same visual style, character designs, outfits, colors, and props across all pages of this comic."
        continuity_block = continuity_notes or ""
        
        # Plus besoin d'intégrer la description textuelle, on utilise l'illustration directement avec image-to-image
        character_section = ""
        
        # Construire la description de la planche complète avec TOUS les détails
        prompt = f"""A professional comic book page in square format with 4 panels arranged in a 2x2 grid layout.
{title_line}
{synopsis_line}
{page_progress}
{continuity_block}
{style_info['prompt_modifier']}.
STYLE LOCK: You MUST keep the EXACT SAME art style and rendering settings as all other pages of this comic. Same medium, same palette, same line weight, same shading and lighting. Do NOT change style between pages.
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
- CRITICAL CONTINUITY: Keep identical character designs, outfits, hair color, skin tone, accessories, props, and overall art style consistent with ALL previous and next pages of this comic. Do NOT change faces, outfits, or colors from one page to another.
- Clear, bold black panel borders with generous spacing between panels
- Each panel should be significantly smaller to leave plenty of white space around them
- Professional comic book page layout with wide gutters (white space between panels)
- CRITICAL: Include ALL speech bubbles with the EXACT text shown above - DO NOT MODIFY, CHANGE, or CORRECT the text in the speech bubbles under any circumstances
- The text in speech bubbles must be COPIED VERBATIM from what is provided - no grammar fixes, no spelling corrections, no rephrasing
- IMPORTANT: The text in the speech bubbles has already been verified for correct French spelling and grammar by GPT-4o-mini - display it exactly as provided, even if you think there might be an error
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

    def _build_continuity_notes(self, story_data: Dict[str, Any], style_info: Dict[str, Any]) -> str:
        """
        Construit un bloc de cohérence global (cast + style) pour toutes les pages
        afin de forcer Gemini à conserver les mêmes personnages / tenues / props.
        """
        # Extraire les noms de personnages depuis les bulles de dialogue
        character_names = set()
        try:
            for page in story_data.get("pages", []):
                for panel in page.get("panels", []):
                    for bubble in panel.get("dialogue_bubbles", []):
                        name = bubble.get("character")
                        if name:
                            character_names.add(name.strip())
        except Exception:
            pass

        if not character_names:
            characters_line = "MAIN CHARACTERS: Keep the same main characters with identical faces, hair, outfits, colors, and props on every page."
        else:
            joined = ", ".join(sorted(character_names))
            characters_line = f"MAIN CHARACTERS: {joined}. Keep their faces, hair, outfits, colors, accessories, and props IDENTICAL on every page."

        style_name = style_info.get("name", "Chosen style")
        style_modifier = style_info.get("prompt_modifier", "")
        style_line = (
            f"STYLE CONSISTENCY: Always keep the EXACT SAME art style ({style_name}). "
            f"Use the same rendering approach described here: {style_modifier}. "
            "Do NOT switch medium (no watercolor/pencil/3D if not the chosen style), "
            "do NOT change color palette, line weight, shading method, or outline thickness between pages. "
            "Match lighting/contrast and overall look IDENTICALLY across all pages."
        )

        return f"{characters_line}\n{style_line}"
    
    async def _generate_page_with_gpt_image_1(
        self,
        prompt: str,
        output_dir: Path,
        page_num: int,
        character_photo_path: Optional[str] = None,
        page_data: Optional[Dict] = None
    ) -> Path:
        """Génère une planche de BD avec gemini-3-pro-image-preview
        
        Si character_photo_path est fourni, utilise image-to-image avec l'illustration transformée.
        Sinon, utilise text-to-image uniquement.
        
        Args:
            prompt: Prompt détaillé pour la planche
            output_dir: Répertoire de sortie
            page_num: Numéro de la planche
            character_photo_path: Chemin vers l'illustration du personnage (si fourni)
            page_data: Non utilisé (conservé pour compatibilité)
        """
        
        try:
            # Si une illustration de personnage est fournie, utiliser image-to-image
            if character_photo_path and Path(character_photo_path).exists():
                print(f"   🎨 Appel gemini-3-pro-image-preview (image-to-image avec illustration)...")
                print(f"   📸 Utilisation illustration personnage: {character_photo_path}")
                
                # Charger l'illustration
                character_img = Image.open(character_photo_path)
                print(f"   📏 Illustration: {character_img.size}, mode: {character_img.mode}")
                
                # Utiliser le prompt complet pour image-to-image
                # Le prompt contient toute l'histoire avec les descriptions détaillées de chaque case
                full_prompt = f"""Transform this character illustration into a comic book page with 4 panels in a 2x2 grid layout. 

Use the character from the provided image as the main character in all 4 panels, maintaining their recognizable appearance.

IMPORTANT: Follow this complete story and scene description exactly:

{prompt}

The character from the provided image must be the main character performing all the actions described above in all 4 panels."""
                
                # Convertir l'image en bytes pour Gemini
                img_bytes = io.BytesIO()
                character_img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Utiliser image-to-image avec Gemini
                import google.genai.types as types
                response = self.gemini_client.models.generate_content(
                    model="gemini-3-pro-image-preview",
                    contents=[
                        types.Part.from_bytes(
                            img_bytes.read(),
                            mime_type="image/png"
                        ),
                        full_prompt
                    ]
                )
            else:
                print(f"   🎨 Appel gemini-3-pro-image-preview (text-to-image uniquement)...")
                print(f"   📝 Prompt détaillé ({len(prompt)} caractères)")
                
                # Générer l'image avec text-to-image uniquement
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
                img.save(output_path, 'PNG', optimize=True)
                
                print(f"   ✅ Planche sauvegardée: {output_path.name} ({actual_width}x{actual_height})")
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
            story_data, character_illustration_path = await self.generate_comic_story(
                theme=theme,
                num_pages=num_pages,
                art_style=art_style,
                custom_prompt=custom_prompt,
                character_photo_path=character_photo_path
            )
            
            # 2. Générer les images (avec illustration du personnage pour référence)
            print("🎨 Étape 2: Génération des planches...")
            pages, comic_id = await self.generate_comic_pages(
                story_data=story_data,
                art_style=art_style,
                character_photo_path=character_illustration_path,  # Utiliser l'illustration transformée
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

