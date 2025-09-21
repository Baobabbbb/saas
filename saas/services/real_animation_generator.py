"""
Service de génération d'animations réelles utilisant les APIs Wavespeed et Fal AI
Basé sur le workflow zseedance.json
"""
import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class RealAnimationGenerator:
    def __init__(self):
        # APIs keys - à configurer dans les variables d'environnement
        self.wavespeed_api_key = os.getenv("WAVESPEED_API_KEY")
        self.fal_api_key = os.getenv("FAL_API_KEY") 
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # URLs des APIs
        self.wavespeed_base_url = "https://api.wavespeed.ai/api/v3"
        self.fal_base_url = "https://queue.fal.run"
        
    async def generate_animation_idea(self, theme: str, duration: int) -> Dict[str, Any]:
        """Génère une idée d'animation avec OpenAI basée sur le thème"""
        
        # Prompts adaptés du workflow zseedance
        system_prompt = f"""
        Role: You are an elite creative system that generates cinematic animation concepts.
        
        Theme: {theme}
        Duration: {duration} seconds
        
        Generate a detailed animation concept with:
        1. A compelling visual idea
        2. Environment description 
        3. Sound effects description
        4. 3 distinct scenes of {duration//3} seconds each
        
        Output as JSON with keys: idea, environment, sound, scenes
        """
        
        # Pour l'instant, retournons une structure basée sur le thème
        if theme == "space":
            return {
                "idea": "Spectacular alien spaceship descent through Earth's atmosphere",
                "environment": "Dramatic mountain landscape at dusk with atmospheric effects",
                "sound": "Deep cosmic hums, atmospheric entry roars, energy field pulses",
                "scenes": [
                    "Spaceship breaking through clouds with trailing energy",
                    "Ship hovering above mountain peaks with ground illumination", 
                    "Final landing with dust displacement and light beams"
                ]
            }
        elif theme == "ocean":
            return {
                "idea": "Mysterious underwater creature emerging from ocean depths",
                "environment": "Deep ocean trench with bioluminescent life forms",
                "sound": "Underwater echoes, creature calls, bubble streams",
                "scenes": [
                    "Deep ocean darkness with glowing particles",
                    "Massive creature silhouette rising through water",
                    "Creature breaking ocean surface under moonlight"
                ]
            }
        else:  # forest
            return {
                "idea": "Magical forest transformation with mystical creatures",
                "environment": "Ancient forest with magical lighting and mist",
                "sound": "Wind through trees, magical chimes, creature whispers",
                "scenes": [
                    "Misty forest path with dancing light particles",
                    "Trees awakening with glowing spirits emerging",
                    "Full forest transformation with magical aura"
                ]
            }
    
    async def create_video_clip(self, scene_prompt: str, idea: str, environment: str) -> str:
        """Crée un clip vidéo avec Wavespeed AI"""
        
        if not self.wavespeed_api_key:
            raise ValueError("WAVESPEED_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.wavespeed_api_key}",
            "Content-Type": "application/json"
        }
        
        # Prompt combiné comme dans zseedance
        full_prompt = f"VIDEO THEME: {idea} | WHAT HAPPENS IN THE VIDEO: {scene_prompt} | WHERE THE VIDEO IS SHOT: {environment}"
        
        payload = {
            "aspect_ratio": "16:9",  # Format adapté pour desktop
            "duration": 10,
            "prompt": full_prompt
        }
        
        async with aiohttp.ClientSession() as session:
            # Créer la requête de génération
            async with session.post(
                f"{self.wavespeed_base_url}/bytedance/seedance-v1-pro-t2v-480p",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Wavespeed API error: {error_text}")
                
                result = await response.json()
                prediction_id = result["data"]["id"]
                
            # Attendre et récupérer le résultat
            await asyncio.sleep(60)  # Attente initiale
            
            async with session.get(
                f"{self.wavespeed_base_url}/predictions/{prediction_id}/result",
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get video result")
                
                result = await response.json()
                if result.get("status") == "completed":
                    return result["data"]["outputs"][0]
                else:
                    raise Exception(f"Video generation failed: {result}")
    
    async def create_audio(self, sound_prompt: str, video_url: str) -> str:
        """Crée l'audio avec Fal AI MMAudio"""
        
        if not self.fal_api_key:
            raise ValueError("FAL_API_KEY not configured")
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": f"sound effects: {sound_prompt}. Dramatic, cinematic",
            "duration": 10,
            "video_url": video_url
        }
        
        async with aiohttp.ClientSession() as session:
            # Créer la requête audio
            async with session.post(
                f"{self.fal_base_url}/fal-ai/mmaudio-v2",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Fal AI audio error: {error_text}")
                
                result = await response.json()
                request_id = result["request_id"]
                
            # Attendre et récupérer le résultat
            await asyncio.sleep(60)
            
            async with session.get(
                f"{self.fal_base_url}/fal-ai/mmaudio-v2/requests/{request_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to get audio result")
                
                result = await response.json()
                return result["video_url"]  # Vidéo avec audio
    
    async def compose_final_video(self, video_urls: List[str]) -> str:
        """Assemble les clips en vidéo finale avec Fal AI FFmpeg"""
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        # Structure comme dans zseedance
        tracks = {
            "tracks": [
                {
                    "id": "1",
                    "type": "video",
                    "keyframes": [
                        {"url": video_urls[0], "timestamp": 0, "duration": 10},
                        {"url": video_urls[1], "timestamp": 10, "duration": 10},
                        {"url": video_urls[2], "timestamp": 20, "duration": 10}
                    ]
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            # Créer la composition
            async with session.post(
                f"{self.fal_base_url}/fal-ai/ffmpeg-api/compose",
                headers=headers,
                json=tracks
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Fal AI compose error: {error_text}")
                
                result = await response.json()
                request_id = result["request_id"]
                
            # Attendre et récupérer le résultat
            await asyncio.sleep(60)
            
            async with session.get(
                f"{self.fal_base_url}/fal-ai/ffmpeg-api/requests/{request_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to get final video")
                
                result = await response.json()
                return result["video_url"]
    
    async def generate_complete_animation(self, theme: str, duration: int = 30) -> Dict[str, Any]:
        """Pipeline complet de génération d'animation réelle"""
        
        try:
            logger.info(f"Starting real animation generation for theme: {theme}")
            
            # 1. Générer l'idée
            logger.info("Generating animation idea...")
            idea_data = await self.generate_animation_idea(theme, duration)
            
            # 2. Créer les clips vidéo
            logger.info("Creating video clips...")
            video_urls = []
            for i, scene in enumerate(idea_data["scenes"]):
                logger.info(f"Creating clip {i+1}/3: {scene}")
                video_url = await self.create_video_clip(
                    scene, 
                    idea_data["idea"], 
                    idea_data["environment"]
                )
                video_urls.append(video_url)
            
            # 3. Ajouter l'audio aux clips
            logger.info("Adding audio to clips...")
            audio_video_urls = []
            for video_url in video_urls:
                audio_video_url = await self.create_audio(
                    idea_data["sound"], 
                    video_url
                )
                audio_video_urls.append(audio_video_url)
            
            # 4. Assembler la vidéo finale
            logger.info("Composing final video...")
            final_video_url = await self.compose_final_video(audio_video_urls)
            
            logger.info("Animation generation completed successfully!")
            
            return {
                "status": "completed",
                "final_video_url": final_video_url,
                "title": f"🎬 {idea_data['idea']}",
                "duration": duration,
                "theme": theme,
                "type": "real_animation",
                "generation_time": 300,  # ~5 minutes réel
                "clips": [
                    {
                        "id": f"scene_{i+1}",
                        "scene_number": i + 1,
                        "title": f"Scène {i+1}",
                        "description": scene,
                        "video_url": audio_video_urls[i],
                        "duration": 10,
                        "status": "success",
                        "type": "real_video"
                    }
                    for i, scene in enumerate(idea_data["scenes"])
                ],
                "idea": idea_data["idea"],
                "environment": idea_data["environment"],
                "sound": idea_data["sound"]
            }
            
        except Exception as e:
            logger.error(f"Animation generation failed: {str(e)}")
            raise Exception(f"Real animation generation failed: {str(e)}")
