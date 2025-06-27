"""
Service d'assemblage de vidéos finales
Assemble les clips individuels en une vidéo cohérente
"""
import os
import json
import asyncio
import subprocess
from typing import List, Dict, Any
from pathlib import Path
import time

class VideoAssembler:
    """Assembleur de vidéos pour créer l'animation finale"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.output_dir = cache_dir / "final_videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration par défaut
        self.default_fps = 24
        self.default_resolution = (1024, 576)
        self.transition_duration = 0.5  # Durée des transitions en secondes
    
    async def assemble_video(self, video_clips: List[Dict], animation_id: str) -> Dict[str, Any]:
        """
        Assembler tous les clips en une vidéo finale
        
        Args:
            video_clips: Liste des clips générés
            animation_id: ID unique de l'animation
            
        Returns:
            Informations sur la vidéo finale
        """
        print(f"🎞️ Assemblage de {len(video_clips)} clips")
        
        # Nom de la vidéo finale
        final_filename = f"{animation_id}_final.mp4"
        final_path = self.output_dir / final_filename
        
        try:
            # Méthode 1: Assemblage simple (concatenation)
            result = await self._simple_concatenation(video_clips, final_path, animation_id)
            
            if result["status"] == "success":
                print(f"✅ Vidéo finale assemblée: {final_filename}")
                return result
            else:
                # Fallback: créer un fichier de métadonnées
                return await self._create_metadata_file(video_clips, final_path, animation_id)
                
        except Exception as e:
            print(f"❌ Erreur assemblage: {e}")
            return await self._create_metadata_file(video_clips, final_path, animation_id)
    
    async def _simple_concatenation(self, clips: List[Dict], output_path: Path, animation_id: str) -> Dict[str, Any]:
        """Assemblage simple par concaténation"""
        
        # Calculer la durée totale
        total_duration = sum(clip.get('duration', 5) for clip in clips)
        
        # Pour la démo, créer un script de montage textuel
        # En production, ceci utiliserait FFmpeg ou une bibliothèque de montage vidéo
        
        montage_script = self._generate_montage_script(clips, animation_id)
        script_path = output_path.with_suffix('.montage.txt')
        
        # Écrire le script de montage
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(montage_script)
        
        # Simuler l'assemblage (en production, ici on appellerait FFmpeg)
        await self._simulate_video_assembly(clips, output_path)
        
        return {
            "status": "success",
            "filename": output_path.name,
            "path": str(output_path),
            "url": f"/static/animations/{output_path.name}",
            "duration": total_duration,
            "clips_count": len(clips),
            "resolution": self.default_resolution,
            "fps": self.default_fps,
            "montage_script": str(script_path),
            "assembly_method": "simple_concatenation",
            "timestamp": time.time()
        }
    
    def _generate_montage_script(self, clips: List[Dict], animation_id: str) -> str:
        """Générer un script de montage détaillé"""
        
        script_lines = [
            f"# Script de montage pour animation {animation_id}",
            f"# Généré le {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Nombre de clips: {len(clips)}",
            "",
            "# Configuration globale",
            f"resolution: {self.default_resolution[0]}x{self.default_resolution[1]}",
            f"fps: {self.default_fps}",
            f"transition_duration: {self.transition_duration}s",
            "",
            "# Timeline des clips:"
        ]
        
        current_time = 0
        for i, clip in enumerate(clips):
            duration = clip.get('duration', 5)
            script_lines.extend([
                f"",
                f"## Clip {i+1} ({clip.get('clip_id', 'unknown')})",
                f"scene_id: {clip.get('scene_id', i+1)}",
                f"start_time: {current_time}s",
                f"duration: {duration}s",
                f"end_time: {current_time + duration}s",
                f"source_file: {clip.get('filename', 'missing')}",
                f"prompt: {clip.get('prompt', 'No prompt')[:100]}...",
                f"status: {clip.get('status', 'unknown')}"
            ])
            
            # Ajouter transition si pas le dernier clip
            if i < len(clips) - 1:
                script_lines.extend([
                    f"transition: fade ({self.transition_duration}s)",
                    f"transition_start: {current_time + duration - self.transition_duration/2}s"
                ])
            
            current_time += duration
        
        script_lines.extend([
            "",
            f"# Durée totale: {current_time}s",
            "",
            "# Commandes FFmpeg équivalentes:",
            "# (à implémenter en production)",
        ])
        
        # Ajouter des commandes FFmpeg d'exemple
        ffmpeg_cmd = self._generate_ffmpeg_command(clips, "output.mp4")
        script_lines.extend([
            "",
            "# Commande FFmpeg pour assemblage:",
            f"# {ffmpeg_cmd}"
        ])
        
        return "\n".join(script_lines)
    
    def _generate_ffmpeg_command(self, clips: List[Dict], output_file: str) -> str:
        """Générer une commande FFmpeg pour l'assemblage"""
        
        # Commande de base pour concaténer des vidéos
        inputs = []
        filter_parts = []
        
        for i, clip in enumerate(clips):
            filename = clip.get('filename', f'clip_{i}.mp4')
            inputs.append(f"-i {filename}")
            filter_parts.append(f"[{i}:v] [{i}:a]")
        
        input_str = " ".join(inputs)
        filter_str = "".join(filter_parts) + f"concat=n={len(clips)}:v=1:a=1[outv][outa]"
        
        cmd = f"ffmpeg {input_str} -filter_complex \"{filter_str}\" -map \"[outv]\" -map \"[outa]\" -c:v libx264 -c:a aac {output_file}"
        
        return cmd
    
    async def _simulate_video_assembly(self, clips: List[Dict], output_path: Path):
        """Simuler l'assemblage vidéo (remplacer par FFmpeg en production)"""
        
        # Créer un fichier de résumé de l'animation
        summary = {
            "animation_summary": {
                "total_clips": len(clips),
                "total_duration": sum(clip.get('duration', 5) for clip in clips),
                "resolution": f"{self.default_resolution[0]}x{self.default_resolution[1]}",
                "fps": self.default_fps,
                "clips": []
            }
        }
        
        for clip in clips:
            summary["animation_summary"]["clips"].append({
                "clip_id": clip.get('clip_id'),
                "scene_id": clip.get('scene_id'),
                "duration": clip.get('duration', 5),
                "filename": clip.get('filename'),
                "prompt_preview": clip.get('prompt', '')[:100],
                "status": clip.get('status', 'unknown')
            })
        
        # Écrire le fichier de résumé
        summary_content = json.dumps(summary, indent=2, ensure_ascii=False)
        
        # Créer un fichier placeholder pour la vidéo finale
        placeholder_content = f"""# Vidéo Finale Assemblée
Animation ID: {output_path.stem.replace('_final', '')}
Nombre de clips: {len(clips)}
Durée totale: {sum(clip.get('duration', 5) for clip in clips)}s
Résolution: {self.default_resolution[0]}x{self.default_resolution[1]}
FPS: {self.default_fps}
Créé le: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Résumé JSON:
{summary_content}
"""
        
        # Écrire le fichier placeholder
        placeholder_path = output_path.with_suffix('.final.txt')
        with open(placeholder_path, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        
        # Simuler le temps d'assemblage
        await asyncio.sleep(2)
        
        print(f"    🎬 Placeholder vidéo finale créé: {placeholder_path.name}")
    
    async def _create_metadata_file(self, clips: List[Dict], output_path: Path, animation_id: str) -> Dict[str, Any]:
        """Créer un fichier de métadonnées si l'assemblage échoue"""
        
        metadata = {
            "animation_id": animation_id,
            "status": "metadata_only",
            "clips": clips,
            "total_duration": sum(clip.get('duration', 5) for clip in clips),
            "clips_count": len(clips),
            "error": "Video assembly failed, metadata file created instead",
            "timestamp": time.time(),
            "note": "This is a fallback when video assembly is not available"
        }
        
        metadata_path = output_path.with_suffix('.metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "fallback",
            "filename": metadata_path.name,
            "path": str(metadata_path),
            "url": f"/static/animations/{metadata_path.name}",
            "duration": metadata["total_duration"],
            "clips_count": len(clips),
            "assembly_method": "metadata_only",
            "is_fallback": True,
            "timestamp": time.time()
        }
    
    def check_ffmpeg_availability(self) -> bool:
        """Vérifier si FFmpeg est disponible sur le système"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def create_preview_thumbnails(self, clips: List[Dict], animation_id: str) -> List[str]:
        """Créer des thumbnails de prévisualisation pour chaque clip"""
        thumbnails = []
        
        for i, clip in enumerate(clips):
            thumbnail_name = f"{animation_id}_thumb_{i:03d}.jpg"
            thumbnail_path = self.output_dir / thumbnail_name
            
            # Pour la démo, créer un fichier texte de placeholder
            thumb_content = f"""Thumbnail {i+1}
Clip: {clip.get('clip_id', 'unknown')}
Scene: {clip.get('scene_id', i+1)}
Duration: {clip.get('duration', 5)}s
Prompt: {clip.get('prompt', 'No prompt')[:50]}...
"""
            
            thumb_text_path = thumbnail_path.with_suffix('.thumb.txt')
            with open(thumb_text_path, 'w', encoding='utf-8') as f:
                f.write(thumb_content)
            
            thumbnails.append(f"/static/animations/{thumb_text_path.name}")
        
        return thumbnails
    
    def get_assembly_options(self) -> Dict[str, Any]:
        """Retourner les options d'assemblage disponibles"""
        return {
            "methods": [
                "simple_concatenation",
                "fade_transitions",
                "crossfade_transitions",
                "advanced_editing"
            ],
            "transitions": [
                "cut",
                "fade",
                "crossfade",
                "slide",
                "zoom"
            ],
            "output_formats": ["mp4", "webm", "avi"],
            "quality_presets": [
                "web_optimized",
                "high_quality", 
                "mobile_friendly",
                "social_media"
            ],
            "ffmpeg_available": self.check_ffmpeg_availability()
        }
