import json
import math
from typing import List
from openai import AsyncOpenAI
from config import config
from models.schemas import StoryIdea, Scene

class SceneCreator:
    """Service de création de scènes détaillées pour l'animation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    
    def calculate_scene_distribution(self, total_duration: int) -> List[int]:
        """
        Calcule la distribution optimale des scènes pour Wan 2.5
        Wan 2.5 limite: clips de 5s ou 10s uniquement
        """
        return config.get_clip_durations(total_duration)

    def create_scene_system_prompt(self) -> str:
        """Prompt système optimisé pour Wan 2.5 avec cohérence narrative"""
        return f"""✅ Générateur de Scènes pour Dessins Animés Wan 2.5 (Alibaba)

Rôle: Tu es un scénariste expert en animations pour enfants qui crée des scènes cohérentes et narratives pour Wan 2.5, le modèle de génération vidéo d'Alibaba.

🎯 OBJECTIF PRINCIPAL: COHÉRENCE NARRATIVE
- Chaque scène doit s'enchaîner naturellement avec la précédente
- Les personnages doivent être reconnaissables d'une scène à l'autre
- L'environnement doit rester cohérent tout au long de l'histoire
- L'histoire doit avoir un début, un milieu et une fin clairs

🎨 STYLE WAN 2.5 OPTIMISÉ:
- Style: {config.WAN25_PROMPT_STYLE}
- Format: clips de 10 secondes maximum
- Audio: intégré automatiquement (lip-sync et effets sonores)
- Résolution: HD 720p/1080p
- Public: enfants de 3-8 ans

📝 ÉLÉMENTS OBLIGATOIRES PAR SCÈNE:
1. PERSONNAGES: Décrire clairement les personnages (apparence, vêtements, expressions)
2. ACTION: Mouvement ou action précise en cours
3. ENVIRONNEMENT: Décor détaillé et cohérent
4. CAMÉRA: Angle et mouvement cinématographique
5. ÉMOTION: État émotionnel des personnages
6. CONTINUITÉ: Référence à la scène précédente pour enchaînement fluide

🎬 STRUCTURE NARRATIVE (adaptée à la durée):
- DÉBUT (1-2 premières scènes): Introduction du personnage et du contexte
- MILIEU (scènes centrales): Développement de l'action, problème ou découverte
- FIN (2 dernières scènes): Résolution positive et conclusion satisfaisante

🚫 À ÉVITER ABSOLUMENT:
- Personnages qui changent d'apparence entre les scènes
- Environnements incohérents (ex: forêt → désert sans transition)
- Actions statiques ou personnages immobiles
- Scènes sans lien narratif avec les autres
- Violence, peur, contenu inapproprié pour enfants

✅ BONNES PRATIQUES WAN 2.5:
- Utiliser des descriptions visuelles précises
- Mentionner les couleurs vives et contrastées
- Décrire les expressions faciales des personnages
- Inclure des mouvements fluides et naturels
- Créer des transitions logiques entre scènes

FORMAT DE SORTIE:
json
{{
  "Idea": "L'idée principale de l'histoire",
  "Environment": "L'environnement général cohérent",
  "Sound": "Description audio globale",
  "Scene 1": "Description détaillée avec personnages, action, environnement",
  "Scene 2": "Suite logique avec continuité visuelle et narrative",
  "Scene N": "Conclusion satisfaisante de l'histoire"
}}"""

    async def create_scenes_from_idea(self, story_idea: StoryIdea, duration: int) -> List[Scene]:
        """Crée des scènes détaillées à partir d'une idée d'histoire"""
        
        scene_durations = self.calculate_scene_distribution(duration)
        num_scenes = len(scene_durations)
        
        system_prompt = self.create_scene_system_prompt()
        
        user_prompt = f"""Crée {num_scenes} scènes cinématographiques détaillées basées sur cette idée d'histoire:

IDÉE: {story_idea.idea}
ENVIRONNEMENT: {story_idea.environment}
SON: {story_idea.sound}
DURÉE TOTALE: {duration} secondes
DURÉES DES SCÈNES: {scene_durations} secondes chacune

L'histoire doit être divisée en {num_scenes} scènes cohérentes qui racontent l'histoire complète:
- Début engageant (scènes 1-2)
- Développement/action (scènes milieu) 
- Conclusion satisfaisante (dernières scènes)

Chaque scène doit:
- Être optimisée pour Wan 2.5 (Alibaba) avec cohérence visuelle
- Maintenir les MÊMES personnages reconnaissables tout au long
- Garder le MÊME environnement cohérent (pas de changements brusques)
- Inclure mouvements fluides et expressions faciales
- S'enchaîner naturellement avec la scène précédente
- Durée: exactement {scene_durations} secondes par scène
- Public: enfants 3-8 ans, contenu joyeux et positif

IMPORTANT COHÉRENCE:
- Scene 1: Introduction claire du/des personnage(s) principal(aux) avec description précise
- Scènes suivantes: RÉUTILISER ces mêmes personnages, ne PAS en créer de nouveaux
- Environnement: Rester dans le même lieu ou faire des transitions logiques
- Continuité: Chaque scène continue l'histoire de la précédente

