import openai
from openai import AsyncOpenAI
import json
import os
import uuid
import math
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import requests
import asyncio
from dotenv import load_dotenv

# Importer notre nouveau générateur avec IA
from .stable_diffusion_generator import StableDiffusionGenerator
from .comic_ai_enhancer import ComicAIEnhancer

load_dotenv()

class ComicGenerator:
    """Générateur de bandes dessinées moderne avec IA intégrée"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.stability_key = os.getenv("STABILITY_API_KEY")
        self.fal_key = os.getenv("FAL_API_KEY")
        self.image_model = os.getenv("IMAGE_MODEL", "stability-ai")
        self.video_model = os.getenv("VIDEO_MODEL", "sd3-large-turbo")
        self.client = AsyncOpenAI(api_key=self.openai_key)
        
        # Utiliser le nouveau générateur avec IA
        self.sd_generator = StableDiffusionGenerator()
        self.ai_enhancer = ComicAIEnhancer() if os.getenv("ENABLE_AI_BUBBLES", "true").lower() == "true" else None
        
        # Forcer l'activation des bulles IA pour résoudre le problème d'affichage
        if not self.ai_enhancer:
            print("⚠️ Force l'activation des bulles IA...")
            self.ai_enhancer = ComicAIEnhancer()
        
        print(f"🎨 ComicGenerator initialisé avec {'IA activée' if self.ai_enhancer else 'IA désactivée'}")
        
        # Configuration des styles artistiques avec mots-clés de cohérence
        self.art_styles = {
            "cartoon": "cartoon style, colorful, child-friendly, simple clean lines, bright colors, Disney-style animation, rounded shapes, friendly characters",
            "realistic": "photorealistic style, detailed, professional illustration, high quality, cinematic lighting, realistic textures, detailed shadows",
            "manga": "manga style, anime inspired, black and white with screentones, dynamic poses, Japanese comic art, expressive eyes, detailed lineart",
            "comics": "american comic book style, bold colors, dynamic shading, superhero aesthetic, Marvel/DC style, action poses, dramatic lighting",
            "watercolor": "watercolor painting style, soft colors, artistic brush strokes, dreamy atmosphere, painted texture, flowing colors, artistic illustration"
        }
        
        # Thèmes prédéfinis avec structures narratives
        self.theme_templates = {
            "adventure": {
                "setting": "mysterious forest and ancient castle",
                "conflict": "finding a hidden treasure while avoiding dangers",
                "characters": ["brave young explorer", "wise old guide", "mischievous forest creature"]
            },
            "animals": {
                "setting": "African savanna and watering hole", 
                "conflict": "helping lost baby animal find its family",
                "characters": ["kind elephant", "playful monkey", "lost baby zebra"]
            },
            "space": {
                "setting": "colorful alien planet with floating islands",
                "conflict": "repairing broken spaceship to return home",
                "characters": ["young astronaut", "friendly alien", "helpful robot"]
            },
            "magic": {
                "setting": "enchanted kingdom with magical creatures",
                "conflict": "learning to use new magical powers responsibly", 
                "characters": ["apprentice wizard", "wise fairy godmother", "magical talking animal"]
            },
            "friendship": {
                "setting": "school playground and neighborhood",
                "conflict": "resolving misunderstanding between best friends",
                "characters": ["shy new student", "outgoing class leader", "understanding teacher"]
            }
        }
    
    async def generate_comic_script(self, theme: str, story_length: str, custom_request: str = None) -> Dict[str, Any]:
        """Génère le scénario complet de la BD avec GPT-4o-mini selon les spécifications avancées"""
        
        # Déterminer le nombre de pages selon la longueur
        # Support à la fois des anciennes valeurs (short, medium, long) et des nouvelles valeurs numériques
        if story_length.isdigit():
            num_pages = int(story_length)
        else:
            page_counts = {"short": 4, "medium": 8, "long": 12}
            num_pages = page_counts.get(story_length, 4)
        
        # Récupérer le template du thème
        theme_info = self.theme_templates.get(theme, self.theme_templates["adventure"])
        
        # Prompt GPT-4o-mini optimisé pour BD réalistes
        prompt = f"""Tu es un système intelligent capable de créer automatiquement une bande dessinée complète. Ton objectif est de générer une histoire structurée en {num_pages} scènes avec une forte cohérence narrative et visuelle pour des enfants de 6 à 10 ans.

CONSIGNES POUR L'HISTOIRE :
- Thème demandé : {theme}
- Nombre de scènes : {num_pages}
- Demande spéciale : {custom_request or "Aucune"}
- Décor suggéré : {theme_info['setting']}
- Conflit principal : {theme_info['conflict']}

RÈGLES NARRATIVES :
1. Histoire originale, immersive et adaptée aux enfants de 6-10 ans
2. Personnages identifiables dès la première scène avec cohérence visuelle totale
3. Chaque scène indépendante visuellement mais faisant avancer la trame
4. Lieux visuellement intéressants (jungle, école, laboratoire, château, ville, forêt magique...)
5. Ton globalement positif, engageant et accessible
6. Dialogues courts (1-2 répliques max par personnage) avec humour, surprise ou tendresse

DESCRIPTIONS VISUELLES OBLIGATOIRES pour chaque scène :
- Personnages présents, leurs vêtements, positions, actions, émotions
- Décor détaillé, ambiance lumineuse, objets visibles
- Cadrage dynamique comme une case de BD moderne
- Éléments essentiels : âge apparent, traits distinctifs, nature du lieu
- Ambiance (chaleureuse, nocturne, mystérieuse, ensoleillée...)

FORMAT JSON EXACT REQUIS :
{{
  "title": "Titre accrocheur de la BD",
  "synopsis": "Résumé captivant en 1-2 phrases",
  "main_characters": [
    {{
      "name": "Nom du personnage",
      "age": "Âge précis (ex: 8 ans)",
      "physical_description": "Description physique TRÈS détaillée (taille, cheveux, yeux, traits distinctifs)",
      "clothing": "Vêtements précis qui seront IDENTIQUES dans toutes les scènes",
      "personality": "Traits de personnalité marquants",
      "role": "Rôle dans l'histoire"
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "location": "Lieu précis de la scène",
      "time_of_day": "Moment de la journée/ambiance lumineuse",
      "visual_description": "Description TRÈS détaillée pour Stable Diffusion (décor, personnages, positions, actions, émotions, objets, cadrage, style BD réaliste)",
      "characters_present": ["Nom1", "Nom2"],
      "dialogues": [
        {{
          "character": "Nom du personnage",
          "text": "Dialogue court et impactant",
          "emotion": "émotion exprimée",
          "bubble_position": "position suggérée de la bulle (haut-gauche, haut-droite, bas-gauche, bas-droite, centre)",
          "character_position": "position suggérée du personnage (gauche, droite, centre, arrière-plan)"
        }}
      ],
      "mood": "Ambiance de la scène",
      "story_progression": "Rôle de cette scène dans la progression narrative"
    }}
  ]
}}

