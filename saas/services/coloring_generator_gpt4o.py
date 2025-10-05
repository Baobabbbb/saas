"""
Service de génération de coloriages avec GPT-4o-mini + DALL-E 3
Transforme des thèmes ou des photos en pages de coloriage noir et blanc
Utilise gpt-4o-mini pour l'analyse et DALL-E 3 pour la génération
Avec un prompt optimisé pour des coloriages de qualité professionnelle
Note: gpt-image-1 nécessite une organisation OpenAI vérifiée
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
    Générateur de coloriages avec GPT-4o-mini + DALL-E 3
    Supporte la génération par thème et la conversion de photos
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
                print("❌ ERREUR: OPENAI_API_KEY non trouvée dans .env")
                raise ValueError("OPENAI_API_KEY manquante")
            
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # URL de base pour les images (production Railway ou local)
            self.base_url = os.getenv("BASE_URL", "https://herbbie.com")
            
            # Prompt spécial pour les coloriages (fourni par l'utilisateur)
            self.coloring_prompt_template = """A black and white line drawing coloring illustration, suitable for direct printing on standard size (8.5x11 inch) paper, without paper borders. The overall illustration style is fresh and simple, using clear and smooth black outline lines, without shadows, grayscale, or color filling, with a pure white background for easy coloring. [At the same time, for the convenience of users who are not good at coloring, please generate a complete colored version in the lower right corner as a small image for reference] Suitable for: [6-9 year old children]

