"""
Service Runway Gen-4 Turbo pour de VRAIS dessins animés narratifs
Version qui génère des histoires complètes avec text-to-video
"""

import os
import time
from typing import Dict, Any, List
from datetime import datetime
import asyncio
import httpx
import traceback

class RunwayStoryService:
    """Service de génération de vrais dessins animés avec histoires complètes"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = os.getenv("RUNWAY_BASE_URL", "https://api.dev.runwayml.com")
        
        if not self.api_key or self.api_key == "your-runway-api-key-here":
            print("❌ RUNWAY_API_KEY manquante - ERREUR FATALE")
            raise Exception("Clé API Runway manquante - impossible de continuer")
        else:
            print(f"🔑 Clé API Runway détectée: {self.api_key[:20]}...")
            print("🎬 MODE PRODUCTION - Vrais dessins animés narratifs")
        
        print(f"📺 Service Runway Story initialisé - Vrais dessins animés TV")
        print(f"📡 Base URL: {self.base_url}")

    def _create_story_narrative(self, style: str, theme: str, custom_prompt: str = "") -> Dict[str, Any]:
        """Crée une histoire narrative complète selon le thème"""
        
        story_templates = {
            "adventure": {
                "title": "La Grande Aventure",
                "story": """Notre jeune héros découvre une carte mystérieuse qui le mène vers une aventure extraordinaire. 
                Il traverse des forêts enchantées, rencontre des créatures magiques qui deviennent ses amis, 
                et découvre un trésor qui n'est pas fait d'or, mais d'amitié et de courage. 
                À la fin, il rentre chez lui transformé par cette aventure, plus sage et plus confiant.""",
                "scenes": [
                    "Le héros trouve la carte mystérieuse et décide de partir à l'aventure",
                    "Il traverse la forêt enchantée et rencontre ses premiers amis magiques", 
                    "Ensemble, ils surmontent des obstacles et découvrent le vrai trésor",
                    "Le héros rentre chez lui, enrichi par cette belle aventure"
                ]
            },
            "magic": {
                "title": "Le Monde des Sortilèges",
                "story": """Dans un royaume magique, une jeune apprentie sorcière apprend à maîtriser ses pouvoirs. 
                Elle découvre que la vraie magie ne vient pas des sortilèges, mais de la bienveillance et de l'entraide. 
                Quand une terrible malédiction menace le royaume, elle unit tous les habitants pour la briser, 
                prouvant que ensemble, on peut accomplir des miracles.""",
                "scenes": [
                    "La jeune sorcière apprend ses premiers sorts dans l'école de magie",
                    "Elle découvre une malédiction qui menace tout le royaume magique",
                    "Elle rassemble tous les habitants pour unir leurs forces magiques",
                    "Ensemble, ils brisent la malédiction et sauvent le royaume"
                ]
            },
            "space": {
                "title": "Voyage vers les Étoiles",
                "story": """Un jeune astronaute part explorer l'espace et découvre des planètes merveilleuses. 
                Sur chaque planète, il rencontre des aliens sympathiques qui lui apprennent leurs coutumes. 
                Il comprend que l'univers est plein de diversité et de beauté, et que l'amitié transcende toutes les différences. 
                Il revient sur Terre avec de nombreux amis cosmiques.""",
                "scenes": [
                    "L'astronaute décolle dans son vaisseau spatial vers l'inconnu",
                    "Il découvre la première planète colorée avec des aliens amicaux",
                    "Il visite d'autres mondes et apprend leurs cultures uniques",
                    "Il revient sur Terre avec ses nouveaux amis de l'espace"
                ]
            },
            "animals": {
                "title": "La Famille de la Forêt", 
                "story": """Dans la forêt, tous les animaux vivent comme une grande famille. 
                Quand le petit lapin se perd, tous les animaux s'unissent pour le retrouver. 
                Cette aventure leur enseigne l'importance de l'entraide et de la solidarité. 
                Désormais, ils veillent encore plus les uns sur les autres.""",
                "scenes": [
                    "Les animaux de la forêt vivent heureux ensemble",
                    "Le petit lapin se perd et tout le monde s'inquiète",
                    "Tous les animaux s'organisent pour partir à sa recherche",
                    "Ils le retrouvent et célèbrent leur amitié renforcée"
                ]
            },
            "friendship": {
                "title": "Les Amis pour la Vie",
                "story": """Deux enfants très différents se rencontrent et deviennent les meilleurs amis du monde. 
                Ensemble, ils découvrent que leurs différences les rendent plus forts. 
                Quand l'un d'eux doit déménager, ils promettent de rester amis pour toujours. 
                Leur amitié résiste à la distance et au temps.""",
                "scenes": [
                    "Deux enfants différents se rencontrent et apprennent à se connaître",
                    "Ils découvrent qu'ils se complètent parfaitement malgré leurs différences",
                    "L'un d'eux doit partir, mais ils promettent de rester amis",
                    "Ils prouvent que la vraie amitié surmonte tous les obstacles"
                ]
            }
        }
        
        # Prendre le template selon le thème
        base_story = story_templates.get(theme, story_templates["adventure"])
        
        # Personnaliser avec le prompt de l'utilisateur
        if custom_prompt:
            base_story["story"] = f"{base_story['story']} {custom_prompt}"
            
        return base_story

    def _create_text_to_video_prompt(self, style: str, story_scene: str, scene_number: int) -> str:
        """Crée un prompt simplifié mais narratif pour une scène"""
        
        style_prompts = {
            "cartoon": "Cartoon animation style, colorful characters",
            "fairy_tale": "Fairy tale animation style, magical atmosphere",
            "anime": "Anime animation style, expressive characters",
            "realistic": "Semi-realistic animation style, detailed",
            "paper_craft": "Paper craft animation style, layered cutout",
            "watercolor": "Watercolor animation style, artistic brushstrokes"
        }
        
        base_style = style_prompts.get(style, style_prompts["cartoon"])
        
        # Prompt court et efficace
        prompt = f"{base_style}. Scene {scene_number}: {story_scene}. Characters moving and interacting naturally. Child-friendly, bright colors, engaging story."
        
        return prompt

    async def generate_animation(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer un vrai dessin animé narratif complet"""
        
        style = animation_data.get("style", "cartoon")
        theme = animation_data.get("theme", "adventure")
        orientation = animation_data.get("orientation", "landscape")
        custom_prompt = animation_data.get("prompt", "")
        
        print(f"🎬 Génération VRAI DESSIN ANIMÉ - Style: {style}, Thème: {theme}")
        print(f"📝 Histoire personnalisée: {custom_prompt}")
        
        try:
            # Étape 1: Créer l'histoire narrative complète
            story_data = self._create_story_narrative(style, theme, custom_prompt)
            print(f"📚 Histoire créée: {story_data['title']}")
            print(f"📖 Résumé: {story_data['story'][:100]}...")
            
            # Étape 2: Générer la vidéo principale avec text-to-video
            main_scene = story_data['scenes'][0]  # Première scène comme vidéo principale
            video_prompt = self._create_text_to_video_prompt(style, main_scene, 1)
            
            print(f"🎯 Génération de la scène principale...")
            print(f"📝 Prompt vidéo: {video_prompt[:150]}...")
            
            # Ratio mapping pour text-to-video
            ratio_map = {
                "landscape": "1280:720",  # Format TV standard
                "portrait": "720:1280",
                "square": "720:720"
            }
            ratio = ratio_map.get(orientation, "1280:720")
            
            # Générer la vidéo principale avec animation narrative avancée (10 secondes max)
            main_video_url = await self._generate_text_to_video(video_prompt, ratio, duration=10)
            
            # Étape 3: Optionnel - Générer des scènes supplémentaires (si budget le permet)
            additional_scenes = []
            try:
                # Générer une scène supplémentaire courte
                if len(story_data['scenes']) > 1:
                    second_scene = story_data['scenes'][1]
                    second_prompt = self._create_text_to_video_prompt(style, second_scene, 2)
                    second_video = await self._generate_text_to_video(second_prompt, ratio, duration=10)
                    additional_scenes.append({
                        'title': f"Scène 2: {second_scene[:50]}...",
                        'video_url': second_video,
                        'prompt': second_scene
                    })
            except Exception as e:
                print(f"⚠️ Scène supplémentaire échouée (normal si quota atteint): {e}")
            
            # Retourner le vrai dessin animé
            return {
                "id": f"runway_story_{int(time.time())}",
                "title": story_data['title'],
                "description": f"Dessin animé {style} - {story_data['title']}",
                "video_url": main_video_url,
                "thumbnail_url": main_video_url,  # Runway génère un thumbnail automatiquement
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": 10 + (len(additional_scenes) * 10),
                "style": style,
                "theme": theme,
                "orientation": orientation,
                "prompt": custom_prompt,
                "story": story_data['story'],
                "story_scenes": story_data['scenes'],
                "additional_videos": additional_scenes,
                "narrative_type": "full_animated_story",
                "production_type": "text_to_video"
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du dessin animé: {e}")
            print(f"📊 Traceback complet: {traceback.format_exc()}")
            raise Exception(f"Impossible de générer le dessin animé: {str(e)}")

    async def _generate_text_to_video(self, prompt: str, ratio: str = "1280:720", duration: int = 15) -> str:
        """Génère une vidéo narrative en utilisant text-to-image puis image-to-video avec des prompts très détaillés"""
        
        print(f"🎬 Génération de dessin animé narratif (text-to-image + image-to-video)...")
        
        # Étape 1: Créer une image très détaillée pour l'animation
        detailed_image_prompt = f"{prompt} High-quality animation keyframe, professional character design, cinematic composition."
        
        # Générer l'image de base avec plus de détails
        image_url = await self._generate_detailed_image(detailed_image_prompt.strip(), ratio)
        
        # Étape 2: Créer un prompt d'animation simplifié
        animation_prompt = f"Characters move naturally with gestures and expressions. Camera movement enhances storytelling. Smooth professional animation quality. Complete narrative sequence."
        
        # Générer l'animation narrative
        video_url = await self._generate_narrative_video(image_url, animation_prompt.strip(), duration)
        
        return video_url

    async def _generate_detailed_image(self, prompt: str, ratio: str = "1280:720") -> str:
        """Génère une image très détaillée optimisée pour l'animation narrative"""
        
        print(f"🎨 Génération d'image narrative détaillée...")
        
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
            
            print(f"⏳ Tâche image narrative créée: {task_id}")
            
            image_url = await self._wait_for_task_completion(task_id, "image")
            return image_url

    async def _generate_narrative_video(self, image_url: str, animation_prompt: str, duration: int = 15) -> str:
        """Génère une vidéo narrative à partir de l'image avec des instructions d'animation détaillées"""
        
        print(f"🎥 Génération de vidéo narrative avec animation avancée...")
        print(f"🖼️ Image source: {image_url}")
        
        payload = {
            "model": "gen4_turbo",
            "promptImage": image_url,
            "promptText": animation_prompt,
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
            
            print(f"⏳ Tâche vidéo narrative créée: {task_id}")
            
            video_url = await self._wait_for_task_completion(task_id, "video")
            return video_url

    def _get_headers(self) -> Dict[str, str]:
        """Headers pour l'authentification Runway"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }

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

# Instance globale du service story
runway_story_service = RunwayStoryService()
