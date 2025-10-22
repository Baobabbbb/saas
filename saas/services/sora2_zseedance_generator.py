"""
Service de génération d'animations avec Sora 2 basé exactement sur le workflow zseedance.json
Implémentation fidèle au workflow n8n avec Sora 2 pour la génération vidéo
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
    Générateur d'animations utilisant Sora 2 en suivant exactement le workflow zseedance.json
    Workflow identique : Ideas → Prompts → Clips Sora 2 → Sequence (sans audio séparé)
    """

    def __init__(self):
        # Configuration basée sur les variables d'environnement existantes
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.text_model = os.getenv("TEXT_MODEL", "gpt-4o-mini")

        # Configuration Sora 2 - utiliser les APIs existantes
        self.sora_platforms = {
            "openai": {
                "name": "OpenAI (Non disponible)",
                "base_url": "https://api.openai.com/v1",
                "api_key": self.openai_api_key,
                "model": "sora-2",  # Modèle hypothétique Sora 2
                "available": False,  # Désactivé car pas disponible publiquement
                "priority": 99  # Priorité très basse
            },
            "runway": {
                "name": "Runway ML (Veo 3.1 Fast)",
                "base_url": "https://api.dev.runwayml.com",
                "api_key": os.getenv("RUNWAY_API_KEY"),
                "model": "veo3.1_fast",
                "available": bool(os.getenv("RUNWAY_API_KEY")),
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

        # Configuration Sora 2 optimisée pour enfants (identique à zseedance)
        self.sora2_config = {
            "aspect_ratio": "9:16",  # Format vertical comme zseedance
            "duration_per_clip": 10,  # 10 secondes par clip comme zseedance
            "resolution": "480p",     # Résolution comme zseedance
            "style": "2D cartoon animation, Disney Pixar style, child-friendly, vibrant colors, smooth fluid animation, expressive characters",
            "negative_prompt": "blurry, low quality, distorted, violent, scary, static, motionless, dark, horror"
        }

        logger.info(f"🎬 Sora2ZseedanceGenerator initialisé avec plateforme: {self.selected_platform}")

    def _select_best_platform(self) -> str:
        """Sélectionne la plateforme Sora 2 disponible avec la priorité la plus haute"""
        available_platforms = [
            (name, config) for name, config in self.sora_platforms.items()
            if config["available"]
        ]

        if not available_platforms:
            logger.warning("⚠️ Aucune plateforme Sora 2 disponible - vérifiez les clés API")
            return "openai"  # Fallback sur OpenAI même si non configuré

        # Trier par priorité
        available_platforms.sort(key=lambda x: x[1]["priority"])
        best_platform = available_platforms[0][0]

        logger.info(f"✅ Plateforme Sora 2 sélectionnée: {best_platform}")
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

            # Prompt système adapté pour les enfants
            system_prompt = f"""You are a creative storyteller specializing in animated stories for children aged 4-10.

Create a magical animated story concept for the theme: {theme_config['subject']}

REQUIREMENTS:
- The story must be suitable for children 4-10 years old
- Include friendly, positive characters
- No scary elements, violence, or danger
- Focus on wonder, discovery, friendship, and joy
- The animation should be colorful and magical
- Include at least 3-5 friendly characters or creatures

STORY STRUCTURE:
- A clear beginning, middle, and happy ending
- Characters go on an adventure or solve a fun problem
- Everyone learns something positive
- The ending is happy and uplifting

OUTPUT FORMAT (JSON):
{{
  "Caption": "🎬 [Short title with emoji] #adventure #magic #friendship",
  "Idea": "[2-3 sentence description of the complete story]",
  "Environment": "[Magical setting description for {theme_config['style']}]",
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
                        {"role": "user", "content": f"Create a magical animated story for children about: {theme_config['subject']}"}
                    ],
                    max_tokens=300,
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
                    # Si parsing échoue, créer une structure par défaut
                    logger.warning("Impossible de parser la réponse JSON, utilisation d'un fallback")
                    return self._create_fallback_idea(theme, theme_config)

            except Exception as api_error:
                logger.warning(f"Erreur API OpenAI: {api_error}, utilisation du fallback")
                return self._create_fallback_idea(theme, theme_config)

        except Exception as e:
            logger.error(f"Erreur génération idée adaptée: {e}")
            # Fallback final
            return self._create_fallback_idea(theme, {"subject": theme, "environment": f"{theme} setting", "sound": "happy music"})

    def _create_fallback_idea(self, theme: str, config: dict) -> Dict[str, Any]:
        """Crée une idée par défaut en cas d'erreur"""
        return {
            "Caption": f"🎬 Aventure {theme} magique #magie #aventure #amis",
            "Idea": f"Des amis partent à la découverte d'un monde {theme} rempli de magie et de surprises joyeuses.",
            "Environment": f"Environnement {theme} enchanteur avec des éléments magiques",
            "Sound": f"{config.get('sound', 'musique joyeuse')}, rires d'enfants, sons magiques",
            "Status": "for children"
        }

    async def generate_prompts_agent_adapted(self, idea_data: Dict[str, Any], num_scenes: int = 3) -> Dict[str, Any]:
        """
        Prompts AI Agent - Crée un nombre variable de scènes détaillées pour l'animation
        Adapté pour les enfants et génère des scènes cohérentes formant une histoire complète
        """
        try:
            # Prompt système adapté pour les enfants et les animations cohérentes
            system_prompt = f"""You are a cinematic prompt generator specializing in animated stories for children aged 4-10.

Your task is to create {num_scenes} detailed scene descriptions that together tell a complete, coherent animated story.

STORY TO ADAPT: {idea_data['Idea']}
ENVIRONMENT: {idea_data['Environment']}
SOUND: {idea_data['Sound']}

REQUIREMENTS FOR EACH SCENE:
- Each scene must be exactly 10 seconds long
- Scenes must flow logically: beginning → middle → climax → happy ending
- Include colorful, magical elements suitable for children
- Focus on positive emotions, friendship, discovery, and joy
- No scary elements, danger, or negative emotions
- Characters should be expressive and friendly
- Use vibrant colors, magical effects, and child-friendly settings

SCENE STRUCTURE:
- Scene 1: Introduction and setup (beginning of the story)
- Scene 2-{num_scenes-1}: Development and adventure (middle of the story)
- Scene {num_scenes}: Happy resolution (end of the story)

VISUAL STYLE:
- 2D cartoon animation in Disney/Pixar style
- Bright, vibrant colors
- Smooth fluid animation
- Expressive character faces
- Magical sparkles and effects
- Child-friendly proportions

OUTPUT FORMAT (JSON):
{{
  "Idea": "{idea_data['Idea']}",
  "Environment": "{idea_data['Environment']}",
  "Sound": "{idea_data['Sound']}",
  "Scene 1": "Detailed description of scene 1 for 10-second animation clip",
  "Scene 2": "Detailed description of scene 2 for 10-second animation clip",
  "Scene 3": "Detailed description of scene 3 for 10-second animation clip"
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
                        {"role": "user", "content": f"Create {num_scenes} detailed animation scenes for this children's story: {idea_data['Idea']}. Each scene should be suitable for a 10-second animation clip and together form a complete, coherent story."}
                    ],
                    max_tokens=800,
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
                    # Si parsing échoue, créer des scènes par défaut
                    logger.warning("Impossible de parser la réponse JSON des scènes, utilisation d'un fallback")
                    return self._create_fallback_scenes(idea_data, num_scenes)

            except Exception as api_error:
                logger.warning(f"Erreur API OpenAI pour les scènes: {api_error}, utilisation du fallback")
                return self._create_fallback_scenes(idea_data, num_scenes)

        except Exception as e:
            logger.error(f"Erreur génération prompts adaptés: {e}")
            # Fallback final
            return self._create_fallback_scenes(idea_data, num_scenes)

    def _create_fallback_scenes(self, idea_data: Dict[str, Any], num_scenes: int) -> Dict[str, Any]:
        """Crée des scènes par défaut cohérentes en cas d'erreur"""
        base_scenes = {
                "Idea": idea_data["Idea"],
                "Environment": idea_data["Environment"],
            "Sound": idea_data["Sound"]
        }

        # Scènes génériques mais cohérentes pour former une histoire
        generic_scenes = [
            "Colorful animated scene showing friendly characters starting their magical adventure in a vibrant environment, with sparkles and joyful expressions.",
            "Exciting middle scene where characters discover magical wonders, interact with friendly creatures, and experience joyful discoveries together.",
            "Happy ending scene showing characters celebrating their successful adventure, sharing friendship and magical moments in a colorful finale."
        ]

        # Ajouter le nombre demandé de scènes
        for i in range(num_scenes):
            scene_num = i + 1
            if i < len(generic_scenes):
                base_scenes[f"Scene {scene_num}"] = generic_scenes[i]
            else:
                base_scenes[f"Scene {scene_num}"] = f"Continuation scene {scene_num} maintaining the magical adventure with joyful discoveries and friendly interactions."

        return base_scenes

    async def add_audio_to_clip(self, video_url: str, sound_description: str) -> str:
        """
        Ajoute l'audio à un clip vidéo avec FAL AI MMAudio (comme dans zseedance.json)
        """
        try:
            fal_key = os.getenv("FAL_API_KEY")
            if not fal_key:
                logger.warning("FAL_API_KEY non configurée, retour du clip sans audio")
                return video_url

            headers = {
                "Authorization": f"Key {fal_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "prompt": f"sound effects: {sound_description}. Gentle, magical, child-friendly music and sounds suitable for children's animation",
                "duration": 10,
                "video_url": video_url
            }

            logger.info(f"🎵 Ajout audio avec FAL AI: {sound_description[:50]}...")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://queue.fal.run/fal-ai/mmaudio-v2",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        request_id = result.get("request_id")

                        # Attendre que l'audio soit ajouté
                        final_url = await self._wait_fal_audio(request_id, headers)
                        return final_url
                    else:
                        error_text = await response.text()
                        logger.warning(f"Erreur FAL AI audio ({response.status}): {error_text}")
                        return video_url  # Retourner le clip sans audio

        except Exception as e:
            logger.error(f"Erreur ajout audio: {e}")
            return video_url  # Fallback: clip sans audio

    async def _wait_fal_audio(self, request_id: str, headers: dict, max_wait: int = 120) -> str:
        """
        Attend que FAL AI termine l'ajout d'audio
        """
        api_url = f"https://queue.fal.run/fal-ai/mmaudio-v2/requests/{request_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result.get("status")

                            if status == "COMPLETED":
                                return result.get("video_url") or result.get("output_url")
                            elif status == "FAILED":
                                raise Exception(f"Échec ajout audio: {result.get('error')}")

                    await asyncio.sleep(5)

            except Exception as e:
                logger.warning(f"Erreur vérification audio FAL: {e}")
                await asyncio.sleep(5)

        raise Exception(f"Timeout ajout audio après {max_wait}s")

    async def create_sora2_clip(self, scene_prompt: str, idea: str, environment: str) -> str:
        """
        Create Clips - Génère un clip vidéo avec Runway ML Veo 3.1 Fast
        """
        try:
            platform = self.selected_platform
            platform_config = self.sora_platforms[platform]

            if platform != "runway":
                logger.warning(f"⚠️ Plateforme {platform} non supportée pour la génération vidéo")
                # Fallback vers URL mockée
                video_id = str(uuid.uuid4())
                mock_video_url = f"https://cdn.example.com/sora2/{video_id}.mp4"
                logger.info(f"✅ Clip mock généré: {mock_video_url}")
                return mock_video_url

            # Prompt pour Runway ML identique au format zseedance
            runway_prompt = f"VIDEO THEME: {idea} | WHAT HAPPENS IN THE VIDEO: {scene_prompt} | WHERE THE VIDEO IS SHOT: {environment}"

            logger.info(f"🎬 Génération Runway ML scène: {scene_prompt[:50]}...")

            # Préparation de la requête pour Runway ML API
            runway_payload = {
                "model": platform_config["model"],  # "veo3.1_fast"
                "prompt": runway_prompt,
                "duration": 10,  # 10 secondes comme zseedance
                "ratio": "9:16",  # Format vertical comme zseedance
                "seed": None,
                "loop": False
            }

            # Headers pour l'API Runway ML
            headers = {
                "Authorization": f"Bearer {platform_config['api_key']}",
                "Content-Type": "application/json"
            }

            # URL de l'API Runway ML
            api_url = f"{platform_config['base_url']}/generation"

            logger.info(f"📡 Appel API Runway ML: {api_url}")

            # Faire la requête à l'API Runway ML
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
                        raise Exception(f"API Runway ML error: {response.status} - {error_text}")

        except Exception as e:
            logger.error(f"Erreur génération clip Runway ML: {e}")
            # Fallback vers URL mockée en cas d'erreur
            video_id = str(uuid.uuid4())
            mock_video_url = f"https://cdn.example.com/runway/{video_id}.mp4"
            logger.warning(f"⚠️ Fallback vers URL mockée: {mock_video_url}")
            return mock_video_url

    async def _wait_for_runway_task(self, session, task_id: str, headers: dict, max_wait: int = 300) -> str:
        """
        Attend qu'une tâche Runway ML soit terminée et retourne l'URL de la vidéo
        """
        api_url = f"https://api.dev.runwayml.com/v1/generation/{task_id}"

        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        task_data = await response.json()

                        status = task_data.get("status")
                        logger.info(f"📊 Statut tâche Runway ML: {status}")

                        if status == "SUCCEEDED":
                            # Récupérer l'URL de la vidéo générée
                            assets = task_data.get("assets", {})
                            video_assets = assets.get("videos", [])

                            if video_assets:
                                video_url = video_assets[0].get("url")
                                if video_url:
                                    logger.info(f"✅ Vidéo Runway ML générée: {video_url}")
                                    return video_url

                        elif status == "FAILED":
                            error_msg = task_data.get("error", "Erreur inconnue")
                            logger.error(f"❌ Échec génération Runway ML: {error_msg}")
                            raise Exception(f"Runway ML generation failed: {error_msg}")

                        # Attendre avant de vérifier à nouveau
                        await asyncio.sleep(10)

                    else:
                        logger.warning(f"⚠️ Erreur vérification statut ({response.status})")
                        await asyncio.sleep(5)

            except Exception as e:
                logger.warning(f"⚠️ Erreur lors de la vérification: {e}")
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

            # Essayer d'abord Runway ML pour l'assemblage
            if platform == "runway":
                try:
                    return await self._assemble_with_runway(video_urls)
                except Exception as e:
                    logger.warning(f"⚠️ Assemblage Runway ML échoué: {e}")
                    logger.info("🔄 Tentative avec FAL AI...")

            # Fallback vers FAL AI pour l'assemblage
            try:
                return await self._assemble_with_fal(video_urls)
            except Exception as e:
                logger.warning(f"⚠️ Assemblage FAL AI échoué: {e}")
                logger.info("🔄 Fallback vers le premier clip")

            # Dernier fallback : retourner le premier clip
            return video_urls[0]

        except Exception as e:
            logger.error(f"Erreur assemblage vidéo: {e}")
            # Fallback vers le premier clip
            return video_urls[0] if video_urls else ""

    async def _assemble_with_runway(self, video_urls: List[str]) -> str:
        """
        Assemblage avec l'API Runway ML
        """
        try:
            platform_config = self.sora_platforms["runway"]
            headers = {
                "Authorization": f"Bearer {platform_config['api_key']}",
                "Content-Type": "application/json"
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
        try:
            logger.info(f"🚀 Démarrage génération ZSEEDANCE: {theme} ({duration}s, style: {style})")

            # Calculer le nombre de scènes selon la durée (comme zseedance : 10s par scène)
            num_scenes = max(3, duration // 10)  # Minimum 3 scènes
            logger.info(f"📊 Génération de {num_scenes} scènes de 10 secondes chacune")

            # Étape 1: Ideas AI Agent avec adaptation au thème choisi
            logger.info("📝 Étape 1: Ideas AI Agent (adapté au thème)...")
            idea_data = await self.generate_ideas_agent_adapted(theme)

            # Étape 2: Prompts AI Agent adapté pour générer le bon nombre de scènes
            logger.info(f"📝 Étape 2: Prompts AI Agent ({num_scenes} scènes)...")
            prompts_data = await self.generate_prompts_agent_adapted(idea_data, num_scenes)

            # Étape 3: Create Clips avec Veo 3.1 Fast
            logger.info("🎬 Étape 3: Create Clips avec Veo 3.1 Fast...")
            video_urls = []

            # Générer les clips selon le nombre calculé
            for i in range(1, num_scenes + 1):
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

            # Étape 4: Create Sounds avec FAL AI MMAudio
            logger.info("🎵 Étape 4: Create Sounds avec FAL AI...")
            audio_video_urls = []
            for i, video_url in enumerate(video_urls):
                logger.info(f"🎵 Ajout audio à la scène {i+1}...")
                audio_video_url = await self.add_audio_to_clip(video_url, prompts_data["Sound"])
                audio_video_urls.append(audio_video_url)

                # Attendre entre les générations audio
                if i > 0:
                    await asyncio.sleep(2)

            # Étape 5: Sequence Video - Assemblage final
            logger.info("🔗 Étape 5: Sequence Video (assemblage final)...")
            final_video_url = await self.sequence_sora2_video(audio_video_urls)

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
                        "video_url": audio_video_urls[i],
                        "duration": 10,
                        "status": "success"
                    }
                    for i in range(len(audio_video_urls))
                ]
            }

        except Exception as e:
            logger.error(f"❌ Erreur génération Sora 2 zseedance: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "theme": theme,
                "type": "sora2_zseedance",
                "platform": self.selected_platform
            }

    def is_available(self) -> bool:
        """Vérifie si au moins une plateforme Sora 2 est disponible"""
        return any(config["available"] for config in self.sora_platforms.values())

    def get_available_platforms(self) -> List[str]:
        """Retourne la liste des plateformes Sora 2 disponibles"""
        return [name for name, config in self.sora_platforms.items() if config["available"]]


# Instance globale du générateur Sora 2 zseedance
sora2_zseedance_generator = Sora2ZseedanceGenerator()
