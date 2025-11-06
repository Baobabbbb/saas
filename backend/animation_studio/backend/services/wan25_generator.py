"""
Service de génération vidéo via Wan 2.5 (Alibaba)
Remplace complètement le système Seedance avec audio intégré
Basé sur la documentation: https://wavespeed.ai/docs/docs-api/alibaba/alibaba-wan-2.5-text-to-video-fast
"""

import asyncio
import aiohttp
import os
import time
from typing import List, Dict, Any, Optional
from ...config import WAN25_MODEL, WAN25_BASE_URL, WAN25_DEFAULT_RESOLUTION
from models.schemas import Scene, VideoClip

class Wan25Generator:
    """Service de génération vidéo EXCLUSIF Wan 2.5 avec audio intégré"""
    
    def __init__(self):
        self.base_url = WAN25_BASE_URL
        self.api_key = os.getenv("WAVESPEED_API_KEY")
        self.model = WAN25_MODEL
        self.default_resolution = WAN25_DEFAULT_RESOLUTION
        
    async def generate_video_clip(self, scene: Scene) -> VideoClip:
        """
        Génère un clip vidéo Wan 2.5 avec audio intégré
        
        Args:
            scene: Scène à générer
            
        Returns:
            VideoClip avec URL de la vidéo générée (audio inclus)
        """
        
        # Adaptation durée Wan 2.5 (max 10s)
        duration = min(int(scene.duration), config.WAN25_MAX_DURATION)
        duration = max(duration, config.WAN25_MIN_DURATION)  # Min 5s
        
        # Créer le prompt optimisé pour Wan 2.5
        optimized_prompt = self._create_wan25_optimized_prompt(scene)
        
        # Préparation paramètres Wan 2.5 selon la documentation
        wan25_params = {
            "prompt": optimized_prompt,
            "negative_prompt": config.WAN25_NEGATIVE_PROMPT,
            "size": self._resolution_to_size(self.default_resolution),
            "duration": duration,
            "enable_prompt_expansion": True,  # Optimisation automatique du prompt
            "seed": -1  # Seed aléatoire pour variété
        }
        
        # Note: Audio intégré automatiquement par Wan 2.5
        # Pas besoin de paramètre audio séparé
        
        try:
            # Appel API Wan 2.5
            result = await self._submit_wan25_generation(wan25_params)
            
            # Créer le VideoClip avec les résultats
            return VideoClip(
                scene_number=scene.scene_number,
                video_url=result["video_url"],
                duration=duration,
                status="completed",
                prompt=optimized_prompt
            )
            
        except Exception as e:
            print(f"❌ Erreur génération Wan 2.5 scène {scene.scene_number}: {str(e)}")
            return VideoClip(
                scene_number=scene.scene_number,
                video_url="",
                duration=duration,
                status=f"failed: {str(e)}",
                prompt=optimized_prompt
            )
    
    def _create_wan25_optimized_prompt(self, scene: Scene) -> str:
        """
        Crée un prompt optimisé pour Wan 2.5
        Focus sur cohérence narrative et continuité visuelle
        """
        
        # Prompt structuré pour cohérence maximale
        prompt_parts = [
            f"STYLE: {config.WAN25_PROMPT_STYLE}",
            f"SCENE: {scene.description}",
            f"ACTION: {scene.action}",
            f"SETTING: {scene.environment}",
            f"CHARACTERS: {scene.characters}",
            "CAMERA: smooth cinematic camera movement, dynamic angle",
            "MOOD: child-friendly, joyful, engaging, colorful",
            "CONTINUITY: maintain visual consistency with previous scenes"
        ]
        
        # Ajouter contexte audio si disponible
        if hasattr(scene, 'audio_description') and scene.audio_description:
            prompt_parts.append(f"AUDIO SYNC: {scene.audio_description}")
        
        return " | ".join(prompt_parts)
    
    def _resolution_to_size(self, resolution: str) -> str:
        """Convertit résolution en format Wan 2.5 (widthheight)"""
        return config.WAN25_RESOLUTIONS.get(resolution, "1280*720")
    
    async def _submit_wan25_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Soumet la génération à l'API Wan 2.5
        
        Endpoints selon documentation:
        - POST: https://api.wavespeed.ai/api/v3/alibaba/wan-2.5/text-to-video-fast
        - GET: https://api.wavespeed.ai/api/v3/predictions/{requestId}/result
        """
        
        url = f"{self.base_url}/alibaba/wan-2.5/text-to-video-fast"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            # Soumettre la génération
            async with session.post(url, json=params, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Erreur API Wan 2.5 ({response.status}): {error_text}")
                
                result = await response.json()
                
                # Vérifier le format de réponse
                if result.get("code") != 200:
                    raise Exception(f"Erreur API Wan 2.5: {result.get('message', 'Erreur inconnue')}")
                
                # Extraire l'ID de la prédiction
                request_id = result.get("data", {}).get("id")
                if not request_id:
                    raise Exception(f"ID de prédiction manquant dans la réponse: {result}")
                
                print(f"✅ Wan 2.5 génération soumise: {request_id}")
                
                # Attendre la complétion
                return await self._wait_for_completion(request_id)
    
    async def _wait_for_completion(self, request_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """
        Attend la completion de la génération Wan 2.5
        
        Args:
            request_id: ID de la prédiction
            max_attempts: Nombre maximum de tentatives (30 × 15s = 7.5 minutes)
            
        Returns:
            Dict avec video_url et status
        """
        
        url = f"{self.base_url}/predictions/{request_id}/result"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for attempt in range(max_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            print(f"⚠️ Tentative {attempt + 1}/{max_attempts}: Status {response.status}")
                            await asyncio.sleep(15)
                            continue
                        
                        result = await response.json()
                        data = result.get("data", {})
                        status = data.get("status")
                        
                        if status == "completed":
                            # Extraire l'URL de la vidéo
                            outputs = data.get("outputs", [])
                            if outputs and len(outputs) > 0:
                                video_url = outputs[0]
                                print(f"✅ Wan 2.5 génération terminée: {video_url[:50]}...")
                                return {
                                    "video_url": video_url,
                                    "status": "completed"
                                }
                            else:
                                raise Exception("Aucune sortie vidéo dans la réponse complétée")
                        
                        elif status == "failed":
                            error_msg = data.get("error", "Erreur inconnue")
                            raise Exception(f"Échec génération Wan 2.5: {error_msg}")
                        
                        elif status in ["created", "processing"]:
                            print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Génération en cours ({status})...")
                            await asyncio.sleep(15)  # Attendre 15s entre chaque vérification
                            continue
                        
                        else:
                            print(f"⚠️ Status inconnu: {status}")
                            await asyncio.sleep(15)
                            continue
                            
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                print(f"⚠️ Erreur tentative {attempt + 1}: {str(e)}")
                await asyncio.sleep(15)
        
        raise Exception(f"Timeout: Génération Wan 2.5 non terminée après {max_attempts * 15}s")
    
    async def generate_all_clips(self, scenes: List[Scene]) -> List[VideoClip]:
        """
        Génère tous les clips vidéo en parallèle (avec limite)
        
        Args:
            scenes: Liste des scènes à générer
            
        Returns:
            Liste des VideoClips générés
        """
        
        print(f"\n🎬 Génération de {len(scenes)} clips Wan 2.5...")
        
        # Générer les clips avec limite de concurrence (3 max en parallèle)
        semaphore = asyncio.Semaphore(3)
        
        async def generate_with_semaphore(scene: Scene) -> VideoClip:
            async with semaphore:
                print(f"🎥 Génération clip {scene.scene_number}/{len(scenes)}...")
                return await self.generate_video_clip(scene)
        
        # Générer tous les clips en parallèle (avec limite)
        clips = await asyncio.gather(
            *[generate_with_semaphore(scene) for scene in scenes],
            return_exceptions=True
        )
        
        # Traiter les résultats et exceptions
        processed_clips = []
        for i, clip in enumerate(clips):
            if isinstance(clip, Exception):
                print(f"❌ Erreur clip {i + 1}: {str(clip)}")
                # Créer un clip d'erreur
                processed_clips.append(VideoClip(
                    scene_number=i + 1,
                    video_url="",
                    duration=10,
                    status=f"failed: {str(clip)}",
                    prompt=""
                ))
            else:
                processed_clips.append(clip)
        
        # Vérifier qu'au moins un clip est valide
        valid_clips = [c for c in processed_clips if c.status == "completed"]
        print(f"\n✅ {len(valid_clips)}/{len(scenes)} clips générés avec succès")
        
        if not valid_clips:
            raise Exception("Aucun clip vidéo n'a pu être généré avec Wan 2.5")
        
        return processed_clips

