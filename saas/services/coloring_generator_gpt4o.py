"""
Service de génération de coloriages
- GPT-4o analyse + Gemini text-to-image pour les photos uploadées (Gemini bloque image-to-image)
- gemini-2.5-flash-image pour les thèmes prédéfinis
- gpt-image-1-mini pour les photos uploadées (image-to-image)
"""
import os
import uuid
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import io
import requests
from openai import AsyncOpenAI
from google import genai
from google.genai import types
from dotenv import load_dotenv
from services.supabase_storage import get_storage_service

load_dotenv()


class ColoringGeneratorGPT4o:
    """
    Générateur de coloriages
    - gpt-image-1-mini (image-to-image) pour photos uploadées
    - gemini-2.5-flash-image (text-to-image) pour thèmes
    """
    
    def __init__(self):
        try:
            self.output_dir = Path("static/coloring")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self.upload_dir = Path("static/uploads/coloring")
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Configuration OpenAI (pour gpt-4o-mini si nécessaire)
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("[ERROR] OPENAI_API_KEY non trouvee dans .env")
                raise ValueError("OPENAI_API_KEY manquante")
            
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # Configuration Gemini pour la génération d'images
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not self.gemini_api_key:
                print("[ERROR] GEMINI_API_KEY non trouvee dans .env")
                raise ValueError("GEMINI_API_KEY manquante")
            
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            
            # URL de base pour les images (production Railway ou local)
            self.base_url = os.getenv("BASE_URL", "https://herbbie.com")
            
            # Prompts pour l'édition d'image directe (IMAGE-TO-IMAGE pour photos)
            # Prompt simplifié et direct pour Gemini
            self.edit_prompt_with_model = """Transform this image into a black and white line drawing coloring page. Use thick black outlines only, no shadows, no grayscale, pure white background. Make it suitable for children to color. [At the same time, for the convenience of users who are not good at coloring, please generate a complete colored version in the lower right corner as a small image for reference]"""

            self.edit_prompt_without_model = """Transform this image into a black and white line drawing coloring page. Use thick black outlines only, no shadows, no grayscale, pure white background. Make it suitable for children to color. NO colored reference image."""
            
            # Prompts pour la génération par thème (TEXT-TO-IMAGE)
            self.coloring_prompt_with_model = """A black and white line drawing coloring illustration, suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders. The overall illustration style is fresh and simple, using clear and smooth black outline lines, without shadows, grayscale, or color filling, with a pure white background for easy coloring. [At the same time, for the convenience of users who are not good at coloring, please generate a complete colored version in the lower right corner as a small image for reference] Suitable for: [6-9 year old children]

Subject: {subject}"""
            
            self.coloring_prompt_without_model = """A black and white line drawing coloring illustration, suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders. The overall illustration style is fresh and simple, using clear and smooth black outline lines, without shadows, grayscale, or color filling, with a pure white background for easy coloring. NO colored reference image. Suitable for: [6-9 year old children]

Subject: {subject}"""
            
            # Initialisation silencieuse
        except Exception as e:
            # Erreur silencieuse lors de l'initialisation
            raise
    
    async def _analyze_photo_for_coloring(self, photo_path: str) -> str:
        """Analyse une photo avec gpt-4o-mini pour créer une description ULTRA DÉTAILLÉE pour coloriage
        
        Cette description sera utilisée dans le prompt pour Gemini afin de créer un coloriage
        reconnaissable sans utiliser l'image directement.
        
        Args:
            photo_path: Chemin vers la photo
            
        Returns:
            Description très détaillée de la photo en anglais
        """
        try:
            print(f"[COLORING] Analyse approfondie de la photo: {photo_path}")
            
            # Charger et encoder l'image en base64
            with open(photo_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Convertir en base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Déterminer le type MIME
            photo_path_obj = Path(photo_path)
            ext = photo_path_obj.suffix.lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(ext, 'image/jpeg')
            
            # Analyser avec gpt-4o (vision) - Description ULTRA DÉTAILLÉE et EXHAUSTIVE
            # Utilisation de gpt-4o au lieu de gpt-4o-mini car moins de restrictions
            print(f"   🤖 Utilisation gpt-4o (au lieu de gpt-4o-mini) pour éviter les blocages...")
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are an expert visual analyst. Analyze this photo and create an EXTREMELY DETAILED, EXHAUSTIVE, and PRECISE description in English that will allow an image generation model to recreate this exact scene as a black and white line drawing coloring page with MAXIMUM FIDELITY and RECOGNIZABILITY.

CRITICAL: Your description must be so detailed that someone reading it could draw or generate a coloring page that looks EXACTLY like a line drawing version of this photo. Every single visible detail matters.

ANALYSIS CRITERIA (describe EVERYTHING in extreme detail, NO length limit):

1. MAIN SUBJECT(S) - PEOPLE (if present):
   - Exact approximate age(s)
   - Gender(s)
   - Face shape(s): round, oval, square, rectangular, triangular, heart-shaped, diamond-shaped
   - Face width relative to length
   - Forehead: high, low, average; width; shape
   - Cheekbones: prominent, flat, average; position
   - Jawline: sharp, rounded, square, soft, defined
   - Chin: pointed, rounded, square, cleft, dimpled
   - Exact skin tone: very fair, fair, light, light-medium, medium, medium-tan, tan, olive, dark, very dark
   - Undertones: warm (yellow/golden), cool (pink/blue), neutral
   - Exact hair color: light blonde, dark blonde, light brown, medium brown, dark brown, black, auburn, red, strawberry blonde, etc. (be VERY specific)
   - Hair length: very short, short, medium-short, medium, medium-long, long, very long
   - Hair texture: straight, wavy, curly, very curly, kinky, coily
   - Haircut style: bangs (fringe), side part, center part, no part, layers, one length, etc.
   - Exact eye color: bright blue, light blue, dark blue, blue-gray, green, hazel, light brown, medium brown, dark brown, black, gray, etc.
   - Eye shape: round, almond-shaped, oval, wide-set, close-set, upturned, downturned
   - Eye size: small, medium, large relative to face
   - Nose shape: small, medium, large relative to face; pointed, rounded, bulbous, upturned, downturned
   - Mouth size: small, medium, large relative to face
   - Lip fullness: thin, medium, full
   - Expression: smiling (how wide), neutral, serious, etc.
   - Distinctive features: freckles (number, location, color, size), moles (location, size, color), dimples, scars, birthmarks
   - Body build: slim, average, stocky, etc.
   - Apparent height: short, average, tall

2. CLOTHING (COMPLETE DETAILED DESCRIPTION):
   - Exact type of each garment (t-shirt, polo shirt, button-down shirt, sweater, hoodie, dress, jeans, pants, shorts, skirt, etc.)
   - Exact color of each garment: exact shade and color name (e.g., "bright red", "navy blue", "light gray")
   - Style: fitted, loose, oversized, etc.
   - Patterns: solid, stripes (direction, width, colors), prints (describe pattern in detail), logos (describe), graphics (describe)
   - Details: sleeves length, collar type, pockets, zippers, buttons, etc.
   - Shoes: type, color, style
   - Accessories: glasses (frame shape, color), jewelry (earrings, necklace, bracelets, rings - describe each), hat/cap (type, color, style, logos), watch, bag/backpack

3. POSE AND POSITION:
   - Body position: standing, sitting, leaning, lying down, etc.
   - Pose: arms position, legs position, head position (straight, tilted, turned)
   - Posture: confident, relaxed, tense, etc.
   - Expression and emotion: happy, serious, neutral, playful, etc.

4. BACKGROUND AND ENVIRONMENT:
   - What is visible in the background: objects, furniture, nature, buildings, etc.
   - Background colors and tones
   - Lighting: direction (front, side, top), quality (bright, soft, harsh, natural)
   - Any shadows and where they fall
   - Overall composition and framing

5. OBJECTS AND ELEMENTS:
   - Any objects visible: describe each in detail (type, color, size, position)
   - Animals if present: type, color, size, position, pose
   - Plants if present: type, size, position
   - Any other elements in the scene

6. COMPOSITION AND LAYOUT:
   - Overall composition: centered, off-center, etc.
   - Main subject position in frame
   - Proportions: how elements relate to each other
   - Photo angle: front view, slight angle, profile, etc.

7. DISTINCTIVE FEATURES:
   - Any unique or distinctive elements that make this photo recognizable
   - Any text visible (describe exactly)
   - Any logos or brands visible (describe exactly)

OUTPUT FORMAT:
Start with a general overview, then provide EXTREMELY DETAILED paragraph-by-paragraph descriptions covering ALL the above points.

CRITICAL REQUIREMENTS:
- Be EXTREMELY SPECIFIC about colors (don't just say "red shirt" - say "bright red short-sleeved t-shirt with a round neckline")
- Describe EXACT proportions and relationships between elements
- Mention EVERY visible detail, no matter how small
- Use precise descriptive language
- Write in English, factual and precise style
- NO length limit - the more detail, the better
- The goal is MAXIMUM FIDELITY - someone should be able to recreate this exact scene as a coloring page from your description"""
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
            
            description = response.choices[0].message.content.strip()
            print(f"[COLORING] Photo analysée en détail ({len(description)} caractères): {description[:150]}...")
            
            return description
            
        except Exception as e:
            print(f"[ERROR] Erreur analyse photo: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Échec analyse photo pour coloriage: {e}")
    
    async def _generate_coloring_from_description(
        self,
        photo_description: str,
        custom_prompt: Optional[str] = None,
        with_colored_model: bool = True,
        original_photo_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Génère un coloriage avec Gemini text-to-image en utilisant une description ultra détaillée
        
        Args:
            photo_description: Description très détaillée de la photo (obtenue via GPT-4o-mini)
            custom_prompt: Prompt personnalisé optionnel
            with_colored_model: Si True, inclut un modèle coloré en coin
            original_photo_path: Chemin vers la photo originale (pour préserver les dimensions)
        
        Returns:
            Chemin local de l'image générée
        """
        try:
            # Construire le prompt final avec la description ultra détaillée
            base_coloring_instructions = """A black and white line drawing coloring page with MAXIMUM FIDELITY to the following detailed description. The coloring page must be suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders.

REQUIREMENTS:
- Clear, smooth black outline lines only
- No shadows, grayscale, or color filling
- Pure white background
- Line weight should be consistent and appropriate for coloring
- Suitable for 6-9 year old children
- MAXIMUM FIDELITY: Every detail from the description below must be accurately represented in the line drawing

"""
            
            if with_colored_model:
                base_coloring_instructions += "[At the same time, for the convenience of users who are not good at coloring, please generate a complete colored version in the lower right corner as a small image for reference]\n\n"
            
            if custom_prompt:
                final_prompt = f"{base_coloring_instructions}{custom_prompt}\n\nDETAILED DESCRIPTION OF THE SCENE TO RECREATE:\n{photo_description}"
            else:
                final_prompt = f"""{base_coloring_instructions}DETAILED DESCRIPTION OF THE SCENE TO RECREATE AS A COLORING PAGE:

{photo_description}

CRITICAL: Recreate this exact scene as a black and white line drawing coloring page. Every detail mentioned in the description above (people, clothing, poses, expressions, objects, background, composition) must be accurately represented. The coloring page should look like a line drawing version of the scene described above."""
            
            print(f"[PROMPT TEXT-TO-IMAGE] {final_prompt[:200]}...")
            
            # Détecter les dimensions originales si la photo est fournie
            original_width, original_height = None, None
            if original_photo_path:
                try:
                    input_img = Image.open(original_photo_path)
                    original_width, original_height = input_img.size
                    aspect_ratio = original_width / original_height
                    print(f"[DIMENSIONS] Dimensions originales: {original_width}x{original_height} (ratio: {aspect_ratio:.2f})")
                except Exception as e:
                    print(f"[WARNING] Impossible de lire les dimensions originales: {e}")
            
            # Appeler Gemini avec text-to-image
            print(f"[API] Appel Gemini gemini-3-pro-image-preview (text-to-image)...")
            response = self.gemini_client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[final_prompt]
            )
            
            print(f"[RESPONSE] Réponse reçue de gemini-3-pro-image-preview")
            
            # Extraire l'image de la réponse
            image_data = None
            if hasattr(response, 'candidates') and response.candidates is not None and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data is not None:
                            if hasattr(part.inline_data, 'data'):
                                data = part.inline_data.data
                                
                                if isinstance(data, str):
                                    try:
                                        image_data = base64.b64decode(data)
                                        print(f"[DEBUG] Image décodée depuis base64: {len(image_data)} bytes")
                                    except Exception as e:
                                        print(f"[ERROR] Erreur décodage base64: {e}")
                                        continue
                                elif isinstance(data, bytes):
                                    image_data = data
                                    print(f"[DEBUG] Données déjà en bytes: {len(image_data)} bytes")
                                
                                if image_data:
                                    try:
                                        test_img = Image.open(io.BytesIO(image_data))
                                        print(f"[DEBUG] Image valide: {test_img.size}")
                                        break
                                    except Exception as e:
                                        print(f"[ERROR] Données décodées ne sont pas une image valide: {e}")
                                        image_data = None
                                        continue
            
            if not image_data:
                print(f"[ERROR] Aucune image trouvée dans la réponse")
                raise Exception("Format de réponse gemini-3-pro-image-preview inattendu - aucune image trouvée")
            
            # Charger l'image générée
            generated_img = Image.open(io.BytesIO(image_data))
            generated_width, generated_height = generated_img.size
            generated_ratio = generated_width / generated_height
            
            print(f"[GENERATED] Image générée: {generated_width}x{generated_height} (ratio: {generated_ratio:.2f})")
            
            # Déterminer la taille finale
            min_size = 1536
            if original_width and original_height:
                if original_width < min_size or original_height < min_size:
                    final_width = final_height = min_size
                    print(f"[SMALL] Image originale petite ({original_width}x{original_height}), utilisation taille minimale {min_size}x{min_size}")
                else:
                    final_width, final_height = original_width, original_height
                    print(f"[TARGET] Redimensionnement vers: {original_width}x{original_height}")
            else:
                # Si pas de dimensions originales, utiliser les dimensions générées ou minimum
                final_width = max(generated_width, min_size)
                final_height = max(generated_height, min_size)
                print(f"[DEFAULT] Utilisation dimensions générées: {final_width}x{final_height}")
            
            # Redimensionner si nécessaire
            if generated_width != final_width or generated_height != final_height:
                target_ratio = final_width / final_height
                ratio_diff = abs(generated_ratio - target_ratio) / target_ratio if target_ratio > 0 else 1
                
                if ratio_diff > 0.05:
                    print(f"[WARNING] Différence de ratio détectée: {ratio_diff*100:.1f}%")
                    # Adapter en préservant le ratio cible et en centrant
                    if target_ratio > generated_ratio:
                        new_width = final_width
                        new_height = int(final_width / generated_ratio)
                    else:
                        new_height = final_height
                        new_width = int(final_height * generated_ratio)
                    
                    temp_resized = generated_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    final_img = Image.new('RGB', (final_width, final_height), 'white')
                    x_offset = (final_width - new_width) // 2
                    y_offset = (final_height - new_height) // 2
                    final_img.paste(temp_resized, (x_offset, y_offset))
                    print(f"[ADJUSTED] Image centrée avec ratio préservé: {new_width}x{new_height} -> {final_width}x{final_height}")
                else:
                    final_img = generated_img.resize((final_width, final_height), Image.Resampling.LANCZOS)
                    print(f"[RESIZED] Redimensionnement direct: {generated_width}x{generated_height} -> {final_width}x{final_height}")
            else:
                final_img = generated_img
                print(f"[NO RESIZE] Dimensions déjà correctes: {final_width}x{final_height}")
            
            # Sauvegarder
            output_path = self.output_dir / f"coloring_photo_direct_{uuid.uuid4().hex[:8]}.png"
            final_img.save(output_path, 'PNG', optimize=True)
            print(f"[OK] Coloriage photo sauvegardé ({final_width}x{final_height}): {output_path.name}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"[ERROR] Erreur génération coloriage depuis description: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _convert_photo_to_coloring_with_gpt_image_1(
        self,
        photo_path: str,
        with_colored_model: bool = True
    ) -> Optional[str]:
        """
        Convertit une photo en coloriage avec gpt-image-1-mini images.edit
        
        Args:
            photo_path: Chemin vers la photo
            with_colored_model: Si True, inclut un modèle coloré en coin
        
        Returns:
            Chemin local de l'image générée
        """
        try:
            print(f"[COLORING PHOTO] Conversion avec gpt-image-1-mini images.edit: {photo_path}")
            
            # Charger l'image
            input_image = Image.open(photo_path)
            original_width, original_height = input_image.size
            
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
            temp_input_path = self.output_dir / f"temp_input_{uuid.uuid4().hex[:8]}.png"
            square_image.save(temp_input_path, 'PNG')
            
            # Créer un masque blanc en RGBA (tout l'image sera modifiée)
            mask_image = Image.new('RGBA', (size, size), (255, 255, 255, 255))
            temp_mask_path = self.output_dir / f"temp_mask_{uuid.uuid4().hex[:8]}.png"
            mask_image.save(temp_mask_path, 'PNG')
            
            # Prompt pour transformer en coloriage pour enfants
            if with_colored_model:
                edit_prompt = """Transform this image into a black and white line drawing coloring page for children. Use the uploaded image as reference and transform it into a coloring page with thick black outlines only, no shadows, no grayscale, pure white background. Make it suitable for children to color. At the same time, generate a complete colored version in the lower right corner as a small image for reference."""
            else:
                edit_prompt = """Transform this image into a black and white line drawing coloring page for children. Use the uploaded image as reference and transform it into a coloring page with thick black outlines only, no shadows, no grayscale, pure white background. Make it suitable for children to color. NO colored reference image."""
            
            print(f"[PROMPT] {edit_prompt[:100]}...")
            
            # Utiliser images.edit pour transformer en coloriage
            with open(temp_input_path, "rb") as input_file, open(temp_mask_path, "rb") as mask_file:
                response = await self.client.images.edit(
                    image=input_file,
                    mask=mask_file,
                    prompt=edit_prompt,
                    n=1,
                    size=f"{size}x{size}",
                    model="gpt-image-1-mini"
                )
            
            # Récupérer l'URL de l'image générée
            image_url = response.data[0].url
            
            # Télécharger l'image
            import httpx
            async with httpx.AsyncClient() as client:
                image_response = await client.get(image_url)
                image_response.raise_for_status()
                image_data = image_response.content
            
            # Charger l'image générée
            generated_img = Image.open(io.BytesIO(image_data))
            
            # Redimensionner aux dimensions originales si nécessaire
            if generated_img.size != (original_width, original_height):
                generated_img = generated_img.resize((original_width, original_height), Image.Resampling.LANCZOS)
            
            # Sauvegarder
            output_path = self.output_dir / f"coloring_photo_gpt_image_1_{uuid.uuid4().hex[:8]}.png"
            generated_img.save(output_path, 'PNG', optimize=True)
            print(f"[OK] Coloriage photo sauvegardé ({original_width}x{original_height}): {output_path.name}")
            
            # Nettoyer les fichiers temporaires
            temp_input_path.unlink(missing_ok=True)
            temp_mask_path.unlink(missing_ok=True)
            
            return str(output_path)
            
        except Exception as e:
            print(f"[ERROR] Erreur conversion photo avec gpt-image-1-mini: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def generate_coloring_from_photo(
        self, 
        photo_path: str,
        custom_prompt: Optional[str] = None,
        with_colored_model: bool = True,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convertit une photo en coloriage avec gpt-image-1-mini images.edit
        
        Args:
            photo_path: Chemin vers la photo
            custom_prompt: Prompt personnalisé optionnel (non utilisé pour l'instant)
            with_colored_model: Si True, inclut un modèle coloré en coin
        
        Returns:
            Dict avec le résultat
        """
        try:
            print(f"[COLORING PHOTO] Conversion avec gpt-image-1-mini images.edit: {photo_path}")
            
            # Utiliser gpt-image-1-mini images.edit pour transformer la photo en coloriage
            coloring_path_str = await self._convert_photo_to_coloring_with_gpt_image_1(
                photo_path,
                with_colored_model
            )
            
            if not coloring_path_str:
                raise Exception("Échec de la génération gpt-image-1-mini")
            
            # Convertir en Path
            coloring_path = Path(coloring_path_str)
            
            # 📤 Upload OBLIGATOIRE vers Supabase Storage
            storage_service = get_storage_service()
            if not storage_service:
                raise Exception("Service Supabase Storage non disponible")

            if not user_id:
                raise Exception("user_id requis pour l'upload Supabase Storage")

            upload_result = await storage_service.upload_file(
                file_path=str(coloring_path),
                user_id=user_id,
                content_type="coloring",
                custom_filename=coloring_path.name
            )

            if not upload_result["success"]:
                raise Exception(f"Échec upload Supabase Storage: {upload_result.get('error', 'Erreur inconnue')}")

            image_url = upload_result["signed_url"]
            print(f"✅ Image uploadée vers Supabase Storage: {image_url[:50]}...")
            
            # Construire la réponse
            result = {
                "success": True,
                "source_photo": photo_path,
                "images": [{
                    "image_url": image_url,
                    "source": "gpt-image-1-mini (images.edit)"
                }],
                "total_images": 1,
                "metadata": {
                    "source_photo": photo_path,
                    "method": "gpt-image-1-mini images.edit",
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-image-1-mini",
                    "with_colored_model": with_colored_model
                }
            }
            
            print(f"[OK] Coloriage photo généré avec succès (gpt-image-1-mini images.edit): {coloring_path.name}")
            return result
            
        except Exception as e:
            print(f"[ERROR] Erreur conversion photo: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "images": []
            }
    
    async def _edit_photo_to_coloring_direct(
        self,
        photo_path: str,
        custom_prompt: Optional[str] = None,
        with_colored_model: bool = True
    ) -> Optional[str]:
        """
        Édite directement une photo en coloriage avec gemini-3-pro-image-preview (IMAGE-TO-IMAGE)
        CETTE MÉTHODE MAXIMISE LA RESSEMBLANCE en envoyant directement l'image
        
        Args:
            photo_path: Chemin vers la photo
            custom_prompt: Prompt personnalisé optionnel
            with_colored_model: Si True, inclut un modèle coloré
        
        Returns:
            Chemin local de l'image générée
        """
        try:
            # Construire le prompt
            if custom_prompt:
                final_prompt = custom_prompt
            else:
                final_prompt = self.edit_prompt_with_model if with_colored_model else self.edit_prompt_without_model
            
            print(f"[PROMPT IMAGE-TO-IMAGE] {final_prompt[:100]}...")
            
            # Déterminer l'extension et le nom de fichier
            photo_path_obj = Path(photo_path)
            filename = photo_path_obj.name
            
            print(f"[FILE] Ouverture image: {filename}")
            
            # Détecter les dimensions originales de l'image
            input_img = Image.open(photo_path)
            original_width, original_height = input_img.size
            aspect_ratio = original_width / original_height
            print(f"[DIMENSIONS] Image originale: {original_width}x{original_height} (ratio: {aspect_ratio:.2f})")
            
            print(f"[API] Appel Gemini gemini-3-pro-image-preview avec photo...")
            
            # Appeler Gemini avec image-to-image (texte et image vers image)
            response = self.gemini_client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[final_prompt, input_img]
            )
            
            print(f"[RESPONSE] Reponse recue de gemini-3-pro-image-preview")
            
            # Vérifier prompt_feedback pour voir s'il y a un blocage
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                if hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                    block_reason = response.prompt_feedback.block_reason
                    block_message = getattr(response.prompt_feedback, 'block_reason_message', None)
                    print(f"[ERROR] Génération bloquée par Gemini! Reason: {block_reason}, Message: {block_message}")
                    raise Exception(f"Génération bloquée par Gemini (sécurité): {block_reason}. Message: {block_message}")
            
            # Gemini retourne les images dans response.candidates[0].content.parts
            image_data = None
            if hasattr(response, 'candidates') and response.candidates is not None and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data is not None:
                            # Debug: afficher la structure
                            print(f"[DEBUG] inline_data type: {type(part.inline_data)}")
                            inline_attrs = [attr for attr in dir(part.inline_data) if not attr.startswith('_')]
                            print(f"[DEBUG] inline_data attributes: {inline_attrs}")
                            
                            # Essayer différentes méthodes d'accès aux données
                            if hasattr(part.inline_data, 'data'):
                                data = part.inline_data.data
                                print(f"[DEBUG] data type: {type(data)}, length: {len(data) if isinstance(data, (str, bytes)) else 'N/A'}")
                                
                                # Si c'est une string, c'est probablement du base64
                                if isinstance(data, str):
                                    try:
                                        image_data = base64.b64decode(data)
                                        print(f"[DEBUG] Decode base64 string: {len(image_data)} bytes")
                                    except Exception as e:
                                        print(f"[ERROR] Erreur decode base64: {e}")
                                        continue
                                elif isinstance(data, bytes):
                                    image_data = data
                                    print(f"[DEBUG] Data already bytes: {len(image_data)} bytes")
                                else:
                                    # Essayer de convertir en string puis décoder
                                    try:
                                        data_str = str(data)
                                        image_data = base64.b64decode(data_str)
                                        print(f"[DEBUG] Converted to string then decoded: {len(image_data)} bytes")
                                    except Exception as e:
                                        print(f"[ERROR] Impossible de decoder les donnees: {e}")
                                        continue
                                
                                # Vérifier que les données sont valides
                                if image_data:
                                    try:
                                        test_img = Image.open(io.BytesIO(image_data))
                                        print(f"[DEBUG] Image valide: {test_img.size}")
                                        break
                                    except Exception as e:
                                        print(f"[ERROR] Donnees decodees ne sont pas une image valide: {e}")
                                        image_data = None
                                        continue
                        elif hasattr(part, 'text') and part.text:
                            print(f"[TEXT] {part.text[:100]}...")
            
            if image_data:
                # Charger l'image générée
                generated_img = Image.open(io.BytesIO(image_data))
                generated_width, generated_height = generated_img.size
                generated_ratio = generated_width / generated_height
                
                print(f"[GENERATED] Image generee: {generated_width}x{generated_height} (ratio: {generated_ratio:.2f})")
                print(f"[TARGET] Redimensionnement vers: {original_width}x{original_height} (ratio: {aspect_ratio:.2f})")
                
                # Déterminer la taille finale (au minimum 1536x1536 pour éviter les coupures)
                min_size = 1536
                if original_width < min_size or original_height < min_size:
                    # Si l'image originale est petite, utiliser une taille carrée plus grande
                    final_width = final_height = min_size
                    print(f"[SMALL] Image originale petite ({original_width}x{original_height}), utilisation taille minimale {min_size}x{min_size}")
                else:
                    final_width, final_height = original_width, original_height

                # Vérifier si les ratios sont similaires (tolérance de 5%)
                target_ratio = final_width / final_height
                ratio_diff = abs(generated_ratio - target_ratio) / target_ratio
                if ratio_diff > 0.05:
                    print(f"[WARNING] Difference de ratio detectee: {ratio_diff*100:.1f}%")
                    # Adapter en préservant le ratio cible et en centrant
                    if target_ratio > generated_ratio:
                        # Image cible plus large -> adapter la largeur
                        new_width = final_width
                        new_height = int(final_width / generated_ratio)
                    else:
                        # Image cible plus haute -> adapter la hauteur
                        new_height = final_height
                        new_width = int(final_height * generated_ratio)

                    # Redimensionner avec le ratio préservé
                    temp_resized = generated_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Créer une image blanche aux dimensions finales
                    final_img = Image.new('RGB', (final_width, final_height), 'white')

                    # Centrer l'image redimensionnée
                    x_offset = (final_width - new_width) // 2
                    y_offset = (final_height - new_height) // 2
                    final_img.paste(temp_resized, (x_offset, y_offset))
                    print(f"[ADJUSTED] Image centree avec ratio preserve: {new_width}x{new_height} -> {final_width}x{final_height}")
                else:
                    # Ratios similaires -> redimensionnement direct
                    final_img = generated_img.resize((final_width, final_height), Image.Resampling.LANCZOS)
                    print(f"[RESIZED] Redimensionnement direct: {generated_width}x{generated_height} -> {final_width}x{final_height}")

                # Sauvegarder avec les dimensions finales
                output_path = self.output_dir / f"coloring_photo_direct_{uuid.uuid4().hex[:8]}.png"
                final_img.save(output_path, 'PNG', optimize=True)
                print(f"[OK] Coloriage photo sauvegarde ({final_width}x{final_height}): {output_path.name}")
                
                return str(output_path)
            else:
                print(f"[ERROR] Aucune image trouvée dans la réponse")
                raise Exception("Format de reponse gemini-2.5-flash-image inattendu - aucune image trouvée")
            
        except Exception as e:
            print(f"[ERROR] Erreur edition image-to-image: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _generate_coloring_with_gpt_image_1(
        self, 
        subject: str,
        custom_prompt: Optional[str] = None,
        with_colored_model: bool = True
    ) -> Optional[str]:
        """
        Génère un coloriage avec gemini-2.5-flash-image (TEXT-TO-IMAGE)
        Utilisé pour la génération par thème
        
        Args:
            subject: Description du sujet
            custom_prompt: Prompt personnalisé optionnel
            with_colored_model: Si True, inclut un modèle coloré en coin
        
        Returns:
            Chemin local de l'image générée
        """
        try:
            # Construire le prompt final
            if custom_prompt:
                final_prompt = custom_prompt
            else:
                prompt_template = self.coloring_prompt_with_model if with_colored_model else self.coloring_prompt_without_model
                final_prompt = prompt_template.format(subject=subject)
            
            print(f"[PROMPT TEXT-TO-IMAGE] {final_prompt[:150]}...")
            
            # Appeler Gemini avec text-to-image
            print(f"[API] Appel Gemini gemini-2.5-flash-image...")
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[final_prompt]
            )
            
            print(f"[RESPONSE] Reponse recue de gemini-2.5-flash-image")
            
            # Gemini retourne les images dans response.candidates[0].content.parts
            image_data = None
            if hasattr(response, 'candidates') and response.candidates is not None and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data is not None:
                            # Debug: afficher la structure
                            print(f"[DEBUG] inline_data type: {type(part.inline_data)}")
                            inline_attrs = [attr for attr in dir(part.inline_data) if not attr.startswith('_')]
                            print(f"[DEBUG] inline_data attributes: {inline_attrs}")
                            
                            # Essayer différentes méthodes d'accès aux données
                            if hasattr(part.inline_data, 'data'):
                                data = part.inline_data.data
                                print(f"[DEBUG] data type: {type(data)}, length: {len(data) if isinstance(data, (str, bytes)) else 'N/A'}")
                                
                                # Si c'est une string, c'est probablement du base64
                                if isinstance(data, str):
                                    try:
                                        image_data = base64.b64decode(data)
                                        print(f"[DEBUG] Decode base64 string: {len(image_data)} bytes")
                                    except Exception as e:
                                        print(f"[ERROR] Erreur decode base64: {e}")
                                        continue
                                elif isinstance(data, bytes):
                                    image_data = data
                                    print(f"[DEBUG] Data already bytes: {len(image_data)} bytes")
                                else:
                                    # Essayer de convertir en string puis décoder
                                    try:
                                        data_str = str(data)
                                        image_data = base64.b64decode(data_str)
                                        print(f"[DEBUG] Converted to string then decoded: {len(image_data)} bytes")
                                    except Exception as e:
                                        print(f"[ERROR] Impossible de decoder les donnees: {e}")
                                        continue
                                
                                # Vérifier que les données sont valides
                                if image_data:
                                    try:
                                        test_img = Image.open(io.BytesIO(image_data))
                                        print(f"[DEBUG] Image valide: {test_img.size}")
                                        break
                                    except Exception as e:
                                        print(f"[ERROR] Donnees decodees ne sont pas une image valide: {e}")
                                        image_data = None
                                        continue
                        elif hasattr(part, 'text') and part.text:
                            print(f"[TEXT] {part.text[:100]}...")
            
            if not image_data:
                # Debug: inspecter la réponse complète
                print(f"[ERROR] Aucune image trouvée dans la réponse")
                print(f"[DEBUG] Response type: {type(response)}")
                print(f"[DEBUG] Response has candidates: {hasattr(response, 'candidates')}")
                if hasattr(response, 'candidates'):
                    print(f"[DEBUG] Candidates value: {response.candidates}")
                    print(f"[DEBUG] Candidates is None: {response.candidates is None}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"[DEBUG] Prompt feedback: {response.prompt_feedback}")
                raise Exception("Format de reponse gemini-2.5-flash-image inattendu - aucune image trouvée")
            
            if image_data:
                # Charger l'image générée
                generated_img = Image.open(io.BytesIO(image_data))
                print(f"[OK] Image generee recue ({len(image_data)} bytes)")
                print(f"[ORIGINAL] Dimensions generees: {generated_img.size}")

                # Garder les dimensions naturelles de l'image générée par l'API
                output_path = self.output_dir / f"coloring_theme_{uuid.uuid4().hex[:8]}.png"
                generated_img.save(output_path, 'PNG', optimize=True)
                print(f"[OK] Coloriage theme sauvegarde ({generated_img.size[0]}x{generated_img.size[1]}): {output_path.name}")

                return str(output_path)
            else:
                print(f"[ERROR] Aucune image trouvée dans la réponse")
                raise Exception("Format de reponse gemini-2.5-flash-image inattendu - aucune image trouvée")
            
        except Exception as e:
            print(f"[ERROR] Erreur generation text-to-image: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    async def generate_coloring_from_theme(self, theme: str, with_colored_model: bool = True, custom_prompt: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Génération de coloriage par thème (TEXT-TO-IMAGE classique)
        
        Args:
            theme: Thème du coloriage
            with_colored_model: Si True, inclut un modèle coloré en coin
            custom_prompt: Prompt personnalisé optionnel (prioritaire sur le thème)
        
        Returns:
            Dict avec le résultat
        """
        try:
            if custom_prompt:
                print(f"[COLORING THEME] Generation personnalisee (text-to-image): {custom_prompt}")
            else:
                print(f"[COLORING THEME] Generation par theme (text-to-image): {theme}")
            
            # Créer une description basée sur le thème
            theme_descriptions = {
                'animaux': "A cute friendly cat playing in a meadow with flowers",
                'animals': "A happy dog playing with a ball in a park",
                'dinosaures': "A friendly smiling T-Rex dinosaur in a prehistoric forest",
                'dinosaurs': "A friendly smiling T-Rex dinosaur in a prehistoric forest",
                'dragons': "A cute friendly dragon with wings playing in a magical forest",
                'espace': "An astronaut floating in space near colorful planets and stars",
                'space': "An astronaut floating in space near colorful planets and stars",
                'fees': "A beautiful fairy with butterfly wings holding a magic wand with sparkles",
                'fairies': "A beautiful fairy with butterfly wings holding a magic wand with sparkles",
                'nature': "Beautiful sunflowers in a garden with butterflies",
                'princesses': "A beautiful princess with a crown and elegant dress in a castle",
                'princess': "A beautiful princess with a crown and elegant dress in a castle",
                'pirates': "A friendly pirate with a treasure map on a pirate ship",
                'mermaids': "A beautiful mermaid with flowing hair swimming near coral reefs",
                'sirènes': "A beautiful mermaid with flowing hair swimming near coral reefs",
                'vehicules': "A colorful race car speeding on a track",
                'vehicles': "A colorful race car speeding on a track",
                'ocean': "Colorful fish swimming in a coral reef with sea creatures",
                'océan': "Colorful fish swimming in a coral reef with sea creatures",
                'farm': "Happy farm animals including cows, pigs, chickens and a red barn",
                'ferme': "Happy farm animals including cows, pigs, chickens and a red barn",
                'seasons': "A beautiful tree showing all four seasons with falling leaves",
                'saisons': "A beautiful tree showing all four seasons with falling leaves",
                'sports': "Children playing soccer in a sunny park",
                'fruits': "Smiling fruits including apples, bananas, and strawberries",
                'superheroes': "A brave superhero flying through the sky with a cape",
                'super-héros': "A brave superhero flying through the sky with a cape",
                'robots': "A friendly futuristic robot with mechanical parts",
            }
            
            # Initialiser la description
            description = None
            
            # Si un prompt personnalisé est fourni, l'utiliser directement
            if custom_prompt:
                description = custom_prompt  # Utiliser le prompt personnalisé comme description
                # Créer un prompt complet avec le style de coloriage
                if with_colored_model:
                    full_custom_prompt = f"""A black and white line drawing coloring illustration of: {custom_prompt}

The illustration should be:
- Suitable for direct printing on standard size (8.5x11 inch) paper
- Fresh and simple style with clear, smooth black outline lines
- No shadows, grayscale, or color filling
- Pure white background for easy coloring
- Include a small colored reference version in the lower right corner (10-15% of total size)
- Suitable for children aged 6-9 years old"""
                else:
                    full_custom_prompt = f"""A black and white line drawing coloring illustration of: {custom_prompt}

The illustration should be:
- Suitable for direct printing on standard size (8.5x11 inch) paper
- Fresh and simple style with clear, smooth black outline lines
- No shadows, grayscale, or color filling
- Pure white background for easy coloring
- NO colored reference image
- Suitable for children aged 6-9 years old"""
                
                print(f"[CUSTOM PROMPT] {full_custom_prompt[:150]}...")
                coloring_path_str = await self._generate_coloring_with_gpt_image_1("", full_custom_prompt, with_colored_model)
            else:
                # Obtenir la description basée sur le thème
                description = theme_descriptions.get(theme.lower(), f"A {theme} scene suitable for children coloring")
                print(f"[DESCRIPTION] {description}")
                
                # Générer avec gpt-image-1-mini (text-to-image)
                coloring_path_str = await self._generate_coloring_with_gpt_image_1(description, None, with_colored_model)
            
            if not coloring_path_str:
                raise Exception("Echec de la generation gpt-image-1-mini - chemin vide")
            
            print(f"[OK] Chemin gpt-image-1-mini recu: {coloring_path_str}")
            
            # Convertir en Path
            coloring_path = Path(coloring_path_str)
            
            # 📤 Upload OBLIGATOIRE vers Supabase Storage
            storage_service = get_storage_service()
            if not storage_service:
                raise Exception("Service Supabase Storage non disponible")

            if not user_id:
                raise Exception("user_id requis pour l'upload Supabase Storage")

            upload_result = await storage_service.upload_file(
                file_path=str(coloring_path),
                user_id=user_id,
                content_type="coloring",
                custom_filename=coloring_path.name
            )

            if not upload_result["success"]:
                raise Exception(f"Échec upload Supabase Storage: {upload_result.get('error', 'Erreur inconnue')}")

            image_url = upload_result["signed_url"]
            print(f"✅ Image uploadée vers Supabase Storage: {image_url[:50]}...")
            
            # Construire la réponse
            result = {
                "success": True,
                "theme": theme,
                "images": [{
                    "image_url": image_url,
                    "theme": theme,
                    "source": "gpt-image-1-mini (text-to-image)"
                }],
                "total_images": 1,
                "metadata": {
                    "theme": theme,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-image-1-mini",
                    "method": "text-to-image",
                    "with_colored_model": with_colored_model
                }
            }
            
            print(f"[OK] Coloriage theme genere avec succes: {coloring_path.name}")
            return result
            
        except Exception as e:
            print(f"[ERROR] Erreur generation theme: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "images": []
            }
    
    # Méthodes de compatibilité
    async def generate_coloring_pages(self, theme: str) -> Dict[str, Any]:
        """Alias pour compatibilité"""
        return await self.generate_coloring_from_theme(theme)
    
    async def generate_coloring(self, theme: str) -> Dict[str, Any]:
        """Alias pour compatibilité"""
        return await self.generate_coloring_from_theme(theme)


# Instance globale - initialisation paresseuse gérée dans main.py
coloring_generator = None
