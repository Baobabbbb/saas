"""
Service de génération de coloriages avec gpt-image-1
- Image-to-image direct pour les photos uploadées (meilleure ressemblance)
- Text-to-image pour les thèmes prédéfinis
Organisation OpenAI vérifiée requise pour gpt-image-1
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
from dotenv import load_dotenv

load_dotenv()


class ColoringGeneratorGPT4o:
    """
    Générateur de coloriages avec gpt-image-1
    - Image-to-image pour photos uploadées
    - Text-to-image pour thèmes
    """
    
    def __init__(self):
        try:
            self.output_dir = Path("static/coloring")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self.upload_dir = Path("static/uploads/coloring")
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Configuration OpenAI
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("[ERROR] OPENAI_API_KEY non trouvee dans .env")
                raise ValueError("OPENAI_API_KEY manquante")
            
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # URL de base pour les images (production Railway ou local)
            self.base_url = os.getenv("BASE_URL", "https://herbbie.com")
            
            # Prompts pour l'édition d'image directe (IMAGE-TO-IMAGE pour photos)
            self.edit_prompt_with_model = """Transform this photo into a black and white line drawing coloring page while preserving EXACTLY the same composition, pose, proportions, and all visual details.

Requirements:
- Keep the EXACT same subject, pose, and positioning as the original photo
- Convert to clear, smooth black outline lines only
- Pure white background
- No shadows, grayscale, or color filling
- Suitable for printing on 8.5x11 inch paper
- Add a small colored reference version in the lower right corner
- Maintain all distinctive features and details from the original photo
- Suitable for 6-9 year old children

IMPORTANT: The coloring page must look as similar as possible to the original photo in terms of composition and details."""

            self.edit_prompt_without_model = """Transform this photo into a black and white line drawing coloring page while preserving EXACTLY the same composition, pose, proportions, and all visual details.

Requirements:
- Keep the EXACT same subject, pose, and positioning as the original photo
- Convert to clear, smooth black outline lines only
- Pure white background
- No shadows, grayscale, or color filling
- Suitable for printing on 8.5x11 inch paper
- NO colored reference image
- Maintain all distinctive features and details from the original photo
- Suitable for 6-9 year old children

IMPORTANT: The coloring page must look as similar as possible to the original photo in terms of composition and details."""
            
            # Prompts pour la génération par thème (TEXT-TO-IMAGE)
            self.coloring_prompt_with_model = """A black and white line drawing coloring illustration, suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders. The overall illustration style is fresh and simple, using clear and smooth black outline lines, without shadows, grayscale, or color filling, with a pure white background for easy coloring. [At the same time, for the convenience of users who are not good at coloring, please generate a complete colored version in the lower right corner as a small image for reference] Suitable for: [6-9 year old children]

Subject: {subject}"""
            
            self.coloring_prompt_without_model = """A black and white line drawing coloring illustration, suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders. The overall illustration style is fresh and simple, using clear and smooth black outline lines, without shadows, grayscale, or color filling, with a pure white background for easy coloring. NO colored reference image. Suitable for: [6-9 year old children]

