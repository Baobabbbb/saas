"""
Service CrewAI COMPLET pour la génération de bandes dessinées
Version avec génération d'images réelles
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, FileWriterTool
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from .stable_diffusion_generator import stable_diffusion_generator

# Charger les variables d'environnement
load_dotenv()


class ComicSpecification(BaseModel):
    """Spécification pour la génération de BD"""
    style: str
    hero_name: str
    story_type: str
    custom_request: str
    num_images: int = 2


class TaskOutput(BaseModel):
    """Modèle générique pour les outputs de tâches"""
    result: str


class CrewAIComicCompleteV3:
    """Service CrewAI complet pour la génération de BD avec images réelles"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("⚠️ OpenAI API key not found")
            
        # Configurer le modèle LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",            api_key=self.api_key,
            temperature=0.7
        )

    def create_scenario_writer(self) -> Agent:
        """Crée l'agent scénariste"""
        return Agent(
            role='Scénariste BD Expert Franco-Belge',
            goal='Créer des scénarios de bande dessinée captivants dans le style franco-belge',
            backstory=(
                "Tu es un scénariste expert en bande dessinée franco-belge avec 20 ans d'expérience. "
                "Tu as travaillé sur des séries comme Tintin, Astérix, et Gaston Lagaffe. "
                "Tu excelles dans la création d'histoires avec des personnages attachants, "
                "des dialogues naturels et des intrigues bien construites."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_bubble_designer(self) -> Agent:
        """Crée l'agent concepteur de bulles"""
        return Agent(
            role='Concepteur de Bulles BD Franco-Belge',
            goal='Concevoir les spécifications exactes des bulles de dialogue pour BD',
            backstory=(
                "Tu es un expert en design de bulles de bande dessinée avec une spécialisation "
                "dans le style franco-belge. Tu maîtrises parfaitement l'art de placer les bulles "                "de dialogue, leurs formes, couleurs et typographies pour maximiser la lisibilité "
                "et l'impact émotionnel de l'histoire."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_image_director(self) -> Agent:
        """Crée l'agent directeur artistique"""
        return Agent(
            role='Directeur Artistique BD',
            goal='Créer des prompts détaillés pour générer des images de BD de qualité professionnelle',
            backstory=(
                "Tu es un directeur artistique spécialisé en bande dessinée avec une expertise "
                "dans la création de visuels saisissants. Tu maîtrises tous les styles artistiques "
                "et tu sais créer des prompts précis qui produisent des illustrations parfaites "                "pour chaque scène d'une bande dessinée."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_layout_composer(self) -> Agent:
        """Crée l'agent compositeur de mise en page"""
        return Agent(
            role='Compositeur BD Professionnel',
            goal='Assembler tous les éléments pour créer une bande dessinée complète et cohérente',
            backstory=(
                "Tu es un compositeur professionnel de bande dessinée avec 15 ans d'expérience "
                "dans l'assemblage final de BD. Tu excelles dans la coordination de tous les "
                "éléments : scénario, bulles, images et mise en page pour créer des œuvres "
                "finies de qualité professionnelle."            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_scenario_task(self, agent: Agent) -> Task:
        """Crée la tâche de création de scénario"""
        return Task(
            description=(
                "Crée un scénario de bande dessinée complet basé sur les spécifications suivantes :\n"
                "- Style : {style}\n"
                "- Héros principal : {hero_name}\n"
                "- Type d'histoire : {story_type}\n"
                "- Demande spécifique : {custom_request}\n"
                "- Nombre d'images : {num_images}\n\n"
                "Le scénario doit inclure :\n"
                "1. Un titre accrocheur\n"
                "2. Les personnages principaux avec leurs rôles\n"
                "3. L'intrigue principale\n"
                "4. La division en chapitres/scènes correspondant au nombre d'images\n"
                "5. Les dialogues pour chaque scène\n"
                "6. Les descriptions d'action et de décor\n\n"
                "Format de sortie : JSON structuré avec tous ces éléments."
            ),
            expected_output="JSON complet avec titre, personnages, intrigue, chapitres et dialogues",
            agent=agent,
            output_json=TaskOutput
        )

    def create_design_bubbles_task(self, agent: Agent, context_tasks: List[Task]) -> Task:
        """Crée la tâche de conception des bulles"""
        return Task(
            description=(
                "Conçoit les spécifications exactes des bulles de dialogue pour la BD.\n"
                "En te basant sur le scénario créé, définis :\n"
                "1. Le type de bulles (parole, pensée, cri, narration)\n"
                "2. La forme (ronde, rectangulaire, nuage)\n"
                "3. La couleur de bordure et de remplissage\n"
                "4. La taille et police du texte\n"
                "5. L'emplacement suggéré sur l'image\n"
                "6. Les appendices (queues) pour pointer vers les personnages\n\n"
                "Format de sortie : JSON avec spécifications détaillées pour chaque bulle."
            ),
            expected_output="JSON avec spécifications complètes des bulles (forme, couleur, position, texte)",
            agent=agent,
            context=context_tasks,
            output_json=TaskOutput
        )

    def create_image_prompts_task(self, agent: Agent, context_tasks: List[Task]) -> Task:
        """Crée la tâche de génération des prompts d'images"""
        return Task(
            description=(
                "Crée des prompts détaillés pour générer des images de BD de qualité professionnelle.\n"
                "En te basant sur le scénario et les spécifications de bulles, crée pour chaque scène :\n"
                "1. Description détaillée de la composition\n"
                "2. Apparence et position des personnages\n"
                "3. Décor et ambiance\n"
                "4. Style artistique spécifique\n"
                "5. Éclairage et couleurs\n"
                "6. Espace réservé pour les bulles de dialogue\n\n"
                "Format de sortie : JSON avec un prompt détaillé pour chaque image."
            ),
            expected_output="JSON avec prompts détaillés pour chaque image de la BD",
            agent=agent,
            context=context_tasks,
            output_json=TaskOutput
        )

    def create_final_composition_task(self, agent: Agent, context_tasks: List[Task]) -> Task:
        """Crée la tâche de composition finale"""
        return Task(
            description=(
                "Assemble tous les éléments pour créer la bande dessinée finale.\n"
                "Combine le scénario, les spécifications de bulles et les prompts d'images "
                "en une structure complète et cohérente.\n"
                "Vérifie que tous les éléments sont compatibles et bien intégrés.\n"
                "Optimise la mise en page pour une lecture fluide.\n\n"
                "Format de sortie : JSON final avec tous les éléments de la BD assemblés."
            ),
            expected_output="JSON final complet avec scénario, bulles, prompts et mise en page",
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
        Génère une bande dessinée complète avec CrewAI et images réelles
        """
        try:
            print("🚀 Démarrage génération BD complète avec CrewAI V3 (Images réelles)")
            
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
              # Parser le résultat CrewAI (qui peut avoir plusieurs niveaux d'encodage JSON)
            try:
                # Extraire le contenu du résultat CrewAI
                if hasattr(result, 'raw'):
                    raw_result = result.raw
                else:
                    raw_result = result
                
                print(f"🔍 Type de résultat CrewAI: {type(raw_result)}")
                print(f"🔍 Résultat brut CrewAI: {str(raw_result)[:200]}...")
                
                # Si c'est déjà un dict, on l'utilise directement
                if isinstance(raw_result, dict):
                    comic_data = raw_result
                # Sinon, on essaie de parser le JSON
                elif isinstance(raw_result, str):
                    # Premier parsing pour obtenir la structure avec "result"
                    parsed_result = json.loads(raw_result)
                    
                    # Extraire et parser le contenu du champ "result"
                    if isinstance(parsed_result, dict) and 'result' in parsed_result:
                        comic_data_str = parsed_result['result']
                        if isinstance(comic_data_str, str):
                            comic_data = json.loads(comic_data_str)
                        else:
                            comic_data = comic_data_str
                    else:
                        comic_data = parsed_result
                else:
                    # Dernier recours : convertir en string et parser
                    raw_str = str(raw_result)
                    comic_data = json.loads(raw_str)
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erreur de parsing JSON: {e}")
                print(f"📄 Contenu brut: {raw_result}")
                raise ValueError(f"Impossible de parser le résultat CrewAI: {e}")
            
            # Post-traitement : génération des images réelles et application des bulles
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
              # Utiliser le générateur d'images réelles avec Stable Diffusion
            pages = await stable_diffusion_generator.generate_comic_images(comic_data, spec)
            
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


# Instance globale
crewai_comic_complete_v3 = CrewAIComicCompleteV3()
