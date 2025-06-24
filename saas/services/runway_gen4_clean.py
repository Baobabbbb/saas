"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Compatible avec l'API officielle Runway ML
"""

import os
import asyncio
import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

class RunwayGen4Service:
    """Service de génération vidéo Runway Gen-4 Turbo"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = os.getenv("RUNWAY_BASE_URL", "https://api.runwayml.com/v1")
        
        if not self.api_key or self.api_key == "your-runway-api-key-here":
            print("⚠️ RUNWAY_API_KEY manquante - mode simulation activé")
            self.api_key = None
        
        # Configuration par défaut pour Gen-4 Turbo
        self.default_config = {
            "duration": 10,           # 5 ou 10 secondes
            "aspect_ratio": "16:9",   # 16:9, 9:16, 1:1
            "resolution": "720p",     # 720p recommandé
            "motion_control": "balanced",  # low, balanced, high
            "seed": None,
            "watermark": False        # Désactiver le watermark si possible
        }
        
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
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers pour l'authentification Runway"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _create_optimized_prompt(
        self, 
        style: str, 
        theme: str, 
        custom_prompt: str = "",
        orientation: str = "landscape"
    ) -> str:
        """Crée un prompt optimisé pour Runway Gen-4 Turbo et les enfants"""
        
        # Mapping des thèmes pour enfants
        theme_prompts = {
            "adventure": "exciting adventure with brave characters exploring magical places",
            "magic": "magical world with sparkles, fairy dust, and enchanted creatures",
            "animals": "cute friendly animals playing together in a colorful environment",
            "friendship": "heartwarming friendship story with characters helping each other",
            "space": "colorful space adventure with friendly aliens and bright planets",
            "underwater": "underwater adventure with colorful fish and sea creatures",
            "forest": "enchanted forest with talking animals and magical trees",
            "superhero": "young superhero saving the day with colorful powers"
        }
        
        # Style adapté pour Runway
        style_prompt = self.supported_styles.get(style, self.supported_styles["cartoon"])
        theme_prompt = theme_prompts.get(theme, f"{theme} themed story")
        
        # Construction du prompt optimisé
        prompt_parts = [
            style_prompt,
            theme_prompt,
            "suitable for children",
            "bright vibrant colors",
            "smooth fluid animation",
            "joyful and positive atmosphere",
            "high quality animation"
        ]
        
        if custom_prompt:
            prompt_parts.insert(2, custom_prompt)
        
        final_prompt = ", ".join(prompt_parts)
        
        # Limiter la longueur du prompt (Runway a une limite)
        if len(final_prompt) > 500:
            final_prompt = final_prompt[:500] + "..."
        
        return final_prompt
    
    async def generate_animation(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer une animation avec Runway Gen-4 Turbo"""
        
        # Extraire les paramètres
        style = animation_data.get("style", "cartoon")
        theme = animation_data.get("theme", "adventure")
        orientation = animation_data.get("orientation", "landscape")
        custom_prompt = animation_data.get("prompt", "")
        title = animation_data.get("title", f"Animation {theme}")
        
        if not self.api_key:
            # Mode simulation pour les tests
            print("🔄 Mode simulation - Pas de clé API Runway")
            
            return {
                "id": f"runway_sim_{int(time.time())}",
                "title": title,
                "description": f"Animation {style} - {theme} (simulation)",
                "video_url": "https://example.com/simulation.mp4",
                "thumbnail_url": None,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": 10,
                "style": style,
                "theme": theme,
                "orientation": orientation
            }
        
        try:
            # Créer le prompt optimisé
            optimized_prompt = self._create_optimized_prompt(
                style, theme, custom_prompt, orientation
            )
            
            # Configuration de l'aspect ratio
            aspect_ratio_map = {
                "landscape": "16:9",
                "portrait": "9:16",
                "square": "1:1"
            }
            aspect_ratio = aspect_ratio_map.get(orientation, "16:9")
            
            # Payload pour Runway Gen-4 Turbo
            payload = {
                "model": "gen4-turbo",
                "prompt": optimized_prompt,
                "duration": 10,
                "aspect_ratio": aspect_ratio,
                "resolution": "720p",
                "motion_control": "balanced",
                "seed": None,
                "watermark": False
            }
            
            print(f"🎬 Génération Runway - Style: {style}, Thème: {theme}")
            print(f"📝 Prompt: {optimized_prompt[:100]}...")
            
            # Appel à l'API Runway
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers=self._get_headers(),
                    json=payload
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    print(f"❌ Erreur Runway API: {response.status_code} - {error_detail}")
                    raise Exception(f"Erreur API Runway: {response.status_code} - {error_detail}")
                
                result = response.json()
                task_id = result.get("id")
                
                if not task_id:
                    raise Exception("ID de tâche manquant dans la réponse Runway")
                
                print(f"⏳ Tâche Runway créée: {task_id}")
                
                # Polling pour attendre la génération
                video_url = await self._wait_for_completion(task_id)
                
                # Retourner le résultat dans le format attendu
                return {
                    "id": task_id,
                    "title": title,
                    "description": f"Animation {style} - {theme}",
                    "video_url": video_url,
                    "thumbnail_url": None,
                    "status": "completed",
                    "created_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "duration": 10,
                    "style": style,
                    "theme": theme,
                    "orientation": orientation
                }
                
        except Exception as e:
            print(f"❌ Erreur génération Runway: {e}")
            raise Exception(f"Erreur lors de la génération avec Runway: {str(e)}")
    
    async def _wait_for_completion(self, task_id: str, max_wait: int = 300) -> str:
        """Attendre la completion de la génération avec polling"""
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers=self._get_headers()
                    )
                    
                    if response.status_code != 200:
                        print(f"⚠️ Erreur polling: {response.status_code}")
                        await asyncio.sleep(5)
                        continue
                    
                    result = response.json()
                    status = result.get("status")
                    
                    print(f"📊 Status Runway: {status}")
                    
                    if status == "completed":
                        video_url = result.get("output", {}).get("video_url")
                        if video_url:
                            print(f"✅ Vidéo générée: {video_url}")
                            return video_url
                        else:
                            raise Exception("URL vidéo manquante dans la réponse")
                    
                    elif status == "failed":
                        error = result.get("error", "Erreur inconnue")
                        raise Exception(f"Génération échouée: {error}")
                    
                    elif status in ["queued", "processing"]:
                        # Continuer à attendre
                        await asyncio.sleep(10)
                    
                    else:
                        print(f"⚠️ Status inconnu: {status}")
                        await asyncio.sleep(5)
                        
            except Exception as e:
                print(f"⚠️ Erreur pendant le polling: {e}")
                await asyncio.sleep(5)
        
        raise Exception(f"Timeout: La génération a pris plus de {max_wait} secondes")
    
    def validate_animation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valider les données d'animation pour Runway"""
        
        errors = []
        
        # Vérifier les champs requis
        if not data.get("style"):
            errors.append("Style requis")
        elif data["style"] not in self.supported_styles:
            errors.append(f"Style non supporté. Styles disponibles: {list(self.supported_styles.keys())}")
        
        if not data.get("theme"):
            errors.append("Thème requis")
        
        if not data.get("orientation"):
            errors.append("Orientation requise")
        elif data["orientation"] not in ["landscape", "portrait", "square"]:
            errors.append("Orientation doit être: landscape, portrait, ou square")
        
        return {
            "isValid": len(errors) == 0,
            "errors": errors
        }

# Instance globale du service
runway_gen4_service = RunwayGen4Service()
