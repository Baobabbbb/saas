"""
Service de génération de coloriages avec Stable Diffusion 3 + ControlNet
Transforme n'importe quelle photo en page de coloriage noir et blanc
"""
import os
import uuid
import base64
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Literal
from PIL import Image, ImageEnhance, ImageOps
import io
import requests
from dotenv import load_dotenv
from services.supabase_storage import get_storage_service

load_dotenv()


class ColoringGeneratorSD3ControlNet:
    """
    Générateur de coloriages avec Stable Diffusion 3 et ControlNet
    Supporte Canny (détection contours) et Scribble (style croquis)
    """
    
    def __init__(self):
        self.output_dir = Path("static/coloring")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.upload_dir = Path("static/uploads/coloring")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.stability_key = os.getenv("STABILITY_API_KEY")
        
        # Vérification de la clé API
        if not self.stability_key:
            print("❌ ERREUR: STABILITY_API_KEY non trouvée dans .env")
            raise ValueError("STABILITY_API_KEY manquante")
        
        print(f"✅ Clé Stability AI détectée: {self.stability_key[:15]}...")
        
        # Configuration Stable Diffusion 3
        # Note: Utilisation de l'endpoint control/structure (ControlNet officiel)
        self.sd3_api_url = "https://api.stability.ai/v2beta/stable-image/control/structure"
        self.sd3_model = "sd3-medium"  # ou sd3-large
        
        # URL de base pour les images (production Railway ou local)
        self.base_url = os.getenv("BASE_URL", "https://herbbie.com")
        
        # Prompts optimisés pour coloriages
        self.base_prompt = """Convert this image into a black-and-white coloring book page. 
Clean outlines, simple cartoon-like drawing style, no shading, no gray areas, 
only black ink contours on white background. Suitable for kids to color. 
Keep the main subject recognizable and remove unnecessary background details."""
        
        self.negative_prompt = """no colors, no shading, no grey, no background clutter, 
no text, no logos, no watermarks, no realistic textures, no gradients, no shadows"""
        
        print(f"✅ ColoringGeneratorSD3ControlNet initialisé")
        print(f"   - Modèle: {self.sd3_model}")
        print(f"   - API: Stability AI Control Sketch")
    
    async def generate_coloring_from_photo(
        self, 
        photo_path: str,
        control_mode: Literal["canny", "scribble"] = "canny",
        control_strength: float = 0.7,
        custom_prompt: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convertit une photo en coloriage avec ControlNet
        
        Args:
            photo_path: Chemin vers la photo
            control_mode: "canny" (contours nets) ou "scribble" (style croquis)
            control_strength: Force du contrôle (0.5-1.0)
            custom_prompt: Prompt personnalisé optionnel
        
        Returns:
            Dict avec le résultat
        """
        try:
            print(f"🎨 Conversion photo en coloriage: {photo_path}")
            print(f"   - Mode ControlNet: {control_mode}")
            print(f"   - Force: {control_strength}")
            
            # 1. Charger et préparer la photo
            image = Image.open(photo_path)
            image = self._resize_image(image, max_size=1024)
            
            # 2. Appliquer ControlNet pour extraire les contours
            control_image = self._apply_controlnet(image, mode=control_mode)
            
            # 3. Sauvegarder l'image de contrôle (debug)
            control_path = self.output_dir / f"control_{uuid.uuid4().hex[:8]}.png"
            control_image.save(control_path)
            print(f"✅ Image de contrôle sauvegardée: {control_path.name}")
            
            # 4. Générer le coloriage avec SD3
            coloring_path = await self._generate_with_sd3_control(
                control_image=control_image,
                prompt=custom_prompt or self.base_prompt,
                control_strength=control_strength
            )
            
            if not coloring_path:
                raise Exception("Échec de la génération SD3")
            
            # 5. Post-traiter pour optimiser (noir/blanc pur)
            final_path = await self._post_process_coloring(coloring_path)
            
            # 📤 Upload vers Supabase Storage si user_id fourni
            storage_service = get_storage_service()
            if storage_service and user_id:
                upload_result = await storage_service.upload_file(
                    file_path=str(final_path),
                    user_id=user_id,
                    content_type="coloring",
                    custom_filename=final_path.name
                )
                
                if upload_result["success"]:
                    image_url = upload_result["signed_url"]
                    control_image_url = image_url  # Même fichier pour les deux
                    print(f"✅ Image uploadée vers Supabase Storage")
                else:
                    image_url = f"{self.base_url}/static/coloring/{final_path.name}"
                    control_image_url = f"{self.base_url}/static/coloring/{control_path.name}"
                    print(f"⚠️ Upload Supabase échoué, utilisation chemin local")
            else:
                image_url = f"{self.base_url}/static/coloring/{final_path.name}"
                control_image_url = f"{self.base_url}/static/coloring/{control_path.name}"
            
            # 6. Construire la réponse
            result = {
                "success": True,
                "source_photo": photo_path,
                "images": [{
                    "image_url": image_url,
                    "control_mode": control_mode,
                    "control_strength": control_strength,
                    "source": "sd3_controlnet"
                }],
                "control_image_url": control_image_url,
                "total_images": 1,
                "metadata": {
                    "source_photo": photo_path,
                    "control_mode": control_mode,
                    "control_strength": control_strength,
                    "created_at": datetime.now().isoformat(),
                    "model": "sd3-controlnet"
                }
            }
            
            print(f"✅ Coloriage généré avec succès: {final_path.name}")
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
    
    def _resize_image(self, image: Image.Image, max_size: int = 1024) -> Image.Image:
        """Redimensionner l'image tout en gardant le ratio"""
        width, height = image.size
        
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"📐 Image redimensionnée: {width}x{height} → {new_width}x{new_height}")
        
        return image
    
    def _apply_controlnet(
        self, 
        image: Image.Image, 
        mode: Literal["canny", "scribble"]
    ) -> Image.Image:
        """
        Applique ControlNet pour extraire les contours
        
        Args:
            image: Image PIL
            mode: "canny" ou "scribble"
        
        Returns:
            Image PIL avec contours extraits
        """
        print(f"🔍 Application ControlNet ({mode})...")
        
        # Convertir PIL en numpy array
        img_array = np.array(image)
        
        # Convertir en niveaux de gris si nécessaire
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        if mode == "canny":
            # Canny Edge Detection - contours nets
            edges = self._apply_canny(gray)
        else:  # scribble
            # Scribble - style croquis simplifié
            edges = self._apply_scribble(gray)
        
        # Convertir en RGB pour compatibilité
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        # Retourner en PIL Image
        control_image = Image.fromarray(edges_rgb)
        
        print(f"✅ ControlNet appliqué ({mode})")
        return control_image
    
    def _apply_canny(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Applique Canny Edge Detection
        Produit des contours nets et précis
        """
        # Appliquer un flou pour réduire le bruit
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 1.4)
        
        # Détection de contours Canny
        # Seuils ajustables pour plus ou moins de détails
        low_threshold = 50
        high_threshold = 150
        edges = cv2.Canny(blurred, low_threshold, high_threshold)
        
        # Dilater légèrement les contours pour les rendre plus visibles
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Inverser (fond blanc, contours noirs)
        edges = cv2.bitwise_not(edges)
        
        return edges
    
    def _apply_scribble(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Applique un effet scribble/sketch
        Produit un style de croquis simplifié
        """
        # Méthode 1: XDoG (eXtended Difference of Gaussians)
        sigma1 = 0.5
        sigma2 = 2.0
        
        # Appliquer deux flous gaussiens différents
        blur1 = cv2.GaussianBlur(gray_image, (0, 0), sigma1)
        blur2 = cv2.GaussianBlur(gray_image, (0, 0), sigma2)
        
        # Différence entre les deux
        dog = blur1 - blur2
        
        # Normaliser et seuiller
        dog = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
        _, edges = cv2.threshold(dog, 10, 255, cv2.THRESH_BINARY)
        
        # Inverser pour fond blanc
        edges = cv2.bitwise_not(edges)
        
        return edges
    
    async def _generate_with_sd3_control(
        self,
        control_image: Image.Image,
        prompt: str,
        control_strength: float
    ) -> Optional[Path]:
        """
        Génère le coloriage avec Stable Diffusion 3 + Control Sketch
        
        Args:
            control_image: Image de contrôle (contours)
            prompt: Prompt de génération
            control_strength: Force du contrôle (0.5-1.0)
        
        Returns:
            Path vers l'image générée
        """
        try:
            print(f"🎨 Génération SD3 avec Control Sketch...")
            print(f"   - Prompt: {prompt[:80]}...")
            
            # Convertir l'image de contrôle en bytes
            img_byte_arr = io.BytesIO()
            control_image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Préparer la requête
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Accept": "image/*"
            }
            
            files = {
                "image": ("control.png", img_byte_arr, "image/png")
            }
            
            data = {
                "prompt": prompt,
                "negative_prompt": self.negative_prompt,
                "control_strength": control_strength,
                "output_format": "png"
            }
            
            # Appeler l'API Stability AI silencieusement
            
            response = requests.post(
                self.sd3_api_url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
            
            print(f"📥 Réponse API: {response.status_code}")
            
            if response.status_code == 200:
                # Sauvegarder l'image générée
                output_path = self.output_dir / f"coloring_sd3_{uuid.uuid4().hex[:8]}.png"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Image SD3 générée: {output_path.name}")
                return output_path
            else:
                error_msg = f"Erreur API Stability: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_detail = response.text[:500]
                    error_msg += f" - {error_detail}"
                
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            print(f"❌ Erreur génération SD3: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _post_process_coloring(self, image_path: Path) -> Path:
        """
        Post-traite l'image pour obtenir un coloriage optimal
        - Noir et blanc pur
        - Contours nets
        - Fond blanc
        """
        try:
            print(f"🔧 Post-traitement du coloriage...")
            
            with Image.open(image_path) as img:
                # Convertir en niveaux de gris
                gray = img.convert('L')
                
                # Augmenter le contraste pour des lignes plus nettes
                enhancer = ImageEnhance.Contrast(gray)
                high_contrast = enhancer.enhance(2.5)
                
                # Augmenter la luminosité pour éclaircir le fond
                brightness_enhancer = ImageEnhance.Brightness(high_contrast)
                brightened = brightness_enhancer.enhance(1.2)
                
                # Appliquer un seuillage adaptatif pour noir/blanc pur
                # Plus le seuil est élevé, plus le fond sera blanc
                threshold = 200
                bw = brightened.point(lambda x: 0 if x < threshold else 255, '1')
                
                # Reconvertir en RGB
                final = bw.convert('RGB')
                
                # Nettoyer les petits artefacts (optionnel)
                # final = final.filter(ImageFilter.MedianFilter(size=3))
                
                # Sauvegarder
                final.save(image_path, 'PNG', optimize=True)
                
                print(f"✅ Post-traitement terminé")
                return image_path
                
        except Exception as e:
            print(f"⚠️ Erreur post-traitement: {e}")
            return image_path
    
    async def generate_coloring_from_theme(self, theme: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Génération par thème (pour compatibilité)
        Note: Cette méthode n'utilise pas ControlNet car pas de photo source
        """
        print(f"⚠️ Génération par thème avec SD3 (sans ControlNet)")
        print(f"   Pour de meilleurs résultats, utilisez generate_coloring_from_photo()")
        
        # Utiliser l'API SD3 standard pour génération de novo
        return await self._generate_theme_without_controlnet(theme)
    
    async def _generate_theme_without_controlnet(self, theme: str) -> Dict[str, Any]:
        """Génération simple sans ControlNet (fallback)"""
        try:
            # Créer un prompt pour le thème
            theme_prompts = {
                'animaux': "A cute cat in a meadow",
                'animals': "A friendly dog with a ball",
                'dinosaures': "A friendly T-Rex in a forest",
                'espace': "An astronaut floating in space",
                'fees': "A fairy with butterfly wings",
                'nature': "Sunflowers in a garden",
            }
            
            scene = theme_prompts.get(theme.lower(), f"A {theme} scene")
            
            prompt = f"{scene}. {self.base_prompt}"
            
            # Appeler SD3 sans ControlNet
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Accept": "image/*"
            }
            
            data = {
                "prompt": prompt,
                "negative_prompt": self.negative_prompt,
                "output_format": "png",
                "model": "sd3-medium"
            }
            
            response = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/sd3",
                headers=headers,
                files={"none": ''},
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                output_path = self.output_dir / f"coloring_{theme}_{uuid.uuid4().hex[:8]}.png"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # Post-traiter
                final_path = await self._post_process_coloring(output_path)
                
                # 📤 Upload vers Supabase Storage si user_id fourni
                storage_service = get_storage_service()
                if storage_service and user_id:
                    upload_result = await storage_service.upload_file(
                        file_path=str(final_path),
                        user_id=user_id,
                        content_type="coloring",
                        custom_filename=final_path.name
                    )
                    
                    if upload_result["success"]:
                        image_url = upload_result["signed_url"]
                        print(f"✅ Image uploadée vers Supabase Storage")
                    else:
                        image_url = f"{self.base_url}/static/coloring/{final_path.name}"
                        print(f"⚠️ Upload Supabase échoué, utilisation chemin local")
                else:
                    image_url = f"{self.base_url}/static/coloring/{final_path.name}"
                
                return {
                    "success": True,
                    "theme": theme,
                    "images": [{
                        "image_url": image_url,
                        "theme": theme,
                        "source": "sd3_standard"
                    }],
                    "total_images": 1,
                    "metadata": {
                        "theme": theme,
                        "created_at": datetime.now().isoformat(),
                        "model": "sd3-medium"
                    }
                }
            else:
                raise Exception(f"Erreur API: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur génération thème: {e}")
            return {
                "success": False,
                "error": str(e),
                "images": []
            }
    
    # Méthodes de compatibilité
    async def generate_coloring_pages(self, theme: str) -> Dict[str, Any]:
        return await self.generate_coloring_from_theme(theme)
    
    async def generate_coloring(self, theme: str) -> Dict[str, Any]:
        return await self.generate_coloring_from_theme(theme)


# Instance globale
coloring_generator = ColoringGeneratorSD3ControlNet()

