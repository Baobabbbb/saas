"""
Service de génération de coloriages avec gemini-3-pro-image-preview
- Image-to-image direct pour les photos uploadées (meilleure ressemblance)
- Text-to-image pour les thèmes prédéfinis
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
    Générateur de coloriages avec gemini-3-pro-image-preview
    - Image-to-image pour photos uploadées
    - Text-to-image pour thèmes
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
            self.edit_prompt_with_model = """Transform this photo into a black and white line drawing coloring page with MAXIMUM FIDELITY to the original image.

CRITICAL REQUIREMENTS FOR HIGH RESEMBLANCE:
- Preserve EXACTLY the same facial features, expressions, and proportions as in the photo
- Keep the EXACT same body pose, limb positions, and orientation
- Maintain the EXACT same clothing details, patterns, accessories, and textures
- Preserve the EXACT same background elements and spatial composition
- Keep the EXACT same viewing angle and perspective
- Maintain PRECISE proportions and scale relationships between all elements
- Replicate the EXACT same hairstyle, hair length, and hair details
- Keep the EXACT same object positions and arrangements

STYLE REQUIREMENTS:
- Convert to clear, smooth black outline lines only
- Pure white background
- No shadows, grayscale, or color filling
- Suitable for printing on 8.5x11 inch paper
- Add a small colored reference version in the lower right corner (10-15% of total size)
- Line weight should be consistent and appropriate for coloring
- Suitable for 6-9 year old children

ABSOLUTE PRIORITY: Maximum fidelity to the original photo. Every visual detail, proportion, facial feature, pose, and composition element must be preserved as accurately as possible. The coloring page MUST look like a line drawing version of THIS EXACT photo."""

            self.edit_prompt_without_model = """Transform this photo into a black and white line drawing coloring page with MAXIMUM FIDELITY to the original image.

CRITICAL REQUIREMENTS FOR HIGH RESEMBLANCE:
- Preserve EXACTLY the same facial features, expressions, and proportions as in the photo
- Keep the EXACT same body pose, limb positions, and orientation
- Maintain the EXACT same clothing details, patterns, accessories, and textures
- Preserve the EXACT same background elements and spatial composition
- Keep the EXACT same viewing angle and perspective
- Maintain PRECISE proportions and scale relationships between all elements
- Replicate the EXACT same hairstyle, hair length, and hair details
- Keep the EXACT same object positions and arrangements

STYLE REQUIREMENTS:
- Convert to clear, smooth black outline lines only
- Pure white background
- No shadows, grayscale, or color filling
- Suitable for printing on 8.5x11 inch paper
- NO colored reference image
- Line weight should be consistent and appropriate for coloring
- Suitable for 6-9 year old children

ABSOLUTE PRIORITY: Maximum fidelity to the original photo. Every visual detail, proportion, facial feature, pose, and composition element must be preserved as accurately as possible. The coloring page MUST look like a line drawing version of THIS EXACT photo."""
            
            # Prompts pour la génération par thème (TEXT-TO-IMAGE)
            self.coloring_prompt_with_model = """A black and white line drawing coloring illustration, suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders. The overall illustration style is fresh and simple, using clear and smooth black outline lines, without shadows, grayscale, or color filling, with a pure white background for easy coloring. [At the same time, for the convenience of users who are not good at coloring, please generate a complete colored version in the lower right corner as a small image for reference] Suitable for: [6-9 year old children]

Subject: {subject}"""
            
            self.coloring_prompt_without_model = """A black and white line drawing coloring illustration, suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders. The overall illustration style is fresh and simple, using clear and smooth black outline lines, without shadows, grayscale, or color filling, with a pure white background for easy coloring. NO colored reference image. Suitable for: [6-9 year old children]

Subject: {subject}"""
            
            # Initialisation silencieuse
        except Exception as e:
            # Erreur silencieuse lors de l'initialisation
            raise
    
    async def generate_coloring_from_photo(
        self, 
        photo_path: str,
        custom_prompt: Optional[str] = None,
        with_colored_model: bool = True,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convertit une photo en coloriage avec gpt-image-1-mini IMAGE-TO-IMAGE DIRECT
        Cette méthode utilise l'édition d'image directe pour maximiser la ressemblance
        
        Args:
            photo_path: Chemin vers la photo
            custom_prompt: Prompt personnalisé optionnel
            with_colored_model: Si True, inclut un modèle coloré en coin
        
        Returns:
            Dict avec le résultat
        """
        try:
            print(f"[COLORING PHOTO] Conversion IMAGE-TO-IMAGE: {photo_path}")
            
            # Utiliser l'édition d'image DIRECTE avec gpt-image-1-mini (IMAGE-TO-IMAGE)
            print(f"[IMAGE-TO-IMAGE] Transformation directe avec gpt-image-1-mini edit...")
            coloring_path_str = await self._edit_photo_to_coloring_direct(
                photo_path, 
                custom_prompt, 
                with_colored_model
            )
            
            if not coloring_path_str:
                raise Exception("Echec de la generation gpt-image-1-mini (image-to-image)")
            
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
                    "source": "gpt-image-1-mini (image-to-image direct)"
                }],
                "total_images": 1,
                "metadata": {
                    "source_photo": photo_path,
                    "method": "image-to-image direct editing",
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-image-1-mini",
                    "with_colored_model": with_colored_model
                }
            }
            
            print(f"[OK] Coloriage photo genere avec succes (image-to-image): {coloring_path.name}")
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
            
            # Gemini retourne les images dans response.parts
            image_data = None
            for part in response.parts:
                if part.inline_data is not None:
                    # Récupérer l'image depuis inline_data
                    generated_img = part.as_image()
                    # Convertir PIL Image en bytes
                    img_byte_arr = io.BytesIO()
                    generated_img.save(img_byte_arr, format='PNG')
                    image_data = img_byte_arr.getvalue()
                    break
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
                raise Exception("Format de reponse gemini-3-pro-image-preview inattendu - aucune image trouvée")
            
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
        Génère un coloriage avec gemini-3-pro-image-preview (TEXT-TO-IMAGE)
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
            print(f"[API] Appel Gemini gemini-3-pro-image-preview...")
            response = self.gemini_client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[final_prompt]
            )
            
            print(f"[RESPONSE] Reponse recue de gemini-3-pro-image-preview")
            
            # Gemini retourne les images dans response.parts
            image_data = None
            for part in response.parts:
                if part.inline_data is not None:
                    # Récupérer l'image depuis inline_data
                    generated_img = part.as_image()
                    # Convertir PIL Image en bytes
                    img_byte_arr = io.BytesIO()
                    generated_img.save(img_byte_arr, format='PNG')
                    image_data = img_byte_arr.getvalue()
                    break
                elif hasattr(part, 'text') and part.text:
                    print(f"[TEXT] {part.text[:100]}...")
            
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
                raise Exception("Format de reponse gemini-3-pro-image-preview inattendu - aucune image trouvée")
            
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