Respecte exactement le format JSON demandé avec Scene 1, Scene 2, etc."""

        try:
            response = await self.client.chat.completions.create(
                model=config.TEXT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Créativité contrôlée
                max_tokens=2000
            )
            
            # Parser la réponse JSON
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            scenes_data = json.loads(content)
            
            # Extraire les scènes
            scenes = []
            for i in range(num_scenes):
                scene_key = f"Scene {i + 1}"
                if scene_key in scenes_data:
                    # Coercer la description en texte si l'IA renvoie un objet
                    raw_value = scenes_data[scene_key]
                    description_text = self._coerce_scene_text(raw_value)

                    # Créer le prompt optimisé pour Wan 2.5
                    optimized_prompt = self.optimize_prompt_for_wan25(
                        description_text,
                        story_idea,
                        i + 1
                    )
                    
                    # Extraire personnages et actions pour la scène
                    characters, action, environment = self._parse_scene_elements(description_text, story_idea)
                    
                    scene = Scene(
                        scene_number=i + 1,
                        description=description_text,
                        duration=scene_durations[i],
                        prompt=optimized_prompt,
                        characters=characters,
                        action=action,
                        environment=environment,
                        audio_description=story_idea.sound
                    )
                    scenes.append(scene)
            
            return scenes
            
        except json.JSONDecodeError as e:
            # Fallback avec scènes génériques
            return self.create_fallback_scenes(story_idea, scene_durations)
        
        except Exception as e:
            raise Exception(f"Erreur lors de la création des scènes: {str(e)}")

    def _coerce_scene_text(self, value) -> str:
        """Transforme une valeur de scène (str ou dict) en description texte exploitable."""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            # Chercher un champ descriptif fréquent
            for key in ["Description", "description", "scene", "text", "content", "prompt"]:
                v = value.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()
            # Sinon concaténer les valeurs textuelles
            parts = [str(v).strip() for v in value.values() if isinstance(v, str) and v.strip()]
            if parts:
                return ". ".join(parts)
            # Dernier recours: JSON brut
            return json.dumps(value, ensure_ascii=False)
        # Types inattendus
        return str(value)

    def optimize_prompt_for_wan25(self, scene_description: str, story_idea: StoryIdea, scene_number: int) -> str:
        """
        Optimise le prompt pour Wan 2.5 avec cohérence narrative maximale
        Format inspiré de zseedance.json mais adapté pour Wan 2.5
        """
        
        # Style Wan 2.5 optimisé
        style_prefix = f"STYLE: {config.WAN25_PROMPT_STYLE}"
        
        # Thème général pour cohérence
        theme = f"STORY THEME: {story_idea.idea}"
        
        # Description de la scène avec numéro pour continuité
        scene_info = f"SCENE {scene_number}: {scene_description}"
        
        # Environnement cohérent
        environment_info = f"ENVIRONMENT: {story_idea.environment}, consistent visual style"
        
        # Audio sync hint pour Wan 2.5
        audio_hint = f"AUDIO: {story_idea.sound}, synchronized sound effects"
        
        # Continuité visuelle
        continuity = "CONTINUITY: maintain same characters and setting from previous scenes"
        
        # Assemblage optimisé pour Wan 2.5
        final_prompt = f"{style_prefix} | {theme} | {scene_info} | {environment_info} | {audio_hint} | {continuity}"
        
        return final_prompt
    
    def _parse_scene_elements(self, scene_description: str, story_idea: StoryIdea) -> tuple:
        """
        Extrait les éléments clés de la scène pour cohérence
        Returns: (characters, action, environment)
        """
        # Personnages par défaut basés sur l'idée
        characters = "animated character from the story"
        
        # Action extraite de la description
        action = scene_description[:100] if len(scene_description) > 100 else scene_description
        
        # Environnement de l'histoire
        environment = story_idea.environment
        
        return characters, action, environment

    def create_fallback_scenes(self, story_idea: StoryIdea, scene_durations: List[int]) -> List[Scene]:
        """Crée des scènes de fallback en cas d'erreur"""
        scenes = []
        
        # Scènes génériques basées sur l'idée
        scene_templates = [
            "Introduction du personnage principal dans l'environnement coloré",
            "Le personnage découvre quelque chose d'intéressant et s'approche",
            "Action principale de l'histoire avec mouvements dynamiques",
            "Résolution positive avec apprentissage ou découverte",
            "Conclusion joyeuse avec personnage satisfait"
        ]
        
        for i, duration in enumerate(scene_durations):
            template = scene_templates[min(i, len(scene_templates) - 1)]
            
            scene = Scene(
                scene_number=i + 1,
                description=f"{template} - {story_idea.idea}",
                duration=duration,
                prompt=self.optimize_prompt_for_wan25(
                    template,
                    story_idea,
                    i + 1
                ),
                characters="main character",
                action=template,
                environment=story_idea.environment,
                audio_description=story_idea.sound
            )
            scenes.append(scene)
        
        return scenes

    def extract_scenes_from_text(self, text: str) -> List[str]:
        """Extrait les descriptions de scènes d'un texte (méthode utilitaire du workflow n8n)"""
        scenes = []
        
        # Recherche de patterns "Scene X:" ou "Scène X:"
        import re
        scene_pattern = r'(?:Scene|Scène)\s*(\d+):\s*(.+?)(?=(?:Scene|Scène)\s*\d+:|$)'
        matches = re.findall(scene_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            scene_text = match[1].strip()
            if scene_text:
                scenes.append(scene_text)
        
        return scenes 