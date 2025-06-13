"""
Service Veo3 adapté pour l'API fal-ai
Génération de vidéos courtes à partir de prompts texte
"""

import os
import asyncio
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime

class Veo3FalService:
    """Service de génération vidéo Veo3 via fal-ai"""
    
    def __init__(self):
        self.api_key = os.getenv("FAL_API_KEY")
        self.base_url = os.getenv("FAL_BASE_URL", "https://queue.fal.run")
        self.endpoint = "fal-ai/veo3"
        
        if not self.api_key:
            raise ValueError("FAL_API_KEY manquante dans les variables d'environnement")
        
        # Configuration par défaut
        self.default_config = {
            "aspect_ratio": "16:9",  # 16:9, 9:16, 1:1
            "duration": "8s",        # Durée fixe 8 secondes
            "generate_audio": True,  # Audio activé par défaut
            "enhance_prompt": True   # Amélioration automatique du prompt
        }
        
        print(f"🎬 Service Veo3 fal-ai initialisé")
        print(f"📡 Base URL: {self.base_url}")
        print(f"🔗 Endpoint: {self.endpoint}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers pour l'authentification fal-ai"""
        return {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_video(
        self, 
        prompt: str, 
        aspect_ratio: str = "16:9",
        generate_audio: bool = True,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une vidéo à partir d'un prompt
        
        Args:
            prompt: Description de la vidéo à générer
            aspect_ratio: Format (16:9, 9:16, 1:1)
            generate_audio: Générer l'audio (false = -33% crédits)
            seed: Seed pour reproductibilité
            negative_prompt: Ce qu'on ne veut pas voir
        
        Returns:
            Dict contenant l'URL de la vidéo générée
        """
        try:
            print(f"🎬 Génération vidéo Veo3 via fal-ai...")
            print(f"📝 Prompt: {prompt[:100]}...")
            print(f"📐 Aspect ratio: {aspect_ratio}")
            print(f"🔊 Audio: {generate_audio}")
            
            # Préparation des données de requête
            request_data = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "duration": self.default_config["duration"],
                "generate_audio": generate_audio,
                "enhance_prompt": self.default_config["enhance_prompt"]
            }
            
            # Ajout optionnel du seed
            if seed:
                request_data["seed"] = seed
                print(f"🎲 Seed: {seed}")
              # Ajout optionnel du prompt négatif
            if negative_prompt:
                request_data["negative_prompt"] = negative_prompt
                print(f"🚫 Negative prompt: {negative_prompt[:50]}...")
            
            # 1. Lancement de la génération asynchrone
            async with httpx.AsyncClient(timeout=30.0) as client:
                submit_url = f"{self.base_url}/{self.endpoint}"
                print(f"📤 Soumission requête: {submit_url}")
                
                response = await client.post(
                    submit_url,
                    headers=self._get_headers(),
                    json=request_data
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    if "Exhausted balance" in error_text:
                        raise Exception(f"Quota fal-ai épuisé. Veuillez recharger votre compte sur fal.ai/dashboard/billing")
                    else:
                        raise Exception(f"Erreur soumission: {response.status_code} - {error_text}")
                
                submission_result = response.json()
                request_id = submission_result.get("request_id")
                
                if not request_id:
                    raise Exception("Pas de request_id retourné")
                
                print(f"✅ Requête soumise, ID: {request_id}")
                
                # 2. Attente et polling du statut
                result = await self._poll_for_completion(request_id)
                
                return result
                
        except Exception as e:
            print(f"❌ Erreur génération vidéo Veo3: {e}")
            raise
    
    async def _poll_for_completion(self, request_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """
        Attend la complétion de la génération vidéo
        
        Args:
            request_id: ID de la requête
            max_wait_time: Temps d'attente maximum en secondes
        
        Returns:
            Résultat de la génération
        """
        start_time = datetime.now()
        polling_interval = 5  # Vérification toutes les 5 secondes
        
        print(f"⏳ Attente de la génération (max {max_wait_time}s)...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                # Vérification du timeout
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > max_wait_time:
                    raise Exception(f"Timeout: génération non terminée après {max_wait_time}s")
                
                # Vérification du statut
                status_url = f"{self.base_url}/{self.endpoint}/requests/{request_id}/status"
                
                try:
                    status_response = await client.get(
                        status_url,
                        headers=self._get_headers()
                    )
                    
                    if status_response.status_code != 200:
                        print(f"⚠️ Erreur status: {status_response.status_code}")
                        await asyncio.sleep(polling_interval)
                        continue
                    
                    status_data = status_response.json()
                    status = status_data.get("status")
                    
                    print(f"📊 Status: {status} (temps écoulé: {elapsed:.1f}s)")
                    
                    if status == "COMPLETED":
                        # Récupération du résultat
                        result_url = f"{self.base_url}/{self.endpoint}/requests/{request_id}"
                        result_response = await client.get(
                            result_url,
                            headers=self._get_headers()
                        )
                        
                        if result_response.status_code != 200:
                            raise Exception(f"Erreur récupération résultat: {result_response.status_code}")
                        
                        result = result_response.json()
                        
                        # Extraction de l'URL vidéo
                        video_data = result.get("video")
                        if not video_data or not video_data.get("url"):
                            raise Exception("Pas d'URL vidéo dans le résultat")
                        
                        video_url = video_data["url"]
                        file_size = video_data.get("file_size", 0)
                        
                        print(f"✅ Vidéo générée avec succès!")
                        print(f"🎥 URL: {video_url}")
                        print(f"📊 Taille: {file_size / 1024 / 1024:.1f} MB")
                        
                        return {
                            "video_url": video_url,
                            "file_size": file_size,
                            "request_id": request_id,
                            "generation_time": elapsed
                        }
                    
                    elif status == "FAILED":
                        raise Exception("Génération échouée")
                    
                    elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                        # Attente avant la prochaine vérification
                        await asyncio.sleep(polling_interval)
                        continue
                    
                    else:
                        print(f"⚠️ Status inconnu: {status}")
                        await asyncio.sleep(polling_interval)
                        continue
                        
                except Exception as e:
                    print(f"⚠️ Erreur lors du polling: {e}")
                    await asyncio.sleep(polling_interval)
                    continue
    
    async def generate_animation_from_comic(
        self, 
        comic_data: Dict[str, Any],
        orientation: str = "portrait"
    ) -> Dict[str, Any]:
        """
        Génère une animation à partir des données d'une BD
        
        Args:
            comic_data: Données de la BD avec title, scenes, etc.
            orientation: portrait ou landscape
        
        Returns:
            Données de l'animation générée
        """
        try:
            print(f"🎬 Génération d'animation à partir de la BD...")
            
            # Extraction des informations de la BD
            title = comic_data.get("title", "Animation")
            scenes = comic_data.get("scenes", [])
            
            if not scenes:
                raise ValueError("Aucune scène trouvée dans la BD")
            
            # Construction du prompt global pour l'animation
            prompt_parts = [f"Animation style cartoon pour '{title}'."]
            
            # Ajout des descriptions de scènes
            for i, scene in enumerate(scenes[:3]):  # Max 3 scènes pour rester cohérent
                description = scene.get("description", "")
                if description:
                    prompt_parts.append(f"Scène {i+1}: {description}")
            
            # Ajout de contexte pour l'animation
            prompt_parts.extend([
                "Style: Animation fluide, couleurs vives, adapté aux enfants.",
                "Mouvement: Transitions douces entre les scènes, personnages expressifs.",
                "Qualité: Haute définition, style professionnel."
            ])
            
            animation_prompt = " ".join(prompt_parts)
            
            # Détermination de l'aspect ratio
            aspect_ratio = "9:16" if orientation == "portrait" else "16:9"
            
            # Génération de l'animation
            result = await self.generate_video(
                prompt=animation_prompt,
                aspect_ratio=aspect_ratio,
                generate_audio=True,  # Audio pour les animations
                seed=comic_data.get("seed")  # Utilise le même seed que la BD
            )
            
            # Enrichissement du résultat
            result.update({
                "title": title,
                "source_comic": comic_data.get("title"),
                "orientation": orientation,
                "scene_count": len(scenes)
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération animation: {e}")
            raise
    
    async def close(self):
        """Nettoyage des ressources"""
        print("🧹 Nettoyage service Veo3 fal-ai")
        # Pas de ressources à nettoyer pour httpx.AsyncClient en context manager


# Instance globale du service
veo3_fal_service = Veo3FalService()
