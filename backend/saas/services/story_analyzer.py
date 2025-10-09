"""
Service d'analyse et découpage d'histoires en scènes
Utilise GPT-4o-mini pour analyser et segmenter les histoires
"""
import json
import asyncio
from typing import List, Dict, Any
import aiohttp

class StoryAnalyzer:
    """Analyseur d'histoires pour le découpage en scènes"""
    
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def segment_story(self, story: str, target_duration: int, min_scene: int, max_scene: int) -> List[Dict[str, Any]]:
        """
        Découper une histoire en scènes visuellement cohérentes
        
        Args:
            story: Texte de l'histoire
            target_duration: Durée totale cible
            min_scene: Durée minimale par scène
            max_scene: Durée maximale par scène
            
        Returns:
            Liste de scènes avec descriptions et durées
        """
        print(f"📝 Analyse de l'histoire ({len(story)} caractères)")
        
        # Calculer le nombre optimal de scènes
        optimal_scenes = max(3, min(10, target_duration // 8))  # Environ 8s par scène
        
        # Prompt pour GPT-4o-mini
        prompt = f"""
Tu es un expert en narration visuelle et en découpage cinématographique.

MISSION: Analyser cette histoire et la découper en {optimal_scenes} scènes visuelles parfaites pour un dessin animé.

HISTOIRE À ANALYSER:
{story}

CONTRAINTES:
- Durée totale cible: {target_duration} secondes
- Nombre de scènes: {optimal_scenes}
- Durée par scène: entre {min_scene}s et {max_scene}s
- Chaque scène doit être visuellement distincte et intéressante
- La somme des durées DOIT égaler exactement {target_duration} secondes

INSTRUCTIONS:
1. Identifie les moments clés de l'histoire
2. Crée {optimal_scenes} scènes avec une action claire et visuelle
3. Assigne une durée optimale à chaque scène
4. Assure-toi que la progression narrative est fluide

RETOURNE UNIQUEMENT ce JSON (pas d'explication):
{{
    "scenes": [
        {{
            "scene_number": 1,
            "duration": X,
            "title": "Titre court de la scène",
            "description": "Description détaillée de ce qui se passe visuellement",
            "action": "Action principale visible",
            "setting": "Lieu et environnement",
            "characters": ["personnage1", "personnage2"],
            "visual_focus": "Élément visuel central de la scène",
            "narrative_purpose": "Rôle dans l'histoire"
        }}
    ],
    "total_duration": {target_duration},
    "story_analysis": "Analyse brève de la structure narrative"
}}
"""
        
        try:
            # Appel à l'API OpenAI
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Tu es un expert en découpage narratif et cinématographique. Tu réponds uniquement avec du JSON valide."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                async with session.post(self.base_url, headers=headers, json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # Parser le JSON retourné
                        try:
                            parsed_result = json.loads(content)
                            scenes = parsed_result.get('scenes', [])
                            
                            # Vérifier et corriger les durées
                            scenes = self._correct_scene_durations(scenes, target_duration)
                            
                            print(f"✅ {len(scenes)} scènes générées")
                            return scenes
                            
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Erreur parsing JSON: {e}")
                            return self._generate_fallback_scenes(story, target_duration, optimal_scenes)
                    
                    else:
                        print(f"❌ Erreur API OpenAI: {response.status}")
                        return self._generate_fallback_scenes(story, target_duration, optimal_scenes)
        
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            return self._generate_fallback_scenes(story, target_duration, optimal_scenes)
    
    def _correct_scene_durations(self, scenes: List[Dict], target_duration: int) -> List[Dict]:
        """Corriger les durées pour qu'elles correspondent exactement à la cible"""
        if not scenes:
            return scenes
        
        current_total = sum(scene.get('duration', 8) for scene in scenes)
        
        if abs(current_total - target_duration) < 1:
            return scenes  # Déjà correct
        
        print(f"🔧 Correction durées: {current_total}s → {target_duration}s")
        
        # Répartition proportionnelle
        factor = target_duration / current_total if current_total > 0 else 1
        
        corrected_scenes = []
        running_total = 0
        
        for i, scene in enumerate(scenes):
            if i == len(scenes) - 1:  # Dernière scène
                corrected_duration = target_duration - running_total
            else:
                corrected_duration = round(scene.get('duration', 8) * factor)
                corrected_duration = max(5, min(15, corrected_duration))  # Entre 5 et 15s
            
            scene_copy = scene.copy()
            scene_copy['duration'] = corrected_duration
            corrected_scenes.append(scene_copy)
            running_total += corrected_duration
        
        return corrected_scenes
    
    def _generate_fallback_scenes(self, story: str, target_duration: int, num_scenes: int) -> List[Dict]:
        """Générer des scènes de fallback en cas d'échec de l'API"""
        print(f"🔄 Génération de scènes fallback")
        
        scene_duration = target_duration // num_scenes
        remainder = target_duration % num_scenes
        
        scenes = []
        for i in range(num_scenes):
            duration = scene_duration + (1 if i < remainder else 0)
            
            scene = {
                "scene_number": i + 1,
                "duration": duration,
                "title": f"Scène {i + 1}",
                "description": f"Scène {i + 1} de l'histoire: {story[:50]}...",
                "action": f"Action de la scène {i + 1}",
                "setting": "Environnement général de l'histoire",
                "characters": ["personnage principal"],
                "visual_focus": f"Élément central scène {i + 1}",
                "narrative_purpose": f"Progression narrative scène {i + 1}"
            }
            scenes.append(scene)
        
        return scenes
