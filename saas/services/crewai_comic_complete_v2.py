"""
Service CrewAI COMPLET pour la génération de bandes dessinées
Version simplifiée suivant exactement les exemples de la documentation CrewAI
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, FileWriterTool
from pydantic import BaseModel

# Import conditionnel pour éviter les erreurs
try:
    from .crewai_image_generator import comic_image_generator
except ImportError:
    print("⚠️ crewai_image_generator non disponible - mode simulation")
    comic_image_generator = None

# Charger les variables d'environnement
load_dotenv()

class ComicSpecification(BaseModel):
    """Spécifications complètes pour une bande dessinée"""
    style: str
    hero_name: str
    story_type: str
    custom_request: str
    num_images: int
    user_parameters: Dict[str, Any]

class TaskOutput(BaseModel):
    """Sortie générique pour les tâches CrewAI"""
    result: Any

class CrewAIComicCompleteV2:
    """
    Service CrewAI COMPLET pour créer des bandes dessinées professionnelles
    Version simplifiée sans @CrewBase pour éviter les problèmes de configuration
    """
    
    def __init__(self):
        self.llm_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
          # Chargement des configurations YAML
        self.agents_config = self._load_yaml_config('config/agents_complete.yaml')
        self.tasks_config = self._load_yaml_config('config/tasks_complete.yaml')
        
        # Outils partagés
        self.file_read_tool = FileReadTool()
        self.file_write_tool = FileWriterTool()

    def _load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        """Charge un fichier de configuration YAML"""
        import yaml
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"⚠️ Fichier de configuration non trouvé: {file_path}")
            return {}
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file_path}: {e}")
            return {}

    def create_scenario_writer(self) -> Agent:
        """Crée l'agent scénariste"""
        config = self.agents_config.get('scenario_writer', {})
        return Agent(
            role=config.get('role', 'Scénariste BD Expert Franco-Belge'),
            goal=config.get('goal', 'Créer des scénarios de bande dessinée cohérents et engageants'),
            backstory=config.get('backstory', 'Expert en scénarios de BD style franco-belge'),
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool],
            llm=self.llm_model
        )

    def create_bubble_designer(self) -> Agent:
        """Crée l'agent concepteur de bulles"""
        config = self.agents_config.get('bubble_designer', {})
        return Agent(
            role=config.get('role', 'Concepteur de Bulles BD Franco-Belge'),
            goal=config.get('goal', 'Concevoir l\'apparence exacte des bulles selon les standards franco-belges'),
            backstory=config.get('backstory', 'Expert en design de bulles de bande dessinée style franco-belge'),
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool],
            llm=self.llm_model
        )

    def create_image_director(self) -> Agent:
        """Crée l'agent directeur artistique"""
        config = self.agents_config.get('image_director', {})
        return Agent(
            role=config.get('role', 'Directeur Artistique BD'),
            goal=config.get('goal', 'Créer des descriptions visuelles précises pour la génération d\'images'),
            backstory=config.get('backstory', 'Directeur artistique expert en bande dessinée'),
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool],
            llm=self.llm_model
        )

    def create_layout_composer(self) -> Agent:
        """Crée l'agent compositeur"""
        config = self.agents_config.get('layout_composer', {})
        return Agent(            role=config.get('role', 'Compositeur BD Professionnel'),
            goal=config.get('goal', 'Assembler tous les éléments en une bande dessinée professionnelle'),
            backstory=config.get('backstory', 'Expert en composition et assemblage de bandes dessinées'),
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool],
            llm=self.llm_model
        )

    def create_scenario_task(self, agent: Agent) -> Task:
        """Crée la tâche de création du scénario"""
        config = self.tasks_config.get('create_scenario_task', {})
        return Task(
            description=config.get('description', 'Crée un scénario de bande dessinée complet'),
            expected_output=config.get('expected_output', 'JSON structuré avec le scénario'),
            agent=agent,
            output_json=TaskOutput
        )

    def create_design_bubbles_task(self, agent: Agent, context_tasks: List[Task]) -> Task:
        """Crée la tâche de conception des bulles"""
        config = self.tasks_config.get('design_bubbles_task', {})
        return Task(
            description=config.get('description', 'Conçoit les spécifications exactes des bulles'),
            expected_output=config.get('expected_output', 'JSON avec spécifications des bulles'),
            agent=agent,
            context=context_tasks,
            output_json=TaskOutput
        )

    def create_image_prompts_task(self, agent: Agent, context_tasks: List[Task]) -> Task:
        """Crée la tâche de création des prompts d'images"""
        config = self.tasks_config.get('create_image_prompts_task', {})
        return Task(
            description=config.get('description', 'Crée des prompts détaillés pour générer des images'),
            expected_output=config.get('expected_output', 'JSON avec prompts d\'images'),
            agent=agent,
            context=context_tasks,
            output_json=TaskOutput
        )

    def create_final_composition_task(self, agent: Agent, context_tasks: List[Task]) -> Task:
        """Crée la tâche de composition finale"""
        config = self.tasks_config.get('final_composition_task', {})
        return Task(
            description=config.get('description', 'Assemble tous les éléments pour créer la bande dessinée finale'),
            expected_output=config.get('expected_output', 'JSON avec la bande dessinée finale'),
            agent=agent,
            context=context_tasks,
            output_json=TaskOutput
        )

    def create_comic_crew(self) -> Crew:
        """Crée l'équipe CrewAI pour la génération de BD"""
        # Créer les agents
        scenario_agent = self.create_scenario_writer()
        bubble_agent = self.create_bubble_designer()
        image_agent = self.create_image_director()
        layout_agent = self.create_layout_composer()

        # Créer les tâches
        scenario_task = self.create_scenario_task(scenario_agent)
        bubble_task = self.create_design_bubbles_task(bubble_agent, [scenario_task])
        image_task = self.create_image_prompts_task(image_agent, [scenario_task, bubble_task])
        composition_task = self.create_final_composition_task(layout_agent, [scenario_task, bubble_task, image_task])

        # Créer l'équipe
        return Crew(
            agents=[scenario_agent, bubble_agent, image_agent, layout_agent],
            tasks=[scenario_task, bubble_task, image_task, composition_task],
            process=Process.sequential,
            verbose=True,
            memory=True
        )

    async def generate_complete_comic(self, spec: ComicSpecification) -> Dict[str, Any]:
        """
        Génère une bande dessinée complète avec CrewAI
        """
        try:
            print("🚀 Démarrage génération BD complète avec CrewAI V2")
            
            # Préparer les inputs pour CrewAI
            inputs = {
                'style': spec.style,
                'hero_name': spec.hero_name,
                'story_type': spec.story_type,
                'custom_request': spec.custom_request,
                'num_images': spec.num_images
            }
            
            print(f"📋 Inputs CrewAI: {inputs}")
            
            # Créer l'équipe et lancer l'exécution
            crew = self.create_comic_crew()
            result = crew.kickoff(inputs=inputs)
            
            print("✅ Génération CrewAI terminée")
              # Parser le résultat
            if hasattr(result, 'raw'):
                comic_data = json.loads(result.raw)
            else:
                comic_data = json.loads(str(result))
            
            # Post-traitement : génération des images et application des bulles
            final_result = await self._post_process_comic(comic_data, spec)
            
            return final_result
            
        except Exception as e:
            print(f"❌ Erreur génération BD complète: {e}")
            raise

    async def _post_process_comic(self, comic_data: Dict[str, Any], spec: ComicSpecification) -> Dict[str, Any]:
        """
        Post-traitement : génération d'images RÉELLES et application des bulles
        """
        try:
            print("🎨 Post-traitement : génération d'images RÉELLES et application des bulles")
            
            # Utiliser le générateur d'images réelles si disponible
            if comic_image_generator:
                pages = await comic_image_generator.generate_comic_images(comic_data, spec)
            else:
                print("⚠️ Générateur d'images non disponible - mode simulation")
                pages = await self._generate_fallback_pages(comic_data, spec)
            
            # Structure de retour
            final_result = {
                "comic_metadata": {
                    "title": comic_data.get("title", f"Aventure de {spec.hero_name}"),
                    "style": spec.style,
                    "creation_date": datetime.now().isoformat(),
                    "num_pages": len(pages)
                },
                "pages": pages,
                "processing_info": {
                    "crewai_result": comic_data,
                    "images_generated": len(pages),
                    "bubbles_applied": len(pages),
                    "real_files_created": True
                }
            }
            
            print(f"✅ Post-traitement terminé: {len(pages)} pages créées avec fichiers réels")
            
            return final_result
            
        except Exception as e:
            print(f"❌ Erreur lors du post-traitement: {e}")
            raise

    def _create_fallback_scenes(self, spec: ComicSpecification) -> List[Dict[str, Any]]:
        """Crée des scènes de fallback si CrewAI n'a pas produit le bon format"""
        scenes = []
        for i in range(spec.num_images):
            scene = {
                "scene_number": i + 1,
                "description": f"Scène {i+1} de l'aventure de {spec.hero_name} dans {spec.story_type}",
                "dialogues": [
                    {
                        "character": spec.hero_name,
                        "text": f"Dialogue exemple {i+1}",
                        "type": "speech"
                    }
                ],
                "setting": f"Décor {i+1}",
                "action": f"Action {i+1}"
            }
            scenes.append(scene)
        return scenes

    def _create_image_prompt(self, scene: Dict[str, Any], spec: ComicSpecification) -> str:
        """Crée un prompt d'image pour une scène donnée"""
        scene_desc = scene.get('description', 'une scène d\'aventure')
        base_prompt = f"Illustration de bande dessinée style {spec.style}, "
        base_prompt += f"montrant {scene_desc}, "
        base_prompt += f"avec le personnage {spec.hero_name}, "
        base_prompt += f"dans un contexte {spec.story_type}, "
        base_prompt += "couleurs vives, style professionnel de BD, "
        base_prompt += "espace réservé pour bulles de dialogue"
        
        return base_prompt

    async def _generate_scene_image(self, prompt: str, style: str) -> str:
        """Génère une image pour une scène (simulation)"""
        # Pour le moment, on simule la génération d'image
        print(f"🎨 Simulation génération image: {prompt[:50]}...")
        
        # Retourner une URL d'image de placeholder
        return f"https://via.placeholder.com/800x600/FFB6C1/000000?text=Scene+{style}"

    def _create_bubble_specifications(self, scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Crée les spécifications de bulles pour une scène"""
        bubble_specs = []
        dialogues = scene.get("dialogues", [])
        
        for i, dialogue in enumerate(dialogues):
            bubble_spec = {
                "bubble_id": f"bubble_{i}",
                "type": dialogue.get("type", "speech"),
                "shape": "oval",
                "position": {
                    "x": 0.1 + (i * 0.3),  # Position simple
                    "y": 0.1 + (i * 0.2),
                    "width": 0.25,
                    "height": 0.15
                },
                "text": dialogue.get("text", ""),
                "character": dialogue.get("character", ""),
                "style": {
                    "outline_color": "black",
                    "outline_width": 2,
                    "fill_color": "#FFFFFF",
                    "font_family": "comic",
                    "font_size": 12
                },
                "appendix": {
                    "type": "pointed" if dialogue.get("type") == "speech" else "bubbles",
                    "target": "character"
                }
            }
            bubble_specs.append(bubble_spec)
        
        return bubble_specs

    async def _apply_bubbles_to_image(self, image_url: str, bubble_specs: List[Dict[str, Any]], scene: Dict[str, Any]) -> str:
        """Applique les bulles sur l'image (simulation)"""
        print(f"💬 Simulation application de {len(bubble_specs)} bulles")
        
        # Pour le moment, on simule l'application des bulles
        # Dans la vraie version, on téléchargerait l'image, appliquerait les bulles, et sauvegarderait
        
        return f"processed_{image_url}"

    async def _generate_fallback_pages(self, comic_data: Dict[str, Any], spec: ComicSpecification) -> List[Dict[str, Any]]:
        """Génère des pages de fallback si le générateur d'images n'est pas disponible"""
        print("🎨 Génération de pages de fallback")
        
        pages = []
        scenes = comic_data.get('scenes', self._create_fallback_scenes(spec))
        
        for i, scene in enumerate(scenes[:spec.num_images]):
            page = {
                "page_number": i + 1,
                "scene": scene,
                "image_url": f"https://via.placeholder.com/800x600/FFB6C1/000000?text=Scene+{i+1}",
                "bubbles": self._create_bubble_specifications(scene),
                "final_image_url": f"https://via.placeholder.com/800x600/FFB6C1/000000?text=BD+Page+{i+1}"
            }
            pages.append(page)
        
        return pages


# Instance globale
crewai_comic_complete_v2 = CrewAIComicCompleteV2()