EXEMPLE DE DESCRIPTION VISUELLE pour Stable Diffusion :
"Realistic comic book illustration of two children (8-year-old boy in red t-shirt and blue jeans, 9-year-old girl in yellow dress) standing in front of a mysterious ancient castle at sunset. Dynamic comic book composition, cinematic lighting with golden hour glow, hand-drawn style, vivid colors, expressive characters looking amazed, detailed stone architecture background, no text or speech bubbles, 2D digital art in European comic style."

Assure-toi que :
- Les descriptions visuelles sont suffisamment détaillées pour Stable Diffusion
- Les personnages gardent exactement les mêmes vêtements et traits dans toutes les scènes
- Chaque scène fait progresser l'histoire de manière logique
- L'histoire est complète avec début, développement et fin satisfaisante"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )
            
            script_text = response.choices[0].message.content.strip()
            
            # Nettoyer et parser le JSON
            if script_text.startswith("```json"):
                script_text = script_text[7:-3]
            elif script_text.startswith("```"):
                script_text = script_text[3:-3]
                
            script_data = json.loads(script_text)
            return script_data
            
        except Exception as e:
            print(f"❌ Erreur génération script: {e}")
            # PLUS DE FALLBACK - Générer une erreur stricte
            raise Exception(f"❌ ÉCHEC GÉNÉRATION SCRIPT: {e}. Impossible de continuer sans script valide.")
    
    async def generate_comic_images(self, script_data: Dict[str, Any], art_style: str) -> List[Dict[str, Any]]:
        """Génère les images de chaque scène avec Stable Diffusion selon les nouvelles spécifications"""
        
        comic_id = str(uuid.uuid4())
        comic_dir = Path(f"static/generated_comics/{comic_id}")
        comic_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le style pour utilisation dans les méthodes de génération
        self.current_art_style = art_style
        style_prompt = self.art_styles.get(art_style, self.art_styles["cartoon"])
        pages = []
        
        # Créer une seed de base déterministe pour la cohérence
        consistency_string = f"{script_data['title']}_{art_style}_{len(script_data.get('scenes', script_data.get('pages', [])))}"
        base_seed = abs(hash(consistency_string)) % 999999
        
        print(f"🎲 Seed de base pour cohérence: {base_seed}")
        
        # Seed fixe pour les personnages principaux (cohérence des apparences)
        character_seeds = {}
        for i, char in enumerate(script_data["main_characters"]):
            char_seed = (base_seed + i * 1000) % 999999
            character_seeds[char["name"]] = char_seed
            print(f"👤 {char['name']} - seed: {char_seed}")
        
        # Adapter au nouveau format (scenes) ou ancien format (pages)
        scenes_data = script_data.get("scenes", script_data.get("pages", []))
        
        for scene_data in scenes_data:
            scene_num = scene_data.get("scene_number", scene_data.get("page_number", 1))
            
            try:
                # Construire le prompt optimisé pour Stable Diffusion
                if "visual_description" in scene_data:
                    # Nouveau format avec description détaillée
                    base_prompt = scene_data["visual_description"]
                else:
                    # Ancien format - construire le prompt
                    character_descriptions = []
                    for char in script_data["main_characters"]:
                        if char["name"] in scene_data.get("characters_present", []):
                            physical = char.get("physical_description", char.get("description", ""))
                            clothing = char.get("clothing", "")
                            char_desc = f"{char['name']}: {physical}, wearing {clothing}"
                            character_descriptions.append(char_desc)
                    
                    char_context = ". ".join(character_descriptions) if character_descriptions else ""
                    base_prompt = f"Realistic comic book illustration. Scene: {scene_data.get('scene_description', '')}. Characters: {char_context}."

                # Construire le prompt final optimisé pour Stability AI avec renforcement du thème
                theme_context = self._get_theme_visual_keywords(script_data.get("theme", "adventure"))
                full_prompt = f"""{base_prompt}
Theme context: {theme_context}
Style requirements: {style_prompt}, realistic comic book illustration, cinematic lighting, hand-drawn style, dynamic composition, vivid colors, expressive characters, detailed background environment, professional comic book art quality, no text or speech bubbles, 2D digital art, European/American comic book style.
Technical specs: high resolution, sharp focus, masterpiece quality, detailed illustration."""

                # Créer une seed spécifique pour cette scène
                page_characters = scene_data.get("characters_present", [])
                char_seed_sum = sum(character_seeds.get(char, 0) for char in page_characters)
                scene_seed = (base_seed + scene_num * 100 + char_seed_sum) % 999999
                
                # Debug des seeds pour traçabilité
                self._debug_seed_info(script_data["title"], base_seed, character_seeds, scene_seed, scene_num)
                
                # Générer l'image avec Stability AI OBLIGATOIRE
                image_path = await self._generate_stable_diffusion_image(
                    full_prompt, 
                    comic_dir, 
                    scene_num,
                    scene_seed
                )
                
                # Ajouter les bulles de dialogue (nouveau format)
                dialogues = scene_data.get("dialogues", [])
                final_image_path = await self._add_speech_bubbles(
                    image_path,
                    dialogues,
                    comic_dir,
                    scene_num
                )
                
                page_info = {
                    "page_number": scene_num,
                    "image_url": self._get_correct_image_url(comic_id, scene_num, comic_dir),
                    "description": f"Page {scene_num} de votre bande dessinée",  # Description simple sans prompt
                    "dialogues": dialogues,
                    "location": scene_data.get("location", ""),
                    "mood": scene_data.get("mood", ""),
                    "panels": [{"layout": scene_data.get("panel_layout", "single scene")}]
                }
                
                pages.append(page_info)
                print(f"✅ Scène {scene_num} générée: {final_image_path}")
                
            except Exception as e:
                print(f"❌ ERREUR CRITIQUE Scène {scene_num}: {e}")
                # AUCUN FALLBACK - Interrompre complètement la génération
                raise Exception(f"Échec génération BD - Scène {scene_num}: {e}. ARRÊT IMMÉDIAT (aucun fallback autorisé).")
        
        # Sauvegarder les données de cohérence
        self._save_character_consistency_data(comic_dir, script_data, character_seeds, base_seed)
        
        return pages, comic_id
    
    async def _translate_prompt_to_english(self, french_prompt: str) -> str:
        """Traduit automatiquement un prompt français vers l'anglais pour Stability AI"""
        try:
            # Prompt de traduction optimisé pour les descriptions visuelles
            translation_prompt = f"""Translate this French visual description to English for an AI image generator.
Keep the artistic and technical terms precise. Focus on visual details, composition, and style.

French text: {french_prompt}

English translation (visual description only, no extra text):"""

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in visual descriptions for AI art generation. Translate French to English while preserving artistic and technical terminology."},
                    {"role": "user", "content": translation_prompt}
                ],
                max_tokens=500,
                temperature=0.3  # Basse température pour une traduction précise
            )
            
            english_prompt = response.choices[0].message.content.strip()
            print(f"🌐 Traduction: {french_prompt[:50]}... → {english_prompt[:50]}...")
            return english_prompt
            
        except Exception as e:
            print(f"⚠️ Erreur traduction: {e}")
            # Fallback: traduction simple des mots-clés
            simple_translation = french_prompt.replace("Illustration réaliste", "Realistic illustration")
            simple_translation = simple_translation.replace("style BD", "comic book style")
            simple_translation = simple_translation.replace("enfants", "children")
            simple_translation = simple_translation.replace("personnage", "character")
            return simple_translation

    async def _generate_stable_diffusion_image(self, prompt: str, output_dir: Path, page_num: int, seed: int) -> Path:
        """Génère une image EXCLUSIVEMENT avec Stability AI - AUCUN FALLBACK autorisé"""
        
        output_path = output_dir / f"page_{page_num}_raw.png"
        
        # EXIGENCE: Stability AI OBLIGATOIRE - Pas de fallback
        if not (self.image_model == "stability-ai" and self.stability_key):
            raise Exception("❌ ERREUR CONFIGURATION: IMAGE_MODEL doit être 'stability-ai' et STABILITY_API_KEY doit être configurée. Aucun fallback autorisé.")
        
        try:
            print(f"🎨 Génération Stability AI OBLIGATOIRE pour page {page_num} (seed: {seed})...")
            # Traduire le prompt en anglais pour Stability AI
            english_prompt = await self._translate_prompt_to_english(prompt)
            return await self._generate_with_stability_ai_corrected(english_prompt, output_path, seed)
        except Exception as e:
            # AUCUN FALLBACK - Propager l'erreur pour arrêter la génération
            error_msg = f"❌ ÉCHEC STABILITY AI PAGE {page_num}: {e}. GÉNÉRATION INTERROMPUE - Aucun fallback autorisé."
            print(error_msg)
            raise Exception(error_msg)

    # ================================================================================
    # FONCTIONS DE FALLBACK SUPPRIMÉES - SEULE STABILITY AI EST AUTORISÉE
    # ================================================================================
    # Les fonctions suivantes ont été supprimées pour forcer l'usage exclusif de Stability AI :
    # - _generate_with_fal()
    # - _generate_with_huggingface() 
    # - _generate_with_public_api()
    # - _generate_programmatic_image()
    # - _generate_programmatic_image_sync()
    # - _create_placeholder_image()
    #
    # SEULE FONCTION AUTORISÉE POUR LA GÉNÉRATION D'IMAGES BD :
    # - _generate_with_stability_ai_corrected()
    # ================================================================================

    def _save_character_consistency_data(self, comic_dir: Path, script_data: Dict, character_seeds: Dict, base_seed: int):
        """Sauvegarde les données de cohérence pour référence future"""
        consistency_data = {
            "base_seed": base_seed,
            "character_seeds": character_seeds,
            "main_characters": script_data["main_characters"],
            "art_style_used": None,  # sera renseigné lors de l'appel
            "generation_timestamp": datetime.now().isoformat()
        }
        
        consistency_file = comic_dir / "consistency_data.json"
        with open(consistency_file, 'w', encoding='utf-8') as f:
            json.dump(consistency_data, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Données de cohérence sauvegardées: {consistency_file}")
    
    # SUPPRESSION COMPLÈTE DES FONCTIONS DE FALLBACK - Plus jamais utilisées
    # _create_placeholder_image() - SUPPRIMÉE
    # _generate_programmatic_image() - SUPPRIMÉE
    
    def _detect_character_positions(self, img: Image.Image) -> List[tuple]:
        """Détecte approximativement les positions des personnages dans l'image"""
        width, height = img.size
        
        # Conversion en RGB si nécessaire
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Zones probables où se trouvent les personnages basées sur des heuristiques visuelles
        character_positions = []
        
        # Analyser l'image par zones pour détecter des concentrations de couleurs "peau"
        zones = [
            (width * 0.2, height * 0.4, width * 0.4, height * 0.8),  # Gauche
            (width * 0.6, height * 0.4, width * 0.8, height * 0.8),  # Droite
            (width * 0.4, height * 0.3, width * 0.6, height * 0.7),  # Centre
        ]
        
        for i, (x1, y1, x2, y2) in enumerate(zones):
            # Zone d'échantillonnage pour détecter des couleurs de peau ou des visages
            sample_points = [
                (int(x1 + (x2-x1)*0.3), int(y1 + (y2-y1)*0.2)),  # Position probable du visage
                (int(x1 + (x2-x1)*0.5), int(y1 + (y2-y1)*0.3)),
                (int(x1 + (x2-x1)*0.7), int(y1 + (y2-y1)*0.2)),
            ]
            
            skin_like_pixels = 0
            for px, py in sample_points:
                if 0 <= px < width and 0 <= py < height:
                    r, g, b = img.getpixel((px, py))
                    # Heuristique simple pour détecter des couleurs de peau
                    if (150 <= r <= 255 and 100 <= g <= 200 and 80 <= b <= 180) or \
                       (200 <= r <= 255 and 180 <= g <= 230 and 150 <= b <= 200):
                        skin_like_pixels += 1
            
            # Si on détecte suffisamment de pixels "peau", c'est probablement un personnage
            if skin_like_pixels >= 1:
                char_x = x1 + (x2-x1) * 0.5
                char_y = y1 + (y2-y1) * 0.4  # Partie haute pour viser vers le visage
                character_positions.append((char_x, char_y))
        
        # Si aucun personnage détecté, utiliser des positions par défaut
        if not character_positions:
            character_positions = [
                (width * 0.3, height * 0.6),  # Gauche-centre
                (width * 0.7, height * 0.6),  # Droite-centre
            ]
        
        return character_positions

    def _calculate_smart_bubble_positions(self, width: int, height: int, num_bubbles: int, 
                                        character_positions: List[tuple]) -> List[tuple]:
        """Calcule des positions intelligentes pour les bulles en évitant les personnages"""
        
        # Zones préférées pour les bulles (en haut et dans les coins)
        preferred_zones = [
            (width * 0.15, height * 0.15),  # Haut-gauche
            (width * 0.85, height * 0.15),  # Haut-droite
            (width * 0.15, height * 0.85),  # Bas-gauche
            (width * 0.85, height * 0.85),  # Bas-droite
            (width * 0.5, height * 0.1),    # Haut-centre
            (width * 0.1, height * 0.5),    # Gauche-centre
            (width * 0.9, height * 0.5),    # Droite-centre
            (width * 0.5, height * 0.9),    # Bas-centre
        ]
        
        bubble_positions = []
        min_distance_from_chars = 100  # Distance minimale des personnages
        
        for i in range(num_bubbles):
            best_position = None
            best_score = -1
            
            for zone_x, zone_y in preferred_zones:
                if any(abs(zone_x - bx) < 80 and abs(zone_y - by) < 80 for bx, by in bubble_positions):
                    continue  # Éviter le chevauchement avec les bulles existantes
                
                # Calculer la distance minimale aux personnages
                min_dist_to_char = min(
                    math.sqrt((zone_x - char_x)**2 + (zone_y - char_y)**2)
                    for char_x, char_y in character_positions
                ) if character_positions else min_distance_from_chars
                
                # Score basé sur la distance aux personnages et la position préférée
                if min_dist_to_char >= min_distance_from_chars:
                    score = min_dist_to_char + (height - zone_y) * 0.1  # Préférer le haut
                    if score > best_score:
                        best_score = score
                        best_position = (zone_x, zone_y)
            
            if best_position:
                bubble_positions.append(best_position)
            else:
                # Fallback sur les positions par défaut
                default_positions = [
                    (width * 0.2, height * 0.2),
                    (width * 0.8, height * 0.2), 
                    (width * 0.2, height * 0.8),
                    (width * 0.8, height * 0.8)
                ]
                if i < len(default_positions):
                    bubble_positions.append(default_positions[i])
                else:
                    bubble_positions.append((width * 0.5, height * 0.1))
        
        return bubble_positions

    def _calculate_bubble_tail_direction(self, bubble_x: float, bubble_y: float, 
                                       character_positions: List[tuple]) -> tuple:
        """Calcule la direction de la queue de bulle vers le personnage le plus proche"""
        if not character_positions:
            return (bubble_x, bubble_y + 20)  # Direction par défaut vers le bas
        
        # Trouver le personnage le plus proche
        min_distance = float('inf')
        closest_char = character_positions[0]
        
        for char_x, char_y in character_positions:
            distance = math.sqrt((bubble_x - char_x)**2 + (bubble_y - char_y)**2)
            if distance < min_distance:
                min_distance = distance
                closest_char = (char_x, char_y)
        
        char_x, char_y = closest_char
        
        # Calculer le vecteur direction normalisé
        dx = char_x - bubble_x
        dy = char_y - bubble_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            # Normaliser et ajuster la longueur de la queue
            tail_length = 25
            tail_x = bubble_x + (dx / length) * tail_length
            tail_y = bubble_y + (dy / length) * tail_length
            return (tail_x, tail_y)
        
        return (bubble_x, bubble_y + 20)

    async def _add_speech_bubbles(self, image_path: Path, dialogues: List[Dict], comic_dir: Path, page_num: int) -> Path:
        """Utilise un système hybride pour garantir la visibilité des bulles"""
        
        if not dialogues:
            # Si pas de dialogue, copier l'image originale
            final_path = comic_dir / f"page_{page_num}_final.png"
            img = Image.open(image_path)
            img.save(final_path)
            return final_path
        
        # Toujours utiliser le système PIL fiable pour garantir des bulles visibles
        print(f"🎨 Génération de bulles PIL fiables pour page {page_num}")
        return await self._add_speech_bubbles_pil_reliable(image_path, dialogues, comic_dir, page_num)
    
    async def _add_speech_bubbles_pil_reliable(self, image_path: Path, dialogues: List[Dict], comic_dir: Path, page_num: int) -> Path:
        """Ajoute les bulles de dialogue à l'image avec queues dirigées vers les personnages"""
        
        if not dialogues:
            # Si pas de dialogue, copier l'image originale
            final_path = comic_dir / f"page_{page_num}_final.png"
            img = Image.open(image_path)
            img.save(final_path)
            return final_path
        
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Détecter les positions des personnages dans l'image
        character_positions = self._detect_character_positions(img)
        print(f"🎯 Personnages détectés aux positions: {character_positions}")
        
        # Charger les polices avec style cohérent avec le site (Nunito)
        try:
            # Tenter de charger Nunito (police du site) ou une police similaire
            font = ImageFont.truetype("nunito-bold.ttf", 22)
            small_font = ImageFont.truetype("nunito-regular.ttf", 18)
        except:
            try:
                # Fallback sur Arial Bold pour un rendu plus proche de Nunito
                font = ImageFont.truetype("arialbd.ttf", 22)
                small_font = ImageFont.truetype("arial.ttf", 18)
            except:
                try:
                    font = ImageFont.truetype("Arial.ttf", 22)
                    small_font = ImageFont.truetype("Arial.ttf", 18)
                except:
                    font = ImageFont.load_default()
                    small_font = font
        
        width, height = img.size
        
        # Position intelligente des bulles pour éviter de chevaucher les personnages
        bubble_positions = self._calculate_smart_bubble_positions(width, height, len(dialogues), character_positions)
        
        # Utiliser les suggestions de position de l'IA si disponibles
        for i, dialogue in enumerate(dialogues):
            character_pos_hint = dialogue.get("character_position", "")
            if character_pos_hint and i < len(character_positions):
                # Ajuster la position détectée du personnage selon l'indication de l'IA
                char_x, char_y = character_positions[i]
                if "gauche" in character_pos_hint:
                    char_x = width * 0.25
                elif "droite" in character_pos_hint:
                    char_x = width * 0.75
                elif "centre" in character_pos_hint:
                    char_x = width * 0.5
                    
                if "arrière-plan" in character_pos_hint:
                    char_y = height * 0.3
                
                character_positions[i] = (char_x, char_y)
        
        for i, dialogue in enumerate(dialogues):
            if i >= len(bubble_positions):
                break
                
            # Position calculée intelligemment
            x, y = bubble_positions[i]
            
            # Ajuster selon la position suggérée si spécifiée (override intelligent)
            bubble_pos = dialogue.get("bubble_position", "")
            if "haut-gauche" in bubble_pos:
                x, y = width * 0.2, height * 0.2
            elif "haut-droite" in bubble_pos:
                x, y = width * 0.7, height * 0.2
            elif "bas-gauche" in bubble_pos:
                x, y = width * 0.2, height * 0.7
            elif "bas-droite" in bubble_pos:
                x, y = width * 0.7, height * 0.7
            elif "centre" in bubble_pos:
                x, y = width * 0.5, height * 0.5
                 
            text = dialogue["text"]
            emotion = dialogue.get("emotion", "normal")
            bubble_type = dialogue.get("bubble_type", "normal")
            
            # Découper le texte en lignes avec largeur optimisée
            words = text.split()
            lines = []
            current_line = ""
            max_width_chars = 28  # Augmenté pour des bulles plus harmonieuses
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if len(test_line) > max_width_chars:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            
            if current_line:
                lines.append(current_line)
            
            # Calculer la taille de la bulle avec proportions modernes
            line_heights = []
            line_widths = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_widths.append(bbox[2] - bbox[0])
                line_heights.append(bbox[3] - bbox[1])
            
            max_width = max(line_widths) if line_widths else 100
            text_height = sum(line_heights) + (len(lines) - 1) * 4  # Espacement réduit
            
            # Dimensions de bulle harmonisées avec le style du site
            bubble_width = max_width + 50  # Plus de padding pour un look moderne
            bubble_height = text_height + 40  # Proportions plus équilibrées
            
            # Assurer des dimensions minimales élégantes
            bubble_width = max(bubble_width, 120)
            bubble_height = max(bubble_height, 60)
            
            # Ajuster la position pour rester dans l'image avec marge de sécurité
            margin = 20  # Marge pour éviter que les bulles touchent les bords
            x = max(bubble_width//2 + margin, min(x, width - bubble_width//2 - margin))
            y = max(bubble_height//2 + margin, min(y, height - bubble_height//2 - margin))
            
            # Dessiner la bulle selon le type et l'émotion
            bubble_x1 = x - bubble_width//2
            bubble_y1 = y - bubble_height//2
            bubble_x2 = x + bubble_width//2
            bubble_y2 = y + bubble_height//2
            
            # Couleur de bulle selon l'émotion - Harmonisée avec la charte graphique du site
            bubble_color = "#f5f0ff"  # Violet très clair (cohérent avec le site)
            outline_color = "#6B4EFF"  # Couleur primaire du site
            outline_width = 2
            
            if emotion in ["excitation", "joie", "bonheur"]:
                bubble_color = "#FFF5E0"  # Accent-light du site (jaune clair)
                outline_color = "#FFD166"  # Accent du site
            elif emotion in ["peur", "inquiétude", "nervosité"]:
                bubble_color = "#f5f0ff"  # Primary-light maintenu
                outline_color = "#6B4EFF"  # Primary
                outline_width = 3
            elif emotion in ["colère", "frustration"]:
                bubble_color = "#FFE5EB"  # Secondary-light du site (rose clair)
                outline_color = "#FF85A1"  # Secondary du site
                outline_width = 3
            elif emotion in ["tristesse", "mélancolie"]:
                bubble_color = "#E5F9F9"  # Success-light du site (bleu-vert clair)
                outline_color = "#A0E7E5"  # Success du site
            
            # Type de bulle avec bordures arrondies cohérentes avec le site
            border_radius = 16  # Cohérent avec border-radius: 16px du site
            
            if bubble_type == "pensée" or "pensée" in emotion:
                # Bulle de pensée (nuage) avec style arrondi moderne
                draw.ellipse([bubble_x1, bubble_y1, bubble_x2, bubble_y2], 
                           fill=bubble_color, outline=outline_color, width=outline_width)
                # Petits cercles pour la queue de pensée avec style harmonisé
                for j in range(3):
                    circle_x = x - 20 + j * 10
                    circle_y = bubble_y2 + 10 + j * 8
                    circle_size = 8 - j * 2
                    draw.ellipse([circle_x-circle_size, circle_y-circle_size, 
                                circle_x+circle_size, circle_y+circle_size], 
                               fill=bubble_color, outline=outline_color, width=1)
            elif bubble_type == "cri" or emotion in ["excitation", "surprise", "colère"]:
                # Bulle dentelée mais avec des coins plus arrondis
                points = []
                steps = 12
                for i in range(steps):
                    angle = 2 * 3.14159 * i / steps
                    if i % 2 == 0:
                        radius = min(bubble_width, bubble_height) / 2 - 2  # Moins pointu
                    else:
                        radius = min(bubble_width, bubble_height) / 2 - 6  # Moins agressif
                    px = x + radius * math.cos(angle)
                    py = y + radius * math.sin(angle)
                    points.append((px, py))
                draw.polygon(points, fill=bubble_color, outline=outline_color, width=outline_width)
            else:
                # Bulle normale avec style arrondi moderne (rectangle aux coins arrondis)
                # Créer une forme arrondie plus moderne que l'ellipse simple
                rounded_rect_points = []
                corners = 8  # Nombre de points pour arrondir chaque coin
                corner_radius = min(bubble_width, bubble_height) * 0.15  # Rayon des coins
                
                # Créer approximation de rectangle arrondi avec polygone
                for corner in range(4):
                    start_angle = corner * math.pi / 2 + math.pi / 4
                    if corner == 0:  # Coin haut-droite
                        center_x, center_y = bubble_x2 - corner_radius, bubble_y1 + corner_radius
                    elif corner == 1:  # Coin bas-droite  
                        center_x, center_y = bubble_x2 - corner_radius, bubble_y2 - corner_radius
                    elif corner == 2:  # Coin bas-gauche
                        center_x, center_y = bubble_x1 + corner_radius, bubble_y2 - corner_radius
                    else:  # Coin haut-gauche
                        center_x, center_y = bubble_x1 + corner_radius, bubble_y1 + corner_radius
                    
                    for i in range(corners):
                        angle = start_angle + (math.pi / 2) * i / (corners - 1)
                        px = center_x + corner_radius * math.cos(angle)
                        py = center_y + corner_radius * math.sin(angle)
                        rounded_rect_points.append((px, py))
                
                # Si on ne peut pas faire un rectangle arrondi, fallback sur ellipse moderne
                if len(rounded_rect_points) >= 8:
                    draw.polygon(rounded_rect_points, fill=bubble_color, outline=outline_color, width=outline_width)
                else:
                    # Ellipse avec proportions plus modernes
                    ellipse_x1 = x - bubble_width//2 + 5
                    ellipse_y1 = y - bubble_height//2 + 3
                    ellipse_x2 = x + bubble_width//2 - 5  
                    ellipse_y2 = y + bubble_height//2 - 3
                    draw.ellipse([ellipse_x1, ellipse_y1, ellipse_x2, ellipse_y2], 
                               fill=bubble_color, outline=outline_color, width=outline_width)
                
                # Calculer la direction intelligente de la queue vers le personnage
                tail_x, tail_y = self._calculate_bubble_tail_direction(x, y, character_positions)
                
                # Déterminer le point de sortie de la bulle (bord le plus proche de la destination)
                angle = math.atan2(tail_y - y, tail_x - x)
                
                # Point de sortie sur le bord de la bulle avec style arrondi
                bubble_radius_x = bubble_width // 2 - 5  # Ajusté pour le style arrondi
                bubble_radius_y = bubble_height // 2 - 3
                exit_x = x + bubble_radius_x * math.cos(angle) * 0.9
                exit_y = y + bubble_radius_y * math.sin(angle) * 0.9
                
                # Créer une queue triangulaire plus élégante et arrondie
                tail_base_width = 10  # Légèrement plus étroite pour un look moderne
                perpendicular_angle = angle + math.pi / 2
                
                tail_point1_x = exit_x + tail_base_width * math.cos(perpendicular_angle) / 2
                tail_point1_y = exit_y + tail_base_width * math.sin(perpendicular_angle) / 2
                tail_point2_x = exit_x - tail_base_width * math.cos(perpendicular_angle) / 2
                tail_point2_y = exit_y - tail_base_width * math.sin(perpendicular_angle) / 2
                
                # Queue triangulaire avec bordures arrondies
                tail_points = [
                    (tail_point1_x, tail_point1_y),
                    (tail_point2_x, tail_point2_y), 
                    (tail_x, tail_y)
                ]
                
                draw.polygon(tail_points, fill=bubble_color, outline=outline_color, width=outline_width)
            
            # Dessiner le texte avec style cohérent avec le site
            text_start_y = y - text_height // 2
            current_y = text_start_y
            
            # Couleur de texte cohérente avec la charte graphique
            text_color = "#333333"  # Couleur --text du site
            
            # Ajustement de couleur selon l'émotion pour une meilleure lisibilité
            if emotion in ["colère", "frustration"]:
                text_color = "#333333"  # Garder le texte sombre pour lisibilité
            elif emotion in ["tristesse", "mélancolie"]:
                text_color = "#333333"  # Texte standard pour lisibilité
            elif emotion in ["excitation", "joie", "bonheur"]:
                text_color = "#333333"  # Texte sombre sur fond clair
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                text_x = x - line_width // 2
                
                # Ajouter une très légère ombre pour améliorer la lisibilité (effet moderne)
                shadow_offset = 1
                shadow_color = "#cccccc"  # Gris très clair pour l'ombre
                draw.text((text_x + shadow_offset, current_y + shadow_offset), 
                         line, fill=shadow_color, font=font)
                
                # Texte principal avec couleur harmonisée
                draw.text((text_x, current_y), line, fill=text_color, font=font)
                current_y += (bbox[3] - bbox[1]) + 4  # Espacement légèrement réduit pour plus de modernité
        
        # Sauvegarder l'image finale
        final_path = comic_dir / f"page_{page_num}_final.png"
        img.save(final_path)
        
        return final_path
    
    async def create_complete_comic(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une bande dessinée complète avec IA intégrée"""
        
        start_time = datetime.now()
        
        try:
            print("🎨 Génération BD avec IA intégrée...")
            
            # 1. Générer le script avec notre système existant
            print("📝 Génération du scénario...")
            script_data = await self.generate_comic_script(
                theme=request_data["theme"],
                story_length=request_data.get("story_length", "short"),
                custom_request=request_data.get("custom_request")
            )
            
            # 2. Préparer les données pour le générateur Stable Diffusion
            print("🔧 Préparation des données pour le générateur...")
            
            # Créer un objet spec compatible
            class ComicSpec:
                def __init__(self, data):
                    # Extraire le nom du héros correctement
                    characters = data.get("characters", ["Héros"])
                    if isinstance(characters, list) and len(characters) > 0:
                        first_char = characters[0]
                        if isinstance(first_char, dict):
                            self.hero_name = first_char.get("name", "Héros")
                        else:
                            self.hero_name = str(first_char)
                    else:
                        self.hero_name = "Héros"
                    
                    self.story_type = data.get("theme", "adventure")
                    self.style = data.get("art_style", "cartoon")
                    self.num_images = len(data.get("scenes", []))
                    if self.num_images == 0:
                        self.num_images = 4  # Valeur par défaut
            
            spec = ComicSpec({
                "characters": script_data.get("main_characters", ["Héros"]),
                "theme": request_data["theme"],
                "art_style": request_data.get("art_style", "cartoon"),
                "scenes": script_data.get("scenes", [])
            })
            
            # Convertir le script en format compatible avec le générateur SD
            comic_data = {
                "chapters": []
            }
            
            scenes = script_data.get("scenes", [])
            for i, scene in enumerate(scenes):
                chapter = {
                    "scene": i + 1,
                    "description": scene.get("description", f"Scène {i+1}"),
                    "action_description": scene.get("action_description", scene.get("description", ""))
                }
                comic_data["chapters"].append(chapter)
            
            # Si pas de scènes, créer des scènes génériques
            if not comic_data["chapters"]:
                for i in range(4):
                    comic_data["chapters"].append({
                        "scene": i + 1,
                        "description": f"Aventure de {spec.hero_name} - Scène {i+1}",
                        "action_description": f"Une aventure passionnante avec {spec.hero_name}"
                    })
            
            # 3. Générer les images avec le système natif qui gère les thèmes
            print("🎨 Génération des images avec thème espace...")
            pages, comic_id = await self.generate_comic_images(script_data, request_data.get("art_style", "cartoon"))
            
            # 5. Les pages sont déjà au bon format depuis generate_comic_images
            formatted_pages = pages
            
            # 6. Sauvegarder les métadonnées
            metadata = {
                "comic_id": comic_id,
                "title": script_data.get("title", "Aventure BD"),
                "synopsis": script_data.get("synopsis", "Une aventure passionnante"),
                "characters": script_data.get("main_characters", []),
                "theme": request_data["theme"],
                "art_style": request_data.get("art_style", "cartoon"),
                "story_length": request_data.get("story_length", "short"),
                "creation_date": datetime.now().isoformat(),
                "generation_time": (datetime.now() - start_time).total_seconds(),
                "ai_bubbles_enabled": self.ai_enhancer is not None,
                "ai_models_used": {
                    "vision": os.getenv("COMIC_VISION_MODEL", "gpt-4o"),
                    "text": os.getenv("COMIC_TEXT_MODEL", "gpt-4o-mini")
                }
            }
            
            print(f"✅ BD générée avec succès: {len(formatted_pages)} pages")
            
            return {
                "status": "success",
                "comic_id": comic_id,
                "title": script_data.get("title", "Aventure BD"),
                "pages": formatted_pages,
                "total_pages": len(formatted_pages),
                "theme": request_data["theme"],
                "art_style": request_data.get("art_style", "cartoon"),
                "generation_time": (datetime.now() - start_time).total_seconds(),
                "comic_metadata": metadata
            }
            
        except Exception as e:
            print(f"❌ Erreur création BD: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "comic_id": None,
                "title": "Erreur de génération",
                "pages": [],
                "total_pages": 0
            }
    
    async def _generate_with_stability_ai_corrected(self, prompt: str, output_path: Path, seed: int) -> Path:
        """Version corrigée de Stability AI - utilise requests synchrone qui fonctionne mieux"""
        try:
            import requests
            
            # API Stability AI v2beta
            api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
            
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Accept": "image/*"
            }
            
            # Utiliser requests avec files au lieu d'aiohttp
            files = {
                "prompt": (None, prompt),
                "model": (None, "sd3-medium"),
                "aspect_ratio": (None, "3:2"),
                "seed": (None, str(seed)),
                "output_format": (None, "png")
            }
            
            print(f"🎯 Stability AI SD3 - Seed: {seed}")
            
            # Utiliser requests (synchrone) qui gère mieux multipart/form-data
            response = requests.post(
                api_url,
                headers=headers,
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                image_data = response.content
                
                if len(image_data) > 1000:
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    
                    print(f"✅ Image Stability AI générée: {output_path} ({len(image_data)} bytes)")
                    return output_path
                else:
                    raise Exception("Image trop petite")
            else:
                print(f"❌ Erreur API Stability AI ({response.status_code}): {response.text}")
                raise Exception(f"API error: {response.status_code}")
                        
        except Exception as e:
            print(f"❌ Erreur Stability AI: {e}")
            raise e
    
    async def _generate_with_dalle(self, prompt: str, output_path: Path, seed: int) -> Path:
        """Génération avec DALL-E d'OpenAI"""
        try:
            # Optimiser le prompt pour DALL-E (style BD)
            dalle_prompt = f"{prompt}, comic book style, detailed illustration, vibrant colors, professional comic art"
            
            print(f"🎨 DALL-E prompt: {dalle_prompt[:100]}...")
            
            # Utiliser DALL-E 3 via l'API OpenAI
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1024x1024",  # DALL-E 3 supporte 1024x1024
                quality="standard",
                n=1
            )
            
            # Télécharger l'image générée
            image_url = response.data[0].url
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as img_response:
                    if img_response.status == 200:
                        content = await img_response.read()
                        
                        with open(output_path, 'wb') as f:
                            f.write(content)
                        
                        print(f"✅ Image DALL-E générée: {output_path} ({len(content)} bytes)")
                        return output_path
                    else:
                        raise Exception(f"Erreur téléchargement: {img_response.status}")
            
        except Exception as e:
            print(f"❌ Erreur DALL-E: {e}")
            raise e
    
    async def _generate_with_stability_ai(self, prompt: str, output_path: Path, seed: int) -> Path:
        """Génération avec l'API officielle Stability AI (nouvelles APIs v2beta)"""
        try:
            import aiohttp
            
            # Configuration pour les nouvelles APIs Stability AI v2beta
            # Utilisation de SD3 pour la qualité optimale des BD
            api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
            
            headers = {
                "Authorization": f"Bearer {self.stability_key}"
                # Pas de Content-Type ni Accept pour multipart/form-data, aiohttp gère tout automatiquement
            }
            
            # Paramètres optimisés pour les bandes dessinées réalistes
            data = aiohttp.FormData()
            data.add_field("prompt", prompt)
            data.add_field("model", "sd3-medium")  # Modèle stable et rapide
            data.add_field("aspect_ratio", "3:2")  # Ratio supporté proche de 4:3
            data.add_field("seed", str(seed))
            data.add_field("output_format", "png")
            
            print(f"🎨 Envoi à Stability AI SD3 - Seed: {seed}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        # L'image est retournée directement en binaire
                        image_data = await response.read()
                        
                        # Sauvegarder l'image
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                            
                        print(f"✅ Image générée avec Stability AI SD3: {output_path} ({len(image_data)} bytes)")
                        return output_path
                    else:
                        error_text = await response.text()
                        print(f"❌ Erreur API Stability AI SD3 ({response.status}): {error_text}")
                        
                        # Fallback vers Core API si SD3 échoue
                        return await self._generate_with_stability_core(prompt, output_path, seed)
                        
        except Exception as e:
            print(f"❌ Erreur Stability AI SD3: {e}")
            # Fallback vers Core API
            return await self._generate_with_stability_core(prompt, output_path, seed)
    
    async def _generate_with_stability_core(self, prompt: str, output_path: Path, seed: int) -> Path:
        """Fallback avec Stability AI Core"""
        try:
            import aiohttp
            
            api_url = "https://api.stability.ai/v2beta/stable-image/generate/core"
            
            headers = {
                "Authorization": f"Bearer {self.stability_key}"
                # Pas de Content-Type ni Accept pour multipart/form-data, aiohttp gère tout automatiquement
            }
            
            data = aiohttp.FormData()
            data.add_field("prompt", prompt)
            data.add_field("aspect_ratio", "3:2")
            data.add_field("seed", str(seed))
            data.add_field("output_format", "png")
            
            print(f"🎨 Fallback vers Stability AI Core - Seed: {seed}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        print(f"✅ Image générée avec Stability AI Core: {output_path} ({len(image_data)} bytes)")
                        return output_path
                    else:
                        error_text = await response.text()
                        print(f"❌ Erreur API Stability AI Core ({response.status}): {error_text}")
                        raise Exception(f"API Core Error: {response.status}")
                        
        except Exception as e:
            print(f"❌ Erreur Stability AI Core: {e}")
            # PLUS DE FALLBACK - Lever une erreur stricte
            raise Exception(f"❌ ÉCHEC COMPLET Stability AI: {e}. Aucune image de fallback autorisée.")
    
    def _debug_seed_info(self, title: str, base_seed: int, character_seeds: Dict, page_seed: int, page_num: int):
        """Affiche les informations de debug pour les seeds"""
        title_display = title[:20] + '...' if len(title) > 20 else title
        
        char_lines = ""
        for name, seed in character_seeds.items():
            line_content = f"{name}: {seed}"
            padding = " " * (35 - len(line_content))
            char_lines += f"│     {line_content}{padding}│\n"
        
        debug_box = f"""
╭─────────────────────────────────────────────╮
│  🎲 DEBUG SEEDS - BD: {title_display}
├─────────────────────────────────────────────┤
│  📖 Page {page_num:2d} - Seed: {page_seed:>6d}
│  🎯 Base seed: {base_seed:>6d}
│  👥 Character seeds: {len(character_seeds)} personnages
{char_lines}╰─────────────────────────────────────────────╯
        """
        
        print(debug_box)
    
    def _get_correct_image_url(self, comic_id: str, scene_num: int, comic_dir: Path) -> str:
        """Détermine l'URL correcte de l'image en fonction des fichiers qui existent"""
        base_url = f"/static/generated_comics/{comic_id}/page_{scene_num}"
        
        # Ordre de priorité des fichiers à vérifier
        possible_files = [
            f"page_{scene_num}_bubble_2_sd3_advanced.png",  # Fichier final avec bulles SD3
            f"page_{scene_num}_bubble_1_sd3_advanced.png",  # Fichier avec une bulle SD3
            f"page_{scene_num}_final.png",                  # Fichier final classique
            f"page_{scene_num}_base.png",                   # Fichier de base sans bulles
        ]
        
        for filename in possible_files:
            filepath = comic_dir / filename
            if filepath.exists():
                return f"/static/generated_comics/{comic_id}/{filename}"
        
        # Fallback : retourner le fichier de base même s'il n'existe pas
        return f"/static/generated_comics/{comic_id}/page_{scene_num}_base.png"
    
    def _get_theme_visual_keywords(self, theme: str) -> str:
        """Renforce le thème avec des mots-clés visuels spécifiques"""
        theme_keywords = {
            "space": "space setting, alien planets, spaceships, stars, cosmic background, futuristic technology, astronauts, space suits, galaxies, nebulae, alien creatures, space stations, rockets, zero gravity, sci-fi environment",
            "adventure": "adventure setting, mysterious forests, ancient castles, treasure maps, exploration gear, jungle environments, hidden temples, mountain landscapes, caves, waterfalls",
            "animals": "natural wildlife setting, African savanna, jungle environments, animal habitats, nature scenes, wildlife photography style, natural lighting, grasslands, trees, watering holes",
            "magic": "magical fantasy setting, enchanted forests, fairy tale castles, magical creatures, sparkling effects, mystical atmosphere, fantasy landscape, magical portals, floating objects",
            "friendship": "school environments, playground scenes, neighborhood settings, modern urban environments, classroom scenes, friendly atmosphere, warm lighting, contemporary settings"
        }
        return theme_keywords.get(theme, theme_keywords["adventure"])
    
    async def _add_speech_bubbles_pil_simple(self, image_path: Path, dialogues: List[Dict], comic_dir: Path, page_num: int) -> Path:
        """Génère des bulles de dialogue fiables avec PIL - Version simplifiée et visible"""
        
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        print(f"🎯 Génération de {len(dialogues)} bulles PIL fiables")
        
        # Charger une police simple et visible
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", 20)
            except:
                font = ImageFont.load_default()
        
        width, height = img.size
        
        # Positions fixes pour garantir la visibilité
        bubble_positions = [
            (width * 0.15, height * 0.15),  # Haut-gauche
            (width * 0.85, height * 0.15),  # Haut-droite
            (width * 0.15, height * 0.85),  # Bas-gauche
            (width * 0.85, height * 0.85),  # Bas-droite
        ]
        
        for i, dialogue in enumerate(dialogues):
            if i >= len(bubble_positions):
                break
                
            text = dialogue.get("text", "...")
            x, y = bubble_positions[i]
            
            # Calculer la taille de la bulle
            lines = self._wrap_text(text, 20)  # Max 20 caractères par ligne
            line_height = 25
            text_width = max(len(line) * 12 for line in lines)  # Approximation
            text_height = len(lines) * line_height
            
            # Dimensions de la bulle avec padding
            bubble_width = text_width + 40
            bubble_height = text_height + 30
            
            # Ajuster la position pour que la bulle reste dans l'image
            bubble_x = max(20, min(x - bubble_width//2, width - bubble_width - 20))
            bubble_y = max(20, min(y - bubble_height//2, height - bubble_height - 20))
            
            # Dessiner la bulle (fond blanc, bordure noire épaisse)
            bubble_rect = [bubble_x, bubble_y, bubble_x + bubble_width, bubble_y + bubble_height]
            draw.ellipse(bubble_rect, fill="white", outline="black", width=3)
            
            # Ajouter le texte centré
            text_x = bubble_x + 20
            text_y = bubble_y + 15
            
            for j, line in enumerate(lines):
                line_y = text_y + j * line_height
                draw.text((text_x, line_y), line, fill="black", font=font)
            
            print(f"   💬 Bulle {i+1}: '{text[:30]}...' à position ({bubble_x}, {bubble_y})")
        
        # Sauvegarder l'image finale
        final_path = comic_dir / f"page_{page_num}_final.png"
        img.save(final_path)
        
        print(f"✅ {len(dialogues)} bulles PIL fiables générées: {final_path}")
        return final_path
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Divise le texte en lignes de largeur maximale"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_width:
                current_line = current_line + " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
