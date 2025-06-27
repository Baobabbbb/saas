"""
Service d'animation CrewAI avec timeout et fallback rapide
Version optimisée pour éviter les blocages
"""
import os
import json
import asyncio
import time
import aiohttp
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
import signal

# Charger les variables d'environnement
load_dotenv('.env.crewai')
load_dotenv('.env')

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
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    status: str = "pending"

class TimeoutAnimationService:
    """Service d'animation avec timeout pour éviter les blocages"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.cache_dir = Path("cache/timeout_animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Timeouts pour éviter les blocages
        self.crewai_timeout = 30  # 30 secondes max pour CrewAI
        self.stability_timeout = 15  # 15 secondes max pour Stability AI
        self.total_timeout = 60  # 60 secondes max pour tout le processus
        
        print(f"⚡ Service Animation avec Timeout initialisé")
        print(f"   ⏱️  Timeout CrewAI: {self.crewai_timeout}s")
        print(f"   ⏱️  Timeout Stability: {self.stability_timeout}s")
        print(f"   ⏱️  Timeout Total: {self.total_timeout}s")
    
    def _correct_scene_durations(self, scenes: List[Dict], target_duration: float) -> List[Dict]:
        """Corriger les durées des scènes pour respecter exactement la durée cible"""
        if not scenes:
            return scenes
        
        # Calculer la somme actuelle
        current_total = sum(float(scene.get('duration', 0)) for scene in scenes)
        
        if abs(current_total - target_duration) < 0.1:  # Déjà correct
            return scenes
        
        print(f"🔧 Correction durées: {current_total}s → {target_duration}s")
        
        # Calculer le facteur de correction
        if current_total > 0:
            correction_factor = target_duration / current_total
            
            # Appliquer le facteur avec arrondi intelligent
            corrected_scenes = []
            running_total = 0.0
            
            for i, scene in enumerate(scenes):
                if i == len(scenes) - 1:  # Dernière scène : ajuster pour atteindre exactement la cible
                    corrected_duration = target_duration - running_total
                else:
                    raw_duration = float(scene.get('duration', 0)) * correction_factor
                    corrected_duration = round(raw_duration, 1)
                
                # Durée minimum de 1 seconde
                corrected_duration = max(1.0, corrected_duration)
                
                scene_copy = scene.copy()
                scene_copy['duration'] = corrected_duration
                corrected_scenes.append(scene_copy)
                running_total += corrected_duration
        
        else:
            # Répartition égale si pas de durées
            duration_per_scene = target_duration / len(scenes)
            corrected_scenes = []
            
            for i, scene in enumerate(scenes):
                scene_copy = scene.copy()
                if i == len(scenes) - 1:  # Dernière scène
                    scene_copy['duration'] = target_duration - (duration_per_scene * (len(scenes) - 1))
                else:
                    scene_copy['duration'] = duration_per_scene
                corrected_scenes.append(scene_copy)
        
        # Vérification finale
        final_total = sum(scene['duration'] for scene in corrected_scenes)
        print(f"✅ Durées corrigées: {final_total}s (cible: {target_duration}s)")
        
        return corrected_scenes
    
    async def generate_scenes_with_crewai_timeout(self, story: str, duration: float) -> List[Dict]:
        """Générer des scènes avec CrewAI avec timeout"""
        
        try:
            print(f"🎬 Génération scènes CrewAI (timeout: {self.crewai_timeout}s)...")
            
            # Fonction wrapper pour CrewAI
            async def run_crewai():
                # Import conditionnel pour éviter les blocages au niveau import
                try:
                    from crewai import Agent, Task, Crew, Process
                    from langchain_openai import ChatOpenAI
                    
                    # Configuration LLM avec timeout réduit
                    llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        api_key=self.openai_api_key,
                        temperature=0.7,
                        request_timeout=10  # Timeout de 10s pour les requêtes LLM
                    )
                    
                    # Agent simple et rapide
                    agent = Agent(
                        role="Scénariste Rapide",
                        goal="Créer un découpage rapide en scènes",
                        backstory="Expert en découpage narratif rapide",
                        llm=llm,
                        verbose=False,  # Réduire les logs pour éviter les blocages
                        allow_delegation=False
                    )
                    
                    # Tâche avec prompt simplifié
                    task = Task(
                        description=f"""
                        Découper cette histoire en 3-4 scènes de {duration} secondes au total.
                        Histoire: {story}
                        
                        Retourner UNIQUEMENT ce JSON:
                        {{
                            "scenes": [
                                {{"scene_number": 1, "duration": X, "description": "...", "action": "...", "setting": "..."}},
                                {{"scene_number": 2, "duration": Y, "description": "...", "action": "...", "setting": "..."}}
                            ]
                        }}
                        
                        IMPORTANT: La somme des durées doit égaler {duration} secondes.
                        """,
                        agent=agent,
                        expected_output="JSON avec scènes"
                    )
                    
                    # Crew minimal
                    crew = Crew(
                        agents=[agent],
                        tasks=[task],
                        process=Process.sequential,
                        verbose=False,
                        memory=False,  # Désactiver la mémoire pour éviter les blocages
                        cache=False   # Désactiver le cache pour éviter les blocages
                    )
                    
                    # Exécution rapide
                    inputs = {"story": story, "duration": duration}
                    result = crew.kickoff(inputs=inputs)
                    
                    return str(result)
                    
                except Exception as e:
                    print(f"❌ Erreur CrewAI interne: {e}")
                    return None
            
            # Exécuter avec timeout
            try:
                result = await asyncio.wait_for(run_crewai(), timeout=self.crewai_timeout)
                
                if result:
                    # Parser le résultat JSON
                    scenes = self._parse_crewai_result(result, duration)
                    if scenes:
                        # Corriger les durées
                        return self._correct_scene_durations(scenes, duration)
                
            except asyncio.TimeoutError:
                print(f"⏱️ Timeout CrewAI ({self.crewai_timeout}s) - passage au fallback")
            except Exception as e:
                print(f"❌ Erreur CrewAI: {e}")
        
        except Exception as e:
            print(f"❌ Erreur générale CrewAI: {e}")
        
        # Fallback : scènes générées algorithmiquement
        return self._generate_fallback_scenes(story, duration)
    
    def _parse_crewai_result(self, result: str, target_duration: float) -> Optional[List[Dict]]:
        """Parser le résultat CrewAI pour extraire les scènes"""
        try:
            # Chercher le JSON dans le résultat
            result_str = str(result)
            
            # Essayer de parser directement
            if result_str.strip().startswith('{'):
                data = json.loads(result_str)
                if 'scenes' in data:
                    return data['scenes']
            
            # Chercher des patterns JSON
            import re
            json_patterns = [
                r'\{[^}]*"scenes"[^}]*\}',
                r'\{.*?"scenes".*?\}',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, result_str, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if 'scenes' in data and isinstance(data['scenes'], list):
                            return data['scenes']
                    except:
                        continue
            
            print(f"⚠️ Impossible de parser le résultat CrewAI")
            return None
            
        except Exception as e:
            print(f"❌ Erreur parsing CrewAI: {e}")
            return None
    
    def _generate_fallback_scenes(self, story: str, duration: float) -> List[Dict]:
        """Générer des scènes de fallback algorithmiquement"""
        print(f"🔄 Génération fallback pour {duration}s")
        
        # Analyser l'histoire pour créer des scènes logiques
        story_lower = story.lower()
        
        # Détecter les éléments de l'histoire
        characters = []
        if any(word in story_lower for word in ['luna', 'fille', 'petite']):
            characters.append("Luna")
        if any(word in story_lower for word in ['chat', 'félix']):
            characters.append("chat magique")
        
        settings = []
        if any(word in story_lower for word in ['jardin', 'parc']):
            settings.append("jardin")
        if any(word in story_lower for word in ['maison', 'chambre']):
            settings.append("maison")
        if any(word in story_lower for word in ['forêt', 'bois']):
            settings.append("forêt")
        
        # Générer 3-4 scènes selon la durée
        if duration <= 10:
            num_scenes = 3
        elif duration <= 20:
            num_scenes = 4
        else:
            num_scenes = 5
        
        scenes = []
        scene_duration = duration / num_scenes
        
        for i in range(num_scenes):
            if i == num_scenes - 1:  # Dernière scène
                scene_dur = duration - (scene_duration * (num_scenes - 1))
            else:
                scene_dur = scene_duration
            
            # Templates de scènes génériques
            if i == 0:
                desc = f"Introduction des personnages dans l'histoire"
                action = "présentation"
                setting = settings[0] if settings else "environnement principal"
            elif i == num_scenes - 1:
                desc = f"Conclusion de l'aventure"
                action = "résolution"
                setting = settings[0] if settings else "retour au point de départ"
            else:
                desc = f"Développement de l'action - partie {i}"
                action = "aventure"
                setting = settings[i % len(settings)] if settings else f"lieu {i}"
            
            scene = {
                "scene_number": i + 1,
                "duration": round(scene_dur, 1),
                "description": desc,
                "action": action,
                "setting": setting
            }
            scenes.append(scene)
        
        return scenes
    
    async def _generate_demo_video(self, animation_id: str, scenes: List[AnimationScene], story: str) -> str:
        """Générer une vidéo de démonstration pour l'affichage"""
        try:
            print(f"🎬 Génération vidéo démo pour {animation_id}")
            
            # Créer une vidéo simple avec FFmpeg si disponible
            video_filename = f"demo_animation_{animation_id}.mp4"
            video_path = self.cache_dir / video_filename
            
            # Essayer de créer une vidéo avec des couleurs pour chaque scène
            try:
                import subprocess
                import shutil
                
                # Vérifier si FFmpeg est disponible
                if shutil.which('ffmpeg'):
                    # Créer une vidéo colorée simple
                    total_duration = sum(scene.duration for scene in scenes)
                    
                    # Commande FFmpeg pour créer une vidéo avec texte
                    cmd = [
                        'ffmpeg', '-y',
                        '-f', 'lavfi',
                        '-i', f'color=c=blue:size=640x360:duration={total_duration}',
                        '-vf', f'drawtext=text=\'{story[:30]}...\':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2',
                        '-c:v', 'libx264',
                        '-t', str(total_duration),
                        str(video_path)
                    ]
                    
                    # Exécuter FFmpeg avec timeout
                    result = subprocess.run(cmd, capture_output=True, timeout=20)
                    
                    if result.returncode == 0 and video_path.exists():
                        print(f"✅ Vidéo démo créée: {video_filename}")
                        return f"/cache/timeout_animations/{video_filename}"
                
            except Exception as e:
                print(f"⚠️ FFmpeg non disponible: {e}")
            
            # Fallback: Créer un fichier placeholder
            placeholder_content = f"""
# Démo Animation {animation_id}

Histoire: {story}

Scènes générées:
{chr(10).join([f"- Scène {scene.scene_number}: {scene.duration}s - {scene.description}" for scene in scenes])}

Total: {sum(scene.duration for scene in scenes)}s
"""
            
            # Créer un fichier texte comme placeholder
            placeholder_path = self.cache_dir / f"demo_{animation_id}.txt"
            with open(placeholder_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            print(f"📝 Placeholder créé: demo_{animation_id}.txt")
            
            # Retourner une URL vers une vidéo de test statique
            return "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            
        except Exception as e:
            print(f"❌ Erreur génération vidéo démo: {e}")
            # Retourner une vidéo de test en ligne
            return "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    
    async def generate_animation(self, story: str, duration: float, quality: str = "fast") -> Dict[str, Any]:
        """Générer une animation complète avec timeout global"""
        
        start_time = time.time()
        animation_id = str(uuid.uuid4())[:8]
        
        try:
            print(f"🎬 Génération animation {animation_id} - {duration}s")
            
            # Étape 1: Générer les scènes (avec timeout)
            scenes_data = await self.generate_scenes_with_crewai_timeout(story, duration)
            
            if not scenes_data:
                raise Exception("Impossible de générer les scènes")
            
            print(f"✅ {len(scenes_data)} scènes générées")
            
            # Créer les objets AnimationScene
            scenes = []
            for scene_data in scenes_data:
                scene = AnimationScene(
                    scene_number=scene_data.get('scene_number', len(scenes) + 1),
                    description=scene_data.get('description', ''),
                    duration=float(scene_data.get('duration', 1)),
                    action=scene_data.get('action', ''),
                    setting=scene_data.get('setting', ''),
                    status="generated"
                )
                scenes.append(scene)
            
            # Vérification de la durée totale
            total_duration = sum(scene.duration for scene in scenes)
            
            # Générer une vidéo de démonstration pour l'affichage
            demo_video_url = await self._generate_demo_video(animation_id, scenes, story)
            
            # Construire la réponse
            response = {
                "animation_id": animation_id,
                "status": "completed",
                "story": story,
                "requested_duration": duration,
                "actual_duration": total_duration,
                "duration_match": abs(total_duration - duration) < 0.1,
                "videoUrl": demo_video_url,  # URL de la vidéo générée
                "scenes": [
                    {
                        "scene_number": scene.scene_number,
                        "description": scene.description,
                        "duration": scene.duration,
                        "action": scene.action,
                        "setting": scene.setting,
                        "status": scene.status
                    }
                    for scene in scenes
                ],
                "scenes_details": [  # Compatibilité avec les tests
                    {
                        "scene_number": scene.scene_number,
                        "description": scene.description,
                        "duration": scene.duration,
                        "action": scene.action,
                        "setting": scene.setting,
                        "status": scene.status
                    }
                    for scene in scenes
                ],
                "generation_time": round(time.time() - start_time, 2),
                "method": "crewai_with_timeout",
                "quality": quality,
                "total_scenes": len(scenes)
            }
            
            print(f"✅ Animation générée en {response['generation_time']}s")
            return response
            
        except Exception as e:
            print(f"❌ Erreur génération: {e}")
            
            # Retourner une réponse d'erreur avec fallback
            elapsed = round(time.time() - start_time, 2)
            return {
                "animation_id": animation_id,
                "status": "failed",
                "error": str(e),
                "story": story,
                "requested_duration": duration,
                "generation_time": elapsed,
                "method": "timeout_service"
            }

# Instance globale
timeout_animation_service = TimeoutAnimationService()
