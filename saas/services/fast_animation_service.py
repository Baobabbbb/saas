"""
Service d'animation rapide sans CrewAI pour les tests
"""
import os
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List

class FastAnimationService:
    """Service d'animation rapide pour les tests"""
    
    def __init__(self):
        self.cache_dir = Path("cache/crewai_animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_complete_animation(self, story: str, style_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Générer une animation rapidement sans CrewAI"""
        
        print(f"⚡ Génération animation rapide: {story[:50]}...")
        
        # Créer un nom de fichier unique
        timestamp = int(time.time())
        output_filename = f"fast_animation_{timestamp}.mp4"
        output_path = self.cache_dir / output_filename
        
        # Rechercher la meilleure vidéo existante à copier
        existing_videos = []
        for video_file in self.cache_dir.glob("*.mp4"):
            if video_file.stat().st_size > 100000:  # Au moins 100KB
                existing_videos.append(video_file)
        
        if existing_videos:
            # Prendre la plus grosse vidéo
            best_video = max(existing_videos, key=lambda x: x.stat().st_size)
            shutil.copy2(best_video, output_path)
            print(f"✅ Vidéo copiée: {best_video.name} -> {output_filename} ({output_path.stat().st_size} bytes)")
        else:
            # Créer une vidéo mock minimale
            self._create_minimal_video(output_path)
        
        # Générer des scènes factices rapidement avec durée exacte
        target_duration = int(style_preferences.get('duration', 30))
        scenes_count = 3 if target_duration <= 15 else 4
        
        # Répartition intelligente de la durée
        if target_duration <= 12:
            # Répartition égale pour courtes durées
            base_duration = target_duration // scenes_count
            remainder = target_duration % scenes_count
            durations = [base_duration + (1 if i < remainder else 0) for i in range(scenes_count)]
        else:
            # Répartition proportionnelle pour durées plus longues
            if scenes_count == 3:
                durations = [
                    round(target_duration * 0.3),
                    round(target_duration * 0.4), 
                    target_duration - round(target_duration * 0.3) - round(target_duration * 0.4)
                ]
            else:  # 4 scènes
                durations = [
                    round(target_duration * 0.25),
                    round(target_duration * 0.30),
                    round(target_duration * 0.30),
                    target_duration - round(target_duration * 0.25) - round(target_duration * 0.30) - round(target_duration * 0.30)
                ]
        
        scenes_details = []
        for i in range(scenes_count):
            scenes_details.append({
                "scene_number": i + 1,
                "description": f"Scène {i + 1} du conte: {story[:30]}...",
                "duration": durations[i],
                "action": f"Action magique {i + 1}",
                "setting": "Décor enchanteur",
                "status": "generated",
                "prompt": f"Scene {i + 1}: {story[:50]}... style {style_preferences.get('style', 'cartoon')}",
                "seed": f"seed_fast_{i + 1}"
            })
        
        # Vérification de la durée totale
        actual_total = sum(scene['duration'] for scene in scenes_details)
        print(f"⚡ Service rapide: {scenes_count} scènes, {actual_total}s total (demandé: {target_duration}s)")
        
        # Résultat rapide
        result = {
            "status": "success",
            "video_path": str(output_path),
            "video_url": f"/cache/crewai_animations/{output_filename}",
            "scenes_count": scenes_count,
            "total_duration": actual_total,  # Utiliser la durée réellement calculée
            "generation_time": 2.0,  # Très rapide
            "pipeline_type": "fast_service",
            "scenes_details": scenes_details,
            "crew_results": {
                "scenario": {"total_scenes": scenes_count, "story_analysis": f"Version rapide de: {story}"},
                "art_direction": {"visual_style": {"global_style": f"Style {style_preferences.get('style', 'cartoon')} rapide"}},
                "prompts": {"video_prompts": [{"scene_number": i+1, "prompt": f"Fast scene {i+1}", "duration": durations[i]} for i in range(scenes_count)]}
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "story_input": story,
            "style_preferences": style_preferences
        }
        
        print(f"✅ Animation rapide générée en 2s: {output_filename}")
        return result
    
    def _create_minimal_video(self, output_path: Path):
        """Créer une vidéo minimale si aucune vidéo existante"""
        
        # Créer un fichier MP4 minimal mais valide
        mp4_data = bytearray([
            # ftyp box
            0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
            0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
            0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
            0x61, 0x76, 0x63, 0x31, 0x6D, 0x70, 0x34, 0x31,
        ])
        
        # Ajouter des données pour avoir une taille raisonnable
        for i in range(5000):  # 5KB de données
            mp4_data.append(i % 256)
        
        with open(output_path, 'wb') as f:
            f.write(mp4_data)
        
        print(f"✅ Vidéo minimale créée: {output_path} ({output_path.stat().st_size} bytes)")

# Instance globale
fast_animation_service = FastAnimationService()