Subject: {subject}"""
            
            print(f"OK: ColoringGeneratorGPT4o initialise")
            print(f"   - Photos: gpt-image-1 image-to-image (ressemblance maximale)")
            print(f"   - Themes: gpt-image-1 text-to-image")
            print(f"   - Quality: high")
            print(f"   - API Key presente: Oui")
        except Exception as e:
            print(f"ERREUR: Initialisation ColoringGeneratorGPT4o: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def generate_coloring_from_photo(
        self, 
        photo_path: str,
        custom_prompt: Optional[str] = None,
        with_colored_model: bool = True
    ) -> Dict[str, Any]:
        """
        Convertit une photo en coloriage avec gpt-image-1 IMAGE-TO-IMAGE DIRECT
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
            
            # Utiliser l'édition d'image DIRECTE avec gpt-image-1 (IMAGE-TO-IMAGE)
            print(f"[IMAGE-TO-IMAGE] Transformation directe avec gpt-image-1 edit...")
            coloring_path_str = await self._edit_photo_to_coloring_direct(
                photo_path, 
                custom_prompt, 
                with_colored_model
            )
            
            if not coloring_path_str:
                raise Exception("Echec de la generation gpt-image-1 (image-to-image)")
            
            # Convertir en Path
            coloring_path = Path(coloring_path_str)
            
            # Construire la réponse
            result = {
                "success": True,
                "source_photo": photo_path,
                "images": [{
                    "image_url": f"{self.base_url}/static/coloring/{coloring_path.name}",
                    "source": "gpt-image-1 (image-to-image direct)"
                }],
                "total_images": 1,
                "metadata": {
                    "source_photo": photo_path,
                    "method": "image-to-image direct editing",
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-image-1",
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
        Édite directement une photo en coloriage avec gpt-image-1 (IMAGE-TO-IMAGE)
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
            
            # Ouvrir l'image en mode binaire et créer un tuple (filename, file_data)
            with open(photo_path, "rb") as image_file:
                image_data = image_file.read()
            
            print(f"[API] Appel OpenAI images.edit avec photo ({len(image_data)} bytes)...")
            
            # Appeler gpt-image-1 avec images.edit (IMAGE-TO-IMAGE)
            # IMPORTANT: Passer un tuple (filename, file_data) pour que l'API détecte le MIME type
            response = await self.client.images.edit(
                model="gpt-image-1",
                image=(filename, image_data),  # Tuple (filename, data) pour détecter le MIME type
                prompt=final_prompt,
                size="1024x1024",
                n=1
            )
            
            print(f"[RESPONSE] Reponse recue de gpt-image-1 edit")
            
            # gpt-image-1 retourne base64
            if hasattr(response, 'data') and len(response.data) > 0:
                image_b64 = response.data[0].b64_json
                print(f"[OK] Image editee recue (base64: {len(image_b64)} bytes)")
                
                # Sauvegarder directement depuis base64
                image_bytes = base64.b64decode(image_b64)
                output_path = self.output_dir / f"coloring_photo_direct_{uuid.uuid4().hex[:8]}.png"
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                print(f"[OK] Coloriage photo sauvegarde: {output_path.name}")
                
                return str(output_path)
            else:
                print(f"[ERROR] Format de reponse inattendu")
                raise Exception("Format de reponse gpt-image-1 edit inattendu")
            
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
        Génère un coloriage avec gpt-image-1 (TEXT-TO-IMAGE)
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
            
            # Appeler gpt-image-1 avec qualité high
            print(f"[API] Appel OpenAI images.generate...")
            response = await self.client.images.generate(
                model="gpt-image-1",
                prompt=final_prompt,
                size="1024x1024",
                quality="high",
                n=1
            )
            
            print(f"[RESPONSE] Reponse recue de gpt-image-1 generate")
            
            # gpt-image-1 retourne base64
            if hasattr(response, 'data') and len(response.data) > 0:
                image_b64 = response.data[0].b64_json
                print(f"[OK] Image generee recue (base64: {len(image_b64)} bytes)")
                
                # Sauvegarder directement depuis base64
                image_bytes = base64.b64decode(image_b64)
                output_path = self.output_dir / f"coloring_theme_{uuid.uuid4().hex[:8]}.png"
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                print(f"[OK] Coloriage theme sauvegarde: {output_path.name}")
                
                return str(output_path)
            else:
                print(f"[ERROR] Format de reponse inattendu")
                raise Exception("Format de reponse gpt-image-1 generate inattendu")
            
        except Exception as e:
            print(f"[ERROR] Erreur generation text-to-image: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    async def generate_coloring_from_theme(self, theme: str, with_colored_model: bool = True) -> Dict[str, Any]:
        """
        Génération de coloriage par thème (TEXT-TO-IMAGE classique)
        
        Args:
            theme: Thème du coloriage
            with_colored_model: Si True, inclut un modèle coloré en coin
        
        Returns:
            Dict avec le résultat
        """
        try:
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
            
            # Obtenir la description ou utiliser le thème directement
            description = theme_descriptions.get(theme.lower(), f"A {theme} scene suitable for children coloring")
            print(f"[DESCRIPTION] {description}")
            
            # Générer avec gpt-image-1 (text-to-image)
            coloring_path_str = await self._generate_coloring_with_gpt_image_1(description, None, with_colored_model)
            
            if not coloring_path_str:
                raise Exception("Echec de la generation gpt-image-1 - chemin vide")
            
            print(f"[OK] Chemin gpt-image-1 recu: {coloring_path_str}")
            
            # Convertir en Path
            coloring_path = Path(coloring_path_str)
            
            # Construire la réponse
            result = {
                "success": True,
                "theme": theme,
                "images": [{
                    "image_url": f"{self.base_url}/static/coloring/{coloring_path.name}",
                    "theme": theme,
                    "source": "gpt-image-1 (text-to-image)"
                }],
                "total_images": 1,
                "metadata": {
                    "theme": theme,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-image-1",
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


# Instance globale
coloring_generator = ColoringGeneratorGPT4o()
