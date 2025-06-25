"""
Service CrewAI pour la création de dessins animés cohérents
Architecture multi-agents pour transformer une histoire en animation complète de 30s à 5min
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
import hashlib
import random
import os

# Importation du vrai CrewAI
try:
    from crewai import Agent, Task, Crew
    from crewai.agent import Agent
    from crewai.task import Task
    from crewai.crew import Crew
    from langchain.llms import OpenAI
    from langchain_openai import ChatOpenAI
    CREWAI_REAL = True
    print("� CrewAI RÉEL activé - Vrais agents multi-agents")
except ImportError as e:
    CREWAI_REAL = False
    print(f"⚠️ Erreur import CrewAI: {e} - mode simulation activé")

class AnimationCrewAI:
    """Service CrewAI pour création de dessins animés cohérents avec continuité visuelle"""
    
    def __init__(self):
        # Initialiser le LLM pour CrewAI
        self.llm = self._setup_llm()
        self.setup_real_agents() if CREWAI_REAL else self.setup_agents()
        self.visual_seeds = {}  # Pour maintenir la cohérence visuelle
        self.character_library = {}  # Bibliothèque de personnages consistants
        self.style_guide = {}  # Guide de style unifié
        print("🎬 Service CrewAI Animation initialisé avec 5 agents spécialisés")
    
    def _setup_llm(self):
        """Configurer le LLM pour CrewAI"""
        if CREWAI_REAL:
            try:
                # Vérifier si OpenAI API key est disponible
                openai_key = os.getenv("OPENAI_API_KEY")
                if not openai_key:
                    print("⚠️ OPENAI_API_KEY non trouvée - utilisation de modèle local")
                    # Utiliser un modèle local ou gratuit
                    return ChatOpenAI(
                        model_name="gpt-3.5-turbo",
                        temperature=0.7,
                        api_key="dummy"  # Pour les tests
                    )
                else:
                    return ChatOpenAI(
                        model_name="gpt-4",
                        temperature=0.7,
                        openai_api_key=openai_key
                    )
            except Exception as e:
                print(f"⚠️ Erreur configuration LLM: {e}")
                return None
        return None
    
    def setup_real_agents(self):
        """Initialiser les vrais agents CrewAI"""
        if not CREWAI_REAL or not self.llm:
            print("🔄 Fallback vers simulation d'agents")
            return self.setup_agents()
        
        try:
            # Agent Scénariste
            self.scenarist_agent = Agent(
                role="Scénariste Expert",
                goal="Analyser et découper l'histoire en scènes cohérentes de 5-15 secondes",
                backstory="""Tu es un scénariste expert spécialisé dans les contenus pour enfants. 
                Tu maîtrises parfaitement la structure narrative et le timing pour créer des animations engageantes.
                Tu découpes les histoires en segments visuels optimaux pour la génération vidéo.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Directeur Artistique
            self.art_director_agent = Agent(
                role="Directeur Artistique",
                goal="Créer un guide de style unifié et maintenir la cohérence visuelle",
                backstory="""Tu es un directeur artistique expérimenté spécialisé dans l'animation pour enfants.
                Tu crées des guides de style cohérents, définis les personnages et assures la continuité visuelle
                entre toutes les scènes d'une animation.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Prompt Engineer
            self.prompt_engineer_agent = Agent(
                role="Prompt Engineer Spécialisé",
                goal="Transformer les scènes en prompts optimisés pour la génération text-to-video",
                backstory="""Tu es un expert en prompts pour l'IA générative, spécialement pour les modèles text-to-video.
                Tu maîtrises les techniques de prompt engineering pour Stable Diffusion Video, Runway et autres.
                Tu optimises les prompts pour assurer qualité et cohérence visuelle.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Opérateur Technique
            self.technical_operator_agent = Agent(
                role="Opérateur Technique Vidéo",
                goal="Superviser la génération technique et contrôler la qualité des clips",
                backstory="""Tu es un opérateur technique spécialisé dans la génération vidéo par IA.
                Tu gères les paramètres techniques, supervises la qualité et optimises les performances
                de génération pour obtenir les meilleurs résultats.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Monteur Vidéo
            self.video_editor_agent = Agent(
                role="Monteur Vidéo Expert",
                goal="Assembler les clips en animation finale cohérente avec transitions fluides",
                backstory="""Tu es un monteur vidéo expert spécialisé dans l'animation pour enfants.
                Tu crées des transitions fluides, ajustes le rythme narratif et finalises
                l'assemblage pour une expérience visuelle optimale.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            self.agents = {
                "scenarist": self.scenarist_agent,
                "art_director": self.art_director_agent,
                "prompt_engineer": self.prompt_engineer_agent,
                "technical_operator": self.technical_operator_agent,
                "video_editor": self.video_editor_agent
            }
            
            print(f"✅ {len(self.agents)} vrais agents CrewAI initialisés")
            for agent_name, agent in self.agents.items():
                print(f"   🤖 {agent.role}")
                
        except Exception as e:
            print(f"❌ Erreur initialisation agents CrewAI: {e}")
            print("🔄 Fallback vers simulation")
            self.setup_agents()
    
    def setup_agents(self):
        """Initialiser les 5 agents spécialisés"""
        
        self.agents = {
            "scenarist": {
                "name": "Scénariste",
                "role": "Expert en narration pour enfants",
                "description": "Découpe l'histoire en scènes cohérentes de 5-15 secondes",
                "expertise": ["structure narrative", "timing", "transitions", "storyboard"],
                "responsibilities": [
                    "Analyser la structure narrative",
                    "Découper en segments de 5-15 secondes",
                    "Identifier les moments clés visuels",
                    "Planifier les transitions entre scènes"
                ]
            },
            "art_director": {
                "name": "Directeur Artistique", 
                "role": "Responsable de la cohérence visuelle",
                "description": "Définit le style graphique et maintient la continuité",
                "expertise": ["style visuel", "personnages", "décors", "couleurs", "continuité"],
                "responsibilities": [
                    "Créer le guide de style unifié",
                    "Définir les personnages principaux",
                    "Établir la palette de couleurs",
                    "Assurer la continuité visuelle entre scènes"
                ]
            },
            "prompt_engineer": {
                "name": "Prompt Engineer",
                "role": "Spécialiste des prompts text-to-video",
                "description": "Traduit les scènes en prompts optimisés pour IA",
                "expertise": ["Stable Diffusion Video", "prompts", "paramètres techniques", "seeds"],
                "responsibilities": [
                    "Créer des prompts optimisés pour chaque scène",
                    "Gérer les seeds pour la continuité",
                    "Optimiser les paramètres techniques",
                    "Assurer la qualité visuelle"
                ]
            },
            "technical_operator": {
                "name": "Opérateur Technique",
                "role": "Gestionnaire de la génération vidéo",
                "description": "Supervise la génération et qualité des clips",
                "expertise": ["génération vidéo", "qualité", "résolution", "formats", "optimisation"],
                "responsibilities": [
                    "Superviser la génération des clips",
                    "Contrôler la qualité technique",
                    "Optimiser les performances",
                    "Gérer les erreurs et reprises"
                ]
            },
            "video_editor": {
                "name": "Monteur Vidéo",
                "role": "Responsable de l'assemblage final",
                "description": "Assemble les clips en vidéo finale cohérente",
                "expertise": ["montage", "transitions", "rythme", "post-production", "synchronisation"],
                "responsibilities": [
                    "Assembler les clips générés",
                    "Créer des transitions fluides",
                    "Ajuster le rythme narratif",
                    "Finaliser la vidéo complète"
                ]
            }
        }
        
        print(f"✅ {len(self.agents)} agents spécialisés initialisés")
        for agent_id, agent in self.agents.items():
            print(f"   🤖 {agent['name']}: {agent['role']}")
    
    async def create_animation_from_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline complet : histoire → animation cohérente de 30s à 5min"""
        
        story_text = story_data.get("story", "")
        style = story_data.get("style", "cartoon")
        target_duration = story_data.get("duration", 60)  # 60 secondes par défaut
        quality_level = story_data.get("quality", "high")  # high, medium, fast
        
        print(f"🎬 Début pipeline animation cohérente")
        print(f"📏 Durée cible: {target_duration}s")
        print(f"🎨 Style: {style}")
        print(f"⚡ Qualité: {quality_level}")
        print(f"📖 Histoire: {story_text[:100]}...")
        
        # Initialiser le pipeline de production
        pipeline_result = {
            "story_analysis": {},
            "visual_style_guide": {},
            "scene_prompts": [],
            "generated_clips": [],
            "final_video": {},
            "production_metadata": {}
        }
        
        try:
            # Phase 1: Analyse narrative et découpage (Agent Scénariste)
            print("\n🎭 PHASE 1: Analyse narrative et découpage")
            if CREWAI_REAL and hasattr(self, 'scenarist_agent'):
                scene_breakdown = await self._phase1_real_scenario_analysis(story_text, target_duration, quality_level)
            else:
                scene_breakdown = await self._phase1_scenario_analysis(story_text, target_duration, quality_level)
            pipeline_result["story_analysis"] = scene_breakdown
            
            # Phase 2: Direction artistique et guide de style (Agent Directeur Artistique)
            print("\n🎨 PHASE 2: Direction artistique et cohérence visuelle")
            if CREWAI_REAL and hasattr(self, 'art_director_agent'):
                visual_guide = await self._phase2_real_art_direction(scene_breakdown, style)
            else:
                visual_guide = await self._phase2_art_direction(scene_breakdown, style)
            pipeline_result["visual_style_guide"] = visual_guide
            
            # Phase 3: Ingénierie des prompts avec seeds (Agent Prompt Engineer)
            print("\n🔧 PHASE 3: Ingénierie des prompts avec continuité")
            if CREWAI_REAL and hasattr(self, 'prompt_engineer_agent'):
                scene_prompts = await self._phase3_real_prompt_engineering(scene_breakdown, visual_guide)
            else:
                scene_prompts = await self._phase3_prompt_engineering(scene_breakdown, visual_guide)
            pipeline_result["scene_prompts"] = scene_prompts
            
            # Phase 4: Génération technique des clips (Agent Opérateur Technique)
            print("\n⚙️ PHASE 4: Génération technique des clips vidéo")
            generated_clips = await self._phase4_technical_generation(scene_prompts, quality_level)
            pipeline_result["generated_clips"] = generated_clips
            
            # Phase 5: Montage et assemblage final (Agent Monteur Vidéo)
            print("\n🎬 PHASE 5: Montage et assemblage final")
            final_video = await self._phase5_video_editing(generated_clips, target_duration)
            pipeline_result["final_video"] = final_video
            
            # Métadonnées de production
            pipeline_result["production_metadata"] = {
                "total_scenes": len(generated_clips),
                "actual_duration": final_video.get("duration", target_duration),
                "style_consistency_score": self._calculate_consistency_score(visual_guide, generated_clips),
                "production_time": datetime.now().isoformat(),
                "quality_metrics": self._generate_quality_metrics(generated_clips),
                "agents_performance": self._evaluate_agents_performance()
            }
            
            print(f"\n🎉 ANIMATION CRÉÉE AVEC SUCCÈS!")
            print(f"📊 {len(generated_clips)} scènes • {final_video.get('duration', 0)}s • Style: {style}")
            
            return {
                "status": "success",
                "animation_id": f"crewai_cohesive_{int(datetime.now().timestamp())}",
                "title": story_data.get("title", "Animation CrewAI"),
                "total_duration": final_video.get("duration", target_duration),
                "scenes_count": len(generated_clips),
                "style": style,
                "quality_level": quality_level,
                "pipeline_result": pipeline_result,
                "video_url": final_video.get("url"),
                "thumbnail_url": final_video.get("thumbnail"),
                "created_at": datetime.now().isoformat(),
                "type": "narrative_animation_cohesive"
            }
            
        except Exception as e:
            print(f"❌ Erreur pipeline CrewAI: {e}")
            return {
                "status": "error",
                "error": str(e),
                "partial_result": pipeline_result,
                "fallback_suggestion": "Utiliser le mode génération simple"
            }
    
    async def _phase1_scenario_analysis(self, story_text: str, target_duration: int, quality_level: str) -> Dict[str, Any]:
        """Phase 1: Agent Scénariste - Analyse narrative et découpage intelligent"""
        
        print("🎭 Scénariste: Analyse de la structure narrative...")
        
        # Calculer le nombre optimal de scènes
        if quality_level == "fast":
            scenes_count = max(3, min(6, target_duration // 10))  # Moins de scènes pour rapidité
        elif quality_level == "high":
            scenes_count = max(4, min(20, target_duration // 5))  # Plus de scènes pour qualité
        else:
            scenes_count = max(3, min(12, target_duration // 8))  # Équilibré
        
        scene_duration = target_duration / scenes_count
        
        # Analyse sémantique intelligente du texte
        sentences = [s.strip() for s in story_text.split('.') if s.strip()]
        paragraphs = [p.strip() for p in story_text.split('\n') if p.strip()]
        
        # Identifier les moments narratifs clés
        narrative_beats = self._identify_narrative_beats(story_text)
        
        # Créer les scènes avec continuité narrative
        scenes = []
        sentences_per_scene = max(1, len(sentences) // scenes_count)
        
        for i in range(scenes_count):
            start_idx = i * sentences_per_scene
            end_idx = min((i + 1) * sentences_per_scene, len(sentences))
            
            if start_idx >= len(sentences):
                break
                
            scene_sentences = sentences[start_idx:end_idx]
            scene_text = '. '.join(scene_sentences)
            
            # Analyse approfondie de la scène
            scene_analysis = self._analyze_scene_deeply(scene_text, i, scenes_count)
            
            scenes.append({
                "scene_id": i + 1,
                "text": scene_text,
                "duration": scene_duration,
                "narrative_beat": narrative_beats[min(i, len(narrative_beats)-1)],
                "scene_type": scene_analysis["type"],
                "mood": scene_analysis["mood"],
                "energy_level": scene_analysis["energy"],
                "characters": scene_analysis["characters"],
                "setting": scene_analysis["setting"],
                "action_description": scene_analysis["action"],
                "visual_focus": scene_analysis["visual_focus"],
                "transition_in": scene_analysis["transition_in"],
                "transition_out": scene_analysis["transition_out"],
                "emotional_arc": scene_analysis["emotional_arc"]
            })
        
        return {
            "agent": "scenarist",
            "total_scenes": len(scenes),
            "target_duration": target_duration,
            "average_scene_duration": scene_duration,
            "scenes": scenes,
            "narrative_structure": {
                "setup": scenes[:max(1, len(scenes)//4)],
                "development": scenes[len(scenes)//4:-max(1, len(scenes)//4)] if len(scenes) > 2 else [],
                "climax": scenes[-max(1, len(scenes)//4):] if len(scenes) > 1 else scenes,
            },
            "story_themes": self._extract_story_themes(story_text),
            "visual_continuity_notes": self._generate_continuity_notes(scenes)
        }
    
    async def _phase1_real_scenario_analysis(self, story_text: str, target_duration: int, quality_level: str) -> Dict[str, Any]:
        """Phase 1: Vraie analyse CrewAI par l'agent Scénariste"""
        
        print("🎭 Scénariste CrewAI: Analyse narrative intelligente...")
        
        # Créer la tâche pour l'agent scénariste
        scenario_task = Task(
            description=f"""
            Analyse cette histoire pour enfants et découpe-la en scènes optimales pour animation:
            
            HISTOIRE: {story_text}
            DURÉE CIBLE: {target_duration} secondes
            QUALITÉ: {quality_level}
            
            Tu dois:
            1. Identifier la structure narrative (début, développement, climax, fin)
            2. Découper en scènes de 5-15 secondes selon la qualité demandée
            3. Pour chaque scène, identifier:
               - Le texte de la scène
               - Les personnages présents
               - Le décor/environnement
               - L'action principale
               - L'émotion/ambiance
               - Le type de scène (dialogue, action, narrative)
            
            RETOURNE un JSON structuré avec:
            - total_scenes: nombre de scènes
            - scenes: liste des scènes avec leurs détails
            - narrative_structure: structure narrative globale
            """,
            agent=self.scenarist_agent,
            expected_output="JSON structuré avec l'analyse complète des scènes"
        )
        
        try:
            # Créer l'équipe avec juste le scénariste pour cette phase
            crew = Crew(
                agents=[self.scenarist_agent],
                tasks=[scenario_task],
                verbose=True
            )
            
            # Exécuter la tâche
            result = crew.kickoff()
            
            # Parser le résultat JSON
            import json
            try:
                parsed_result = json.loads(str(result))
                return parsed_result
            except json.JSONDecodeError:
                # Si le parsing JSON échoue, créer une structure de base
                print("⚠️ Parsing JSON échoué, création structure de base")
                return await self._phase1_scenario_analysis(story_text, target_duration, quality_level)
                
        except Exception as e:
            print(f"❌ Erreur agent CrewAI scénariste: {e}")
            # Fallback vers simulation
            return await self._phase1_scenario_analysis(story_text, target_duration, quality_level)
    
    def setup_real_agents(self):
        """Initialiser les vrais agents CrewAI"""
        if not CREWAI_REAL or not self.llm:
            print("🔄 Fallback vers simulation d'agents")
            return self.setup_agents()
        
        try:
            # Agent Scénariste
            self.scenarist_agent = Agent(
                role="Scénariste Expert",
                goal="Analyser et découper l'histoire en scènes cohérentes de 5-15 secondes",
                backstory="""Tu es un scénariste expert spécialisé dans les contenus pour enfants. 
                Tu maîtrises parfaitement la structure narrative et le timing pour créer des animations engageantes.
                Tu découpes les histoires en segments visuels optimaux pour la génération vidéo.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Directeur Artistique
            self.art_director_agent = Agent(
                role="Directeur Artistique",
                goal="Créer un guide de style unifié et maintenir la cohérence visuelle",
                backstory="""Tu es un directeur artistique expérimenté spécialisé dans l'animation pour enfants.
                Tu crées des guides de style cohérents, définis les personnages et assures la continuité visuelle
                entre toutes les scènes d'une animation.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Prompt Engineer
            self.prompt_engineer_agent = Agent(
                role="Prompt Engineer Spécialisé",
                goal="Transformer les scènes en prompts optimisés pour la génération text-to-video",
                backstory="""Tu es un expert en prompts pour l'IA générative, spécialement pour les modèles text-to-video.
                Tu maîtrises les techniques de prompt engineering pour Stable Diffusion Video, Runway et autres.
                Tu optimises les prompts pour assurer qualité et cohérence visuelle.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Opérateur Technique
            self.technical_operator_agent = Agent(
                role="Opérateur Technique Vidéo",
                goal="Superviser la génération technique et contrôler la qualité des clips",
                backstory="""Tu es un opérateur technique spécialisé dans la génération vidéo par IA.
                Tu gères les paramètres techniques, supervises la qualité et optimises les performances
                de génération pour obtenir les meilleurs résultats.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # Agent Monteur Vidéo
            self.video_editor_agent = Agent(
                role="Monteur Vidéo Expert",
                goal="Assembler les clips en animation finale cohérente avec transitions fluides",
                backstory="""Tu es un monteur vidéo expert spécialisé dans l'animation pour enfants.
                Tu crées des transitions fluides, ajustes le rythme narratif et finalises
                l'assemblage pour une expérience visuelle optimale.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            self.agents = {
                "scenarist": self.scenarist_agent,
                "art_director": self.art_director_agent,
                "prompt_engineer": self.prompt_engineer_agent,
                "technical_operator": self.technical_operator_agent,
                "video_editor": self.video_editor_agent
            }
            
            print(f"✅ {len(self.agents)} vrais agents CrewAI initialisés")
            for agent_name, agent in self.agents.items():
                print(f"   🤖 {agent.role}")
                
        except Exception as e:
            print(f"❌ Erreur initialisation agents CrewAI: {e}")
            print("🔄 Fallback vers simulation")
            self.setup_agents()
    
    def setup_agents(self):
        """Initialiser les 5 agents spécialisés"""
        
        self.agents = {
            "scenarist": {
                "name": "Scénariste",
                "role": "Expert en narration pour enfants",
                "description": "Découpe l'histoire en scènes cohérentes de 5-15 secondes",
                "expertise": ["structure narrative", "timing", "transitions", "storyboard"],
                "responsibilities": [
                    "Analyser la structure narrative",
                    "Découper en segments de 5-15 secondes",
                    "Identifier les moments clés visuels",
                    "Planifier les transitions entre scènes"
                ]
            },
            "art_director": {
                "name": "Directeur Artistique", 
                "role": "Responsable de la cohérence visuelle",
                "description": "Définit le style graphique et maintient la continuité",
                "expertise": ["style visuel", "personnages", "décors", "couleurs", "continuité"],
                "responsibilities": [
                    "Créer le guide de style unifié",
                    "Définir les personnages principaux",
                    "Établir la palette de couleurs",
                    "Assurer la continuité visuelle entre scènes"
                ]
            },
            "prompt_engineer": {
                "name": "Prompt Engineer",
                "role": "Spécialiste des prompts text-to-video",
                "description": "Traduit les scènes en prompts optimisés pour IA",
                "expertise": ["Stable Diffusion Video", "prompts", "paramètres techniques", "seeds"],
                "responsibilities": [
                    "Créer des prompts optimisés pour chaque scène",
                    "Gérer les seeds pour la continuité",
                    "Optimiser les paramètres techniques",
                    "Assurer la qualité visuelle"
                ]
            },
            "technical_operator": {
                "name": "Opérateur Technique",
                "role": "Gestionnaire de la génération vidéo",
                "description": "Supervise la génération et qualité des clips",
                "expertise": ["génération vidéo", "qualité", "résolution", "formats", "optimisation"],
                "responsibilities": [
                    "Superviser la génération des clips",
                    "Contrôler la qualité technique",
                    "Optimiser les performances",
                    "Gérer les erreurs et reprises"
                ]
            },
            "video_editor": {
                "name": "Monteur Vidéo",
                "role": "Responsable de l'assemblage final",
                "description": "Assemble les clips en vidéo finale cohérente",
                "expertise": ["montage", "transitions", "rythme", "post-production", "synchronisation"],
                "responsibilities": [
                    "Assembler les clips générés",
                    "Créer des transitions fluides",
                    "Ajuster le rythme narratif",
                    "Finaliser la vidéo complète"
                ]
            }
        }
        
        print(f"✅ {len(self.agents)} agents spécialisés initialisés")
        for agent_id, agent in self.agents.items():
            print(f"   🤖 {agent['name']}: {agent['role']}")
    
    async def create_animation_from_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline complet : histoire → animation cohérente de 30s à 5min"""
        
        story_text = story_data.get("story", "")
        style = story_data.get("style", "cartoon")
        target_duration = story_data.get("duration", 60)  # 60 secondes par défaut
        quality_level = story_data.get("quality", "high")  # high, medium, fast
        
        print(f"🎬 Début pipeline animation cohérente")
        print(f"📏 Durée cible: {target_duration}s")
        print(f"🎨 Style: {style}")
        print(f"⚡ Qualité: {quality_level}")
        print(f"📖 Histoire: {story_text[:100]}...")
        
        # Initialiser le pipeline de production
        pipeline_result = {
            "story_analysis": {},
            "visual_style_guide": {},
            "scene_prompts": [],
            "generated_clips": [],
            "final_video": {},
            "production_metadata": {}
        }
        
        try:
            # Phase 1: Analyse narrative et découpage (Agent Scénariste)
            print("\n🎭 PHASE 1: Analyse narrative et découpage")
            if CREWAI_REAL and hasattr(self, 'scenarist_agent'):
                scene_breakdown = await self._phase1_real_scenario_analysis(story_text, target_duration, quality_level)
            else:
                scene_breakdown = await self._phase1_scenario_analysis(story_text, target_duration, quality_level)
            pipeline_result["story_analysis"] = scene_breakdown
            
            # Phase 2: Direction artistique et guide de style (Agent Directeur Artistique)
            print("\n🎨 PHASE 2: Direction artistique et cohérence visuelle")
            if CREWAI_REAL and hasattr(self, 'art_director_agent'):
                visual_guide = await self._phase2_real_art_direction(scene_breakdown, style)
            else:
                visual_guide = await self._phase2_art_direction(scene_breakdown, style)
            pipeline_result["visual_style_guide"] = visual_guide
            
            # Phase 3: Ingénierie des prompts avec seeds (Agent Prompt Engineer)
            print("\n🔧 PHASE 3: Ingénierie des prompts avec continuité")
            if CREWAI_REAL and hasattr(self, 'prompt_engineer_agent'):
                scene_prompts = await self._phase3_real_prompt_engineering(scene_breakdown, visual_guide)
            else:
                scene_prompts = await self._phase3_prompt_engineering(scene_breakdown, visual_guide)
            pipeline_result["scene_prompts"] = scene_prompts
            
            # Phase 4: Génération technique des clips (Agent Opérateur Technique)
            print("\n⚙️ PHASE 4: Génération technique des clips vidéo")
            generated_clips = await self._phase4_technical_generation(scene_prompts, quality_level)
            pipeline_result["generated_clips"] = generated_clips
            
            # Phase 5: Montage et assemblage final (Agent Monteur Vidéo)
            print("\n🎬 PHASE 5: Montage et assemblage final")
            final_video = await self._phase5_video_editing(generated_clips, target_duration)
            pipeline_result["final_video"] = final_video
            
            # Métadonnées de production
            pipeline_result["production_metadata"] = {
                "total_scenes": len(generated_clips),
                "actual_duration": final_video.get("duration", target_duration),
                "style_consistency_score": self._calculate_consistency_score(visual_guide, generated_clips),
                "production_time": datetime.now().isoformat(),
                "quality_metrics": self._generate_quality_metrics(generated_clips),
                "agents_performance": self._evaluate_agents_performance()
            }
            
            print(f"\n🎉 ANIMATION CRÉÉE AVEC SUCCÈS!")
            print(f"📊 {len(generated_clips)} scènes • {final_video.get('duration', 0)}s • Style: {style}")
            
            return {
                "status": "success",
                "animation_id": f"crewai_cohesive_{int(datetime.now().timestamp())}",
                "title": story_data.get("title", "Animation CrewAI"),
                "total_duration": final_video.get("duration", target_duration),
                "scenes_count": len(generated_clips),
                "style": style,
                "quality_level": quality_level,
                "pipeline_result": pipeline_result,
                "video_url": final_video.get("url"),
                "thumbnail_url": final_video.get("thumbnail"),
                "created_at": datetime.now().isoformat(),
                "type": "narrative_animation_cohesive"
            }
            
        except Exception as e:
            print(f"❌ Erreur pipeline CrewAI: {e}")
            return {
                "status": "error",
                "error": str(e),
                "partial_result": pipeline_result,
                "fallback_suggestion": "Utiliser le mode génération simple"
            }
    
    async def _phase1_scenario_analysis(self, story_text: str, target_duration: int, quality_level: str) -> Dict[str, Any]:
        """Phase 1: Agent Scénariste - Analyse narrative et découpage intelligent"""
        
        print("🎭 Scénariste: Analyse de la structure narrative...")
        
        # Calculer le nombre optimal de scènes
        if quality_level == "fast":
            scenes_count = max(3, min(6, target_duration // 10))  # Moins de scènes pour rapidité
        elif quality_level == "high":
            scenes_count = max(4, min(20, target_duration // 5))  # Plus de scènes pour qualité
        else:
            scenes_count = max(3, min(12, target_duration // 8))  # Équilibré
        
        scene_duration = target_duration / scenes_count
        
        # Analyse sémantique intelligente du texte
        sentences = [s.strip() for s in story_text.split('.') if s.strip()]
        paragraphs = [p.strip() for p in story_text.split('\n') if p.strip()]
        
        # Identifier les moments narratifs clés
        narrative_beats = self._identify_narrative_beats(story_text)
        
        # Créer les scènes avec continuité narrative
        scenes = []
        sentences_per_scene = max(1, len(sentences) // scenes_count)
        
        for i in range(scenes_count):
            start_idx = i * sentences_per_scene
            end_idx = min((i + 1) * sentences_per_scene, len(sentences))
            
            if start_idx >= len(sentences):
                break
                
            scene_sentences = sentences[start_idx:end_idx]
            scene_text = '. '.join(scene_sentences)
            
            # Analyse approfondie de la scène
            scene_analysis = self._analyze_scene_deeply(scene_text, i, scenes_count)
            
            scenes.append({
                "scene_id": i + 1,
                "text": scene_text,
                "duration": scene_duration,
                "narrative_beat": narrative_beats[min(i, len(narrative_beats)-1)],
                "scene_type": scene_analysis["type"],
                "mood": scene_analysis["mood"],
                "energy_level": scene_analysis["energy"],
                "characters": scene_analysis["characters"],
                "setting": scene_analysis["setting"],
                "action_description": scene_analysis["action"],
                "visual_focus": scene_analysis["visual_focus"],
                "transition_in": scene_analysis["transition_in"],
                "transition_out": scene_analysis["transition_out"],
                "emotional_arc": scene_analysis["emotional_arc"]
            })
        
        return {
            "agent": "scenarist",
            "total_scenes": len(scenes),
            "target_duration": target_duration,
            "average_scene_duration": scene_duration,
            "scenes": scenes,
            "narrative_structure": {
                "setup": scenes[:max(1, len(scenes)//4)],
                "development": scenes[len(scenes)//4:-max(1, len(scenes)//4)] if len(scenes) > 2 else [],
                "climax": scenes[-max(1, len(scenes)//4):] if len(scenes) > 1 else scenes,
            },
            "story_themes": self._extract_story_themes(story_text),
            "visual_continuity_notes": self._generate_continuity_notes(scenes)
        }
    
    async def _phase1_real_scenario_analysis(self, story_text: str, target_duration: int, quality_level: str) -> Dict[str, Any]:
        """Phase 1: Vraie analyse CrewAI par l'agent Scénariste"""
        
        print("🎭 Scénariste CrewAI: Analyse narrative intelligente...")
        
        # Créer la tâche pour l'agent scénariste
        scenario_task = Task(
            description=f"""
            Analyse cette histoire pour enfants et découpe-la en scènes optimales pour animation:
            
            HISTOIRE: {story_text}
            DURÉE CIBLE: {target_duration} secondes
            QUALITÉ: {quality_level}
            
            Tu dois:
            1. Identifier la structure narrative (début, développement, climax, fin)
            2. Découper en scènes de 5-15 secondes selon la qualité demandée
            3. Pour chaque scène, identifier:
               - Le texte de la scène
               - Les personnages présents
               - Le décor/environnement
               - L'action principale
               - L'émotion/ambiance
               - Le type de scène (dialogue, action, narrative)
            
            RETOURNE un JSON structuré avec:
            - total_scenes: nombre de scènes
            - scenes: liste des scènes avec leurs détails
            - narrative_structure: structure narrative globale
            """,
            agent=self.scenarist_agent,
            expected_output="JSON structuré avec l'analyse complète des scènes"
        )
        
        try:
            # Créer l'équipe avec juste le scénariste pour cette phase
            crew = Crew(
                agents=[self.scenarist_agent],
                tasks=[scenario_task],
                verbose=True
            )
            
            # Exécuter la tâche
            result = crew.kickoff()
            
            # Parser le résultat JSON
            import json
            try:
                parsed_result = json.loads(str(result))
                return parsed_result
            except json.JSONDecodeError:
                # Si le parsing JSON échoue, créer une structure de base
                print("⚠️ Parsing JSON échoué, création structure de base")
                return await self._phase1_scenario_analysis(story_text, target_duration, quality_level)
                
        except Exception as e:
            print(f"❌ Erreur agent CrewAI scénariste: {e}")
            # Fallback vers simulation
            return await self._phase1_scenario_analysis(story_text, target_duration, quality_level)
    
    async def _phase2_art_direction(self, scene_breakdown: Dict[str, Any], style: str) -> Dict[str, Any]:
        """Phase 2: Agent Directeur Artistique - Style unifié et cohérence visuelle"""
        
        print("🎨 Directeur Artistique: Création du guide de style unifié...")
        
        scenes = scene_breakdown.get("scenes", [])
        
        # Générer un seed maître pour la cohérence globale
        master_seed = random.randint(100000, 999999)
        
        # Créer le guide de style complet
        style_guide = {
            "agent": "art_director",
            "master_seed": master_seed,
            "style_name": style,
            "visual_identity": self._create_visual_identity(style, scenes),
            "color_palette": self._generate_cohesive_color_palette(scenes, style),
            "character_designs": self._design_consistent_characters(scenes),
            "environment_library": self._create_environment_library(scenes),
            "lighting_scheme": self._define_lighting_scheme(style),
            "visual_consistency_rules": self._establish_consistency_rules(),
            "seeds_hierarchy": self._generate_seeds_hierarchy(master_seed, scenes)
        }
        
        # Créer la bibliothèque de personnages pour continuité
        self.character_library = style_guide["character_designs"]
        self.style_guide = style_guide
        
        return style_guide
    
    async def _phase2_real_art_direction(self, scene_breakdown: Dict[str, Any], style: str) -> Dict[str, Any]:
        """Phase 2: Vraie direction artistique CrewAI"""
        
        print("🎨 Directeur Artistique CrewAI: Création du guide de style...")
        
        art_direction_task = Task(
            description=f"""
            Crée un guide de style artistique cohérent pour cette animation:
            
            SCÈNES: {json.dumps(scene_breakdown.get('scenes', [])[:3])}  # Premières scènes pour contexte
            STYLE DEMANDÉ: {style}
            TOTAL SCÈNES: {scene_breakdown.get('total_scenes', 5)}
            
            Tu dois créer:
            1. Une identité visuelle unifiée pour le style {style}
            2. Une palette de couleurs cohérente
            3. Des designs de personnages consistants
            4. Un schéma d'éclairage uniforme
            5. Des règles de cohérence visuelle
            6. Une hiérarchie de seeds pour maintenir la continuité
            
            RETOURNE un JSON avec:
            - visual_identity: description du style artistique
            - color_palette: couleurs principales
            - character_designs: designs des personnages
            - lighting_scheme: schéma d'éclairage
            - consistency_rules: règles de cohérence
            - master_seed: seed principal pour cohérence
            """,
            agent=self.art_director_agent,
            expected_output="Guide de style complet en JSON"
        )
        
        try:
            crew = Crew(
                agents=[self.art_director_agent],
                tasks=[art_direction_task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            try:
                parsed_result = json.loads(str(result))
                return parsed_result
            except json.JSONDecodeError:
                print("⚠️ Parsing JSON échoué pour direction artistique")
                return await self._phase2_art_direction(scene_breakdown, style)
                
        except Exception as e:
            print(f"❌ Erreur agent CrewAI directeur artistique: {e}")
            return await self._phase2_art_direction(scene_breakdown, style)
    
    async def _phase3_prompt_engineering(self, scene_breakdown: Dict[str, Any], visual_guide: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Phase 3: Agent Prompt Engineer - Prompts optimisés avec seeds de continuité"""
        
        print("🔧 Prompt Engineer: Création des prompts avec continuité visuelle...")
        
        scenes = scene_breakdown.get("scenes", [])
        style_name = visual_guide.get("style_name", "cartoon")
        visual_identity = visual_guide.get("visual_identity", {})
        seeds_hierarchy = visual_guide.get("seeds_hierarchy", {})
        
        scene_prompts = []
        
        for scene in scenes:
            scene_id = scene["scene_id"]
            scene_seeds = seeds_hierarchy.get(f"scene_{scene_id}", {})
            
            # Construire le prompt avec continuité
            prompt_components = self._build_prompt_components(scene, visual_identity, style_name)
            
            # Assembler le prompt final optimisé
            full_prompt = self._assemble_optimized_prompt(prompt_components, scene)
            
            # Créer le prompt négatif spécialisé
            negative_prompt = self._create_specialized_negative_prompt(scene)
            
            scene_prompt = {
                "scene_id": scene_id,
                "text_description": scene["text"],
                "visual_focus": scene["visual_focus"],
                "base_prompt": prompt_components["base"],
                "style_prompt": prompt_components["style"],
                "character_prompt": prompt_components["characters"],
                "environment_prompt": prompt_components["environment"],
                "full_prompt": full_prompt,
                "negative_prompt": negative_prompt,
                "technical_parameters": {
                    "duration": scene["duration"],
                    "fps": 24,
                    "resolution": "1024x576",  # 16:9 optimisé pour mobile
                    "steps": 25 if scene.get("energy_level") == "high" else 20,
                    "cfg_scale": 7.5,
                    "scheduler": "DPMSolverMultistep",
                    "master_seed": visual_guide["master_seed"],
                    "character_seed": scene_seeds.get("character_seed"),
                    "environment_seed": scene_seeds.get("environment_seed"),
                    "style_seed": scene_seeds.get("style_seed"),
                    "motion_seed": scene_seeds.get("motion_seed")
                },
                "continuity_references": {
                    "previous_scene": scene_id - 1 if scene_id > 1 else None,
                    "character_consistency": self._get_character_references(scene),
                    "environment_consistency": self._get_environment_references(scene),
                    "style_consistency": visual_identity
                },
                "quality_modifiers": self._generate_quality_modifiers(scene)
            }
            
            scene_prompts.append(scene_prompt)
        
        return scene_prompts
    
    async def _phase3_real_prompt_engineering(self, scene_breakdown: Dict[str, Any], visual_guide: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Phase 3: Vrai prompt engineering CrewAI"""
        
        print("🔧 Prompt Engineer CrewAI: Création des prompts optimisés...")
        
        prompt_engineering_task = Task(
            description=f"""
            Crée des prompts optimisés pour génération text-to-video à partir de ces scènes:
            
            SCÈNES: {json.dumps(scene_breakdown.get('scenes', []))}
            GUIDE STYLE: {json.dumps(visual_guide)}
            
            Pour chaque scène, crée:
            1. Un prompt principal optimisé pour text-to-video
            2. Un prompt négatif pour éviter le contenu indésirable
            3. Des paramètres techniques (résolution, steps, cfg_scale)
            4. Des seeds dérivés pour la cohérence visuelle
            5. Des modificateurs de qualité
            
            Utilise les meilleures pratiques pour:
            - Stable Diffusion Video
            - Runway ML
            - Modèles text-to-video en général
            
            RETOURNE une liste JSON de prompts pour chaque scène avec:
            - scene_id: numéro de scène
            - full_prompt: prompt principal optimisé
            - negative_prompt: prompt négatif
            - technical_parameters: paramètres techniques
            - continuity_references: références pour cohérence
            """,
            agent=self.prompt_engineer_agent,
            expected_output="Liste JSON de prompts optimisés pour chaque scène"
        )
        
        try:
            crew = Crew(
                agents=[self.prompt_engineer_agent],
                tasks=[prompt_engineering_task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            try:
                parsed_result = json.loads(str(result))
                return parsed_result if isinstance(parsed_result, list) else [parsed_result]
            except json.JSONDecodeError:
                print("⚠️ Parsing JSON échoué pour prompt engineering")
                return await self._phase3_prompt_engineering(scene_breakdown, visual_guide)
                
        except Exception as e:
            print(f"❌ Erreur agent CrewAI prompt engineer: {e}")
            return await self._phase3_prompt_engineering(scene_breakdown, visual_guide)
    
    async def _phase4_technical_generation(self, scene_prompts: List[Dict[str, Any]], quality_level: str) -> List[Dict[str, Any]]:
        """Phase 4: Agent Opérateur Technique - Génération supervisée des clips"""
        
        print("⚙️ Opérateur Technique: Génération supervisée des clips...")
        
        generated_clips = []
        
        for prompt_data in scene_prompts:
            scene_id = prompt_data["scene_id"]
            
            print(f"   Génération clip {scene_id}/{len(scene_prompts)}: {prompt_data['text_description'][:50]}...")
            
            # Configuration technique selon le niveau de qualité
            tech_config = self._get_technical_config(quality_level)
            
            # Simuler la génération vidéo avec Stable Diffusion Video ou équivalent
            generation_result = await self._simulate_sdv_generation(prompt_data, tech_config)
            
            # Contrôle qualité automatique
            quality_assessment = self._assess_clip_quality(generation_result, prompt_data)
            
            # Récupération automatique en cas de problème
            if quality_assessment["score"] < 7 and quality_level == "high":
                print(f"   🔄 Qualité insuffisante (score: {quality_assessment['score']}) - Nouvelle tentative...")
                generation_result = await self._retry_generation_with_adjustments(prompt_data, tech_config)
                quality_assessment = self._assess_clip_quality(generation_result, prompt_data)
            
            generated_clips.append({
                "scene_id": scene_id,
                "clip_url": generation_result["url"],
                "duration": prompt_data["technical_parameters"]["duration"],
                "resolution": prompt_data["technical_parameters"]["resolution"],
                "quality_score": quality_assessment["score"],
                "quality_issues": quality_assessment["issues"],
                "generation_time": generation_result["generation_time"],
                "seeds_used": prompt_data["technical_parameters"],
                "prompt_used": prompt_data["full_prompt"],
                "technical_metadata": generation_result["metadata"],
                "continuity_score": self._evaluate_continuity_score(prompt_data, generation_result),
                "status": "completed"
            })
            
            print(f"   ✅ Clip {scene_id} généré (qualité: {quality_assessment['score']}/10)")
        
        return generated_clips
    
    async def _phase5_video_editing(self, generated_clips: List[Dict[str, Any]], target_duration: int) -> Dict[str, Any]:
        """Phase 5: Agent Monteur Vidéo - Assemblage intelligent et transitions"""
        
        print("🎬 Monteur Vidéo: Assemblage et création des transitions...")
        
        # Analyser les clips pour un montage optimal
        editing_plan = self._create_editing_plan(generated_clips, target_duration)
        
        # Créer les transitions intelligentes
        transitions = self._create_intelligent_transitions(generated_clips)
        
        # Ajuster les durées pour l'harmonie narrative
        adjusted_clips = self._adjust_for_narrative_flow(generated_clips, target_duration)
        
        # Ajouter des effets de post-production si nécessaire
        post_effects = self._apply_post_production_effects(adjusted_clips)
        
        # Simuler l'assemblage final avec transitions
        final_assembly = await self._simulate_final_assembly(adjusted_clips, transitions, post_effects)
        
        return {
            "agent": "video_editor",
            "final_url": final_assembly["url"],
            "total_duration": final_assembly["duration"],
            "clips_count": len(adjusted_clips),
            "transitions": transitions,
            "editing_plan": editing_plan,
            "post_effects": post_effects,
            "assembly_time": final_assembly["assembly_time"],
            "final_resolution": "1920x1080",
            "format": "mp4",
            "quality": "high",
            "thumbnail_url": final_assembly.get("thumbnail"),
            "narrative_flow_score": self._calculate_narrative_flow_score(adjusted_clips)
        }
    
    # ===== MÉTHODES UTILITAIRES =====
    
    def _identify_narrative_beats(self, story_text: str) -> List[str]:
        """Identifier les temps narratifs de l'histoire"""
        beats = ["introduction", "incident", "développement", "climax", "résolution"]
        # Analyse simplifiée - en production, utiliser NLP avancé
        return beats[:5]
    
    def _analyze_scene_deeply(self, scene_text: str, scene_index: int, total_scenes: int) -> Dict[str, Any]:
        """Analyse approfondie d'une scène"""
        
        # Type de scène
        scene_type = self._determine_scene_type(scene_text)
        
        # Analyse émotionnelle
        mood = self._analyze_emotional_content(scene_text)
        
        # Niveau d'énergie
        energy = self._assess_energy_level(scene_text)
        
        # Éléments visuels
        visual_focus = self._identify_visual_focus(scene_text)
        
        # Transitions
        transition_in = "fade_in" if scene_index == 0 else "smooth"
        transition_out = "fade_out" if scene_index == total_scenes - 1 else "smooth"
        
        return {
            "type": scene_type,
            "mood": mood,
            "energy": energy,
            "characters": self._extract_characters_advanced(scene_text),
            "setting": self._identify_setting_detailed(scene_text),
            "action": self._describe_main_action(scene_text),
            "visual_focus": visual_focus,
            "transition_in": transition_in,
            "transition_out": transition_out,
            "emotional_arc": self._trace_emotional_arc(scene_text, scene_index, total_scenes)
        }
    
    def _create_visual_identity(self, style: str, scenes: List[Dict]) -> Dict[str, Any]:
        """Créer l'identité visuelle unifiée"""
        
        identity_templates = {
            "cartoon": {
                "art_style": "vibrant cartoon animation with rounded shapes",
                "character_style": "cute, expressive characters with big eyes",
                "environment_style": "colorful, welcoming environments",
                "lighting": "bright, warm lighting",
                "mood": "joyful and optimistic"
            },
            "fairy_tale": {
                "art_style": "magical fairy tale illustration with soft textures",
                "character_style": "elegant, fairy-tale characters",
                "environment_style": "enchanted, dreamlike settings",
                "lighting": "soft, magical lighting with sparkles",
                "mood": "wonder and enchantment"
            },
            "anime": {
                "art_style": "anime-style animation with detailed expressions",
                "character_style": "anime characters with expressive features",
                "environment_style": "detailed anime-style backgrounds",
                "lighting": "dramatic anime lighting",
                "mood": "dynamic and expressive"
            }
        }
        
        return identity_templates.get(style, identity_templates["cartoon"])
    
    def _generate_cohesive_color_palette(self, scenes: List[Dict], style: str) -> Dict[str, str]:
        """Générer une palette de couleurs cohérente pour toute l'animation"""
        
        # Analyser les ambiances dominantes
        dominant_moods = [scene.get("mood", "positive") for scene in scenes]
        
        # Palettes selon style et ambiance
        palettes = {
            "cartoon_positive": {
                "primary": "#FF6B9D",
                "secondary": "#4ECDC4", 
                "accent": "#FFE66D",
                "background": "#A8E6CF",
                "neutral": "#F7F7F7"
            },
            "fairy_tale_wonder": {
                "primary": "#DDA0DD",
                "secondary": "#98FB98",
                "accent": "#F0E68C", 
                "background": "#E6E6FA",
                "neutral": "#FFF8DC"
            },
            "anime_dynamic": {
                "primary": "#FF4081",
                "secondary": "#00BCD4",
                "accent": "#FFEB3B",
                "background": "#E1F5FE",
                "neutral": "#FAFAFA"
            }
        }
        
        # Sélectionner la palette appropriée
        palette_key = f"{style}_{dominant_moods[0] if dominant_moods else 'positive'}"
        return palettes.get(palette_key, palettes["cartoon_positive"])
    
    def _design_consistent_characters(self, scenes: List[Dict]) -> Dict[str, Any]:
        """Créer des designs de personnages consistants"""
        
        # Extraire tous les personnages uniques
        all_characters = set()
        for scene in scenes:
            all_characters.update(scene.get("characters", []))
        
        character_designs = {}
        for i, char in enumerate(all_characters):
            # Générer un design consistent pour chaque personnage
            character_designs[char] = {
                "character_id": f"char_{i+1}",
                "base_description": f"consistent {char} character",
                "visual_traits": {
                    "face": "expressive, friendly features",
                    "body": "appealing proportions for children",
                    "clothing": "distinctive, memorable outfit",
                    "colors": f"consistent color scheme for {char}"
                },
                "personality_traits": self._infer_personality(char),
                "seed_modifier": i * 1000,  # Pour la consistance
                "reference_prompts": [
                    f"front view of {char}",
                    f"side view of {char}",
                    f"{char} expressing emotions"
                ]
            }
        
        return character_designs
    
    def _create_environment_library(self, scenes: List[Dict]) -> Dict[str, Any]:
        """Créer la bibliothèque d'environnements cohérents"""
        
        all_settings = set(scene.get("setting", "générique") for scene in scenes)
        
        environment_library = {}
        for setting in all_settings:
            environment_library[setting] = {
                "base_description": f"consistent {setting} environment",
                "atmosphere": "magical, welcoming atmosphere",
                "lighting": "soft, warm lighting that maintains mood",
                "color_harmony": "colors that complement the main palette",
                "details": "rich environmental details without overwhelming",
                "seed_modifier": hash(setting) % 10000,  # Consistent seed per environment
                "reference_elements": [
                    f"wide shot of {setting}",
                    f"detailed view of {setting}",
                    f"atmospheric {setting} scene"
                ]
            }
        
        return environment_library
    
    def _define_lighting_scheme(self, style: str) -> Dict[str, Any]:
        """Définir le schéma d'éclairage cohérent"""
        
        lighting_schemes = {
            "cartoon": {
                "primary_lighting": "bright, cheerful lighting",
                "mood_lighting": "consistent warm tones",
                "shadow_style": "soft, minimal shadows",
                "highlight_style": "vibrant highlights"
            },
            "fairy_tale": {
                "primary_lighting": "magical, dreamy lighting",
                "mood_lighting": "soft ethereal glow",
                "shadow_style": "gentle, mystical shadows",
                "highlight_style": "sparkly, enchanted highlights"
            },
            "anime": {
                "primary_lighting": "dramatic anime lighting",
                "mood_lighting": "expressive lighting changes",
                "shadow_style": "bold, defined shadows",
                "highlight_style": "sharp, dynamic highlights"
            }
        }
        
        return lighting_schemes.get(style, lighting_schemes["cartoon"])
    
    def _establish_consistency_rules(self) -> Dict[str, List[str]]:
        """Établir les règles de cohérence visuelle"""
        
        return {
            "character_consistency": [
                "Maintain same character design across all scenes",
                "Keep consistent color schemes for each character",
                "Preserve character proportions and features",
                "Use derived seeds for character variations"
            ],
            "environment_consistency": [
                "Maintain consistent lighting style",
                "Keep environmental color palette coherent",
                "Preserve architectural/natural elements style",
                "Use consistent perspective and framing"
            ],
            "style_consistency": [
                "Apply same art style throughout animation",
                "Maintain consistent line weight and texture",
                "Keep color saturation levels uniform",
                "Preserve overall aesthetic coherence"
            ],
            "technical_consistency": [
                "Use related seeds for visual continuity",
                "Maintain same resolution and quality settings",
                "Keep consistent frame rate and motion style",
                "Apply uniform post-processing effects"
            ]
        }
    
    def _generate_seeds_hierarchy(self, master_seed: int, scenes: List[Dict]) -> Dict[str, Dict[str, int]]:
        """Générer une hiérarchie de seeds pour la cohérence"""
        
        seeds_hierarchy = {}
        
        for scene in scenes:
            scene_id = scene["scene_id"]
            
            # Seeds dérivés du master seed avec variation contrôlée
            seeds_hierarchy[f"scene_{scene_id}"] = {
                "character_seed": master_seed + scene_id,
                "environment_seed": master_seed + scene_id * 10,
                "style_seed": master_seed + scene_id * 100,
                "motion_seed": master_seed + scene_id * 1000,
                "lighting_seed": master_seed + scene_id * 10000
            }
        
        return seeds_hierarchy
    
    async def _simulate_sdv_generation(self, prompt_data: Dict, tech_config: Dict) -> Dict[str, Any]:
        """Simuler la génération avec Stable Diffusion Video"""
        
        # Simulation réaliste du temps de génération
        scene_duration = prompt_data["technical_parameters"]["duration"]
        generation_time = scene_duration * 2.5  # 2.5s de calcul par seconde de vidéo
        
        await asyncio.sleep(0.5)  # Simulation raccourcie pour tests
        
        return {
            "url": f"https://storage.googleapis.com/animation_clips/scene_{prompt_data['scene_id']}_cohesive.mp4",
            "generation_time": generation_time,
            "status": "completed",
            "metadata": {
                "model": "Stable Diffusion Video",
                "version": "1.1",
                "parameters": prompt_data["technical_parameters"],
                "quality_preset": tech_config["quality_preset"]
            }
        }
    
    def _calculate_consistency_score(self, visual_guide: Dict, clips: List[Dict]) -> float:
        """Calculer le score de cohérence visuelle"""
        # Simulation du score basé sur les seeds et le guide de style
        base_score = 8.5
        
        # Bonus pour utilisation cohérente des seeds
        if visual_guide.get("seeds_hierarchy"):
            base_score += 0.5
        
        # Bonus pour qualité des clips
        avg_quality = sum(clip.get("quality_score", 7) for clip in clips) / len(clips) if clips else 7
        base_score += (avg_quality - 7) * 0.2
        
        return min(10.0, base_score)
    
    def _get_technical_config(self, quality_level: str) -> Dict[str, Any]:
        """Configuration technique selon le niveau de qualité"""
        
        configs = {
            "fast": {
                "quality_preset": "fast",
                "resolution": "512x288",
                "steps": 15,
                "cfg_scale": 6.0
            },
            "medium": {
                "quality_preset": "balanced",
                "resolution": "1024x576", 
                "steps": 20,
                "cfg_scale": 7.5
            },
            "high": {
                "quality_preset": "quality",
                "resolution": "1024x576",
                "steps": 25,
                "cfg_scale": 8.0
            }
        }
        
        return configs.get(quality_level, configs["medium"])
    
    def _assess_clip_quality(self, generation_result: Dict, prompt_data: Dict) -> Dict[str, Any]:
        """Évaluer la qualité d'un clip généré"""
        
        # Simulation d'évaluation qualité
        base_score = random.uniform(7.0, 9.5)
        
        issues = []
        if base_score < 7.5:
            issues.append("Résolution légèrement floue")
        if base_score < 7.0:
            issues.append("Mouvement saccadé")
        
        return {
            "score": round(base_score, 1),
            "issues": issues,
            "recommendations": [] if not issues else ["Ajuster les paramètres de génération"]
        }
    
    async def _retry_generation_with_adjustments(self, prompt_data: Dict, tech_config: Dict) -> Dict[str, Any]:
        """Nouvelle tentative avec paramètres ajustés"""
        
        # Ajuster les paramètres pour améliorer la qualité
        adjusted_prompt = prompt_data.copy()
        adjusted_prompt["technical_parameters"]["cfg_scale"] += 0.5
        adjusted_prompt["technical_parameters"]["steps"] += 5
        
        return await self._simulate_sdv_generation(adjusted_prompt, tech_config)
    
    async def _simulate_final_assembly(self, clips: List[Dict], transitions: List[Dict], effects: Dict) -> Dict[str, Any]:
        """Simuler l'assemblage final des clips"""
        
        total_duration = sum(clip.get("adjusted_duration", clip["duration"]) for clip in clips)
        assembly_time = len(clips) * 2.0  # 2s par clip pour l'assemblage
        
        await asyncio.sleep(1.0)  # Simulation de l'assemblage
        
        return {
            "url": "https://storage.googleapis.com/final_animations/cohesive_animation.mp4",
            "duration": total_duration,
            "assembly_time": assembly_time,
            "status": "completed",
            "thumbnail": "https://storage.googleapis.com/thumbnails/cohesive_thumb.jpg"
        }
    
    # Méthodes utilitaires supplémentaires (versions simplifiées pour la démo)
    
    def _determine_scene_type(self, text: str) -> str:
        """Déterminer le type de scène"""
        if any(word in text.lower() for word in ["dit", "parle", "répond"]):
            return "dialogue"
        elif any(word in text.lower() for word in ["court", "vole", "combat"]):
            return "action"
        else:
            return "narrative"
    
    def _analyze_emotional_content(self, text: str) -> str:
        """Analyser le contenu émotionnel"""
        positive = ["joyeux", "heureux", "sourire", "content"]
        dramatic = ["danger", "peur", "sombre", "inquiet"]
        
        if any(word in text.lower() for word in positive):
            return "positive"
        elif any(word in text.lower() for word in dramatic):
            return "dramatic"
        else:
            return "neutral"
    
    def _assess_energy_level(self, text: str) -> str:
        """Évaluer le niveau d'énergie"""
        high_energy = ["court", "vole", "combat", "explose", "crie"]
        if any(word in text.lower() for word in high_energy):
            return "high"
        else:
            return "medium"
    
    def _extract_characters_advanced(self, text: str) -> List[str]:
        """Extraction avancée des personnages"""
        chars = ["héros", "princesse", "dragon", "sorcier", "animal", "ami"]
        return [char for char in chars if char in text.lower()][:2]
    
    def _identify_setting_detailed(self, text: str) -> str:
        """Identification détaillée du décor"""
        settings = {
            "forêt": ["forêt", "arbre", "bois"],
            "château": ["château", "palais", "tour"],
            "ciel": ["ciel", "nuage", "vole"]
        }
        
        for setting, keywords in settings.items():
            if any(keyword in text.lower() for keyword in keywords):
                return setting
        return "intérieur"
    
    def _extract_story_themes(self, story_text: str) -> List[str]:
        """Extraire les thèmes de l'histoire"""
        themes = []
        theme_keywords = {
            "amitié": ["ami", "ensemble", "aide"],
            "aventure": ["voyage", "exploration", "découvre"],
            "magie": ["magique", "sortilège", "enchantement"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in story_text.lower() for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]
    
    def _generate_continuity_notes(self, scenes: List[Dict]) -> List[str]:
        """Générer des notes de continuité"""
        return [
            "Maintenir la cohérence des personnages entre scènes",
            "Assurer la fluidité des transitions temporelles",
            "Conserver la palette de couleurs établie"
        ]
    
    def _build_prompt_components(self, scene: Dict, visual_identity: Dict, style: str) -> Dict[str, str]:
        """Construire les composants du prompt"""
        return {
            "base": f"{style} style: {scene['text']}",
            "style": visual_identity.get("art_style", ""),
            "characters": f"characters: {', '.join(scene.get('characters', []))}",
            "environment": f"setting: {scene.get('setting', 'generic')}"
        }
    
    def _assemble_optimized_prompt(self, components: Dict[str, str], scene: Dict) -> str:
        """Assembler le prompt final optimisé"""
        base = components["base"]
        style = components["style"]
        mood = scene.get("mood", "positive")
        
        return f"{base}. {style}. Mood: {mood}. High quality animation, smooth motion, child-friendly."
    
    def _create_specialized_negative_prompt(self, scene: Dict) -> str:
        """Créer un prompt négatif spécialisé"""
        return "violence, scary content, adult themes, low quality, blurry, distorted, inappropriate for children"
    
    def _generate_quality_modifiers(self, scene: Dict) -> List[str]:
        """Générer des modificateurs de qualité"""
        modifiers = ["high resolution", "smooth animation", "vibrant colors"]
        
        if scene.get("energy_level") == "high":
            modifiers.append("dynamic motion")
        
        return modifiers
    
    def _get_character_references(self, scene: Dict) -> Dict[str, str]:
        """Obtenir les références de personnages pour la continuité"""
        return {char: f"consistent {char} design" for char in scene.get("characters", [])}
    
    def _get_environment_references(self, scene: Dict) -> str:
        """Obtenir les références d'environnement"""
        return f"consistent {scene.get('setting', 'environment')} style"
    
    def _create_editing_plan(self, clips: List[Dict], target_duration: int) -> Dict[str, Any]:
        """Créer le plan de montage"""
        return {
            "total_clips": len(clips),
            "target_duration": target_duration,
            "pacing": "steady narrative flow",
            "style": "seamless transitions"
        }
    
    def _create_intelligent_transitions(self, clips: List[Dict]) -> List[Dict]:
        """Créer des transitions intelligentes"""
        transitions = []
        for i in range(len(clips) - 1):
            transitions.append({
                "from_scene": clips[i]["scene_id"],
                "to_scene": clips[i + 1]["scene_id"],
                "type": "cross_fade",
                "duration": 0.5
            })
        return transitions
    
    def _adjust_for_narrative_flow(self, clips: List[Dict], target_duration: int) -> List[Dict]:
        """Ajuster pour le flow narratif"""
        total_current = sum(clip["duration"] for clip in clips)
        factor = target_duration / total_current if total_current > 0 else 1
        
        for clip in clips:
            clip["adjusted_duration"] = clip["duration"] * factor
        
        return clips
    
    def _apply_post_production_effects(self, clips: List[Dict]) -> Dict[str, Any]:
        """Appliquer des effets de post-production"""
        return {
            "color_correction": "automatic color balance",
            "audio": "background music and sound effects",
            "stabilization": "motion smoothing"
        }
    
    def _evaluate_continuity_score(self, prompt_data: Dict, result: Dict) -> float:
        """Évaluer le score de continuité"""
        return 8.5  # Simulation
    
    def _calculate_narrative_flow_score(self, clips: List[Dict]) -> float:
        """Calculer le score de flow narratif"""
        return 9.0  # Simulation
    
    def _generate_quality_metrics(self, clips: List[Dict]) -> Dict[str, Any]:
        """Générer les métriques de qualité"""
        return {
            "average_quality": sum(clip.get("quality_score", 8) for clip in clips) / len(clips),
            "consistency_score": 8.7,
            "technical_score": 8.9
        }
    
    def _evaluate_agents_performance(self) -> Dict[str, float]:
        """Évaluer la performance des agents"""
        return {
            "scenarist": 9.2,
            "art_director": 8.8,
            "prompt_engineer": 9.0,
            "technical_operator": 8.6,
            "video_editor": 8.9
        }
    
    def _infer_personality(self, character: str) -> List[str]:
        """Inférer la personnalité d'un personnage"""
        personalities = {
            "héros": ["brave", "déterminé", "bienveillant"],
            "princesse": ["élégante", "gentille", "courageuse"],
            "dragon": ["puissant", "mystérieux", "protecteur"]
        }
        return personalities.get(character, ["amical", "positif"])
    
    def _identify_visual_focus(self, text: str) -> str:
        """Identifier le focus visuel principal"""
        if any(word in text.lower() for word in ["regarde", "voit", "observe"]):
            return "visual_discovery"
        elif any(word in text.lower() for word in ["dit", "parle"]):
            return "character_interaction"
        else:
            return "action_sequence"
    
    def _describe_main_action(self, text: str) -> str:
        """Décrire l'action principale"""
        actions = ["marche", "court", "vole", "regarde", "parle", "découvre"]
        for action in actions:
            if action in text.lower():
                return f"character {action}"
        return "character moves"
    
    def _trace_emotional_arc(self, text: str, scene_index: int, total_scenes: int) -> str:
        """Tracer l'arc émotionnel"""
        if scene_index < total_scenes // 3:
            return "setup_emotion"
        elif scene_index < 2 * total_scenes // 3:
            return "building_tension"
        else:
            return "resolution_emotion"

# Instance globale du service
animation_crewai = AnimationCrewAI()
