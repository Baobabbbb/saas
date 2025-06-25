"""
Architecture CrewAI pour la génération de dessins animés narratifs
Système multi-agents pour créer des vidéos cohérentes à partir de texte
"""

from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
import os
from typing import Dict, List, Any
from datetime import datetime
import json
import asyncio
import aiohttp
import time
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pathlib import Path

class AnimationCrewAI:
    """Orchestrateur principal pour la génération de dessins animés"""
    
    def __init__(self):
        self.llm = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4"
        )
        
        # Initialiser les agents
        self.scenario_agent = self._create_scenario_agent()
        self.art_director_agent = self._create_art_director_agent()
        self.prompt_engineer_agent = self._create_prompt_engineer_agent()
        self.technical_agent = self._create_technical_agent()
        self.video_editor_agent = self._create_video_editor_agent()
        
        print("🎬 Équipe CrewAI Animation initialisée")
        print("👥 5 agents spécialisés prêts")

    def _create_scenario_agent(self) -> Agent:
        """🧩 Agent Scénariste - Découpe l'histoire en scènes"""
        return Agent(
            role="Scénariste Expert",
            goal="Transformer une histoire en séquences visuelles parfaites pour l'animation",
            backstory="""Tu es un scénariste expérimenté spécialisé dans les contenus pour enfants. 
            Tu excelles à découper une histoire en scènes visuelles captivantes de 5-15 secondes chacune.
            Tu sais identifier les moments clés, les transitions fluides et les actions visuellement intéressantes.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def _create_art_director_agent(self) -> Agent:
        """🎨 Agent Directeur Artistique - Définit le style visuel"""
        return Agent(
            role="Directeur Artistique",
            goal="Créer une identité visuelle cohérente et attractive pour le dessin animé",
            backstory="""Tu es un directeur artistique reconnu dans l'animation pour enfants.
            Tu définis des styles visuels harmonieux, des palettes de couleurs adaptées et
            tu assures la cohérence des personnages et décors tout au long de l'histoire.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def _create_prompt_engineer_agent(self) -> Agent:
        """🧠 Agent Prompt Engineer - Optimise pour l'IA générative"""
        return Agent(
            role="Prompt Engineer Expert",
            goal="Créer des prompts parfaits pour générer des vidéos de haute qualité",
            backstory="""Tu es expert en IA générative et en création de prompts pour Stable Diffusion Video
            et Runway. Tu sais comment formuler des descriptions précises qui produisent des vidéos
            fluides, cohérentes et visuellement impressionnantes.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def _create_technical_agent(self) -> Agent:
        """📡 Agent Opérateur Technique - Gère la génération vidéo"""
        return Agent(
            role="Opérateur Technique",
            goal="Orchestrer la génération vidéo via API et garantir la qualité technique",
            backstory="""Tu es un technicien expert en intégration d'APIs de génération vidéo.
            Tu gères les appels API, optimises les paramètres techniques et assures
            que chaque clip est généré correctement avec la meilleure qualité possible.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def _create_video_editor_agent(self) -> Agent:
        """🎬 Agent Monteur Vidéo - Assemble le résultat final"""
        return Agent(
            role="Monteur Vidéo",
            goal="Assembler les clips en une vidéo fluide et engageante",
            backstory="""Tu es un monteur expérimenté spécialisé dans l'animation pour enfants.
            Tu sais assembler les clips pour créer un rythme engageant, des transitions
            fluides et un résultat final professionnel.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_animation_tasks(self, story_text: str, style_preferences: Dict[str, str]) -> List[Task]:
        """Créer les tâches pour chaque agent"""
        
        # 1. Tâche Scénariste
        scenario_task = Task(
            description=f"""
            Analyse cette histoire et découpe-la en scènes visuelles parfaites pour l'animation :
            
            HISTOIRE : {story_text}
            
            INSTRUCTIONS :
            - Créer 4 à 12 scènes de 5-15 secondes chacune
            - Chaque scène doit être visuellement claire et captivante
            - Assurer une progression narrative fluide
            - Adapter le contenu pour les enfants de 3-8 ans
            - Identifier les personnages principaux et les décors
            
            FORMAT DE SORTIE (JSON) :
            {{
                "scenes": [
                    {{
                        "scene_number": 1,
                        "duration": 8,
                        "description": "Description visuelle de la scène",
                        "action": "Action principale visible",
                        "characters": ["personnage1", "personnage2"],
                        "setting": "Description du décor"
                    }}
                ],
                "total_scenes": 6,
                "estimated_duration": 48,
                "narrative_arc": "Résumé de l'arc narratif"
            }}
            """,
            agent=self.scenario_agent,
            expected_output="Structure JSON complète avec toutes les scènes décomposées"
        )

        # 2. Tâche Directeur Artistique  
        art_direction_task = Task(
            description=f"""
            Définis la direction artistique complète pour ce dessin animé :
            
            PRÉFÉRENCES UTILISATEUR : {style_preferences}
            
            INSTRUCTIONS :
            - Choisir un style visuel cohérent et attractif
            - Définir une palette de couleurs harmonieuse
            - Créer des descriptions détaillées pour chaque personnage
            - Assurer la cohérence visuelle entre toutes les scènes
            - Adapter le style à l'âge cible (3-8 ans)
            
            FORMAT DE SORTIE (JSON) :
            {{
                "visual_style": "Description du style général",
                "color_palette": ["couleur1", "couleur2", "couleur3"],
                "atmosphere": "Description de l'ambiance",
                "characters_design": {{
                    "character_name": {{
                        "description": "Description physique détaillée",
                        "style_keywords": ["mot-clé1", "mot-clé2"],
                        "seed": "seed_unique_12345"
                    }}
                }},
                "settings_design": {{
                    "setting_name": {{
                        "description": "Description du décor",
                        "style_keywords": ["mot-clé1", "mot-clé2"]
                    }}
                }},
                "technical_specs": {{
                    "aspect_ratio": "16:9",
                    "quality_level": "high",
                    "animation_style": "smooth"
                }}
            }}
            """,
            agent=self.art_director_agent,
            expected_output="Direction artistique complète en JSON"
        )

        # 3. Tâche Prompt Engineer
        prompt_engineering_task = Task(
            description="""
            Utilise les scènes du scénariste et le style du directeur artistique 
            pour créer des prompts optimaux pour la génération vidéo.
            
            INSTRUCTIONS :
            - Créer un prompt détaillé pour chaque scène
            - Intégrer le style visuel et les personnages cohérents
            - Optimiser pour Runway Gen-4 Turbo / Stable Diffusion Video
            - Assurer la continuité visuelle entre les scènes
            - Inclure tous les éléments techniques nécessaires
            
            FORMAT DE SORTIE (JSON) :
            {{
                "video_prompts": [
                    {{
                        "scene_number": 1,
                        "prompt_text": "Prompt détaillé optimisé pour l'IA",
                        "negative_prompt": "Éléments à éviter",
                        "duration": 8,
                        "seeds": {{"character_seed": "12345", "style_seed": "67890"}},
                        "technical_params": {{
                            "fps": 24,
                            "resolution": "1280x720",
                            "motion_strength": "medium"
                        }}
                    }}
                ],
                "global_style_prompt": "Style général à maintenir",
                "consistency_keywords": ["mot-clé1", "mot-clé2"]
            }}
            """,
            agent=self.prompt_engineer_agent,
            expected_output="Prompts optimisés pour toutes les scènes en JSON"
        )

        # 4. Tâche Opérateur Technique
        technical_task = Task(
            description="""
            Utilise les prompts créés pour générer toutes les vidéos via l'API.
            
            INSTRUCTIONS :
            - Générer chaque scène avec les prompts fournis
            - Surveiller la qualité et les erreurs
            - Optimiser les paramètres techniques
            - Assurer que toutes les vidéos sont générées correctement
            - Fournir les métadonnées de chaque génération
            
            FORMAT DE SORTIE (JSON) :
            {{
                "generated_videos": [
                    {{
                        "scene_number": 1,
                        "video_url": "URL ou chemin vers la vidéo",
                        "actual_duration": 8.2,
                        "generation_status": "success",
                        "quality_score": 8.5,
                        "technical_metadata": {{
                            "resolution": "1280x720",
                            "fps": 24,
                            "filesize_mb": 12.5
                        }}
                    }}
                ],
                "generation_summary": {{
                    "total_videos": 6,
                    "successful_generations": 6,
                    "total_duration": 48.5,
                    "average_quality": 8.3
                }}
            }}
            """,
            agent=self.technical_agent,
            expected_output="Rapport complet de génération avec toutes les vidéos"
        )

        # 5. Tâche Monteur Vidéo
        video_editing_task = Task(
            description="""
            Assemble toutes les vidéos générées en un dessin animé final fluide.
            
            INSTRUCTIONS :
            - Assembler les clips dans l'ordre narratif
            - Créer des transitions fluides entre les scènes
            - Optimiser le rythme et le timing
            - S'assurer de la cohérence visuelle globale
            - Exporter en format haute qualité
            
            FORMAT DE SORTIE (JSON) :
            {{
                "final_video": {{
                    "video_url": "URL vers la vidéo finale",
                    "total_duration": 48.5,
                    "resolution": "1280x720",
                    "fps": 24,
                    "filesize_mb": 85.2
                }},
                "editing_details": {{
                    "transitions_used": ["fade", "cut", "dissolve"],
                    "scenes_included": 6,
                    "quality_adjustments": "Correction couleur, stabilisation",
                    "export_format": "MP4"
                }},
                "final_quality_report": {{
                    "visual_consistency": 9.0,
                    "narrative_flow": 8.8,
                    "technical_quality": 9.2,
                    "overall_score": 9.0
                }}
            }}
            """,
            agent=self.video_editor_agent,
            expected_output="Vidéo finale assemblée avec rapport qualité"
        )

        return [
            scenario_task,
            art_direction_task, 
            prompt_engineering_task,
            technical_task,
            video_editing_task
        ]

    def generate_animated_story(self, story_text: str, style_preferences: Dict[str, str] = None) -> Dict[str, Any]:
        """Génère un dessin animé complet à partir d'une histoire"""
        
        if style_preferences is None:
            style_preferences = {
                "style": "cartoon",
                "mood": "joyful",
                "target_age": "3-8 years"
            }
        
        print(f"🎬 Démarrage génération dessin animé")
        print(f"📝 Histoire: {story_text[:100]}...")
        print(f"🎨 Style: {style_preferences}")
        
        # Créer les tâches
        tasks = self.create_animation_tasks(story_text, style_preferences)
        
        # Créer l'équipe CrewAI
        crew = Crew(
            agents=[
                self.scenario_agent,
                self.art_director_agent,
                self.prompt_engineer_agent,
                self.technical_agent,
                self.video_editor_agent
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Exécuter le processus
        try:
            print("🚀 Lancement du processus CrewAI...")
            result = crew.kickoff()
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "story_input": story_text,
                "style_preferences": style_preferences
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instance globale
animation_crew = AnimationCrewAI()
