"""
Service d'Animation avec CrewAI - Équipe Multi-Agents
Génération automatique de dessins animés à partir de texte narratif
Architecture: Scénariste → Directeur Artistique → Prompt Engineer → Opérateur Technique → Monteur Vidéo
"""

import os
import json
import asyncio
import aiohttp
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Charger les variables d'environnement CrewAI
load_dotenv('.env.crewai')

# Imports CrewAI
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Video processing
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip
import requests

@dataclass
class AnimationScene:
    """Structure d'une scène d'animation"""
    scene_number: int
    description: str
    duration: float
    action: str
    setting: str
    visual_prompt: Optional[str] = None
    seed: Optional[str] = None
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    status: str = "pending"

@dataclass
class VisualStyle:
    """Direction artistique pour l'animation"""
    global_style: str
    color_palette: List[str]
    characters_style: str
    settings_style: str
    mood: str
    keywords: List[str]
    character_seeds: Dict[str, str]
    setting_seeds: Dict[str, str]

class AnimationCrewAIService:
    """Service complet de génération d'animation avec équipe CrewAI"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY") 
        self.cache_dir = Path("cache/crewai_animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration CrewAI
        try:
            self.llm = ChatOpenAI(
                openai_api_key=self.openai_api_key or "dummy",
                model="gpt-4"
            )
        except Exception as e:
            print(f"⚠️ Erreur configuration LLM: {e}")
            self.llm = None
        
        print("Service Animation CrewAI initialise")
        print(f"Cache: {self.cache_dir}")
    
    def create_agents(self) -> Dict[str, Agent]:
        """Créer l'équipe d'agents CrewAI spécialisés"""
        
        agents = {}
        
        # 🧩 Agent 1: Scénariste
        agents['screenwriter'] = Agent(
            role="Scénariste Expert en Animation",
            goal="Découper une histoire en segments courts et visuels parfaits pour l'animation (5-15s chacun)",
            backstory="""Tu es un scénariste expérimenté spécialisé dans l'animation pour enfants. 
            Tu excelles à transformer une histoire narrative en séquence de scènes visuelles captivantes.
            Tu comprends le rythme de l'animation et sais identifier les moments-clés qui feront de bonnes scènes.
            Tu adaptes automatiquement pour les enfants de 3 à 8 ans avec un storytelling fluide.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 🎨 Agent 2: Directeur Artistique
        agents['art_director'] = Agent(
            role="Directeur Artistique et Responsable Cohérence Visuelle",
            goal="Définir un style visuel unifié et créer des seeds pour garantir la cohérence des personnages et décors",
            backstory="""Tu es un directeur artistique expert en animation 2D/3D pour enfants.
            Tu définis des palettes harmonieuses, des styles cohérents et tu crées des 'seeds' spécifiques
            pour chaque personnage et décor afin d'assurer une continuité visuelle parfaite d'une scène à l'autre.
            Tu connais les techniques pour maintenir l'identité visuelle dans la génération IA.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 🧠 Agent 3: Prompt Engineer
        agents['prompt_engineer'] = Agent(
            role="Prompt Engineer Expert en Génération Vidéo IA",
            goal="Transformer chaque scène en prompts riches et précis pour Stable Diffusion Video avec seeds appropriés",
            backstory="""Tu es expert en génération vidéo par IA, spécialisé dans Stable Diffusion Video.
            Tu sais créer des prompts détaillés qui produisent des animations de qualité, en intégrant
            personnages, actions, décors, ambiance et style de façon optimale.
            Tu maîtrises l'usage des seeds pour la cohérence visuelle.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 📡 Agent 4: Opérateur Technique
        agents['technical_operator'] = Agent(
            role="Opérateur Technique et Gestionnaire API",
            goal="Orchestrer les appels API de génération vidéo et s'assurer de la qualité des rendus",
            backstory="""Tu es un technicien expert en APIs de génération vidéo.
            Tu gères les appels techniques, optimises les paramètres de génération,
            gères les erreurs et t'assures que chaque clip vidéo est généré correctement.
            Tu connais les limites techniques et sais adapter les requêtes.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 🎬 Agent 5: Monteur Vidéo
        agents['video_editor'] = Agent(
            role="Monteur Vidéo et Assembleur Final",
            goal="Assembler tous les clips dans l'ordre narratif pour créer une vidéo fluide et homogène",
            backstory="""Tu es un monteur vidéo spécialisé dans l'animation pour enfants.
            Tu connais le rythme narratif, les transitions fluides et tu sais créer
            une expérience visuelle cohérente à partir de clips individuels.
            Tu optimises la durée finale pour respecter les contraintes (30s-5min).""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        return agents
    
    def create_tasks(self, story_text: str, style_preferences: Dict[str, str], agents: Dict[str, Agent]) -> List[Task]:
        """Créer les tâches pour l'équipe d'agents"""
        
        tasks = []
        
        # 📋 Tâche 1: Découpage Narratif
        scenario_task = Task(
            description=f"""
            MISSION: Analyser cette histoire et la découper en scènes visuelles optimales pour l'animation.
            
            HISTOIRE À ANALYSER: {story_text}
            
            CONTRAINTES:
            - Créer 4 à 12 scènes de 5 à 15 secondes chacune
            - Durée totale: entre 30 secondes et 5 minutes maximum
            - Chaque scène doit être visuellement claire et captivante
            - Progression narrative fluide et logique
            - Adapté aux enfants de 3 à 8 ans
            - Identifier les personnages principaux et les décors récurrents
            
            FORMAT JSON OBLIGATOIRE:
            {{
                "story_analysis": {{
                    "main_characters": ["personnage1", "personnage2"],
                    "main_settings": ["décor1", "décor2"],
                    "narrative_arc": "description de l'arc narratif"
                }},
                "scenes": [
                    {{
                        "scene_number": 1,
                        "duration": 8,
                        "description": "Description visuelle précise de la scène",
                        "action": "Action principale visible à l'écran",
                        "setting": "Décor/lieu de la scène",
                        "characters": ["personnages présents"],
                        "visual_focus": "Élément visuel principal"
                    }}
                ],
                "total_scenes": 5,
                "estimated_duration": 40,
                "narrative_coherence": "Explication de la cohérence narrative"
            }}
            """,
            agent=agents['screenwriter'],
            expected_output="Découpage narratif structuré en JSON avec analyse complète"
        )
        
        # 🎨 Tâche 2: Direction Artistique et Seeds
        art_direction_task = Task(
            description=f"""
            MISSION: Définir la direction artistique complète avec seeds pour la cohérence visuelle.
            
            STYLE DEMANDÉ: {style_preferences}
            
            CONTRAINTES:
            - Style visuel cohérent et attractif pour enfants 3-8 ans
            - Palette de couleurs harmonieuse
            - Créer des seeds spécifiques pour chaque personnage et décor
            - Assurer la continuité visuelle entre toutes les scènes
            - Style adapté à la génération vidéo IA
            
            FORMAT JSON OBLIGATOIRE:
            {{
                "visual_style": {{
                    "global_style": "Description du style général (ex: cartoon 3D coloré)",
                    "color_palette": ["#couleur1", "#couleur2", "#couleur3"],
                    "mood": "ambiance générale (joyeux, aventureux, etc.)",
                    "art_keywords": ["cartoon", "colorful", "child-friendly", "smooth"]
                }},
                "character_design": {{
                    "characters_style": "Description du style des personnages",
                    "character_seeds": {{
                        "personnage1": "seed_unique_123",
                        "personnage2": "seed_unique_456"
                    }}
                }},
                "environment_design": {{
                    "settings_style": "Description du style des décors",
                    "setting_seeds": {{
                        "décor1": "seed_env_789",
                        "décor2": "seed_env_012"
                    }}
                }},
                "consistency_guidelines": "Instructions pour maintenir la cohérence visuelle"
            }}
            """,
            agent=agents['art_director'],
            expected_output="Direction artistique complète avec seeds pour cohérence",
            context=[scenario_task]
        )
        
        # 🧠 Tâche 3: Génération de Prompts Optimisés
        prompt_engineering_task = Task(
            description="""
            MISSION: Créer des prompts optimisés pour Stable Diffusion Video avec seeds appropriés.
            
            CONTRAINTES TECHNIQUES:
            - Prompts détaillés mais concis pour la génération vidéo
            - Intégrer le style visuel et les seeds de cohérence
            - Optimisé pour Stable Diffusion Video
            - Éviter les termes incompatibles avec l'IA de génération
            - Assurer la fluidité d'animation entre les scènes
            
            FORMAT JSON OBLIGATOIRE:
            {{
                "video_prompts": [
                    {{
                        "scene_number": 1,
                        "prompt": "Prompt détaillé pour Stable Diffusion Video",
                        "duration": 8,
                        "seed": "seed_approprié",
                        "style_keywords": "mots-clés de style spécifiques",
                        "technical_params": {{
                            "motion": "medium",
                            "aspect_ratio": "16:9",
                            "fps": 24
                        }}
                    }}
                ],
                "global_style_prompt": "Style général à maintenir sur toutes les scènes",
                "consistency_instructions": "Instructions pour maintenir la cohérence"
            }}
            """,
            agent=agents['prompt_engineer'],
            expected_output="Prompts optimisés pour génération vidéo avec paramètres techniques",
            context=[scenario_task, art_direction_task]
        )
        
        # 📡 Tâche 4: Orchestration Technique
        technical_task = Task(
            description="""
            MISSION: Planifier et orchestrer la génération vidéo de toutes les scènes.
            
            RESPONSABILITÉS:
            - Analyser les prompts et paramètres techniques
            - Planifier l'ordre de génération optimal
            - Prévoir la gestion des erreurs et reprises
            - Optimiser les ressources et le temps de génération
            - Valider la qualité attendue de chaque clip
            
            FORMAT JSON OBLIGATOIRE:
            {{
                "generation_plan": {{
                    "total_clips": 5,
                    "estimated_time": "15-20 minutes",
                    "generation_order": [1, 2, 3, 4, 5],
                    "parallel_possible": false
                }},
                "technical_validation": {{
                    "all_prompts_valid": true,
                    "seeds_assigned": true,
                    "durations_optimal": true,
                    "style_consistent": true
                }},
                "fallback_strategy": {{
                    "backup_prompts": "Stratégie en cas d'échec",
                    "quality_thresholds": "Seuils de qualité minimum"
                }},
                "execution_ready": true
            }}
            """,
            agent=agents['technical_operator'],
            expected_output="Plan d'exécution technique validé",
            context=[prompt_engineering_task]
        )
        
        # 🎬 Tâche 5: Plan de Montage
        editing_task = Task(
            description="""
            MISSION: Planifier l'assemblage final et les transitions entre scènes.
            
            OBJECTIFS:
            - Créer un plan de montage fluide et rythmé
            - Définir les transitions entre scènes
            - Optimiser la durée finale (30s-5min)
            - Assurer la cohérence narrative et visuelle
            - Prévoir les ajustements post-génération
            
            FORMAT JSON OBLIGATOIRE:
            {{
                "editing_plan": {{
                    "total_duration": 45,
                    "scene_transitions": [
                        {{
                            "from_scene": 1,
                            "to_scene": 2,
                            "transition_type": "cut/fade/dissolve",
                            "transition_duration": 0.5
                        }}
                    ]
                }},
                "rhythm_analysis": {{
                    "pacing": "Description du rythme narratif",
                    "climax_placement": "Positionnement du point culminant",
                    "emotional_arc": "Arc émotionnel de l'animation"
                }},
                "post_processing": {{
                    "color_correction": "Corrections colorimétriques nécessaires",
                    "audio_sync": "Synchronisation audio si applicable",
                    "final_adjustments": "Ajustements finaux prévus"
                }},
                "export_settings": {{
                    "format": "MP4",
                    "resolution": "1920x1080",
                    "fps": 24,
                    "bitrate": "high"
                }}
            }}
            """,
            agent=agents['video_editor'],
            expected_output="Plan de montage complet et optimisé",
            context=[scenario_task, art_direction_task, technical_task]
        )
        
        tasks.extend([scenario_task, art_direction_task, prompt_engineering_task, technical_task, editing_task])
        
        return tasks
    
    async def call_video_generation_api(self, prompt: str, duration: int = 8, seed: Optional[str] = None) -> Dict[str, Any]:
        """Appel à l'API de génération vidéo (Stable Diffusion Video ou équivalent)"""
        
        if not self.stability_api_key:
            # Mode simulation pour les tests
            print(f"🎭 Mode simulation - Génération: {prompt[:50]}...")
            await asyncio.sleep(2)  # Simuler le temps de génération
            
            return {
                "id": f"sim_video_{uuid.uuid4().hex[:8]}",
                "status": "success",
                "video_url": f"https://example.com/simulated_video_{seed or 'noseed'}.mp4",
                "duration": duration,
                "prompt": prompt,
                "seed": seed
            }
        
        # Configuration pour l'API réelle (Stability AI ou équivalent)
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "duration": min(duration, 15),  # Max 15s par clip
            "seed": seed,
            "motion": "medium",
            "aspect_ratio": "16:9",
            "fps": 24
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # API endpoint pour Stability AI Video
                async with session.post(
                    "https://api.stability.ai/v2alpha/generation/video",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        raise Exception(f"Erreur API Video: {response.status}")
                    
                    result = await response.json()
                    task_id = result.get("id")
                    
                    if not task_id:
                        raise Exception("Pas d'ID de tâche retourné")
                    
                    # Attendre la complétion (polling)
                    max_wait = 180  # 3 minutes max par clip
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        await asyncio.sleep(10)
                        wait_time += 10
                        
                        # Vérifier le statut
                        async with session.get(
                            f"https://api.stability.ai/v2alpha/generation/video/{task_id}",
                            headers=headers
                        ) as status_response:
                            
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                
                                if status_data.get("status") == "completed":
                                    return {
                                        "id": task_id,
                                        "status": "success",
                                        "video_url": status_data.get("video", {}).get("url"),
                                        "duration": duration,
                                        "prompt": prompt,
                                        "seed": seed
                                    }
                                elif status_data.get("status") == "failed":
                                    raise Exception(f"Génération échouée: {status_data.get('error', 'Erreur inconnue')}")
                    
                    raise Exception("Timeout: génération trop longue")
                    
        except Exception as e:
            print(f"❌ Erreur API Vidéo: {e}")
            # Retourner un résultat de simulation en cas d'erreur
            return {
                "id": f"fallback_video_{uuid.uuid4().hex[:8]}",
                "status": "fallback",
                "video_url": None,
                "duration": duration,
                "error": str(e),
                "prompt": prompt,
                "seed": seed
            }
    
    async def download_video(self, video_url: str, scene_number: int) -> str:
        """Télécharger une vidéo générée"""
        
        if not video_url or video_url.startswith("https://example.com"):
            # Mode simulation - créer un fichier factice
            fake_path = self.cache_dir / f"scene_{scene_number}_simulation.mp4"
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
    
    def assemble_final_animation(self, animation_scenes: List[AnimationScene], output_path: str, editing_plan: Dict[str, Any]) -> str:
        """Assembler les vidéos en animation finale selon le plan de montage"""
        
        try:
            clips = []
            
            for scene in animation_scenes:
                if scene.local_path and os.path.exists(scene.local_path):
                    # Si c'est un fichier factice (simulation), créer un clip coloré
                    if os.path.getsize(scene.local_path) == 0:
                        print(f"🎭 Clip de simulation pour scène {scene.scene_number}")
                        # Créer un clip coloré avec texte pour simulation
                        colors = [(100, 150, 200), (200, 100, 150), (150, 200, 100), (200, 150, 100), (100, 200, 150)]
                        color = colors[scene.scene_number % len(colors)]
                        clip = ColorClip(size=(1920, 1080), color=color, duration=scene.duration)
                    else:
                        clip = VideoFileClip(scene.local_path)
                        
                        # Ajuster la durée si nécessaire
                        if clip.duration != scene.duration:
                            clip = clip.subclip(0, min(clip.duration, scene.duration))
                    
                    clips.append(clip)
                    print(f"✅ Clip ajouté: Scène {scene.scene_number} ({scene.duration}s)")
            
            if not clips:
                raise Exception("Aucun clip vidéo disponible pour l'assemblage")
            
            # Assembler selon le plan de montage
            transitions = editing_plan.get("editing_plan", {}).get("scene_transitions", [])
            
            # Pour l'instant, assemblage simple (transitions avancées à implémenter)
            final_animation = concatenate_videoclips(clips, method="compose")
            
            # Exporter l'animation finale
            final_animation.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec=None,  # Pas d'audio pour l'instant
                temp_audiofile=str(self.cache_dir / "temp_audio.wav"),
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Nettoyer les clips
            for clip in clips:
                clip.close()
            final_animation.close()
            
            print(f"🎬 Animation finale assemblée: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur assemblage animation: {e}")
            raise Exception(f"Échec assemblage animation: {str(e)}")
    
    async def generate_complete_animation(self, story_text: str, style_preferences: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Génération complète d'une animation narrative avec équipe CrewAI"""
        
        start_time = time.time()
        
        if style_preferences is None:
            style_preferences = {
                "style": "cartoon 3D coloré",
                "mood": "joyeux et aventureux",
                "target_age": "3-8 ans",
                "theme": "éducatif et divertissant"
            }
        
        print(f"🎬 === DÉBUT GÉNÉRATION ANIMATION CREWAI ===")
        print(f"📝 Histoire: {story_text[:100]}...")
        print(f"🎨 Style: {style_preferences}")
        
        try:
            # 1. Créer l'équipe d'agents
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
                verbose=True,
                memory=True  # Activer la mémoire pour la cohérence
            )
            
            # 4. Exécuter le pipeline CrewAI
            print("🚀 Lancement pipeline CrewAI...")
            crew_result = crew.kickoff()
            
            # 5. Parser les résultats des agents
            print("🔍 Analyse des résultats CrewAI...")
            
            # Extraire les résultats de chaque agent
            tasks_output = crew_result.tasks_output
            
            # Scénariste (tâche 0)
            scenario_result = self._parse_json_result(tasks_output[0].raw if tasks_output else "{}")
            scenes_data = scenario_result.get("scenes", [])
            
            # Directeur Artistique (tâche 1)
            art_result = self._parse_json_result(tasks_output[1].raw if len(tasks_output) > 1 else "{}")
            visual_style = art_result
            
            # Prompt Engineer (tâche 2)
            prompt_result = self._parse_json_result(tasks_output[2].raw if len(tasks_output) > 2 else "{}")
            video_prompts = prompt_result.get("video_prompts", [])
            
            # Plan de montage (tâche 4)
            editing_result = self._parse_json_result(tasks_output[4].raw if len(tasks_output) > 4 else "{}")
            
            print(f"🎥 {len(video_prompts)} scènes à générer")
            
            # 6. Générer les vidéos pour chaque scène
            animation_scenes = []
            
            for i, prompt_data in enumerate(video_prompts):
                scene_num = prompt_data.get("scene_number", i + 1)
                prompt = prompt_data.get("prompt", "")
                duration = prompt_data.get("duration", 8)
                seed = prompt_data.get("seed", None)
                
                print(f"🎬 Génération scène {scene_num}: {prompt[:50]}...")
                
                # Trouver les données de scène correspondantes
                scene_data = next((s for s in scenes_data if s.get("scene_number") == scene_num), {})
                
                # Appel API génération vidéo
                video_result = await self.call_video_generation_api(prompt, duration, seed)
                
                # Créer l'objet AnimationScene
                scene = AnimationScene(
                    scene_number=scene_num,
                    description=scene_data.get("description", prompt),
                    duration=duration,
                    action=scene_data.get("action", ""),
                    setting=scene_data.get("setting", ""),
                    visual_prompt=prompt,
                    seed=seed,
                    video_url=video_result.get("video_url"),
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
                
                animation_scenes.append(scene)
                print(f"✅ Scène {scene_num} traitée")
            
            # 7. Assembler l'animation finale
            print("🎬 Assemblage de l'animation finale...")
            
            timestamp = int(time.time())
            output_filename = f"crewai_animation_{timestamp}.mp4"
            output_path = str(self.cache_dir / output_filename)
            
            final_animation_path = self.assemble_final_animation(animation_scenes, output_path, editing_result)
            
            # 8. Préparer le résultat complet
            total_time = time.time() - start_time
            
            result = {
                "status": "success",
                "video_path": final_animation_path,
                "video_url": f"/static/cache/crewai_animations/{output_filename}",
                "scenes_count": len(animation_scenes),
                "total_duration": sum(scene.duration for scene in animation_scenes),
                "generation_time": round(total_time, 2),
                "pipeline_type": "crewai_multi_agent",
                "agents_used": list(agents.keys()),
                "scenes_details": [
                    {
                        "scene_number": scene.scene_number,
                        "description": scene.description,
                        "duration": scene.duration,
                        "action": scene.action,
                        "setting": scene.setting,
                        "status": scene.status,
                        "prompt": scene.visual_prompt,
                        "seed": scene.seed
                    }
                    for scene in animation_scenes
                ],
                "visual_style": visual_style,
                "narrative_analysis": scenario_result.get("story_analysis", {}),
                "editing_plan": editing_result,
                "timestamp": datetime.now().isoformat(),
                "story_input": story_text,
                "style_preferences": style_preferences
            }
            
            print(f"🎉 === ANIMATION CREWAI GÉNÉRÉE AVEC SUCCÈS ===")
            print(f"⏱️  Temps total: {total_time:.1f}s")
            print(f"🎬 Vidéo: {final_animation_path}")
            print(f"📊 {len(animation_scenes)} scènes assemblées")
            print(f"👥 {len(agents)} agents utilisés")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération CrewAI: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "generation_time": time.time() - start_time,
                "pipeline_type": "crewai_multi_agent"
            }
    
    def _parse_json_result(self, result_text: str) -> Dict[str, Any]:
        """Parser le résultat JSON d'un agent avec gestion d'erreur"""
        try:
            # Nettoyer le texte et extraire le JSON
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                if json_end != -1:
                    result_text = result_text[json_start:json_end]
            
            return json.loads(result_text)
        except Exception as e:
            print(f"⚠️ Erreur parsing JSON: {e}")
            return {}

# Instance globale
animation_crewai_service = AnimationCrewAIService()
