"""
Service Runway Gen-4 Turbo SIMPLIFIÉ pour génération d'animations
Version stable et robuste sans multi-scènes
"""

import os
import time
from typing import Dict, Any
from datetime import datetime
import asyncio
import httpx
import traceback

class RunwaySimpleService:
    """Service de génération vidéo Runway Gen-4 Turbo - Version simplifiée"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = os.getenv("RUNWAY_BASE_URL", "https://api.dev.runwayml.com")
        
        # Vérifier si on a une clé API valide
        if not self.api_key or self.api_key == "your-runway-api-key-here":
            print("❌ RUNWAY_API_KEY manquante - ERREUR FATALE")
            raise Exception("Clé API Runway manquante - impossible de continuer")
        else:
            print(f"🔑 Clé API Runway détectée: {self.api_key[:20]}...")
            print("🚀 MODE PRODUCTION RÉEL - Version simplifiée")
        
        # Styles supportés par Runway Gen-4 Turbo
        self.supported_styles = {
            "cartoon": "colorful cartoon animation style, vibrant colors, smooth animation",
            "fairy_tale": "magical fairy tale illustration style, dreamy and enchanting",
            "anime": "anime animation style, Japanese cartoon aesthetic",
            "realistic": "photorealistic style, natural lighting and movement",
            "paper_craft": "paper cut-out animation style, layered paper craft aesthetic",
            "watercolor": "watercolor painting style, soft brushstrokes, artistic flow"
        }
        
        print(f"🎬 Service Runway Simplifié initialisé")
        print(f"📡 Base URL: {self.base_url}")

    def _create_optimized_prompt(self, style: str, theme: str, custom_prompt: str = "", orientation: str = "landscape") -> str:
        """Crée un prompt optimisé pour Runway Gen-4 Turbo et les enfants"""
        
        # Mapping des thèmes pour enfants
        theme_prompts = {
            "adventure": "exciting adventure with brave characters exploring magical places",
            "magic": "magical world with sparkles, fairy dust, and enchanted creatures",
            "space": "colorful space adventure with friendly aliens and beautiful planets",
            "animals": "cute animals playing together in natural environments",
            "fairy_tale": "enchanted fairy tale world with castles, princesses, and magic",
            "ocean": "underwater adventure with colorful fish and sea creatures",
            "forest": "magical forest with talking trees and woodland creatures"
        }
        
        # Style de base
        base_style = self.supported_styles.get(style, self.supported_styles["cartoon"])
        theme_desc = theme_prompts.get(theme, theme_prompts["adventure"])
        
        # Construction du prompt final
        if custom_prompt:
            full_prompt = f"{base_style}, {theme_desc}, {custom_prompt}, child-friendly, bright colors, happy atmosphere"
        else:
            full_prompt = f"{base_style}, {theme_desc}, child-friendly, bright colors, happy atmosphere, engaging story"
        
        # Ajustements selon l'orientation
        if orientation == "portrait":
            full_prompt += ", vertical composition"
        elif orientation == "square":
            full_prompt += ", square composition"
        else:
            full_prompt += ", cinematic landscape composition"
        
        return full_prompt

    def _create_animation_prompt(self, style: str, theme: str, custom_prompt: str = "") -> str:
        """Créer un prompt d'animation engageant"""
        
        animation_styles = {
            "adventure": "characters moving with excitement, exploration movements, discovery gestures",
            "magic": "magical sparkles flowing, gentle floating movements, enchanting transformations",
            "space": "smooth space travel, gentle floating, friendly waving, cosmic movements",
            "animals": "playful animal movements, jumping, running, friendly interactions",
            "fairy_tale": "graceful magical movements, gentle transformations, dreamy floating",
            "ocean": "flowing water movements, swimming motions, gentle underwater dance",
            "forest": "natural forest movements, leaves rustling, peaceful animal motions"
        }
        
        base_animation = animation_styles.get(theme, animation_styles["adventure"])
        
        if custom_prompt:
            return f"{base_animation}, {custom_prompt}, smooth animation, child-friendly movements"
        else:
            return f"{base_animation}, smooth animation, child-friendly movements, engaging story progression"

    def _create_story_narration(self, style: str, theme: str, custom_prompt: str = "") -> str:
        """Créer une narration pour l'histoire"""
        
        narrations = {
            "adventure": "Une grande aventure commence ! Notre héros découvre un monde merveilleux plein de surprises et d'amis à rencontrer.",
            "magic": "Dans un monde magique étincelant, des créatures extraordinaires vivent des aventures pleines de magie et d'émerveillement.",
            "space": "Embarquons pour un voyage spatial extraordinaire à la découverte de planètes colorées et d'amis venus d'ailleurs !",
            "animals": "Dans la nature, tous les animaux vivent ensemble en harmonie et partagent de belles aventures pleines d'amitié.",
            "fairy_tale": "Il était une fois, dans un royaume enchanté, une merveilleuse histoire d'amitié et de magie qui commence...",
            "ocean": "Plongeons dans les profondeurs océaniques pour découvrir un monde aquatique plein de couleurs et de créatures amicales.",
            "forest": "Au coeur de la forêt magique, les arbres parlent et les animaux vivent des aventures extraordinaires ensemble."
        }
        
        base_narration = narrations.get(theme, narrations["adventure"])
        
        if custom_prompt:
            return f"{base_narration} {custom_prompt}"
        else:
            return base_narration

    async def generate_animation(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer une animation avec Runway Gen-4 Turbo - Version simplifiée et robuste"""
        
        # Extraire les paramètres
        style = animation_data.get("style", "cartoon")
        theme = animation_data.get("theme", "adventure")
        orientation = animation_data.get("orientation", "landscape")
        custom_prompt = animation_data.get("prompt", "")
        title = animation_data.get("title", f"Animation {style} - {theme}")
        
        print(f"🎬 Génération ANIMATION SIMPLIFIÉE - Style: {style}, Thème: {theme}")
        print(f"📝 Prompt personnalisé: {custom_prompt}")
        
        try:
            # Créer un prompt unique optimisé
            optimized_prompt = self._create_optimized_prompt(style, theme, custom_prompt, orientation)
            print(f"🎯 Prompt optimisé: {optimized_prompt[:100]}...")
            
            # Ratio mapping
            ratio_map = {
                "landscape": "1920:1080",
                "portrait": "1080:1920", 
                "square": "1080:1080"
            }
            ratio = ratio_map.get(orientation, "1920:1080")
            
            # Étape 1: Générer l'image principale
            print("🎨 Génération de l'image principale...")
            main_image_url = await self._generate_image_from_text(optimized_prompt, ratio)
            print(f"✅ Image générée: {main_image_url}")
            
            # Étape 2: Créer le prompt d'animation
            animation_prompt = self._create_animation_prompt(style, theme, custom_prompt)
            print(f"🎬 Prompt d'animation: {animation_prompt[:100]}...")
            
            # Étape 3: Générer la vidéo finale
            print("🎥 Génération de la vidéo finale...")
            final_video_url = await self._generate_video_from_image(
                main_image_url, 
                animation_prompt, 
                duration=10  # 10 secondes pour une animation complète
            )
            print(f"✅ Vidéo générée: {final_video_url}")
            
            # Créer une narration pour l'histoire
            story_narration = self._create_story_narration(style, theme, custom_prompt)
            
            # Retourner le résultat final
            return {
                "id": f"runway_simple_{int(time.time())}",
                "title": title,
                "description": f"Animation {style} - {theme} générée avec Runway Gen-4 Turbo",
                "video_url": final_video_url,
                "thumbnail_url": main_image_url,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": 10,
                "style": style,
                "theme": theme,
                "orientation": orientation,
                "prompt": custom_prompt,
                "narration": story_narration,
                "narrative_type": "single_animation"
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")
            print(f"📊 Traceback complet: {traceback.format_exc()}")
            raise Exception(f"Impossible de générer l'animation: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """Headers pour l'authentification Runway selon la documentation officielle"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }

    async def _generate_image_from_text(self, prompt: str, ratio: str = "1920:1080") -> str:
        """Génère une image à partir d'un prompt avec l'API text_to_image de Runway"""
        
        print(f"🎨 Génération d'image avec l'API text_to_image de Runway...")
        
        payload = {
            "model": "gen4_image",
            "promptText": prompt,
            "ratio": ratio
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/text_to_image",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur text_to_image: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway text_to_image: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse text_to_image")
            
            print(f"⏳ Tâche image créée: {task_id}")
            
            # Attendre la génération de l'image
            image_url = await self._wait_for_task_completion(task_id, "image")
            return image_url

    async def _generate_video_from_image(self, image_url: str, prompt: str, duration: int = 10) -> str:
        """Génère une vidéo à partir d'une image avec l'API image_to_video de Runway"""
        
        print(f"🎬 Génération de vidéo avec l'API image_to_video de Runway...")
        print(f"🖼️ Image source: {image_url}")
        
        payload = {
            "model": "gen4_turbo",
            "promptImage": image_url,
            "promptText": prompt,
            "duration": duration,
            "ratio": "1280:720"
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/image_to_video",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur image_to_video: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway image_to_video: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse image_to_video")
            
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
                        f"{self.base_url}/v1/tasks/{task_id}",
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
                    
                    if status in ["completed", "SUCCEEDED"]:
                        output = task_status.get("output")
                        if output and len(output) > 0:
                            result_url = output[0]
                            print(f"✅ {task_type.capitalize()} terminé: {result_url}")
                            return result_url
                        else:
                            raise Exception(f"Aucun output trouvé pour la tâche {task_id}")
                    
                    elif status in ["failed", "FAILED"]:
                        error = task_status.get("error", "Erreur inconnue")
                        raise Exception(f"Tâche {task_id} échouée: {error}")
                    
                    elif status in ["pending", "running", "PENDING", "RUNNING"]:
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

# Instance globale du service
runway_simple_service = RunwaySimpleService()
