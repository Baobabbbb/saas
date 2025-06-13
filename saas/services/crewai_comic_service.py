"""
Service CrewAI pour l'amélioration des bandes dessinées
Basé sur la documentation CrewAI officielle pour créer des agents spécialisés
"""

import os
import json
import asyncio
from typing import Dict, List, Any
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, FileWriterTool
from datetime import datetime

class CrewAIComicService:
    """
    Service utilisant CrewAI pour améliorer la qualité des bandes dessinées
    avec des agents spécialisés selon les meilleures pratiques CrewAI
    """
    
    def __init__(self):
        self.llm_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        
        # Outils partagés
        self.file_read_tool = FileReadTool()
        self.file_write_tool = FileWriterTool()
        
        # Agents spécialisés
        self._setup_agents()
    
    def _setup_agents(self):
        """Configuration des agents spécialisés selon la documentation CrewAI"""
        
        # Agent Scénariste - Expert en narration BD
        self.storyteller_agent = Agent(
            role="Scénariste BD Expert",
            goal="Créer des histoires de bande dessinée cohérentes, engageantes et adaptées au public cible",
            backstory="""Tu es un scénariste de bande dessinée reconnu avec 15 ans d'expérience. 
            Tu maîtrises parfaitement la structure narrative, le rythme et la progression dramatique.
            Tu sais créer des histoires captivantes avec des personnages attachants et des situations intéressantes.
            Tu adaptes ton style selon le public visé (enfants, adolescents, adultes).""",
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool]
        )
        
        # Agent Dialoguiste - Expert en dialogues réalistes
        self.dialogue_agent = Agent(
            role="Dialoguiste Professionnel",
            goal="Créer des dialogues naturels, expressifs et adaptés à chaque personnage avec un placement optimal dans les bulles",
            backstory="""Tu es un dialoguiste expert spécialisé dans l'écriture de dialogues pour la bande dessinée.
            Tu sais créer des répliques naturelles qui sonnent juste, avec la bonne longueur pour les bulles.
            Tu maîtrises les nuances de langage selon l'âge et la personnalité des personnages.
            Tu évites les dialogues trop longs qui ne rentrent pas dans une bulle et privilégies l'impact.""",
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool]
        )
        
        # Agent Layout BD - Expert en mise en page et bulles
        self.layout_agent = Agent(
            role="Expert Layout BD",
            goal="Optimiser le placement des bulles de dialogue et la composition visuelle pour une lecture fluide",
            backstory="""Tu es un expert en mise en page de bande dessinée avec une spécialisation dans le placement des bulles.
            Tu connais parfaitement les règles de lecture occidentale (gauche vers droite, haut vers bas).
            Tu sais positionner les bulles pour qu'elles ne cachent pas les éléments importants de l'image.
            Tu maîtrises les différents types de bulles (parole, pensée, cri) et leur forme optimale.""",
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool]
        )
        
        # Agent Réviseur - Quality Assurance
        self.reviewer_agent = Agent(
            role="Réviseur BD Senior",
            goal="Vérifier la cohérence narrative, la qualité des dialogues et l'efficacité du layout final",
            backstory="""Tu es un réviseur senior avec une expertise dans l'industrie de la bande dessinée.
            Tu as un œil critique pour détecter les incohérences, les dialogues artificiels ou les problèmes de layout.
            Tu t'assures que le produit final respecte les standards professionnels de la BD.
            Tu proposes des améliorations concrètes et réalisables.""",
            verbose=True,
            memory=True,
            tools=[self.file_read_tool, self.file_write_tool]
        )
    
    async def improve_comic_scenario(self, original_scenario: Dict, user_prompt: str, style: str = None) -> Dict:
        """
        Améliore un scénario de BD existant en utilisant l'équipe d'agents CrewAI
        
        Args:
            original_scenario: Scénario original généré
            user_prompt: Prompt utilisateur original
            style: Style de BD demandé
            
        Returns:
            Dict: Scénario amélioré avec de meilleurs dialogues et layout
        """
        
        try:
            # Préparation du contexte partagé
            context = {
                "original_scenario": original_scenario,
                "user_prompt": user_prompt,
                "style": style,
                "improvement_timestamp": datetime.now().isoformat()
            }
            
            # Tâche 1: Amélioration de la narration
            storytelling_task = Task(
                description=f"""
                Analyse et améliore la structure narrative du scénario original.
                
                Contexte:
                - Prompt utilisateur: "{user_prompt}"
                - Style demandé: "{style}"
                - Scénario original: {json.dumps(original_scenario, indent=2)}
                
                Améliore:
                1. La cohérence narrative entre les scènes
                2. La progression dramatique et le rythme
                3. La caractérisation des personnages
                4. L'adaptation au public cible
                
                Garde le même nombre de scènes mais améliore leur description et leur enchaînement.
                """,
                expected_output="""
                Un scénario amélioré au format JSON avec:
                - title: titre amélioré
                - scenes: liste des scènes avec descriptions enrichies
                - narrative_improvements: liste des améliorations apportées
                """,
                agent=self.storyteller_agent
            )
            
            # Tâche 2: Optimisation des dialogues
            dialogue_task = Task(
                description="""
                Optimise tous les dialogues du scénario amélioré.
                
                Pour chaque dialogue:
                1. Assure-toi qu'il soit naturel et authentique
                2. Adapte le langage au personnage et au contexte
                3. Respecte la contrainte de longueur pour les bulles BD (max 40 caractères par ligne, max 3 lignes)
                4. Évite les répétitions et les formulations artificielles
                5. Ajoute des variations dans le style de parole selon les personnages
                
                Crée des dialogues qui sonnent vrais et qui s'intègrent parfaitement dans des bulles de BD.
                """,
                expected_output="""
                Le scénario avec dialogues optimisés au format JSON:
                - Chaque dialogue respecte les contraintes de bulle BD
                - Dialogues naturels et expressifs
                - Variations selon les personnages
                - dialogue_improvements: explications des améliorations
                """,
                agent=self.dialogue_agent,
                context=[storytelling_task]
            )
            
            # Tâche 3: Optimisation du layout
            layout_task = Task(
                description="""
                Optimise le placement et la forme des bulles de dialogue.
                
                Pour chaque scène:
                1. Détermine la position optimale de chaque bulle selon la description de scène
                2. Évite que les bulles cachent des éléments importants
                3. Respecte l'ordre de lecture (gauche→droite, haut→bas)
                4. Choisis le type de bulle approprié (normale, pensée, cri, chuchotement)
                5. Calcule les dimensions optimales selon le texte
                
                Ajoute des métadonnées de placement pour chaque bulle.
                """,
                expected_output="""
                Le scénario final avec métadonnées de layout au format JSON:
                - Positions optimales des bulles (x, y, width, height)
                - Types de bulles (speech, thought, shout, whisper)
                - Ordre de lecture pour chaque scène
                - layout_metadata: informations techniques pour le rendu
                """,
                agent=self.layout_agent,
                context=[storytelling_task, dialogue_task]
            )
            
            # Tâche 4: Révision finale
            review_task = Task(
                description="""
                Effectue une révision complète du scénario amélioré.
                
                Vérifie:
                1. Cohérence narrative globale
                2. Qualité et naturel des dialogues
                3. Efficacité du layout proposé
                4. Respect du brief original
                5. Qualité professionnelle générale
                
                Propose des corrections finales si nécessaire.
                """,
                expected_output="""
                Le scénario final validé avec:
                - Toutes les améliorations intégrées
                - Une note de qualité globale
                - review_notes: commentaires sur les améliorations apportées
                - final_recommendations: suggestions pour le rendu visuel
                """,
                agent=self.reviewer_agent,
                context=[storytelling_task, dialogue_task, layout_task]
            )
            
            # Création et exécution de l'équipe CrewAI
            comic_crew = Crew(
                agents=[
                    self.storyteller_agent,
                    self.dialogue_agent, 
                    self.layout_agent,
                    self.reviewer_agent
                ],
                tasks=[
                    storytelling_task,
                    dialogue_task,
                    layout_task,
                    review_task
                ],
                process=Process.sequential,
                verbose=True,
                memory=True,
                embedder={
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small"
                    }
                }
            )
            
            print("🚀 Lancement de l'équipe CrewAI pour améliorer la BD...")
            
            # Exécution de l'équipe
            result = comic_crew.kickoff(inputs=context)
            
            print("✅ Amélioration CrewAI terminée")
            
            # Parse du résultat final
            try:
                if hasattr(result, 'raw'):
                    improved_scenario = json.loads(result.raw)
                else:
                    improved_scenario = json.loads(str(result))
                    
                # Ajout des métadonnées CrewAI
                improved_scenario["crewai_enhanced"] = True
                improved_scenario["enhancement_timestamp"] = datetime.now().isoformat()
                improved_scenario["original_scenario"] = original_scenario
                
                return improved_scenario
                
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing résultat CrewAI: {e}")
                # Fallback sur le scénario original en cas d'erreur
                return original_scenario
                
        except Exception as e:
            print(f"❌ Erreur dans improve_comic_scenario: {e}")
            # En cas d'erreur, retourner le scénario original
            return original_scenario

    def validate_improved_scenario(self, scenario: Dict) -> Dict:
        """
        Valide et nettoie un scénario amélioré par CrewAI
        
        Args:
            scenario: Scénario à valider
            
        Returns:
            Dict: Scénario validé et nettoyé
        """
        errors = []
        
        # Vérifications de base
        if not scenario.get('title'):
            errors.append("Titre manquant")
            
        if not scenario.get('scenes') or not isinstance(scenario['scenes'], list):
            errors.append("Scènes manquantes ou invalides")
        
        # Validation des scènes
        for i, scene in enumerate(scenario.get('scenes', [])):
            if not scene.get('description'):
                errors.append(f"Description manquante pour la scène {i+1}")
                
            # Validation des dialogues
            for j, dialogue in enumerate(scene.get('dialogues', [])):
                if not dialogue.get('character'):
                    errors.append(f"Personnage manquant pour le dialogue {j+1} de la scène {i+1}")
                    
                if not dialogue.get('text'):
                    errors.append(f"Texte manquant pour le dialogue {j+1} de la scène {i+1}")
                
                # Vérification longueur bulle BD
                text_length = len(dialogue.get('text', ''))
                if text_length > 120:  # ~3 lignes de 40 caractères
                    errors.append(f"Dialogue trop long dans la scène {i+1} ({text_length} caractères)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'scenario': scenario
        }

# Instance globale du service
crewai_comic_service = CrewAIComicService()