Subject: {subject}"""
            
            print(f"✅ ColoringGeneratorGPT4o initialisé")
            print(f"   - Modèle analyse: gpt-4o-mini")
            print(f"   - Modèle génération: DALL-E 3")
            print(f"   - API Key présente: Oui")
        except Exception as e:
            print(f"❌ Erreur initialisation ColoringGeneratorGPT4o: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def generate_coloring_from_photo(
        self, 
        photo_path: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convertit une photo en coloriage avec GPT-4o-mini + DALL-E 3
        
        Args:
            photo_path: Chemin vers la photo
            custom_prompt: Prompt personnalisé optionnel
        
        Returns:
            Dict avec le résultat
        """
        try:
            print(f"🎨 Conversion photo en coloriage: {photo_path}")
            
            # 1. Analyser la photo avec GPT-4o-mini pour extraire une description
            print(f"🔍 Analyse de la photo avec GPT-4o-mini...")
            description = await self._analyze_photo_with_gpt4o(photo_path)
            print(f"📝 Description extraite: {description[:100]}...")
            
            # 2. Générer le coloriage avec DALL-E 3
            print(f"🎨 Génération du coloriage avec DALL-E 3...")
            coloring_url = await self._generate_coloring_with_dalle3(description, custom_prompt)
            
            if not coloring_url:
                raise Exception("Échec de la génération DALL-E 3")
            
            # 3. Télécharger et sauvegarder l'image
            coloring_path = await self._download_and_save_image(coloring_url)
            
            # 4. Construire la réponse
            result = {
                "success": True,
                "source_photo": photo_path,
                "description": description,
                "images": [{
                    "image_url": f"{self.base_url}/static/coloring/{coloring_path.name}",
                    "source": "gpt4o-mini + dalle3"
                }],
                "total_images": 1,
                "metadata": {
                    "source_photo": photo_path,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-4o-mini + dalle3"
                }
            }
            
            print(f"✅ Coloriage généré avec succès: {coloring_path.name}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur conversion photo: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "images": []
            }
    
    async def _analyze_photo_with_gpt4o(self, photo_path: str) -> str:
        """
        Analyse une photo avec GPT-4o-mini pour extraire une description détaillée
        
        Args:
            photo_path: Chemin vers la photo
        
        Returns:
            Description textuelle de la photo
        """
        try:
            # Lire et encoder l'image en base64
            with open(photo_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Déterminer le type MIME
            extension = Path(photo_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            mime_type = mime_types.get(extension, 'image/jpeg')
            
            # Appeler GPT-4o-mini avec vision
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this photo in detail and describe it for creating a coloring page. 
Focus on:
- Main subject (person, animal, object)
- Pose and expression
- Key visual elements
- Setting/background
- Important details to preserve

Provide a clear, concise description (2-3 sentences) that captures the essence of the image for a coloring book illustration suitable for 6-9 year old children."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }],
                max_tokens=300
            )
            
            description = response.choices[0].message.content
            return description
            
        except Exception as e:
            print(f"❌ Erreur analyse GPT-4o-mini: {e}")
            raise
    
    async def _generate_coloring_with_dalle3(
        self, 
        subject: str,
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Génère un coloriage avec DALL-E 3
        
        Args:
            subject: Description du sujet
            custom_prompt: Prompt personnalisé optionnel
        
        Returns:
            URL de l'image générée
        """
        try:
            # Construire le prompt final
            if custom_prompt:
                final_prompt = custom_prompt
            else:
                final_prompt = self.coloring_prompt_template.format(subject=subject)
            
            print(f"📝 Prompt DALL-E 3: {final_prompt[:150]}...")
            
            # Appeler DALL-E 3 (modèle OpenAI officiel pour génération d'images)
            # Note: gpt-image-1 nécessite une organisation vérifiée
            print(f"📡 Appel API OpenAI DALL-E 3...")
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=final_prompt,
                size="1024x1024",
                quality="standard",  # DALL-E 3 accepte: standard, hd
                n=1
            )
            
            print(f"📥 Réponse reçue de DALL-E 3")
            image_url = response.data[0].url
            print(f"✅ Image DALL-E 3 générée: {image_url[:50]}...")
            
            return image_url
            
        except Exception as e:
            print(f"❌ Erreur génération DALL-E 3: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _download_and_save_image(self, image_url: str) -> Path:
        """
        Télécharge et sauvegarde une image depuis une URL
        
        Args:
            image_url: URL de l'image
        
        Returns:
            Path vers l'image sauvegardée
        """
        try:
            # Télécharger l'image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Ouvrir avec PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Sauvegarder
            output_path = self.output_dir / f"coloring_gpt4o_{uuid.uuid4().hex[:8]}.png"
            image.save(output_path, 'PNG', optimize=True)
            
            print(f"✅ Image sauvegardée: {output_path.name}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur téléchargement image: {e}")
            raise
    
    async def generate_coloring_from_theme(self, theme: str) -> Dict[str, Any]:
        """
        Génération de coloriage par thème
        
        Args:
            theme: Thème du coloriage (ex: "animaux", "espace", "dinosaures")
        
        Returns:
            Dict avec le résultat
        """
        try:
            print(f"🎨 Génération coloriage par thème: {theme}")
            
            # Créer une description basée sur le thème
            theme_descriptions = {
                'animaux': "A cute friendly cat playing in a meadow with flowers",
                'animals': "A happy dog playing with a ball in a park",
                'dinosaures': "A friendly smiling T-Rex dinosaur in a prehistoric forest",
                'dinosaurs': "A friendly smiling T-Rex dinosaur in a prehistoric forest",
                'espace': "An astronaut floating in space near colorful planets and stars",
                'space': "An astronaut floating in space near colorful planets and stars",
                'fees': "A beautiful fairy with butterfly wings holding a magic wand with sparkles",
                'fairies': "A beautiful fairy with butterfly wings holding a magic wand with sparkles",
                'nature': "Beautiful sunflowers in a garden with butterflies",
                'princesses': "A beautiful princess with a crown and elegant dress in a castle",
                'pirates': "A friendly pirate with a treasure map on a ship",
                'vehicules': "A colorful race car speeding on a track",
                'vehicles': "A colorful race car speeding on a track",
                'ocean': "Colorful fish swimming in a coral reef with sea creatures",
                'foret': "A magical forest with tall trees, mushrooms and woodland animals",
                'forest': "A magical forest with tall trees, mushrooms and woodland animals",
            }
            
            # Obtenir la description ou utiliser le thème directement
            description = theme_descriptions.get(theme.lower(), f"A {theme} scene")
            print(f"📝 Description: {description}")
            
            # Générer avec DALL-E 3
            print(f"🎨 Appel DALL-E 3...")
            coloring_url = await self._generate_coloring_with_dalle3(description)
            
            if not coloring_url:
                raise Exception("Échec de la génération DALL-E 3 - URL vide")
            
            print(f"✅ URL DALL-E 3 reçue: {coloring_url[:50]}...")
            
            # Télécharger et sauvegarder
            print(f"📥 Téléchargement de l'image...")
            coloring_path = await self._download_and_save_image(coloring_url)
            
            # Construire la réponse
            result = {
                "success": True,
                "theme": theme,
                "images": [{
                    "image_url": f"{self.base_url}/static/coloring/{coloring_path.name}",
                    "theme": theme,
                    "source": "gpt4o-mini + dalle3"
                }],
                "total_images": 1,
                "metadata": {
                    "theme": theme,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-4o-mini + dalle3"
                }
            }
            
            print(f"✅ Coloriage thème généré avec succès: {coloring_path.name}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération thème: {e}")
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
