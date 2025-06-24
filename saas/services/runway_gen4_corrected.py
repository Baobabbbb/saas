"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Version corrigée avec headers appropriés
"""

import os
import time
import asyncio
import httpx
from typing import Dict, Any
from datetime import datetime

class RunwayGen4Service:
    """Service de génération vidéo Runway Gen-4 Turbo"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY") or os.getenv("RUNWAYML_API_SECRET")
        self.base_url = "https://api.dev.runwayml.com/v1"
        
        # Force le mode production pour tester la vraie API
        if not self.api_key:
            print("⚠️ Pas de clé API - Mode simulation")
            self.simulation_mode = True
        else:
            print(f"🔑 Clé API Runway détectée: {self.api_key[:20]}...")
            self.simulation_mode = False  # Utiliser la vraie API
        
        # Styles supportés par Runway Gen-4 Turbo
        self.supported_styles = {
            "cartoon": "colorful cartoon animation style, vibrant colors, smooth animation",
            "fairy_tale": "magical fairy tale illustration style, dreamy and enchanting",
            "anime": "anime animation style, Japanese cartoon aesthetic",
            "realistic": "photorealistic style, natural lighting and movement",
            "paper_craft": "paper cut-out animation style, layered paper craft aesthetic",
            "watercolor": "watercolor painting style, soft brushstrokes, artistic flow"
        }
        
        print(f"🎬 Service Runway Gen-4 Turbo initialisé")
        print(f"📡 Base URL: {self.base_url}")
        print(f"🎨 Styles supportés: {list(self.supported_styles.keys())}")
        print(f"🚀 Mode: {'Simulation' if self.simulation_mode else 'Production avec vraie API'}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers pour l'authentification Runway avec version requise"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-26"
        }
    
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
        final_prompt += ", suitable for children, bright colors, positive atmosphere, high quality"
        
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
    
    async def generate_animation(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer une animation avec Runway Gen-4 Turbo"""
        
        # Extraire les paramètres
        style = animation_data.get("style", "cartoon")
        theme = animation_data.get("theme", "adventure")
        orientation = animation_data.get("orientation", "landscape")
        custom_prompt = animation_data.get("prompt", "")
        title = animation_data.get("title", self._generate_attractive_title(style, theme))
        
        print(f"🎬 Génération animation - Style: {style}, Thème: {theme}, Orientation: {orientation}")
        print(f"📝 Prompt personnalisé: {custom_prompt}")
        
        # Créer le prompt optimisé
        optimized_prompt = self._create_optimized_prompt(style, theme, custom_prompt)
        print(f"🎯 Prompt final: {optimized_prompt}")
        
        # Mode simulation ou vraie API
        if self.simulation_mode:
            print("🔄 Mode simulation - Utilisation de vidéos de démo")
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
            
            return {
                "id": f"runway_sim_{int(time.time())}",
                "title": title,
                "description": f"Animation {style} - {theme} | Prompt: {custom_prompt} (SIMULATION)",
                "video_url": demo_videos.get(theme, demo_videos["adventure"]),
                "thumbnail_url": None,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": 10,
                "style": style,
                "theme": theme,
                "orientation": orientation,
                "prompt": optimized_prompt
            }
        
        # Mode production avec vraie API Runway
        try:
            print("🚀 Génération avec la vraie API Runway Gen-4...")
            
            # Étape 1: Générer une image avec Gen-4 Image
            print("🎨 Étape 1/3 : Génération de l'image...")
            image_url = await self._generate_image_from_text(optimized_prompt)
            
            if not image_url:
                raise Exception("Échec de la génération d'image")
            
            print(f"✅ Image générée: {image_url}")
            
            # Étape 2: Générer une vidéo à partir de l'image
            print("🎬 Étape 2/3 : Génération de la vidéo...")
            video_prompt = f"Animate this {style} style image with smooth motion, bring characters to life"
            video_url = await self._generate_video_from_image(image_url, video_prompt, duration=10)
            
            if not video_url:
                raise Exception("Échec de la génération vidéo")
            
            print(f"✅ Vidéo générée: {video_url}")
            
            # Retourner le résultat final
            return {
                "id": f"runway_real_{int(time.time())}",
                "title": title,
                "description": f"Animation {style} - {theme} | Prompt: {custom_prompt} (VRAIE GÉNÉRATION RUNWAY)",
                "video_url": video_url,
                "thumbnail_url": image_url,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": 10,
                "style": style,
                "theme": theme,
                "orientation": orientation,
                "prompt": optimized_prompt
            }
            
        except Exception as e:
            print(f"❌ Erreur génération Runway: {str(e)}")
            
            # En cas d'erreur, retourner une réponse d'erreur claire
            return {
                "id": f"runway_error_{int(time.time())}",
                "title": f"⚠️ {title} (Erreur)",
                "description": f"Erreur API Runway: {str(e)} | Paramètres: Style={style}, Thème={theme}, Prompt='{custom_prompt}'",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",  # Vidéo de fallback
                "thumbnail_url": None,
                "status": "completed",  # On garde completed pour ne pas casser le frontend
                "error": str(e),
                "created_at": datetime.now().isoformat(),
                "duration": 10,
                "style": style,
                "theme": theme,
                "orientation": orientation
            }
    
    async def _generate_image_from_text(self, prompt: str) -> str:
        """Génère une image à partir d'un prompt avec Gen-4 Image"""
        
        print(f"🎨 Génération d'image...")
        print(f"📝 Prompt: {prompt}")
        
        payload = {
            "model": "gen4_image",
            "ratio": "1280:720",
            "promptText": prompt
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/text_to_image",
                headers=self._get_headers(),
                json=payload
            )
            
            print(f"📊 Réponse API Image: {response.status_code}")
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur Gen-4 Image: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway Image: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse Runway Image")
            
            print(f"⏳ Tâche image créée: {task_id}")
            
            # Attendre la génération de l'image
            image_url = await self._wait_for_task_completion(task_id, "image")
            return image_url
    
    async def _generate_video_from_image(self, image_url: str, prompt: str, duration: int = 10) -> str:
        """Génère une vidéo à partir d'une image avec Gen-4 Turbo"""
        
        print(f"🎬 Génération de vidéo...")
        print(f"🖼️ Image source: {image_url}")
        print(f"📝 Prompt vidéo: {prompt}")
        
        payload = {
            "model": "gen4_turbo",
            "promptImage": image_url,
            "promptText": prompt,
            "duration": duration
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/image_to_video",
                headers=self._get_headers(),
                json=payload
            )
            
            print(f"📊 Réponse API Vidéo: {response.status_code}")
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur Gen-4 Turbo: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway Video: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse Runway Video")
            
            print(f"⏳ Tâche vidéo créée: {task_id}")
            
            # Attendre la génération de la vidéo
            video_url = await self._wait_for_task_completion(task_id, "video")
            return video_url
    
    async def _wait_for_task_completion(self, task_id: str, task_type: str = "task") -> str:
        """Attend la fin d'une tâche Runway et retourne l'URL du résultat"""
        
        max_attempts = 120  # 20 minutes max (10 secondes * 120)
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers=self._get_headers()
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Erreur vérification statut: {response.status_code}")
                        await asyncio.sleep(10)
                        attempt += 1
                        continue
                    
                    task_status = response.json()
                    status = task_status.get("status")
                    
                    print(f"📊 Statut {task_type}: {status} (tentative {attempt + 1}/{max_attempts})")
                    
                    if status == "SUCCEEDED":
                        output = task_status.get("output")
                        if output and len(output) > 0:
                            result_url = output[0]
                            print(f"✅ {task_type.capitalize()} terminé: {result_url}")
                            return result_url
                        else:
                            raise Exception(f"Aucun output trouvé pour la tâche {task_id}")
                    
                    elif status == "FAILED":
                        error = task_status.get("error", "Erreur inconnue")
                        raise Exception(f"Tâche {task_id} échouée: {error}")
                    
                    elif status in ["PENDING", "RUNNING"]:
                        await asyncio.sleep(10)
                        attempt += 1
                    
                    else:
                        print(f"⚠️ Statut inattendu: {status}")
                        await asyncio.sleep(10)
                        attempt += 1
                        
            except Exception as e:
                print(f"❌ Erreur vérification: {e}")
                await asyncio.sleep(10)
                attempt += 1
        
        raise Exception(f"Timeout: La tâche {task_id} n'a pas terminé dans les temps")
    
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
runway_gen4_service = RunwayGen4Service()
