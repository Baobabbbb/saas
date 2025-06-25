"""
Service Intégré de Génération d'Animation avec CrewAI + Runway API
Orchestration complète : Analyse narrative → Génération vidéo → Assemblage final
"""

import os
import json
import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import uuid

# Imports CrewAI
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Video processing
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
import requests

@dataclass
class VideoScene:
    """Structure d'une scène vidéo"""
    scene_number: int
    description: str
    duration: float
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    prompt: Optional[str] = None
    status: str = "pending"

class IntegratedAnimationService:
    """Service complet de génération d'animation narratif avec CrewAI"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.runway_api_key = os.getenv("RUNWAY_API_KEY")
        self.cache_dir = Path("cache/animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration CrewAI
        self.llm = ChatOpenAI(
            api_key=self.openai_api_key,
            model="gpt-4o-mini",
            temperature=0.7
        )
        
        print("🎬 Service Animation Intégré initialisé")
        print(f"📁 Cache: {self.cache_dir}")
    
    def create_agents(self) -> Dict[str, Agent]:
        """Créer les agents CrewAI spécialisés"""
        
        agents = {}
        
        # 1. Scénariste
        agents['screenwriter'] = Agent(
            role="Scénariste Expert",
            goal="Découper une histoire en scènes visuelles parfaites pour l'animation",
            backstory="""Tu es un scénariste expérimenté spécialisé dans les contenus pour enfants. 
            Tu excelles à découper une histoire en 3-8 scènes visuelles captivantes de 5-10 secondes chacune.
            Tu identifies les moments clés et les actions visuellement intéressantes.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 2. Directeur Artistique
        agents['art_director'] = Agent(
            role="Directeur Artistique",
            goal="Définir un style visuel cohérent pour toute l'animation",
            backstory="""Tu es un directeur artistique expert en animation pour enfants.
            Tu définis des styles visuels harmonieux, des palettes de couleurs et
            tu assures la cohérence des personnages tout au long de l'histoire.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 3. Prompt Engineer
        agents['prompt_engineer'] = Agent(
            role="Prompt Engineer Expert",
            goal="Créer des prompts optimaux pour Runway Gen-4",
            backstory="""Tu es expert en IA générative et en création de prompts pour Runway.
            Tu sais comment formuler des descriptions précises de 50-200 caractères qui produisent 
            des vidéos fluides et visuellement impressionnantes.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        return agents
    
    def create_tasks(self, story_text: str, style_preferences: Dict[str, str], agents: Dict[str, Agent]) -> List[Task]:
        """Créer les tâches pour les agents"""
        
        tasks = []
        
        # 1. Tâche Scénariste
        scenario_task = Task(
            description=f"""
            Analyse cette histoire et découpe-la en scènes visuelles pour l'animation :
            
            HISTOIRE : {story_text}
            
            INSTRUCTIONS :
            - Créer 3 à 6 scènes de 5-10 secondes chacune (max 60s total)
            - Chaque scène doit être visuellement claire et captivante
            - Assurer une progression narrative fluide
            - Adapter pour enfants de 3-8 ans
            
            FORMAT JSON OBLIGATOIRE :
            {{
                "scenes": [
                    {{
                        "scene_number": 1,
                        "duration": 8,
                        "description": "Description visuelle précise de la scène",
                        "action": "Action principale visible",
                        "setting": "Décor de la scène"
                    }}
                ],
                "total_scenes": 4,
                "estimated_duration": 32
            }}
            """,
            agent=agents['screenwriter'],
            expected_output="Structure JSON avec toutes les scènes décomposées"
        )
        
        # 2. Tâche Direction Artistique
        art_task = Task(
            description=f"""
            Définis le style visuel pour cette animation :
            
            PRÉFÉRENCES : {style_preferences}
            
            INSTRUCTIONS :
            - Style visuel cohérent et attractif pour enfants
            - Palette de couleurs harmonieuse
            - Descriptions des personnages et décors
            
            FORMAT JSON OBLIGATOIRE :
            {{
                "visual_style": "Style général (ex: cartoon coloré, 3D mignon)",
                "color_palette": ["couleur1", "couleur2", "couleur3"],
                "characters_style": "Description style des personnages",
                "settings_style": "Description style des décors",
                "global_keywords": ["cartoon", "colorful", "child-friendly"]
            }}
            """,
            agent=agents['art_director'],
            expected_output="Direction artistique complète en JSON"
        )
        
        # 3. Tâche Prompt Engineering
        prompt_task = Task(
            description="""
            Crée des prompts optimisés pour Runway Gen-4 basés sur les scènes et le style.
            
            CONTRAINTES RUNWAY :
            - Prompt de 50-200 caractères maximum
            - Éviter les mots interdits (violence, armes, etc.)
            - Style adapté à l'animation pour enfants
            
            FORMAT JSON OBLIGATOIRE :
            {{
                "video_prompts": [
                    {{
                        "scene_number": 1,
                        "prompt": "Prompt court et précis pour Runway",
                        "duration": 8,
                        "style_keywords": "cartoon, colorful, smooth animation"
                    }}
                ],
                "global_style": "Style général à maintenir"
            }}
            """,
            agent=agents['prompt_engineer'],
            expected_output="Prompts optimisés pour toutes les scènes",
            context=[scenario_task, art_task]
        )
        
        tasks.extend([scenario_task, art_task, prompt_task])
        
        return tasks
    
    async def call_runway_api(self, prompt: str, duration: int = 5) -> Dict[str, Any]:
        """Appel à l'API Runway pour générer une vidéo"""
        
        if not self.runway_api_key:
            # Mode simulation pour les tests
            return {
                "id": f"test_video_{uuid.uuid4().hex[:8]}",
                "status": "success",
                "video_url": "https://example.com/test_video.mp4",
                "duration": duration
            }
        
        headers = {
            "Authorization": f"Bearer {self.runway_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompt": prompt[:200],  # Limiter à 200 caractères
            "duration": min(duration, 10),  # Max 10s pour Runway
            "aspect_ratio": "16:9",
            "motion": "medium"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Démarrer la génération
                async with session.post(
                    "https://api.runwayml.com/v1/generate/video",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        raise Exception(f"Erreur API Runway: {response.status}")
                    
                    result = await response.json()
                    task_id = result.get("id")
                    
                    if not task_id:
                        raise Exception("Pas d'ID de tâche retourné par Runway")
                    
                    # Attendre la complétion
                    max_wait = 300  # 5 minutes max
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        await asyncio.sleep(10)
                        wait_time += 10
                        
                        # Vérifier le statut
                        async with session.get(
                            f"https://api.runwayml.com/v1/tasks/{task_id}",
                            headers=headers
                        ) as status_response:
                            
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                
                                if status_data.get("status") == "completed":
                                    return {
                                        "id": task_id,
                                        "status": "success",
                                        "video_url": status_data.get("output", {}).get("video_url"),
                                        "duration": duration
                                    }
                                elif status_data.get("status") == "failed":
                                    raise Exception(f"Génération échouée: {status_data.get('error', 'Erreur inconnue')}")
                    
                    raise Exception("Timeout: génération trop longue")
                    
        except Exception as e:
            print(f"❌ Erreur API Runway: {e}")
            # Retourner un résultat de test en cas d'erreur
            return {
                "id": f"fallback_video_{uuid.uuid4().hex[:8]}",
                "status": "fallback",
                "video_url": None,
                "duration": duration,
                "error": str(e)
            }
    
    async def download_video(self, video_url: str, scene_number: int) -> str:
        """Télécharger une vidéo générée"""
        
        if not video_url or video_url.startswith("https://example.com"):
            # Mode simulation - créer un fichier factice
            fake_path = self.cache_dir / f"scene_{scene_number}_fake.mp4"
            fake_path.touch()
            return str(fake_path)
        
        local_path = self.cache_dir / f"scene_{scene_number}_{int(time.time())}.mp4"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        with open(local_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        print(f"✅ Vidéo téléchargée: {local_path}")
                        return str(local_path)
                    else:
                        raise Exception(f"Erreur téléchargement: {response.status}")
                        
        except Exception as e:
            print(f"❌ Erreur téléchargement vidéo: {e}")
            # Créer un fichier factice en cas d'erreur
            fake_path = self.cache_dir / f"scene_{scene_number}_error.mp4"
            fake_path.touch()
            return str(fake_path)
    
    def assemble_final_video(self, video_scenes: List[VideoScene], output_path: str) -> str:
        """Assembler les vidéos en une animation finale"""
        
        try:
            clips = []
            
            for scene in video_scenes:
                if scene.local_path and os.path.exists(scene.local_path):
                    # Si c'est un fichier factice (pour les tests), créer un clip noir
                    if os.path.getsize(scene.local_path) == 0:
                        print(f"⚠️ Fichier factice détecté pour scène {scene.scene_number}")
                        # Créer un clip coloré de test
                        from moviepy.editor import ColorClip
                        clip = ColorClip(size=(1280, 720), color=(100, 150, 200), duration=scene.duration)
                    else:
                        clip = VideoFileClip(scene.local_path)
                        
                        # Ajuster la durée si nécessaire
                        if clip.duration != scene.duration:
                            clip = clip.subclip(0, min(clip.duration, scene.duration))
                    
                    clips.append(clip)
                    print(f"✅ Clip ajouté: Scène {scene.scene_number} ({scene.duration}s)")
            
            if not clips:
                raise Exception("Aucun clip vidéo disponible pour l'assemblage")
            
            # Assembler les clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Exporter la vidéo finale
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac' if final_video.audio else None,
                temp_audiofile=str(self.cache_dir / "temp_audio.wav"),
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Nettoyer les clips
            for clip in clips:
                clip.close()
            final_video.close()
            
            print(f"🎬 Vidéo finale assemblée: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur assemblage vidéo: {e}")
            raise Exception(f"Échec assemblage vidéo: {str(e)}")
    
    async def generate_complete_animation(self, story_text: str, style_preferences: Dict[str, str] = None) -> Dict[str, Any]:
        """Génération complète d'une animation narrative"""
        
        start_time = time.time()
        
        if style_preferences is None:
            style_preferences = {
                "style": "cartoon coloré",
                "mood": "joyeux",
                "target_age": "3-8 ans"
            }
        
        print(f"🎬 === DÉBUT GÉNÉRATION ANIMATION COMPLÈTE ===")
        print(f"📝 Histoire: {story_text[:100]}...")
        print(f"🎨 Style: {style_preferences}")
        
        try:
            # 1. Créer les agents
            agents = self.create_agents()
            print(f"👥 {len(agents)} agents créés")
            
            # 2. Créer les tâches
            tasks = self.create_tasks(story_text, style_preferences, agents)
            print(f"📋 {len(tasks)} tâches créées")
            
            # 3. Créer l'équipe CrewAI
            crew = Crew(
                agents=list(agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # 4. Exécuter CrewAI
            print("🚀 Lancement CrewAI...")
            crew_result = crew.kickoff()
            
            # 5. Parser les résultats
            print("🔍 Analyse des résultats CrewAI...")
            
            # Extraire les prompts du dernier résultat (prompt engineering)
            last_result = crew_result.tasks_output[-1].raw if crew_result.tasks_output else "{}"
            
            try:
                prompt_data = json.loads(last_result)
                video_prompts = prompt_data.get("video_prompts", [])
            except:
                print("⚠️ Erreur parsing JSON, utilisation de prompts par défaut")
                video_prompts = [
                    {
                        "scene_number": 1,
                        "prompt": f"cartoon animation of {story_text[:50]}",
                        "duration": 8
                    }
                ]
            
            print(f"🎥 {len(video_prompts)} scènes à générer")
            
            # 6. Générer les vidéos pour chaque scène
            video_scenes = []
            
            for prompt_data in video_prompts:
                scene_num = prompt_data.get("scene_number", 1)
                prompt = prompt_data.get("prompt", "")
                duration = prompt_data.get("duration", 5)
                
                print(f"🎬 Génération scène {scene_num}: {prompt[:50]}...")
                
                # Appel API Runway
                video_result = await self.call_runway_api(prompt, duration)
                
                # Créer l'objet VideoScene
                scene = VideoScene(
                    scene_number=scene_num,
                    description=prompt,
                    duration=duration,
                    video_url=video_result.get("video_url"),
                    prompt=prompt,
                    status="generated" if video_result.get("status") == "success" else "error"
                )
                
                # Télécharger la vidéo si disponible
                if scene.video_url:
                    scene.local_path = await self.download_video(scene.video_url, scene_num)
                else:
                    print(f"⚠️ Pas de vidéo générée pour scène {scene_num}")
                    # Créer un fichier factice pour continuer
                    fake_path = self.cache_dir / f"scene_{scene_num}_missing.mp4"
                    fake_path.touch()
                    scene.local_path = str(fake_path)
                
                video_scenes.append(scene)
                print(f"✅ Scène {scene_num} traitée")
            
            # 7. Assembler la vidéo finale
            print("🎬 Assemblage de la vidéo finale...")
            
            timestamp = int(time.time())
            output_filename = f"animation_{timestamp}.mp4"
            output_path = str(self.cache_dir / output_filename)
            
            final_video_path = self.assemble_final_video(video_scenes, output_path)
            
            # 8. Préparer le résultat
            total_time = time.time() - start_time
            
            result = {
                "status": "success",
                "video_path": final_video_path,
                "video_url": f"/static/cache/animations/{output_filename}",
                "scenes_count": len(video_scenes),
                "total_duration": sum(scene.duration for scene in video_scenes),
                "generation_time": round(total_time, 2),
                "scenes_details": [
                    {
                        "scene_number": scene.scene_number,
                        "description": scene.description,
                        "duration": scene.duration,
                        "status": scene.status
                    }
                    for scene in video_scenes
                ],
                "timestamp": datetime.now().isoformat(),
                "story_input": story_text,
                "style_preferences": style_preferences
            }
            
            print(f"🎉 === ANIMATION GÉNÉRÉE AVEC SUCCÈS ===")
            print(f"⏱️  Temps total: {total_time:.1f}s")
            print(f"🎬 Vidéo: {final_video_path}")
            print(f"📊 {len(video_scenes)} scènes assemblées")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération complète: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "generation_time": time.time() - start_time
            }

# Instance globale
integrated_animation_service = IntegratedAnimationService()
