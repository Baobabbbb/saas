import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from config import config
from models.schemas import Scene, VideoClip

class VideoGenerator:
    """Service de génération vidéo via Wavespeed AI SeedANce"""
    
    def __init__(self):
        self.base_url = config.WAVESPEED_BASE_URL
        self.api_key = config.WAVESPEED_API_KEY
        self.model = config.WAVESPEED_MODEL
    
    async def generate_video_clip(self, scene: Scene) -> VideoClip:
        """Génère un clip vidéo pour une scène donnée via Wavespeed AI"""
        
        # Préparer les paramètres selon l'API Wavespeed (inspiré de zseedance.json)
        req_duration = min(int(scene.duration), config.WAVESPEED_MAX_DURATION)
        video_params = {
            "aspect_ratio": config.VIDEO_ASPECT_RATIO,
            "duration": req_duration,
            "prompt": scene.prompt
        }
        
        try:
            # 1. Soumettre la requête de génération
            video_data = await self._submit_video_generation(video_params)

            # Extraire prediction_id de manière robuste
            prediction_id = None
            if video_data:
                if isinstance(video_data, dict):
                    prediction_id = (
                        video_data.get("data", {}).get("id")
                        or video_data.get("id")
                        or video_data.get("prediction_id")
                        or video_data.get("request_id")
                    )
            if not prediction_id:
                # Essayer d'extraire un id depuis 'raw' ou 'headers'
                if isinstance(video_data, dict):
                    headers_map = video_data.get("headers") or {}
                    for key in ["Prediction-Id", "X-Prediction-Id", "Id", "X-Request-Id", "Request-Id"]:
                        if headers_map.get(key):
                            prediction_id = headers_map[key]
                            break
                    if not prediction_id:
                        location = headers_map.get("Location") or headers_map.get("Content-Location") or headers_map.get("Operation-Location")
                        if location:
                            try:
                                prediction_id = location.rstrip("/").split("/")[-1]
                            except Exception:
                                prediction_id = None
            if not prediction_id:
                raise Exception(f"Réponse invalide de l'API Wavespeed: {video_data}")

            # 2. Petite attente initiale avant polling (laisser le job démarrer)
            await asyncio.sleep(min(20, max(8, int(req_duration))))

            # 3. Récupérer le résultat
            result = await self._get_video_result(prediction_id)

            # Récupérer l'URL vidéo dans différentes structures possibles
            video_url = None
            if isinstance(result, dict):
                video_url = (
                    (result.get("video") or {}).get("url")
                    or (result.get("video") or {}).get("path")
                    or (result.get("output") or {}).get("url")
                    or result.get("video_url")
                    or result.get("url")
                )
                if not video_url and isinstance(result.get("outputs"), list) and result["outputs"]:
                    video_url = result["outputs"][0]
                if not video_url and isinstance(result.get("assets"), list) and result["assets"]:
                    first = result["assets"][0]
                    video_url = first.get("url") if isinstance(first, dict) else first
                if not video_url and isinstance(result.get("data"), dict):
                    video_url = result["data"].get("video_url")

            if not video_url:
                raise Exception(f"Aucun URL vidéo dans le résultat: {result}")

            return VideoClip(
                scene_number=scene.scene_number,
                video_url=video_url,
                duration=req_duration,
                status="completed"
            )
            
        except Exception as e:
            # Retourner un clip d'erreur plutôt que de faire échouer tout le pipeline
            return VideoClip(
                scene_number=scene.scene_number,
                video_url="",
                duration=req_duration,
                status=f"failed: {str(e)}"
            )

    async def _submit_video_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Soumet une requête de génération vidéo à Wavespeed AI (avec fallbacks)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Essayer plusieurs variantes de base_url pour éviter les 404 (docs/versions différentes)
        candidate_bases = list(dict.fromkeys([
            self.base_url.rstrip("/"),
            "https://api.wavespeed.ai/api/v3",
            "https://api.wavespeed.ai/v3",
            "https://api.wavespeed.ai/api/v1",
            "https://api.wavespeed.ai/v1",
            "https://api.wavespeed.ai",
        ]))

        async with aiohttp.ClientSession() as session:
            attempts = []
            for base in candidate_bases:
                attempts.extend([
                    (f"{base}/predictions", {"model": self.model, "input": params}),
                    (f"{base}/{self.model}", params),
                    (f"{base}/jobs", {"model": self.model, **params}),
                    (f"{base}/predict", {"model": self.model, "input": params}),
                ])
            last_error = None
            for url, payload in attempts:
                try:
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status in [200, 201, 202]:
                            # Essayer JSON, sinon texte, sinon extraire depuis les headers (Location, Prediction-Id...)
                            try:
                                parsed = await response.json()
                                if parsed:
                                    return parsed
                            except Exception:
                                pass
                            text = await response.text()
                            if text:
                                return {"raw": text, "http_status": response.status, "headers": dict(response.headers)}
                            # Corps vide: tenter d'extraire l'ID depuis les headers
                            headers_map = {k: v for k, v in response.headers.items()}
                            possible_keys = [
                                "Prediction-Id", "X-Prediction-Id", "Id", "X-Request-Id",
                                "Request-Id", "X-Operation-Id"
                            ]
                            for key in possible_keys:
                                if key in headers_map and headers_map[key]:
                                    return {"id": headers_map[key], "headers": headers_map, "http_status": response.status}
                            # Location / Operation-Location peuvent pointer vers /predictions/{id}
                            for loc_key in ["Location", "Content-Location", "Operation-Location"]:
                                loc = headers_map.get(loc_key)
                                if loc and isinstance(loc, str):
                                    # Extraire la dernière partie de l'URL comme ID
                                    try:
                                        candidate_id = loc.rstrip("/").split("/")[-1]
                                        if candidate_id:
                                            return {"id": candidate_id, "headers": headers_map, "http_status": response.status}
                                    except Exception:
                                        pass
                            # Rien trouvé
                            return {"raw": text, "http_status": response.status, "headers": dict(response.headers)}
                        else:
                            last_error = f"HTTP {response.status} - " + (await response.text())
                except Exception as e:
                    last_error = str(e)
            raise Exception(f"Soumission Wavespeed échouée: {last_error}")

    async def _get_video_result(self, prediction_id: str) -> Dict[str, Any]:
        """Récupère le résultat d'une génération vidéo"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        max_retries = 50
        retry_delay = 12  # secondes
        
        for attempt in range(max_retries):
            async with aiohttp.ClientSession() as session:
                candidate_bases = list(dict.fromkeys([
                    self.base_url.rstrip("/"),
                    "https://api.wavespeed.ai/api/v3",
                    "https://api.wavespeed.ai/v3",
                    "https://api.wavespeed.ai/api/v1",
                    "https://api.wavespeed.ai/v1",
                    "https://api.wavespeed.ai",
                ]))
                urls = []
                for base in candidate_bases:
                    urls.extend([
                        f"{base}/predictions/{prediction_id}",
                        f"{base}/predictions/{prediction_id}/result",
                        f"{base}/jobs/{prediction_id}",
                        f"{base}/prediction/{prediction_id}",
                    ])
                for url in urls:
                    try:
                        async with session.get(url, headers=headers) as response:
                            if response.status in [200, 201, 202]:
                                try:
                                    result = await response.json()
                                except Exception:
                                    text = await response.text()
                                    result = {"raw": text}
                                # Vérifier si la génération est terminée
                                status = (
                                    (result.get("status") if isinstance(result, dict) else None)
                                    or (result.get("state") if isinstance(result, dict) else None)
                                    or (result.get("job", {}).get("status") if isinstance(result, dict) else None)
                                )
                                if status in ["completed", "succeeded", "success", "done"] or "outputs" in result or "video" in result or "video_url" in result:
                                    return result
                                elif status in ["failed", "error"]:
                                    raise Exception(f"Génération vidéo échouée: {result.get('error', 'Erreur inconnue')}")
                            # Sinon essayer l'URL suivante
                    except Exception:
                        continue
                # Si aucun endpoint n'a conclu, attendre et réessayer
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
        
        raise Exception("Timeout: La génération vidéo n'a pas abouti dans les temps")

    async def generate_all_clips(self, scenes: List[Scene]) -> List[VideoClip]:
        """Génère tous les clips vidéo pour une liste de scènes"""
        
        clips = []
        
        # Générer les clips en parallèle avec limitation pour éviter la surcharge
        semaphore = asyncio.Semaphore(1)  # 1 simultanée pour éviter rate-limit / timeouts
        
        async def generate_with_semaphore(scene: Scene) -> VideoClip:
            async with semaphore:
                return await self.generate_video_clip(scene)
        
        # Créer les tâches
        tasks = [generate_with_semaphore(scene) for scene in scenes]
        
        # Exécuter toutes les tâches
        clips = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter les résultats et les exceptions
        final_clips = []
        for i, result in enumerate(clips):
            if isinstance(result, Exception):
                # Créer un clip d'erreur
                final_clips.append(VideoClip(
                    scene_number=scenes[i].scene_number,
                    video_url="",
                    duration=scenes[i].duration,
                    status=f"failed: {str(result)}"
                ))
            else:
                final_clips.append(result)
        
        return final_clips

    async def validate_video_url(self, url: str) -> bool:
        """Valide qu'une URL vidéo est accessible"""
        if not url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    return response.status == 200
        except:
            return False

    def get_estimated_generation_time(self, scenes: List[Scene]) -> int:
        """Estime le temps de génération total en secondes"""
        
        # Temps de base par scène (basé sur l'expérience avec SeedANce)
        base_time_per_scene = 120  # 2 minutes par scène en moyenne
        
        # Temps supplémentaire selon la durée de la scène
        duration_factor = sum(scene.duration for scene in scenes) * 2
        
        # Temps de traitement parallèle (avec limitation à 3 simultanés)
        parallel_factor = max(1, len(scenes) / 3)
        
        total_time = (base_time_per_scene * parallel_factor) + duration_factor
        
        return int(total_time) 