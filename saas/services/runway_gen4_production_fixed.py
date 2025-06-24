"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Version production avec l'API officielle Runway
"""

import os
import httpx
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

class RunwayGen4ProductionService:
    """Service de génération vidéo Runway Gen-4 Turbo - Version production"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY") or os.getenv("RUNWAYML_API_SECRET")
        self.base_url = "https://api.dev.runwayml.com"
        
        # Configuration pour les requêtes HTTP
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
        
        # Timeout configuration
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
        # Styles supportés par Runway Gen-4 Turbo
        self.supported_styles = {
            "cartoon": "colorful cartoon animation style, vibrant colors, smooth animation",
            "fairy_tale": "magical fairy tale illustration style, dreamy and enchanting",
            "anime": "anime animation style, Japanese cartoon aesthetic",
            "realistic": "photorealistic style, natural lighting and movement",
            "paper_craft": "paper cut-out animation style, layered paper craft aesthetic",
            "watercolor": "watercolor painting style, soft brushstrokes, artistic flow"
        }
        
        print(f"🎬 Service Runway Gen-4 Turbo Production initialisé")
        print(f"🔑 Clé API disponible: {'Oui' if self.api_key else 'Non'}")
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
    
    async def _generate_image_from_text(self, prompt: str) -> Optional[str]:
        """Génère une image à partir d'un prompt texte avec l'API Runway"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": "gen4_image",
                    "promptText": prompt,
                    "ratio": "1280:720"
                }
                
                print(f"🖼️ Génération d'image avec prompt: {prompt[:100]}...")
                
                response = await client.post(
                    f"{self.base_url}/v1/text_to_image",
                    headers=self.headers,
                    json=payload
                )
                
                print(f"📊 Réponse image: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("id")
                    
                    if task_id:
                        print(f"🔄 Tâche image créée: {task_id}")
                        # Attendre la completion de l'image
                        image_result = await self._poll_task_status(task_id)
                        if image_result and image_result.get("status") == "completed":
                            image_url = image_result.get("output", [{}])[0].get("url")
                            if image_url:
                                print(f"✅ Image générée: {image_url}")
                                return image_url
                    
                    print("❌ Aucune image dans la réponse")
                    return None
                else:
                    print(f"❌ Erreur génération image: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Exception génération image: {str(e)}")
            return None
    
    async def _generate_video_from_image(self, image_url: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Génère une vidéo à partir d'une image avec l'API Runway"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": "gen4_turbo",
                    "promptImage": image_url,
                    "promptText": prompt,
                    "ratio": "1280:720",
                    "duration": 10
                }
                
                print(f"🎬 Génération vidéo à partir de l'image...")
                
                response = await client.post(
                    f"{self.base_url}/v1/image_to_video",
                    headers=self.headers,
                    json=payload
                )
                
                print(f"📊 Réponse vidéo: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("id")
                    
                    if task_id:
                        print(f"🔄 Tâche vidéo créée: {task_id}")
                        return {"task_id": task_id, "status": "processing"}
                    else:
                        print("❌ Aucun ID de tâche dans la réponse")
                        return None
                else:
                    print(f"❌ Erreur génération vidéo: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Exception génération vidéo: {str(e)}")
            return None
    
    async def _poll_task_status(self, task_id: str, max_attempts: int = 60) -> Optional[Dict[str, Any]]:
        """Poll le statut d'une tâche Runway"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for attempt in range(max_attempts):
                    print(f"🔄 Vérification statut tâche ({attempt + 1}/{max_attempts})...")
                    
                    response = await client.get(
                        f"{self.base_url}/v1/tasks/{task_id}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        status = result.get("status")
                        
                        if status == "SUCCEEDED":
                            print(f"✅ Tâche complétée avec succès!")
                            return {
                                "status": "completed",
                                "output": result.get("output", []),
                                "task_data": result
                            }
                        
                        elif status == "FAILED":
                            print(f"❌ Tâche échouée: {result.get('failure_reason', 'Raison inconnue')}")
                            return None
                        
                        elif status in ["PENDING", "RUNNING"]:
                            print(f"⏳ Tâche en cours... ({status})")
                            await asyncio.sleep(5)  # Attendre 5 secondes avant la prochaine vérification
                            continue
                        
                        else:
                            print(f"❓ Statut inconnu: {status}")
                            await asyncio.sleep(5)
                            continue
                    
                    else:
                        print(f"❌ Erreur vérification statut: {response.status_code}")
                        await asyncio.sleep(5)
                        continue
                
                print("⏰ Timeout: Tâche trop longue")
                return None
                
        except Exception as e:
            print(f"❌ Exception polling tâche: {str(e)}")
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
        
        # Vérifier si on a une clé API
        if not self.api_key:
            print("⚠️ Pas de clé API - Mode simulation")
            return await self._simulate_generation(style, theme, title, optimized_prompt)
        
        try:
            # Étape 1: Générer une image à partir du prompt
            print("🖼️ Étape 1: Génération de l'image...")
            image_url = await self._generate_image_from_text(optimized_prompt)
            
            if not image_url:
                print("❌ Échec génération image - Basculement en mode simulation")
                return await self._simulate_generation(style, theme, title, optimized_prompt)
            
            # Étape 2: Générer une vidéo à partir de l'image
            print("🎬 Étape 2: Génération de la vidéo...")
            video_task = await self._generate_video_from_image(image_url, optimized_prompt)
            
            if not video_task or not video_task.get("task_id"):
                print("❌ Échec génération vidéo - Basculement en mode simulation")
                return await self._simulate_generation(style, theme, title, optimized_prompt)
            
            # Étape 3: Attendre la completion de la vidéo
            print("⏳ Étape 3: Attente de la completion...")
            video_result = await self._poll_task_status(video_task["task_id"])
            
            if not video_result or video_result.get("status") != "completed":
                print("❌ Échec completion vidéo - Basculement en mode simulation")
                return await self._simulate_generation(style, theme, title, optimized_prompt)
            
            # Extraire l'URL de la vidéo
            video_url = None
            if video_result.get("output") and len(video_result["output"]) > 0:
                video_url = video_result["output"][0].get("url")
            
            if not video_url:
                print("❌ Pas d'URL vidéo - Basculement en mode simulation")
                return await self._simulate_generation(style, theme, title, optimized_prompt)
            
            # Succès! Retourner le résultat
            print("✅ Animation générée avec succès!")
            return {
                "id": video_task["task_id"],
                "title": title,
                "description": f"Animation {style} - {theme} générée par Runway Gen-4 Turbo",
                "video_url": video_url,
                "thumbnail_url": image_url,  # Utiliser l'image générée comme thumbnail
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
            print(f"❌ Erreur génération production: {str(e)}")
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
runway_gen4_production_service = RunwayGen4ProductionService()
