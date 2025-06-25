"""
Version simplifiée du service d'animation intégré pour les tests
Sans dépendance moviepy pour éviter les conflits
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

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Imports CrewAI
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

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

class SimpleAnimationService:
    """Service d'animation simplifié pour les tests"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.runway_api_key = os.getenv("RUNWAY_API_KEY")
        self.cache_dir = Path("cache/animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration CrewAI
        if self.openai_api_key:
            self.llm = ChatOpenAI(
                api_key=SecretStr(self.openai_api_key),
                model="gpt-4o-mini",
                temperature=0.7
            )
        else:
            print("⚠️ Clé OpenAI non configurée - mode test limité")
            self.llm = None
        
        # Paramètres compatibles avec Stable Diffusion/Runway
        self.available_styles = {
            'cartoon': 'vibrant cartoon animation style, colorful and playful, Disney-Pixar inspired',
            'anime': 'anime animation style, expressive characters, Japanese animation inspired',
            'realistic': 'semi-realistic animation style, detailed but child-friendly',
            'watercolor': 'watercolor animation style, soft painted textures, artistic brush strokes',
            'pixel_art': 'pixel art animation style, retro gaming aesthetic, colorful pixels'
        }
        
        self.available_themes = {
            'adventure': 'exciting adventure scene with exploration and discovery',
            'magic': 'magical scene with sparkles, spell effects, and wonder',
            'animals': 'cute animals in their natural habitat, friendly and endearing',
            'space': 'space adventure with stars, planets, and cosmic elements',
            'underwater': 'underwater scene with marine life and coral reefs',
            'forest': 'enchanted forest with magical creatures and nature',
            'city': 'colorful city environment, friendly urban setting',
            'countryside': 'peaceful countryside landscape, rolling hills, nature'
        }
        
        self.available_moods = {
            'joyful': 'joyful and energetic atmosphere',
            'peaceful': 'calm and serene atmosphere',
            'magical': 'mysterious and magical atmosphere',
            'playful': 'fun and mischievous atmosphere',
            'adventurous': 'exploration and discovery atmosphere'
        }
        
        print("🎬 Service Animation Simple initialisé")
        print(f"📁 Cache: {self.cache_dir}")
        print(f"🔑 OpenAI configuré: {'✅' if self.openai_api_key else '❌'}")
    
    def create_agents(self) -> Dict[str, Agent]:
        """Créer les agents CrewAI spécialisés"""
        
        agents = {}
        
        # 1. Scénariste
        agents['screenwriter'] = Agent(
            role="Scénariste Expert",
            goal="Découper une histoire en scènes visuelles parfaites pour l'animation",
            backstory="""Tu es un scénariste expérimenté spécialisé dans les contenus pour enfants. 
            Tu excelles à découper une histoire en 3-6 scènes visuelles captivantes de 5-10 secondes chacune.
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
            - Créer 3 à 5 scènes de 5-10 secondes chacune (max 50s total)
            - Chaque scène doit être visuellement claire et captivante
            - Assurer une progression narrative fluide
            - Adapter pour enfants de 3-8 ans
            
            RÉPONSE REQUISE (FORMAT JSON) :
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
            Définis le style visuel pour cette animation basée sur les scènes du scénariste :
            
            PRÉFÉRENCES UTILISATEUR : {style_preferences}
            STYLE DEMANDÉ: {style_preferences.get('style', 'cartoon')}
            THÈME: {style_preferences.get('theme', 'adventure')}
            AMBIANCE: {style_preferences.get('mood', 'joyful')}
            
            STYLES DISPONIBLES: {list(self.available_styles.keys())}
            THÈMES DISPONIBLES: {list(self.available_themes.keys())}
            
            INSTRUCTIONS :
            - Utiliser le style visuel demandé par l'utilisateur
            - Adapter le style au thème et à l'ambiance choisis
            - Assurer la cohérence visuelle entre toutes les scènes
            - Style adapté aux enfants de 3-8 ans
            
            RÉPONSE REQUISE (FORMAT JSON) :
            {{
                "visual_style": "Description du style basé sur {style_preferences.get('style', 'cartoon')}",
                "color_palette": ["couleur1", "couleur2", "couleur3"],
                "characters_style": "Description style des personnages pour {style_preferences.get('style', 'cartoon')}",
                "settings_style": "Description style des décors pour {style_preferences.get('theme', 'adventure')}",
                "mood_adaptation": "Adaptation pour ambiance {style_preferences.get('mood', 'joyful')}",
                "global_keywords": ["keywords", "basés", "sur", "choix", "utilisateur"]
            }}
            """,
            agent=agents['art_director'],
            expected_output="Direction artistique personnalisée en JSON",
            context=[scenario_task]
        )
        
        # 3. Tâche Prompt Engineering
        prompt_task = Task(
            description=f"""
            Crée des prompts optimisés pour Runway/Stable Diffusion basés sur les scènes et le style définis.
            
            STYLE UTILISATEUR: {style_preferences.get('style', 'cartoon')}
            THÈME UTILISATEUR: {style_preferences.get('theme', 'adventure')}
            AMBIANCE: {style_preferences.get('mood', 'joyful')}
            
            RÉFÉRENCES STYLE: {self.available_styles.get(style_preferences.get('style', 'cartoon'), 'cartoon style')}
            RÉFÉRENCES THÈME: {self.available_themes.get(style_preferences.get('theme', 'adventure'), 'adventure scene')}
            
            CONTRAINTES TECHNIQUES :
            - Prompt de 50-200 caractères maximum
            - Éviter les mots interdits (violence, armes, etc.)
            - Style adapté à l'animation pour enfants
            - Intégrer EXACTEMENT le style et thème choisis par l'utilisateur
            - Utiliser les références de style et thème ci-dessus
            
            RÉPONSE REQUISE (FORMAT JSON) :
            {{
                "video_prompts": [
                    {{
                        "scene_number": 1,
                        "prompt": "Prompt incorporant {style_preferences.get('style', 'cartoon')} et {style_preferences.get('theme', 'adventure')} (max 200 char)",
                        "duration": 8,
                        "style_keywords": "{style_preferences.get('style', 'cartoon')}, {style_preferences.get('theme', 'adventure')}, {style_preferences.get('mood', 'joyful')}"
                    }}
                ],
                "global_style": "Style {style_preferences.get('style', 'cartoon')} avec thème {style_preferences.get('theme', 'adventure')}",
                "user_preferences_applied": {{
                    "style": "{style_preferences.get('style', 'cartoon')}",
                    "theme": "{style_preferences.get('theme', 'adventure')}",
                    "mood": "{style_preferences.get('mood', 'joyful')}"
                }}
            }}
            """,
            agent=agents['prompt_engineer'],
            expected_output="Prompts optimisés avec préférences utilisateur",
            context=[scenario_task, art_task]
        )
        
        tasks.extend([scenario_task, art_task, prompt_task])
        
        return tasks
    
    async def test_crew_execution(self, story_text: str, style_preferences: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Test de l'exécution CrewAI sans génération vidéo"""
        
        start_time = time.time()
        
        if style_preferences is None:
            style_preferences = {
                "style": "cartoon coloré",
                "mood": "joyeux",
                "target_age": "3-8 ans"
            }
        
        print(f"🎬 === TEST CRÉAWAI SIMPLIFIÉ ===")
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
            
            # 5. Analyser les résultats
            execution_time = time.time() - start_time
            
            print(f"\n✅ === RÉSULTATS CRÉAWAI ===")
            print(f"⏱️  Temps d'exécution: {execution_time:.1f}s")
            print(f"📊 Tâches exécutées: {len(crew_result.tasks_output) if crew_result.tasks_output else 0}")
            
            # Extraire les résultats de chaque tâche
            results = {}
            if crew_result.tasks_output:
                for i, task_output in enumerate(crew_result.tasks_output):
                    task_name = ["scénariste", "directeur artistique", "prompt engineer"][i] if i < 3 else f"tâche_{i}"
                    results[task_name] = {
                        "output": task_output.raw[:200] + "..." if len(task_output.raw) > 200 else task_output.raw,
                        "agent": task_output.agent if hasattr(task_output, 'agent') else "inconnu"
                    }
                    print(f"📋 {task_name}: {task_output.raw[:100]}...")
            
            return {
                "status": "success",
                "execution_time": execution_time,
                "agents_count": len(agents),
                "tasks_count": len(tasks),
                "results": results,
                "story_input": story_text,
                "style_preferences": style_preferences,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erreur test CrewAI: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }

# Instance globale
simple_animation_service = SimpleAnimationService()
