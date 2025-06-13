"""
Service CrewAI amélioré pour l'amélioration UNIQUEMENT textuelle des bandes dessinées
Ce service n'interfère PAS avec la génération d'images ou la composition
Il améliore seulement les dialogues et la narration
"""

import os
import json
import asyncio
from typing import Dict, List, Any
from crewai import Agent, Task, Crew, Process
from datetime import datetime

class CrewAIComicEnhancer:
    """
    Service CrewAI focalisé uniquement sur l'amélioration textuelle
    - Améliore les dialogues pour qu'ils soient plus naturels
    - Optimise les descriptions visuelles
    - Respecte complètement le flux technique existant (images, seeds, composition)
    """
    
    def __init__(self):
        self.llm_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        self._setup_agents()
    
    def _setup_agents(self):
        """Configuration des agents spécialisés pour l'amélioration textuelle uniquement"""
        
        # Agent Dialoguiste - Expert en dialogues naturels
        self.dialogue_agent = Agent(
            role="Dialoguiste Expert",
            goal="Améliorer les dialogues pour qu'ils soient plus naturels, expressifs et adaptés aux bulles de BD",
            backstory="""Tu es un dialoguiste professionnel spécialisé dans la bande dessinée.
            Tu maîtrises l'art de créer des dialogues qui sonnent naturels et authentiques.
            Tu sais adapter le langage selon les personnages et le contexte.
            Tu respectes les contraintes techniques des bulles de BD (longueur, lisibilité).""",
            verbose=True,
            memory=True,
            llm=self.llm_model
        )
        
        # Agent Descripteur - Expert en descriptions visuelles
        self.description_agent = Agent(
            role="Expert en Descriptions Visuelles",
            goal="Améliorer les descriptions des scènes pour qu'elles soient plus précises et visuellement riches",
            backstory="""Tu es un expert en direction artistique pour la bande dessinée.
            Tu sais créer des descriptions visuelles précises qui guident parfaitement la génération d'images.
            Tu maîtrises les codes visuels de la BD : cadrages, compositions, expressions, ambiances.
            Tu adaptes tes descriptions selon le style demandé (cartoon, réaliste, manga, etc.).""",
            verbose=True,
            memory=True,
            llm=self.llm_model
        )
    
    async def enhance_scenario_text_only(
        self, 
        base_scenario: Dict[str, Any], 
        user_prompt: str, 
        style: str
    ) -> Dict[str, Any]:
        """
        Améliore UNIQUEMENT le contenu textuel du scénario (dialogues + descriptions)
        Conserve TOUS les autres éléments techniques : seed, style, structure, etc.
        """
        try:
            print("🎯 Amélioration textuelle CrewAI - Préservation du flux technique")
            
            # Contexte pour les agents
            context = {
                "base_scenario": base_scenario,
                "user_prompt": user_prompt,
                "style": style,
                "technical_elements_to_preserve": {
                    "seed": base_scenario.get("seed"),
                    "title": base_scenario.get("title"),
                    "style": base_scenario.get("style"),
                    "number_of_scenes": len(base_scenario.get("scenes", []))
                }
            }
            
            # Tâche 1: Amélioration des dialogues
            dialogue_task = Task(
                description=f"""
                Améliore UNIQUEMENT les dialogues du scénario pour qu'ils soient plus naturels et expressifs.
                
                CONTRAINTES STRICTES:
                - Garde exactement le même nombre de scènes: {len(base_scenario.get("scenes", []))}
                - Ne modifie PAS les descriptions de scènes (elles seront traitées séparément)
                - Respecte les contraintes de bulles BD: max 50 caractères par ligne, max 3 lignes
                - Garde la même structure narrative et les mêmes personnages
                
                Scénario original: {json.dumps(base_scenario, indent=2, ensure_ascii=False)}
                
                Style demandé: {style}
                Prompt utilisateur: {user_prompt}
                
                Pour chaque dialogue:
                1. Rends-le plus naturel et authentique
                2. Adapte le langage au personnage
                3. Assure-toi qu'il soit adapté aux enfants
                4. Évite les répétitions
                5. Ajoute des nuances émotionnelles
                """,
                expected_output="""
                Un JSON avec UNIQUEMENT les dialogues améliorés:
                {{
                    "scenes": [
                        {{
                            "scene_index": 0,
                            "improved_dialogues": [
                                {{"character": "nom", "text": "dialogue amélioré", "tone": "normal/excited/whisper"}}
                            ]
                        }}
                    ],
                    "dialogue_improvements": ["liste des améliorations apportées"]
                }}
                """,
                agent=self.dialogue_agent
            )
            
            # Tâche 2: Amélioration des descriptions
            description_task = Task(
                description=f"""
                Améliore UNIQUEMENT les descriptions visuelles des scènes pour la génération d'images.
                
                CONTRAINTES STRICTES:
                - Garde exactement le même nombre de scènes: {len(base_scenario.get("scenes", []))}
                - Ne modifie PAS les dialogues (ils sont traités séparément)
                - Les descriptions doivent être optimisées pour Stable Diffusion
                - Intègre le style demandé: {style}
                - Assure-toi de la cohérence visuelle entre les scènes
                
                Scénario original: {json.dumps(base_scenario, indent=2, ensure_ascii=False)}
                
                Pour chaque description:
                1. Rends-la plus précise et visuellement riche
                2. Ajoute des détails sur l'expression des personnages
                3. Précise le cadrage et la composition
                4. Intègre le style artistique demandé
                5. Garde la cohérence du héros principal
                """,
                expected_output="""
                Un JSON avec UNIQUEMENT les descriptions améliorées:
                {{
                    "scenes": [
                        {{
                            "scene_index": 0,
                            "improved_description": "description visuelle améliorée"
                        }}
                    ],
                    "visual_improvements": ["liste des améliorations visuelles"]
                }}
                """,
                agent=self.description_agent
            )
            
            # Création et exécution de l'équipe CrewAI selon la documentation
            enhancement_crew = Crew(
                agents=[self.dialogue_agent, self.description_agent],
                tasks=[dialogue_task, description_task],
                process=Process.sequential,  # Utilise sequential comme recommandé
                verbose=True,
                memory=True
            )
            
            print("🚀 Lancement de l'amélioration textuelle CrewAI...")
            
            # Exécution selon la documentation CrewAI
            result = enhancement_crew.kickoff(inputs=context)
            
            print("✅ Amélioration textuelle terminée")
            
            # Reconstitution du scénario avec améliorations
            enhanced_scenario = self._merge_improvements(
                base_scenario, 
                result, 
                user_prompt, 
                style
            )
            
            return enhanced_scenario
            
        except Exception as e:
            print(f"❌ Erreur lors de l'amélioration CrewAI: {e}")
            import traceback
            traceback.print_exc()
            # Retourne le scénario original en cas d'erreur
            base_scenario["crewai_enhanced"] = False
            base_scenario["enhancement_error"] = str(e)
            return base_scenario
    
    def _merge_improvements(
        self, 
        base_scenario: Dict[str, Any], 
        crewai_result: Any,
        user_prompt: str,
        style: str
    ) -> Dict[str, Any]:
        """
        Fusionne les améliorations CrewAI avec le scénario de base
        en préservant tous les éléments techniques
        """
        try:
            print("🔄 Fusion des améliorations avec le scénario de base...")
            
            # Copie complète du scénario de base (préservation technique)
            enhanced_scenario = base_scenario.copy()
            
            # Extraction du résultat CrewAI selon la documentation
            result_text = crewai_result.raw if hasattr(crewai_result, 'raw') else str(crewai_result)
            
            print(f"📄 Résultat CrewAI brut: {result_text[:200]}...")
            
            # Tentative d'extraction des améliorations du texte
            # Selon la doc, les résultats peuvent être dans différents formats
            dialogue_improvements = None
            description_improvements = None
            
            try:
                # Si c'est du JSON valide
                if result_text.strip().startswith('{'):
                    result_json = json.loads(result_text)
                    if "improved_dialogues" in result_text:
                        dialogue_improvements = result_json
                    elif "improved_description" in result_text:
                        description_improvements = result_json
                else:
                    # Parsing plus intelligent pour extraire les améliorations du texte
                    print("⚠️ Résultat non JSON, analyse textuelle...")
                    enhanced_scenario["crewai_text_result"] = result_text
            except json.JSONDecodeError:
                print("⚠️ Impossible de parser le résultat CrewAI comme JSON")
                enhanced_scenario["crewai_raw_result"] = result_text
            
            # Application basique des améliorations si disponibles
            if dialogue_improvements and enhanced_scenario.get("scenes"):
                for i, scene in enumerate(enhanced_scenario["scenes"]):
                    if dialogue_improvements.get("scenes") and i < len(dialogue_improvements["scenes"]):
                        improved_scene = dialogue_improvements["scenes"][i]
                        if improved_scene.get("improved_dialogues"):
                            scene["dialogues"] = improved_scene["improved_dialogues"]
            
            if description_improvements and enhanced_scenario.get("scenes"):
                for i, scene in enumerate(enhanced_scenario["scenes"]):
                    if description_improvements.get("scenes") and i < len(description_improvements["scenes"]):
                        improved_scene = description_improvements["scenes"][i]
                        if improved_scene.get("improved_description"):
                            scene["description"] = improved_scene["improved_description"]
            
            # Ajout des métadonnées CrewAI
            enhanced_scenario["crewai_enhanced"] = True
            enhanced_scenario["enhancement_timestamp"] = datetime.now().isoformat()
            enhanced_scenario["enhancement_type"] = "text_only"
            enhanced_scenario["original_prompt"] = user_prompt
            enhanced_scenario["requested_style"] = style
            
            print(f"✅ Scénario fusionné avec succès")
            
            return enhanced_scenario
            
        except Exception as e:
            print(f"❌ Erreur lors de la fusion: {e}")
            # En cas d'erreur, retourne le scénario de base avec marquage
            base_scenario["crewai_enhanced"] = False
            base_scenario["enhancement_error"] = f"Fusion failed: {str(e)}"
            return base_scenario
    
    def validate_enhanced_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide que le scénario amélioré conserve la structure requise
        """
        errors = []
        
        # Vérifications de base
        if not scenario.get("scenes"):
            errors.append("Aucune scène trouvée")
        
        if not scenario.get("title"):
            errors.append("Titre manquant")
        
        # Vérification des scènes
        for i, scene in enumerate(scenario.get("scenes", [])):
            if not scene.get("description"):
                errors.append(f"Description manquante pour la scène {i+1}")
            
            if not scene.get("dialogues"):
                errors.append(f"Dialogues manquants pour la scène {i+1}")
            
            # Vérification des dialogues
            for j, dialogue in enumerate(scene.get("dialogues", [])):
                if not isinstance(dialogue, dict):
                    errors.append(f"Format de dialogue invalide - Scène {i+1}, Dialogue {j+1}")
                elif not dialogue.get("text"):
                    errors.append(f"Texte de dialogue manquant - Scène {i+1}, Dialogue {j+1}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "scene_count": len(scenario.get("scenes", [])),
            "has_crewai_enhancements": scenario.get("crewai_enhanced", False)
        }

# Instance globale - sera initialisée à la demande
_crewai_comic_enhancer = None

def get_crewai_comic_enhancer():
    """Retourne l'instance CrewAI, la crée si nécessaire"""
    global _crewai_comic_enhancer
    if _crewai_comic_enhancer is None:
        _crewai_comic_enhancer = CrewAIComicEnhancer()
    return _crewai_comic_enhancer
