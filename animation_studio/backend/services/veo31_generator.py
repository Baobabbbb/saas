"""
Service de génération vidéo via Veo 3.1 Fast (Runway ML)
Remplace complètement le système Wan 2.5 avec qualité supérieure et audio intégré
Basé sur le workflow zseedance.json mais avec Veo 3.1 Fast
"""

import asyncio
import aiohttp
import time
import os
from typing import List, Dict, Any, Optional
from config import config
from models.schemas import Scene, VideoClip

class Veo31Generator:
    """Service de génération vidéo EXCLUSIF Veo 3.1 Fast avec audio intégré"""

    def __init__(self):
        self.base_url = config.VEO31_BASE_URL
        self.api_key = os.getenv("RUNWAY_API_KEY")  # Utilise RUNWAY_API_KEY au lieu de WAVESPEED_API_KEY
        self.model = config.VEO31_MODEL
        self.default_resolution = "720p"  # Veo 3.1 Fast supporte différentes résolutions

    async def generate_video_clip(self, scene: Scene) -> VideoClip:
        """
        Génère un clip vidéo Veo 3.1 Fast avec audio intégré

        Args:
            scene: Scène à générer

        Returns:
            VideoClip avec URL de la vidéo générée (audio inclus)
        """

        # Adaptation durée Veo 3.1 Fast (max 60s)
        duration = min(int(scene.duration), config.VEO31_MAX_DURATION)
        duration = max(duration, config.VEO31_MIN_DURATION)  # Min 5s

        # Créer le prompt optimisé pour Veo 3.1 Fast
        optimized_prompt = self._create_veo31_optimized_prompt(scene)

        # Préparation paramètres Veo 3.1 Fast
        veo31_params = {
            "prompt": optimized_prompt,
            "model": self.model,
            "duration": duration,
            "ratio": "16:9",  # Format adapté
            "seed": -1  # Seed aléatoire pour variété
        }

        try:
            # Appel API Veo 3.1 Fast
            result = await self._submit_veo31_generation(veo31_params)

            # Créer le VideoClip avec les résultats
            return VideoClip(
                scene_number=scene.scene_number,
                video_url=result["video_url"],
                duration=duration,
                status="completed",
                prompt=optimized_prompt
            )

        except Exception as e:
            print(f"❌ Erreur génération Veo 3.1 Fast scène {scene.scene_number}: {str(e)}")
            return VideoClip(
                scene_number=scene.scene_number,
                video_url="",
                duration=duration,
                status=f"failed: {str(e)}",
                prompt=optimized_prompt
            )

    def _create_veo31_optimized_prompt(self, scene: Scene) -> str:
        """
        Crée un prompt optimisé pour Veo 3.1 Fast
        Focus sur cohérence narrative et continuité visuelle
        """

        # Prompt structuré pour cohérence maximale avec Veo 3.1 Fast
        prompt_parts = [
            f"STYLE: 2D cartoon animation, Disney Pixar style, child-friendly, vibrant colors, smooth fluid animation, expressive characters",
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

    async def _submit_veo31_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Soumet la génération à l'API Veo 3.1 Fast
        """

        url = f"{self.base_url}/video"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            # Soumettre la génération
            async with session.post(url, json=params, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Erreur API Veo 3.1 Fast ({response.status}): {error_text}")

                result = await response.json()

                # Vérifier le format de réponse
                if result.get("status") != "success":
                    raise Exception(f"Erreur API Veo 3.1 Fast: {result.get('message', 'Erreur inconnue')}")

                # Extraire l'ID de la prédiction
                task_id = result.get("task_id")
                if not task_id:
                    raise Exception(f"ID de tâche manquant dans la réponse: {result}")

                print(f"✅ Veo 3.1 Fast génération soumise: {task_id}")

                # Attendre la complétion
                return await self._wait_for_completion(task_id)

    async def _wait_for_completion(self, task_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """
        Attend la completion de la génération Veo 3.1 Fast

        Args:
            task_id: ID de la tâche
            max_attempts: Nombre maximum de tentatives (30 × 15s = 7.5 minutes)

        Returns:
            Dict avec video_url et status
        """

        url = f"{self.base_url}/tasks/{task_id}"
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
                        status = result.get("status")

                        if status == "completed":
                            # Extraire l'URL de la vidéo
                            video_url = result.get("output", {}).get("video_url")
                            if video_url:
                                print(f"✅ Veo 3.1 Fast génération terminée: {video_url[:50]}...")
                                return {
                                    "video_url": video_url,
                                    "status": "completed"
                                }
                            else:
                                raise Exception("Aucune URL vidéo dans la réponse complétée")

                        elif status == "failed":
                            error_msg = result.get("error", "Erreur inconnue")
                            raise Exception(f"Échec génération Veo 3.1 Fast: {error_msg}")

                        elif status in ["pending", "processing"]:
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

        raise Exception(f"Timeout: Génération Veo 3.1 Fast non terminée après {max_attempts * 15}s")

    async def generate_all_clips(self, scenes: List[Scene]) -> List[VideoClip]:
        """
        Génère tous les clips vidéo en parallèle (avec limite)

        Args:
            scenes: Liste des scènes à générer

        Returns:
            Liste des VideoClips générés
        """

        print(f"\n🎬 Génération de {len(scenes)} clips Veo 3.1 Fast...")

        # Générer les clips avec limite de concurrence (2 max pour Veo 3.1 Fast)
        semaphore = asyncio.Semaphore(2)

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
            raise Exception("Aucun clip vidéo n'a pu être généré avec Veo 3.1 Fast")

        return processed_clips
