"""
Service de génération d'animations avec Runway ML Veo 3.1 Fast basé exactement sur le workflow zseedance.json
Implémentation fidèle au workflow n8n avec Veo 3.1 Fast pour la génération vidéo
"""

import asyncio
import aiohttp
import json
import logging
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class Sora2ZseedanceGenerator:
    """
    Générateur d'animations utilisant Runway ML Veo 3.1 Fast en suivant exactement le workflow zseedance.json
    Workflow optimisé : Ideas → Prompts → Clips Veo 3.1 Fast (avec audio intégré) → Sequence
    Note: Veo 3.1 Fast génère automatiquement l'audio, pas besoin d'ajout séparé
    """

    def __init__(self):
        # Configuration basée sur les variables d'environnement existantes
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.text_model = os.getenv("TEXT_MODEL", "gpt-4o-mini")

        # Vérification détaillée de la clé Runway
        runway_key = os.getenv("RUNWAY_API_KEY")
        logger.info(f"🔑 Initialisation Runway ML Veo 3.1 Fast - RUNWAY_API_KEY: {'présente' if runway_key else 'ABSENTE'}")
        if runway_key:
            logger.info(f"🔑 Format clé: {'✅ OK (key_)' if runway_key.startswith('key_') else '❌ ERREUR format'}")
            logger.info(f"🔑 Longueur: {len(runway_key)} caractères")

        # Configuration Runway ML Veo 3.1 Fast - text-to-video via /v1/text_to_video
        self.sora_platforms = {
            "openai": {
                "name": "OpenAI (Non disponible)",
                "base_url": "https://api.openai.com/v1",
                "api_key": self.openai_api_key,
                "model": "veo3.1_fast",  # Modèle Veo 3.1 Fast
                "available": False,  # Désactivé car pas disponible publiquement
                "priority": 99  # Priorité très basse
            },
            "runway": {
                "name": "Runway ML (Veo 3.1 Fast)",
                "base_url": "https://api.dev.runwayml.com",
                "api_key": runway_key,
                "model": "veo3.1_fast",  # Veo 3.1 Fast - text-to-video natif
                "available": bool(runway_key and runway_key.startswith('key_')),
                "priority": 1  # Priorité la plus haute maintenant
            },
            "pika": {
                "name": "Pika Labs (Alternative)",
                "base_url": "https://api.pika.art/v1",
                "api_key": os.getenv("PIKA_API_KEY"),
                "model": "pika-1.0",  # Modèle réel Pika
                "available": bool(os.getenv("PIKA_API_KEY")),
                "priority": 3
            }
        }

        # Sélectionner la plateforme disponible avec la priorité la plus haute
        self.selected_platform = self._select_best_platform()

        # Configuration Veo 3.1 Fast optimisée pour enfants (identique à zseedance)
        self.sora2_config = {
            "aspect_ratio": "9:16",  # Format vertical comme zseedance
            "duration_per_clip": 10,  # 10 secondes par clip comme zseedance
            "resolution": "480p",     # Résolution comme zseedance
            "style": "2D cartoon animation, Disney Pixar style, child-friendly, vibrant colors, smooth fluid animation, expressive characters",
            "negative_prompt": "blurry, low quality, distorted, violent, scary, static, motionless, dark, horror"
        }

        logger.info(f"🎬 Sora2ZseedanceGenerator initialisé avec plateforme: {self.selected_platform}")
        logger.info(f"🔧 Plateformes disponibles: {[name for name, config in self.sora_platforms.items() if config['available']]}")
        logger.info(f"🔑 RUNWAY_API_KEY détectée: {bool(os.getenv('RUNWAY_API_KEY'))}")
        if os.getenv('RUNWAY_API_KEY'):
            key = os.getenv('RUNWAY_API_KEY')
            logger.info(f"🔑 Format clé Runway: {'✅ OK' if key.startswith('key_') else '❌ ERREUR'}")
            logger.info(f"🔑 Longueur clé Runway: {len(key)} caractères")
        logger.info(f"🔑 FAL_API_KEY détectée: {bool(os.getenv('FAL_API_KEY'))}")
        if os.getenv('FAL_API_KEY'):
            fal_key = os.getenv('FAL_API_KEY')
            logger.info(f"🔑 Longueur clé FAL: {len(fal_key)} caractères")

    def _select_best_platform(self) -> str:
        """Sélectionne la plateforme Veo 3.1 Fast disponible avec la priorité la plus haute"""
        available_platforms = [
            (name, config) for name, config in self.sora_platforms.items()
            if config["available"]
        ]

        if not available_platforms:
            logger.error("❌ Aucune plateforme Veo 3.1 Fast disponible - vérifiez les clés API")
            raise Exception("Aucune plateforme Veo 3.1 Fast disponible - configurez RUNWAY_API_KEY")

        # Trier par priorité
        available_platforms.sort(key=lambda x: x[1]["priority"])
        best_platform = available_platforms[0][0]

        logger.info(f"✅ Plateforme Veo 3.1 Fast sélectionnée: {best_platform}")
        return best_platform

    async def generate_ideas_agent_adapted(self, theme: str = "space") -> Dict[str, Any]:
        """
        Ideas AI Agent - Génère une idée créative adaptée au thème choisi par l'utilisateur
        Inspiré de zseedance.json mais adapté aux thèmes enfants
        """
        try:
            # Adaptation des thèmes pour les enfants
            theme_adaptations = {
                "space": {
                    "subject": "space adventure with friendly aliens",
                    "environment": "cosmic setting with planets and stars",
                    "sound": "cosmic hums, gentle space winds, magical chimes",
                    "style": "child-friendly space exploration"
                },
                "ocean": {
                    "subject": "magical underwater adventure",
                    "environment": "beautiful ocean with coral reefs and sea creatures",
                    "sound": "gentle ocean waves, friendly sea creature calls, magical bubbles",
                    "style": "whimsical underwater exploration"
                },
                "forest": {
                    "subject": "enchanted forest adventure with magical creatures",
                    "environment": "mystical forest with glowing trees and magical creatures",
                    "sound": "gentle forest winds, magical creature whispers, enchanted chimes",
                    "style": "magical forest exploration for children"
                },
                "adventure": {
                    "subject": "exciting adventure with heroes and discoveries",
                    "environment": "magical world full of wonders and discoveries",
                    "sound": "adventurous music, heroic sounds, discovery chimes",
                    "style": "epic adventure suitable for children"
                },
                "fantasy": {
                    "subject": "magical fantasy world with wizards and dragons",
                    "environment": "enchanted kingdom with castles and magical creatures",
                    "sound": "magical spells, dragon roars (gentle), enchanted music",
                    "style": "child-friendly fantasy adventure"
                },
                "animals": {
                    "subject": "cute animals having fun adventures together",
                    "environment": "beautiful nature setting with friendly animals",
                    "sound": "happy animal sounds, playful music, joyful chimes",
                    "style": "cute animal adventure for children"
                }
            }

            # Récupérer l'adaptation du thème ou utiliser une valeur par défaut
            theme_config = theme_adaptations.get(theme.lower(), theme_adaptations["space"])

            # Prompt système strict pour forcer du JSON valide
            system_prompt = f"""You are a JSON generator for children's animation story ideas.

Create a magical animated story concept for: {theme_config['subject']}

REQUIREMENTS:
- Suitable for children 4-10 years old
- Friendly, positive characters only
- No scary elements, violence, or danger
- Focus on wonder, discovery, friendship, joy
- Colorful, magical animation style
- 3-5 friendly characters or creatures
- Complete story with beginning, middle, happy ending

OUTPUT: Return ONLY valid JSON with this exact structure:
{{
  "Caption": "🎬 [Short title with emoji] #adventure #magic #friendship",
  "Idea": "[2-3 sentence complete story description]",
  "Environment": "[Magical {theme_config['style']} setting]",
  "Sound": "{theme_config['sound']}, happy children's music, joyful sounds",
  "Status": "for children"
}}"""

            # Générer l'idée avec GPT-4o-mini
            try:
                from config import OPENAI_API_KEY, TEXT_MODEL
                if not OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY manquante")

                import openai
                client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

                response = await client.chat.completions.create(
                    model=TEXT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Create a magical animated story idea for children about {theme_config['subject']}."}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=600,
                    temperature=0.8
                )

                # Analyser la réponse pour extraire le JSON
                content = response.choices[0].message.content.strip()
                logger.info(f"🤖 Idée générée: {content[:100]}...")

                # Essayer de parser le JSON
                try:
                    idea_data = json.loads(content)
                    return idea_data
                except json.JSONDecodeError:
                    logger.error(f"Erreur parsing JSON OpenAI: réponse invalide")
                    raise Exception(f"OpenAI API a retourné un JSON invalide pour le thème '{theme}'")

            except Exception as api_error:
                logger.error(f"Erreur API OpenAI: {api_error}")
                raise Exception(f"Échec génération idée pour thème '{theme}': {api_error}")

        except Exception as e:
            logger.error(f"Erreur génération idée adaptée: {e}")
            raise Exception(f"Échec génération idée pour thème '{theme}': {e}")

    async def generate_prompts_agent_adapted(self, idea_data: Dict[str, Any], num_scenes: int = 3) -> Dict[str, Any]:
        """
        Prompts AI Agent - Crée un nombre variable de scènes détaillées pour l'animation
        Adapté pour les enfants et génère des scènes cohérentes formant une histoire complète
        """
        try:
            # Créer la liste des scènes attendues
            scenes_keys = [f"Scene {i+1}" for i in range(num_scenes)]

            # Prompt système strict pour forcer du JSON valide
            system_prompt = f"""You are a JSON generator for children's animation scenes.

STORY: {idea_data['Idea']}
ENVIRONMENT: {idea_data['Environment']}
SOUND: {idea_data['Sound']}

Create {num_scenes} detailed scene descriptions for a children's animated story.
Each scene is exactly 10 seconds long and they form a complete story arc.

REQUIREMENTS:
- Magical, colorful, child-friendly content only
- Positive emotions, friendship, discovery, joy
- Disney/Pixar style 2D animation
- Vibrant colors, magical effects, expressive characters
- No scary elements or negative emotions

OUTPUT: Return ONLY valid JSON with this exact structure:
{{
  "Idea": "{idea_data['Idea']}",
  "Environment": "{idea_data['Environment']}",
  "Sound": "{idea_data['Sound']}",
  {', '.join([f'"{key}": "Detailed description for {key.lower()}"' for key in scenes_keys])}
}}"""

            # Générer les scènes avec GPT-4o-mini
            try:
                from config import OPENAI_API_KEY, TEXT_MODEL
                if not OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY manquante")

                import openai
                client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

                response = await client.chat.completions.create(
                    model=TEXT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate {num_scenes} connected animation scenes for this children's story. Each scene must be detailed enough for a 10-second animation clip."}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=1000,
                    temperature=0.7
                )

                # Analyser la réponse pour extraire le JSON
                content = response.choices[0].message.content.strip()
                logger.info(f"🤖 Scènes générées: {content[:100]}...")

                # Essayer de parser le JSON
                try:
                    scenes_data = json.loads(content)
                    return scenes_data
                except json.JSONDecodeError:
                    logger.error(f"Erreur parsing JSON OpenAI: réponse invalide pour {num_scenes} scènes")
                    raise Exception(f"OpenAI API a retourné un JSON invalide pour {num_scenes} scènes")

            except Exception as api_error:
                logger.error(f"Erreur API OpenAI: {api_error}")
                raise Exception(f"Échec génération scènes: {api_error}")

        except Exception as e:
            logger.error(f"Erreur génération prompts adaptés: {e}")
            raise Exception(f"Échec génération {num_scenes} scènes: {e}")


    # NOTE: add_audio_to_clip et _wait_fal_audio supprimées car Veo 3.1 Fast génère déjà l'audio automatiquement
    # Les clips générés par Veo 3.1 Fast incluent déjà l'audio, pas besoin d'ajout séparé

    async def create_sora2_clip(self, scene_prompt: str, idea: str, environment: str) -> str:
        """
        Create Clips - Génère un clip vidéo avec Runway ML Veo 3.1 Fast
        """
        logger.info(f"🎬 Début create_sora2_clip - plateforme sélectionnée: {self.selected_platform}")
        try:
            platform = self.selected_platform
            platform_config = self.sora_platforms[platform]
            logger.info(f"🎬 Platform config chargé: {platform} - available: {platform_config.get('available', False)}")

            if platform != "runway":
                raise Exception(f"❌ Plateforme {platform} non supportée - seule Runway ML est disponible")

            # Prompt pour Runway ML - limité à 1000 caractères max
            # Format simplifié pour respecter la limite de l'API
            runway_prompt = f"{scene_prompt} in {environment}"
            
            # Limiter à 1000 caractères si nécessaire
            if len(runway_prompt) > 1000:
                runway_prompt = runway_prompt[:997] + "..."

            logger.info(f"🎬 Génération Runway ML scène: {scene_prompt[:50]}...")
            logger.info(f"📝 Prompt longueur: {len(runway_prompt)} caractères")

            # Vérification détaillée de la clé API
            api_key = platform_config['api_key']
            logger.info(f"🔍 DEBUG - Platform config: {platform_config}")
            logger.info(f"🔍 DEBUG - API key présente: {bool(api_key)}")
            logger.info(f"🔍 DEBUG - API key longueur: {len(api_key) if api_key else 0}")
            logger.info(f"🔍 DEBUG - API key commence par 'key_': {api_key.startswith('key_') if api_key else False}")
            logger.info(f"🔍 DEBUG - API key préfixe: {api_key[:10] if api_key else 'None'}")

            if not api_key:
                raise Exception("❌ RUNWAY_API_KEY non configurée dans les variables d'environnement Railway")
            if not api_key.startswith('key_'):
                raise Exception(f"❌ RUNWAY_API_KEY mal formatée: doit commencer par 'key_' (actuellement: {api_key[:10]}...)")

            logger.info(f"✅ Clé API Runway valide: {api_key[:20]}...")

            # Préparation de la requête pour Runway ML veo3.1_fast (text-to-video)
            # Utilisation de l'endpoint /v1/text_to_video (text-to-video pur)
            runway_payload = {
                "model": "veo3.1_fast",  # Veo 3.1 Fast - text-to-video
                "promptText": runway_prompt,  # Prompt texte pour génération directe
                "duration": 8,  # 8 secondes max pour veo3.1_fast (4, 6 ou 8)
                "ratio": "1920:1080",  # Format 16:9 en pixels (requis par API)
                "watermark": False
            }

            # Headers pour l'API Runway ML
            headers = {
                "Authorization": f"Bearer {platform_config['api_key']}",
                "Content-Type": "application/json",
                "X-Runway-Version": "2024-09-13"  # Version requise par l'API
            }

            # URL de l'API Runway ML - endpoint text_to_video pour veo3.1_fast
            api_url = f"{platform_config['base_url']}/v1/text_to_video"

            logger.info(f"📡 Appel API Runway ML: {api_url}")

            # Faire la requête à l'API Runway ML
            logger.info(f"🌐 Requête Runway ML: POST {api_url}")
            logger.info(f"📋 Headers: Authorization=Bearer {api_key[:20]}..., X-Runway-Version={headers.get('X-Runway-Version')}")
            logger.info(f"📦 Payload: {runway_payload}")

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=runway_payload, headers=headers) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        task_id = response_data.get("id")
                        logger.info(f"✅ Tâche Runway ML créée: {task_id}")

                        # Attendre que la génération soit terminée
                        video_url = await self._wait_for_runway_task(session, task_id, headers)
                        return video_url

                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erreur API Runway ML ({response.status}): {error_text}")
                        logger.error(f"🔍 DEBUG - Headers de réponse: {dict(response.headers)}")
                        logger.error(f"🔍 DEBUG - URL complète: {api_url}")
                        raise Exception(f"API Runway ML error: {response.status} - {error_text}")

        except Exception as e:
            logger.error(f"Erreur génération clip Runway ML: {e}")
            # Échec définitif - pas de fallback autorisé
            raise Exception(f"Échec génération vidéo Runway ML: {e}")

    async def _wait_for_runway_task(self, session, task_id: str, headers: dict, max_wait: int = 300) -> str:
        """
        Attend qu'une tâche Runway ML soit terminée et retourne l'URL de la vidéo
        """
        # Endpoint correct pour vérifier le statut d'une tâche
        api_url = f"https://api.dev.runwayml.com/v1/tasks/{task_id}"
        logger.info(f"🔍 URL vérification statut: {api_url}")

        start_time = time.time()
        attempt = 0
        while time.time() - start_time < max_wait:
            try:
                attempt += 1
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        task_data = await response.json()

                        status = task_data.get("status")
                        progress = task_data.get("progress", 0)
                        logger.info(f"📊 Statut tâche Runway ML (tentative {attempt}): {status} - Progression: {progress}%")

                        if status == "SUCCEEDED":
                            # Récupérer l'URL de la vidéo générée
                            output = task_data.get("output", [])
                            if output and len(output) > 0:
                                video_url = output[0]
                                logger.info(f"✅ Vidéo Runway ML générée: {video_url}")
                                # Indentation corrigée pour éviter IndentationError
                                return video_url
                            else:
                                logger.error(f"❌ Pas de vidéo dans la réponse: {task_data}")
                                raise Exception("No video URL in Runway ML response")

                        elif status == "FAILED":
                            error_msg = task_data.get("failure", "Erreur inconnue")
                            logger.error(f"❌ Échec génération Runway ML: {error_msg}")
                            logger.error(f"🔍 Détails: {task_data}")
                            raise Exception(f"Runway ML generation failed: {error_msg}")

                        # Attendre avant de vérifier à nouveau
                        await asyncio.sleep(10)

                    else:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Erreur vérification statut ({response.status}): {error_text[:200]}")
                        await asyncio.sleep(5)

            except Exception as e:
                logger.warning(f"⚠️ Erreur lors de la vérification (tentative {attempt}): {e}")
                await asyncio.sleep(5)

        # Timeout
        logger.error(f"⏰ Timeout génération Runway ML après {max_wait}s")
        raise Exception(f"Runway ML generation timeout after {max_wait} seconds")

    async def sequence_sora2_video(self, video_urls: List[str]) -> str:
        """
        Sequence Video - Assemble les clips avec l'API Runway ML ou FAL AI
        """
        try:
            logger.info(f"🔗 Assemblage de {len(video_urls)} clips vidéo...")

            if len(video_urls) == 0:
                raise Exception("Aucun clip à assembler")

            if len(video_urls) == 1:
                logger.info("✅ Un seul clip - pas d'assemblage nécessaire")
                return video_urls[0]

            platform = self.selected_platform

            # Essayer d'abord Runway ML pour l'assemblage (si disponible)
            if platform == "runway":
                try:
                    logger.info("🔧 Tentative assemblage avec Runway ML...")
                    return await self._assemble_with_runway(video_urls)
                except Exception as e:
                    logger.warning(f"⚠️ Assemblage Runway ML échoué: {e}")
                    logger.info("🔄 Basculement vers FAL AI pour l'assemblage...")

            # Utiliser FAL AI pour l'assemblage (fallback ou méthode principale)
            logger.info("🔧 Assemblage avec FAL AI...")
            try:
                final_url = await self._assemble_with_fal(video_urls)
                logger.info(f"✅ Assemblage FAL AI réussi: {final_url}")
                return final_url
            except Exception as e:
                logger.error(f"❌ Assemblage FAL AI échoué: {e}")
                raise Exception(f"Échec assemblage vidéo FAL AI: {e}")

        except Exception as e:
            logger.error(f"Erreur assemblage vidéo: {e}")
            raise Exception(f"Échec assemblage vidéo complet: {e}")

    async def _assemble_with_runway(self, video_urls: List[str]) -> str:
        """
        Assemblage avec l'API Runway ML
        """
        try:
            platform_config = self.sora_platforms["runway"]
            api_key = platform_config['api_key']
            # La clé contient déjà le préfixe 'key_', ne pas le dupliquer
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Runway-Version": "2024-09-13"  # Version requise par l'API
            }

            # Préparer les keyframes pour Runway ML
            keyframes = []
            current_time = 0
            clip_duration = 10  # 10 secondes par clip

            for i, video_url in enumerate(video_urls):
                keyframes.append({
                    "url": video_url,
                    "timestamp": current_time,
                    "duration": clip_duration
                })
                current_time += clip_duration

            payload = {
                "model": "veo3.1_fast",  # ou un modèle d'assemblage si disponible
                "keyframes": keyframes,
                "width": 1920,
                "height": 1080,
                "fps": 24
            }

            api_url = f"{platform_config['base_url']}/assemble"  # Endpoint hypothétique
            logger.info(f"📡 Appel API Runway ML assemble: {api_url}")

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        task_id = result.get("id")

                        # Attendre la fin de l'assemblage
                        return await self._wait_runway_assemble(session, task_id, headers)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Runway assemble API error: {response.status} - {error_text}")

        except Exception as e:
            logger.error(f"Erreur assemblage Runway ML: {e}")
            raise

    async def _assemble_with_fal(self, video_urls: List[str]) -> str:
        """
        Assemblage avec FAL AI FFmpeg
        """
        try:
            fal_key = os.getenv("FAL_API_KEY")
            if not fal_key:
                raise Exception("FAL_API_KEY non configurée")

            headers = {
                "Authorization": f"Key {fal_key}",
                "Content-Type": "application/json"
            }

            # Préparer les tracks pour FAL AI FFmpeg
            tracks = []
            current_time = 0
            clip_duration = 10  # 10 secondes par clip

            for i, video_url in enumerate(video_urls):
                tracks.append({
                    "id": f"clip_{i+1}",
                    "type": "video",
                    "keyframes": [{
                        "url": video_url,
                        "timestamp": current_time,
                        "duration": clip_duration
                    }]
                })
                current_time += clip_duration

            payload = {
                "tracks": tracks,
                "output_format": "mp4",
                "resolution": "1080p",
                "frame_rate": 24
            }

            api_url = "https://queue.fal.run/fal-ai/ffmpeg-api/compose"
            logger.info(f"📡 Appel FAL AI assemble: {api_url}")

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        request_id = result.get("request_id")

                        # Attendre la fin de l'assemblage
                        return await self._wait_fal_assemble(session, request_id, headers)
                    else:
                        error_text = await response.text()
                        raise Exception(f"FAL assemble API error: {response.status} - {error_text}")

        except Exception as e:
            logger.error(f"Erreur assemblage FAL AI: {e}")
            raise

    async def _wait_runway_assemble(self, session, task_id: str, headers: dict, max_wait: int = 300) -> str:
        """
        Attendre qu'un assemblage Runway ML soit terminé
        """
        api_url = f"https://api.dev.runwayml.com/v1/tasks/{task_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        task_data = await response.json()
                        status = task_data.get("status")

                        if status == "SUCCEEDED":
                            return task_data.get("output_url", task_data.get("video_url"))
                        elif status == "FAILED":
                            raise Exception(f"Assemblage Runway ML échoué: {task_data.get('error')}")

                    await asyncio.sleep(10)

            except Exception as e:
                logger.warning(f"Erreur vérification assemblage Runway: {e}")
                await asyncio.sleep(5)

        raise Exception(f"Timeout assemblage Runway ML après {max_wait}s")

    async def _wait_fal_assemble(self, session, request_id: str, headers: dict, max_wait: int = 300) -> str:
        """
        Attendre qu'un assemblage FAL AI soit terminé
        """
        api_url = f"https://queue.fal.run/fal-ai/ffmpeg-api/requests/{request_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        status = result.get("status")

                        if status == "COMPLETED":
                            return result.get("video_url") or result.get("output_url")
                        elif status == "FAILED":
                            raise Exception(f"Assemblage FAL AI échoué: {result.get('error')}")

                    await asyncio.sleep(10)

            except Exception as e:
                logger.warning(f"Erreur vérification assemblage FAL: {e}")
                await asyncio.sleep(5)

        raise Exception(f"Timeout assemblage FAL AI après {max_wait}s")

    async def generate_complete_animation_zseedance(self, theme: str = "space", duration: int = 30, style: str = "cartoon") -> Dict[str, Any]:
        """
        Pipeline complet basé exactement sur zseedance.json
        Génère un nombre de scènes adapté à la durée demandée (10s par scène)
        """
        logger.info(f"🎬 ZSEEDANCE: Démarrage génération complète - thème: {theme}, durée: {duration}s, style: {style}")
        try:
            logger.info(f"🚀 Démarrage génération ZSEEDANCE: {theme} ({duration}s, style: {style})")

            # Calculer le nombre de scènes selon la durée (8s par scène avec veo3.1_fast)
            # Arrondir pour être plus proche de la durée demandée
            num_scenes = max(3, round(duration / 8))  # Minimum 3 scènes, ~8s par scène
            total_duration = num_scenes * 8
            logger.info(f"📊 Génération de {num_scenes} scènes de 8 secondes chacune (durée totale: {total_duration}s pour {duration}s demandés)")

            # Étape 1: Ideas AI Agent avec adaptation au thème choisi
            logger.info("📝 Étape 1: Ideas AI Agent (adapté au thème)...")
            idea_data = await self.generate_ideas_agent_adapted(theme)
            logger.info(f"✅ Étape 1 terminée: {idea_data.get('Idea', 'N/A')[:50]}...")

            # Étape 2: Prompts AI Agent adapté pour générer le bon nombre de scènes
            logger.info(f"📝 Étape 2: Prompts AI Agent ({num_scenes} scènes)...")
            prompts_data = await self.generate_prompts_agent_adapted(idea_data, num_scenes)
            logger.info(f"✅ Étape 2 terminée: {num_scenes} scènes générées")

            # Étape 3: Create Clips avec Veo 3.1 Fast
            logger.info("🎬 Étape 3: Create Clips avec Veo 3.1 Fast...")
            video_urls = []

            # Générer les clips selon le nombre calculé
            for i in range(1, num_scenes + 1):
                logger.info(f"🎬 Génération clip {i}/{num_scenes}...")
                scene_key = f"Scene {i}"
                if scene_key in prompts_data:
                    scene_prompt = prompts_data[scene_key]
                    logger.info(f"🎬 Génération scène {i}/{num_scenes}: {scene_prompt[:50]}...")

                    # Attendre entre les générations (comme zseedance avec batching)
                    if i > 1:
                        await asyncio.sleep(3)

                    video_url = await self.create_sora2_clip(
                        scene_prompt,
                        prompts_data["Idea"],
                        prompts_data["Environment"]
                    )
                    video_urls.append(video_url)

            # Étape 4: Sequence Video - Assemblage final
            # Note: Veo 3.1 Fast génère déjà l'audio automatiquement, pas besoin d'ajout audio séparé
            logger.info("🔗 Étape 4: Sequence Video (assemblage final des clips avec audio intégré)...")
            final_video_url = await self.sequence_sora2_video(video_urls)

            logger.info("✅ Animation ZSEEDANCE terminée avec succès!")

            return {
                "status": "completed",
                "final_video_url": final_video_url,
                "title": f"🎬 {idea_data['Idea']}",
                "duration": duration,
                "theme": theme,
                "style": style,
                "type": "zseedance_complete",
                "platform": self.selected_platform,
                "scenes_count": num_scenes,
                "video_count": len(video_urls),
                "idea": idea_data,
                "prompts": prompts_data,
                "generated_at": datetime.now().isoformat(),
                "clips": [
                    {
                        "scene_number": i + 1,
                        "video_url": video_urls[i],
                        "duration": 8,  # 8 secondes par clip
                        "status": "success"
                    }
                    for i in range(len(video_urls))
                ]
            }

        except Exception as e:
            logger.error(f"❌ Erreur génération Veo 3.1 Fast zseedance: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "theme": theme,
                "type": "veo3_1_fast_zseedance",
                "platform": self.selected_platform
            }

    def is_available(self) -> bool:
        """Vérifie si au moins une plateforme Veo 3.1 Fast est disponible"""
        return any(config["available"] for config in self.sora_platforms.values())

    def get_available_platforms(self) -> List[str]:
        """Retourne la liste des plateformes Veo 3.1 Fast disponibles"""
        return [name for name, config in self.sora_platforms.items() if config["available"]]


# Instance globale du générateur Veo 3.1 Fast zseedance
sora2_zseedance_generator = Sora2ZseedanceGenerator()
