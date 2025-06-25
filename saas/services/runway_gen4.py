"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Compatible avec l'API officielle Runway ML
Documentation: https://docs.dev.runwayml.com/
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
        else:
            print(f"🔑 Clé API Runway détectée: {self.api_key[:20]}...")
        
        # Configuration par défaut pour Gen-4 Turbo
        self.default_config = {
            "model": "gen4_turbo",       # Modèle officiel Runway
            "duration": 5,               # 5 ou 10 secondes (5 par défaut)
            "ratio": "1280:720",         # 16:9 ratio
            "seed": None
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
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
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
            "space": "space adventure with astronauts, planets, and cosmic wonders",
            "underwater": "underwater adventure with colorful fish and sea creatures",
            "forest": "enchanted forest with magical creatures and talking animals",
            "superhero": "child-friendly superhero saving the day with kindness and courage"
        }
        
        # Styles pour Runway
        style_prompt = self.supported_styles.get(style, self.supported_styles["cartoon"])
        theme_prompt = theme_prompts.get(theme, "fun adventure")
        
        # Construire le prompt final
        if custom_prompt and custom_prompt.strip():
            final_prompt = f"{style_prompt}, {theme_prompt}, {custom_prompt.strip()}"
        else:
            final_prompt = f"{style_prompt}, {theme_prompt}"
        
        # Ajouter des directives pour enfants
        final_prompt += ", suitable for children, bright colors, joyful atmosphere, smooth movement, high quality"
        
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
                "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_720x480_1mb.mp4",
                "thumbnail_url": None,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": 5,
                "style": style,
                "theme": theme,
                "orientation": orientation
            }
        
        try:
            # Créer le prompt optimisé
            optimized_prompt = self._create_optimized_prompt(
                style, theme, custom_prompt, orientation
            )
            
            # Configuration du ratio selon l'orientation
            ratio_map = {
                "landscape": "1280:720",  # 16:9
                "portrait": "720:1280",   # 9:16
                "square": "720:720"       # 1:1
            }
            ratio = ratio_map.get(orientation, "1280:720")
            
            # Pour Runway Gen-4 Turbo, nous avons besoin d'une image de base
            # Pour du text-to-video pur, nous pourrions d'abord générer une image
            # ou utiliser une image de base simple
            
            # Payload pour Runway Gen-4 Turbo
            payload = {
                "model": "gen4_turbo",
                "promptText": optimized_prompt,
                "ratio": ratio,
                "duration": 5,  # 5 secondes par défaut
                "seed": None
            }
            
            # Si nous avons une image de base, nous pouvons l'ajouter
            # Pour l'instant, nous utilisons text-to-video (si supporté)
            # ou nous pourrions générer une image d'abord
            
            print(f"🎬 Génération Runway - Style: {style}, Thème: {theme}")
            print(f"📝 Prompt: {optimized_prompt[:100]}...")
            
            # Appel à l'API Runway (endpoint text-to-video ou image-to-video)
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Essayons d'abord avec image-to-video en utilisant une image générique
                response = await client.post(
                    f"{self.base_url}/image_to_video",
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
                
                return {
                    "id": task_id,
                    "title": title,
                    "description": f"Animation {style} - {theme}",
                    "video_url": video_url,
                    "thumbnail_url": None,
                    "status": "completed",
                    "created_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "duration": 5,
                    "style": style,
                    "theme": theme,
                    "orientation": orientation
                }
                
        except Exception as e:
            print(f"❌ Erreur génération Runway: {str(e)}")
            raise Exception(f"Erreur lors de la génération avec Runway: {str(e)}")

    async def _wait_for_completion(self, task_id: str, max_wait: int = 600) -> str:
        """Attend la completion d'une tâche Runway"""
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers=self._get_headers()
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Erreur status Runway: {response.status_code}")
                        await asyncio.sleep(5)
                        continue
                    
                    result = response.json()
                    status = result.get("status")
                    
                    print(f"📊 Status Runway: {status}")
                    
                    if status == "SUCCEEDED":
                        video_url = result.get("output", {}).get("url")
                        if video_url:
                            print(f"✅ Vidéo Runway générée: {video_url}")
                            return video_url
                        else:
                            raise Exception("URL vidéo manquante dans la réponse")
                    
                    elif status == "FAILED":
                        error_msg = result.get("error", "Erreur inconnue")
                        raise Exception(f"Génération échouée: {error_msg}")
                    
                    # En cours, attendre
                    await asyncio.sleep(10)
                    
            except Exception as e:
                print(f"❌ Erreur polling: {str(e)}")
                await asyncio.sleep(5)
        
        raise Exception("Timeout: La génération a pris trop de temps")

    def get_animation_status(self, animation_id: str) -> Dict[str, Any]:
        """Récupère le statut d'une animation"""
        # Pour la compatibilité avec l'API existante
        return {
            "id": animation_id,
            "status": "completed",
            "progress": 100
        }

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

# Instance globale
runway_gen4_service = RunwayGen4Service()
