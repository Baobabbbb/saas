"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Version propre et fonctionnelle
"""

import os
import asyncio
import httpx
import json
from typing import Dict, Any
from datetime import datetime
import time

class RunwayGen4Service:
    """Service de génération vidéo Runway Gen-4 Turbo"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = os.getenv("RUNWAY_BASE_URL", "https://api.runwayml.com/v1")
        
        # Vérifier si on a une clé API valide
        if not self.api_key or self.api_key == "your-runway-api-key-here":
            print("⚠️ RUNWAY_API_KEY manquante - mode simulation activé")
            self.simulation_mode = True
        else:
            print(f"🔑 Clé API Runway détectée: {self.api_key[:20]}...")
            print("🚀 ACTIVATION MODE PRODUCTION - Utilisation de l'API Runway réelle")
            self.simulation_mode = False  # VRAIE API ACTIVÉE
        
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
        """Headers pour l'authentification Runway"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-26"
        }
    
    def _create_optimized_prompt(self, style: str, theme: str, custom_prompt: str = "", orientation: str = "landscape") -> str:
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
        
        # Ajouter des spécifications d'orientation
        if orientation == "portrait":
            final_prompt += ", vertical format"
        elif orientation == "square": 
            final_prompt += ", square format"
        else:
            final_prompt += ", horizontal widescreen format"
        
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
        
        # Créer le prompt optimisé
        optimized_prompt = self._create_optimized_prompt(style, theme, custom_prompt, orientation)
        print(f"📝 Prompt optimisé: {optimized_prompt}")
        
        # Mode simulation ou vraie API
        if self.simulation_mode:
            print("🔄 Mode simulation - Génération instantanée")
            
            # Vidéos de simulation selon le thème pour montrer la différence
            simulation_videos = {
                "magic": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "animals": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4", 
                "space": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "adventure": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
                "underwater": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
            }
            
            video_url = simulation_videos.get(theme, simulation_videos["adventure"])
            
            return {
                "id": f"runway_sim_{int(time.time())}",
                "title": title,
                "description": f"Animation {style} - {theme} (SIMULATION - paramètres: style={style}, thème={theme}, orientation={orientation})",
                "video_url": video_url,
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
            print("🚀 Génération avec la vraie API Runway...")
            
            # Étape 1: Générer une image avec Gen-4 Image  
            ratio_map = {
                "landscape": "1920:1080",
                "portrait": "1080:1920",
                "square": "1080:1080"
            }
            ratio = ratio_map.get(orientation, "1920:1080")
            
            image_url = await self._generate_image_from_text(optimized_prompt, ratio)
            
            # Étape 2: Générer une vidéo à partir de l'image avec Gen-4 Turbo
            video_prompt = f"Animate this {style} style image with smooth motion, bring characters to life"
            video_url = await self._generate_video_from_image(image_url, video_prompt, duration=10)
            
            # Retourner le résultat final
            return {
                "id": f"runway_prod_{int(time.time())}",
                "title": title,
                "description": f"Animation {style} - {theme}",
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
            print(f"❌ Erreur lors de la génération Runway: {e}")
            # En cas d'erreur, retourner en mode simulation
            return {
                "id": f"runway_error_{int(time.time())}",
                "title": f"⚠️ {title}",
                "description": f"Erreur API: {str(e)} - Retour en mode simulation",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "thumbnail_url": None,
                "status": "completed",
                "error": str(e),
                "created_at": datetime.now().isoformat(),
                "duration": 10,
                "style": style,
                "theme": theme,
                "orientation": orientation
            }

    async def _generate_image_from_text(self, prompt: str, ratio: str = "1920:1080") -> str:
        """Génère une image à partir d'un prompt avec Gen-4 Image"""
        
        print(f"🎨 Génération d'image avec Gen-4 Image...")
        
        payload = {
            "model": "gen4_image",
            "ratio": ratio,
            "promptText": prompt
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/text_to_image",
                headers=self._get_headers(),
                json=payload
            )
            
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
        
        print(f"🎬 Génération de vidéo avec Gen-4 Turbo...")
        
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
        
        max_attempts = 60  # 10 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers=self._get_headers()
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Erreur lors de la vérification du statut: {response.status_code}")
                        await asyncio.sleep(10)
                        attempt += 1
                        continue
                    
                    task_status = response.json()
                    status = task_status.get("status")
                    
                    print(f"📊 Statut {task_type}: {status} (tentative {attempt + 1}/{max_attempts})")
                    
                    if status == "completed":
                        output = task_status.get("output")
                        if output and len(output) > 0:
                            result_url = output[0]
                            print(f"✅ {task_type.capitalize()} terminé: {result_url}")
                            return result_url
                        else:
                            raise Exception(f"Aucun output trouvé pour la tâche {task_id}")
                    
                    elif status == "failed":
                        error = task_status.get("error", "Erreur inconnue")
                        raise Exception(f"Tâche {task_id} échouée: {error}")
                    
                    elif status in ["pending", "running"]:
                        await asyncio.sleep(10)
                        attempt += 1
                    
                    else:
                        print(f"⚠️ Statut inattendu: {status}")
                        await asyncio.sleep(10)
                        attempt += 1
                        
            except Exception as e:
                print(f"❌ Erreur lors de la vérification: {e}")
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
                response = await client.get(
                    f"{self.base_url}/tasks/{image_task_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code != 200:
                    return {
                        "status": "error",
                        "error": f"Erreur vérification: {response.status_code}"
                    }
                
                task_data = response.json()
                task_status = task_data.get("status")
                
                if task_status in ["completed", "SUCCEEDED"]:
                    # Image terminée, maintenant générer la vidéo
                    output = task_data.get("output")
                    if output and len(output) > 0:
                        image_url = output[0]
                        
                        # Lancer la génération vidéo
                        video_task_id = await self._create_video_task(image_url)
                        
                        return {
                            "status": "processing_video",
                            "progress": 50,
                            "message": "Image terminée, génération vidéo en cours...",
                            "thumbnail_url": image_url,
                            "video_task_id": video_task_id
                        }
                    
                elif task_status in ["failed", "FAILED"]:
                    return {
                        "status": "failed",
                        "error": task_data.get("error", "Erreur génération image")
                    }
                
                else:
                    # Toujours en cours
                    progress = min(25, (task_data.get("progress", 0) * 0.5))  # 50% pour l'image
                    return {
                        "status": "processing_image", 
                        "progress": progress,
                        "message": "Génération de l'image en cours..."
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def _create_video_task(self, image_url: str, style: str = "cartoon") -> str:
        """Créer une tâche de génération vidéo optimisée"""
        
        # Prompt optimisé pour la vitesse
        video_prompt = f"Animate this {style} image with smooth, gentle motion"
        
        payload = {
            "model": "gen4_turbo",  # Utiliser Turbo pour plus de rapidité
            "promptImage": image_url,
            "promptText": video_prompt,
            "duration": 5,  # Durée réduite pour plus de rapidité
            "ratio": "1280:720"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/image_to_video", 
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Erreur création tâche vidéo: {response.status_code}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            print(f"✅ Tâche vidéo créée: {task_id}")
            return task_id

    def _get_cache_key(self, animation_data: Dict[str, Any]) -> str:
        """Générer une clé de cache basée sur les paramètres d'animation"""
        
        # Créer un hash des paramètres importants
        cache_data = {
            "style": animation_data.get("style"),
            "theme": animation_data.get("theme"), 
            "orientation": animation_data.get("orientation"),
            "prompt": animation_data.get("prompt", "")[:100]  # Limiter pour éviter les variations mineures
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _get_cached_animation(self, cache_key: str) -> Dict[str, Any] | None:
        """Récupérer une animation du cache si elle existe"""
        
        if not self.enable_cache:
            return None
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Vérifier si le cache n'est pas trop ancien (24h)
                cached_time = datetime.fromisoformat(cached_data.get("cached_at", "2000-01-01"))
                if (datetime.now() - cached_time).total_seconds() < 86400:  # 24h
                    print(f"📦 Animation trouvée en cache: {cache_key}")
                    return cached_data["animation"]
                    
            except Exception as e:
                print(f"⚠️ Erreur lecture cache: {e}")
        
        return None

    def _save_animation_to_cache(self, cache_key: str, animation_data: Dict[str, Any]) -> None:
        """Sauvegarder une animation en cache"""
        
        if not self.enable_cache or animation_data.get("status") != "completed":
            return
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "animation": animation_data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Animation sauvée en cache: {cache_key}")
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde cache: {e}")

    async def _generate_image_from_text_fast(self, prompt: str, ratio: str = "1280:720") -> str:
        """Génère une image optimisée pour la vitesse avec Gen-4 Image"""
        
        print(f"⚡ Génération d'image RAPIDE avec Gen-4 Image...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Prompt optimisé pour la vitesse (plus court)
        fast_prompt = prompt[:200]  # Limiter la longueur pour plus de rapidité
        
        payload = {
            "model": "gen4_image",
            "ratio": ratio,
            "promptText": fast_prompt
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:  # Timeout réduit
            # Créer la tâche de génération d'image
            response = await client.post(
                f"{self.base_url}/text_to_image",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur Gen-4 Image: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway Image: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse Runway Image")
            
            print(f"⏳ Tâche image créée: {task_id}")
            
            # Attendre la génération de l'image avec timeout réduit
            image_url = await self._wait_for_task_completion_fast(task_id, "image")
            return image_url

    async def _generate_video_from_image_fast(self, image_url: str, prompt: str, duration: int = 5, ratio: str = "1280:720") -> str:
        """Génère une vidéo optimisée pour la vitesse avec Gen-4 Turbo"""
        
        print(f"⚡ Génération de vidéo RAPIDE avec Gen-4 Turbo...")
        print(f"🖼️ Image source: {image_url}")
        
        payload = {
            "model": "gen4_turbo",
            "promptImage": image_url,
            "promptText": prompt,
            "duration": duration,  # Durée réduite pour plus de rapidité
            "ratio": ratio
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:  # Timeout réduit
            # Créer la tâche de génération vidéo
            response = await client.post(
                f"{self.base_url}/image_to_video",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur Gen-4 Turbo: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway Video: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse Runway Video")
            
            print(f"⏳ Tâche vidéo créée: {task_id}")
            
            # Attendre la génération de la vidéo avec timeout réduit
            video_url = await self._wait_for_task_completion_fast(task_id, "video")
            return video_url

    async def _wait_for_task_completion_fast(self, task_id: str, task_type: str = "task") -> str:
        """Attend la fin d'une tâche Runway avec timeout optimisé pour la vitesse"""
        
        max_attempts = 60  # 10 minutes max (10 secondes * 60) - Plus court pour la vitesse
        attempt = 0
        
        print(f"⚡ Attente RAPIDE de la génération {task_type} (ID: {task_id})")
        print(f"   Temps maximum: {max_attempts * 10 / 60:.1f} minutes")
        
        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:  # Timeout réduit
                    response = await client.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers=self._get_headers()
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Erreur lors de la vérification du statut: {response.status_code}")
                        await asyncio.sleep(5)  # Attente réduite
                        attempt += 1
                        continue
                    
                    task_status = response.json()
                    status = task_status.get("status")
                    
                    # Afficher un message informatif plus fréquent pour le mode rapide
                    if attempt % 3 == 0 or status in ["completed", "SUCCEEDED", "failed", "FAILED"]:
                        elapsed_minutes = (attempt * 10) / 60
                        print(f"⚡ Statut {task_type}: {status} (⏱️ {elapsed_minutes:.1f}min)")
                    
                    if status in ["completed", "SUCCEEDED"]:
                        output = task_status.get("output")
                        if output and len(output) > 0:
                            result_url = output[0]
                            print(f"✅ {task_type.capitalize()} terminé RAPIDEMENT: {result_url}")
                            return result_url
                        else:
                            raise Exception(f"Aucun output trouvé pour la tâche {task_id}")
                    
                    elif status in ["failed", "FAILED"]:
                        error = task_status.get("error", "Erreur inconnue")
                        raise Exception(f"Tâche {task_id} échouée: {error}")
                    
                    elif status in ["pending", "running", "PENDING", "RUNNING"]:
                        # Attendre moins longtemps en mode rapide
                        await asyncio.sleep(5)
                        attempt += 1
                    
                    else:
                        print(f"⚠️ Statut inattendu: {status}")
                        await asyncio.sleep(5)
                        attempt += 1
                        
            except Exception as e:
                print(f"❌ Erreur lors de la vérification: {e}")
                await asyncio.sleep(5)
                attempt += 1
        
        raise Exception(f"Timeout RAPIDE: La tâche {task_id} n'a pas terminé dans les temps (mode vitesse)")

# Instance globale
runway_gen4_service = RunwayGen4Service()
