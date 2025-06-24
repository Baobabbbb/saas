"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Version SDK officiel Runway
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Import du SDK officiel Runway
try:
    from runwayml import RunwayML
    SDK_AVAILABLE = True
    print("✅ SDK Runway disponible")
except ImportError:
    SDK_AVAILABLE = False
    print("❌ SDK Runway non disponible")

class RunwayGen4SDKService:
    """Service de génération vidéo Runway Gen-4 Turbo - Version SDK officiel"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY") or os.getenv("RUNWAYML_API_SECRET")
        
        # Initialiser le client SDK si disponible
        if SDK_AVAILABLE and self.api_key:
            try:
                # Configurer la variable d'environnement pour le SDK
                os.environ["RUNWAYML_API_SECRET"] = self.api_key
                self.client = RunwayML()
                print("✅ Client SDK Runway initialisé")
                self.use_sdk = True
            except Exception as e:
                print(f"❌ Erreur initialisation SDK: {str(e)}")
                self.client = None
                self.use_sdk = False
        else:
            self.client = None
            self.use_sdk = False
        
        # Styles supportés par Runway Gen-4 Turbo
        self.supported_styles = {
            "cartoon": "colorful cartoon animation style, vibrant colors, smooth animation",
            "fairy_tale": "magical fairy tale illustration style, dreamy and enchanting",
            "anime": "anime animation style, Japanese cartoon aesthetic",
            "realistic": "photorealistic style, natural lighting and movement",
            "paper_craft": "paper cut-out animation style, layered paper craft aesthetic",
            "watercolor": "watercolor painting style, soft brushstrokes, artistic flow"
        }
        
        print(f"🎬 Service Runway Gen-4 Turbo SDK initialisé")
        print(f"🔑 Clé API disponible: {'Oui' if self.api_key else 'Non'}")
        print(f"🛠️ SDK utilisé: {'Oui' if self.use_sdk else 'Non'}")
        print(f"🎨 Styles supportés: {list(self.supported_styles.keys())}")
        
        if not self.api_key:
            print("⚠️ Aucune clé API - Le service basculera en mode simulation")
    
    def _create_optimized_prompt(self, style: str, theme: str, custom_prompt: str = "") -> str:
        """Crée un prompt optimisé pour Runway Gen-4 Turbo et les enfants"""
        
        # Mapping des thèmes pour enfants
        theme_prompts = {
            "adventure": "exciting adventure with brave characters exploring magical places",
            "magic": "magical world with sparkles, fairy dust, and enchanted creatures",
            "animals": "cute friendly animals playing together in a colorful environment",
            "friendship": "heartwarming friendship story with characters helping each other",
            "space": "space adventure with colorful planets, friendly aliens, and starships",
            "underwater": "underwater adventure with colorful fish, coral reefs, and sea creatures",
            "forest": "enchanted forest with magical creatures, talking trees, and fairy lights",
            "superhero": "child-friendly superhero saving the day with positive powers"
        }
        
        # Récupérer les prompts de style et thème
        style_prompt = self.supported_styles.get(style, self.supported_styles["cartoon"])
        theme_prompt = theme_prompts.get(theme, theme_prompts["adventure"])
        
        # Construire le prompt final
        prompt_parts = [style_prompt, theme_prompt]
        
        if custom_prompt and custom_prompt.strip():
            prompt_parts.append(custom_prompt.strip())
        
        # Ajouter des directives spécifiques pour les enfants et Runway
        final_prompt = ", ".join(prompt_parts)
        final_prompt += ", suitable for children, bright colors, positive atmosphere, high quality animation, smooth motion"
        
        return final_prompt
    
    def _generate_attractive_title(self, style: str, theme: str) -> str:
        """Génère un titre attractif pour l'animation"""
        
        title_templates = {
            "adventure": ["Les Explorateurs de", "L'Aventure de", "Le Voyage vers", "La Quête de"],
            "magic": ["Le Monde Magique de", "Les Sortilèges de", "La Magie de", "L'Enchantement de"],
            "animals": ["Les Amis de la", "L'Histoire de", "Les Aventures de", "Le Royaume de"],
            "friendship": ["Les Amis de", "L'Amitié de", "L'Histoire de", "Les Copains de"],
            "space": ["Les Explorateurs de l'", "L'Aventure Spatiale de", "Le Voyage vers", "Les Héros de l'"],
            "underwater": ["Les Secrets de l'", "L'Aventure Sous-Marine de", "Les Trésors de l'", "Le Monde de l'"],
            "forest": ["La Forêt Enchantée de", "Les Mystères de la", "L'Aventure dans la", "Les Amis de la"],
            "superhero": ["Les Super-Héros de", "L'Héro de", "Les Défenseurs de", "Les Gardiens de"]
        }
        
        locations = {
            "adventure": ["l'Inconnu", "la Montagne d'Or", "l'Île Mystérieuse", "la Cité Perdue"],
            "magic": ["Féerie", "l'Arc-en-Ciel", "la Lune", "l'Étoile Dorée"],
            "animals": ["Forêt", "Jungle", "Savane", "Océan"],
            "friendship": ["la Joie", "l'Amitié", "la Bonne Humeur", "l'Entraide"],
            "space": ["Espace", "Galaxie", "Étoiles", "Cosmos"],
            "underwater": ["Océan", "Mer Bleue", "Récif Coloré", "Abysses"],
            "forest": ["Forêt", "Bois Magique", "Clairière", "Arbres Anciens"],
            "superhero": ["la Ville", "l'Univers", "la Planète", "la Justice"]
        }
        
        import random
        template = random.choice(title_templates.get(theme, title_templates["adventure"]))
        location = random.choice(locations.get(theme, locations["adventure"]))
        
        return f"{template} {location}"
    
    async def _generate_with_sdk(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Génère une animation avec le SDK officiel Runway"""
        
        if not self.use_sdk or not self.client:
            return None
        
        try:
            print("🎬 Génération avec SDK officiel Runway...")
            
            # Étape 1: Générer une image
            print("🖼️ Génération de l'image...")
            image_task = await asyncio.to_thread(
                self.client.text_to_image.create,
                model="gen4_image",
                prompt_text=prompt,
                ratio="1280:720"
            )
            
            # Attendre la completion de l'image
            image_result = await asyncio.to_thread(image_task.wait_for_task_output)
            
            if not image_result or not image_result.output:
                print("❌ Échec génération image SDK")
                return None
            
            image_url = image_result.output[0]
            print(f"✅ Image générée: {image_url}")
            
            # Étape 2: Générer une vidéo à partir de l'image
            print("🎬 Génération de la vidéo...")
            video_task = await asyncio.to_thread(
                self.client.image_to_video.create,
                model="gen4_turbo",
                prompt_image=image_url,
                prompt_text=prompt,
                ratio="1280:720",
                duration=10
            )
            
            # Attendre la completion de la vidéo
            video_result = await asyncio.to_thread(video_task.wait_for_task_output)
            
            if not video_result or not video_result.output:
                print("❌ Échec génération vidéo SDK")
                return None
            
            video_url = video_result.output[0]
            print(f"✅ Vidéo générée: {video_url}")
            
            return {
                "video_url": video_url,
                "thumbnail_url": image_url,
                "task_id": video_result.id
            }
            
        except Exception as e:
            print(f"❌ Erreur SDK: {str(e)}")
            return None
    
    async def _simulate_generation(self, style: str, theme: str, title: str, optimized_prompt: str) -> Dict[str, Any]:
        """Mode simulation pour les tests et développement"""
        
        print("🔄 Mode simulation - Génération instantanée")
        
        # Choisir une vidéo de démo en fonction du thème
        demo_videos = {
            "adventure": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "magic": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "animals": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "friendship": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "space": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "underwater": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "forest": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
            "superhero": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
        }
        
        video_url = demo_videos.get(theme, demo_videos["adventure"])
        
        return {
            "id": f"runway_sim_{int(time.time())}",
            "title": title,
            "description": f"Animation {style} - {theme} (Mode simulation)",
            "video_url": video_url,
            "thumbnail_url": None,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration": 10,
            "style": style,
            "theme": theme,
            "orientation": "landscape",
            "prompt": optimized_prompt
        }
    
    async def generate_animation(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer une animation avec Runway Gen-4 Turbo"""
        
        # Extraire les paramètres
        style = animation_data.get("style", "cartoon")
        theme = animation_data.get("theme", "adventure")
        orientation = animation_data.get("orientation", "landscape")
        custom_prompt = animation_data.get("prompt", "")
        title = animation_data.get("title", self._generate_attractive_title(style, theme))
        
        print(f"🎬 Génération animation - Style: {style}, Thème: {theme}, Orientation: {orientation}")
        
        # Créer le prompt optimisé
        optimized_prompt = self._create_optimized_prompt(style, theme, custom_prompt)
        print(f"📝 Prompt optimisé: {optimized_prompt[:100]}...")
        
        # Vérifier si on peut utiliser le SDK
        if not self.api_key or not self.use_sdk:
            print("⚠️ SDK non disponible - Mode simulation")
            return await self._simulate_generation(style, theme, title, optimized_prompt)
        
        try:
            # Essayer de générer avec le SDK
            sdk_result = await self._generate_with_sdk(optimized_prompt)
            
            if sdk_result and sdk_result.get("video_url"):
                # Succès avec le SDK!
                print("✅ Animation générée avec succès via SDK!")
                return {
                    "id": sdk_result.get("task_id", f"runway_sdk_{int(time.time())}"),
                    "title": title,
                    "description": f"Animation {style} - {theme} générée par Runway Gen-4 Turbo",
                    "video_url": sdk_result["video_url"],
                    "thumbnail_url": sdk_result.get("thumbnail_url"),
                    "status": "completed",
                    "created_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "duration": 10,
                    "style": style,
                    "theme": theme,
                    "orientation": orientation,
                    "prompt": optimized_prompt
                }
            else:
                print("❌ Échec SDK - Basculement en mode simulation")
                return await self._simulate_generation(style, theme, title, optimized_prompt)
            
        except Exception as e:
            print(f"❌ Erreur génération SDK: {str(e)}")
            print("🔄 Basculement en mode simulation")
            return await self._simulate_generation(style, theme, title, optimized_prompt)
    
    def validate_animation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les données d'animation"""
        errors = []
        
        if not data.get("style"):
            errors.append("Le style est requis")
        elif data["style"] not in self.supported_styles:
            errors.append(f"Style non supporté. Styles disponibles: {list(self.supported_styles.keys())}")
        
        if not data.get("theme"):
            errors.append("Le thème est requis")
        
        if data.get("prompt") and len(data["prompt"]) > 500:
            errors.append("La description ne peut pas dépasser 500 caractères")
        
        return {
            "isValid": len(errors) == 0,
            "errors": errors
        }

# Instance globale du service
runway_gen4_sdk_service = RunwayGen4SDKService()
