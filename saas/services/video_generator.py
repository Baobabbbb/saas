"""
Service de génération de vidéos avec SD3-Turbo
Utilise l'API Stability AI pour générer les clips vidéo
"""
import os
import json
import asyncio
import aiohttp
import aiofiles
from typing import List, Dict, Any
from pathlib import Path
import time

class VideoGenerator:
    """Générateur de vidéos avec SD3-Turbo"""
    
    def __init__(self, stability_api_key: str, cache_dir: Path):
        self.api_key = stability_api_key
        self.cache_dir = cache_dir
        self.base_url = "https://api.stability.ai/v2alpha/generation/video"
        
        # Créer le dossier pour les vidéos
        self.video_dir = cache_dir / "videos"
        self.video_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration par défaut pour SD3-Turbo
        self.default_config = {
            "width": 1024,
            "height": 576,
            "fps": 24,
            "motion_bucket_id": 40,  # Contrôle l'intensité du mouvement
            "noise_aug_strength": 0.02,  # Réduction du bruit
            "inference_steps": 25  # Nombre d'étapes d'inférence
        }
    
    async def generate_clips(self, video_prompts: List[Dict], animation_id: str) -> List[Dict[str, Any]]:
        """
        Générer tous les clips vidéo pour l'animation
        
        Args:
            video_prompts: Liste des prompts vidéo
            animation_id: ID unique de l'animation
            
        Returns:
            Liste des clips générés avec métadonnées
        """
        print(f"🎥 Génération de {len(video_prompts)} clips vidéo")
        
        clips = []
        total_duration = 0
        
        # Générer les clips un par un pour éviter les limites de rate
        for i, prompt_data in enumerate(video_prompts):
            print(f"  🎬 Clip {i+1}/{len(video_prompts)}")
            
            try:
                clip = await self._generate_single_clip(prompt_data, animation_id, i)
                if clip:
                    clips.append(clip)
                    total_duration += clip.get('duration', 0)
                    print(f"    ✅ Clip {i+1} généré ({clip.get('duration', 0)}s)")
                else:
                    # Créer un clip de fallback
                    fallback_clip = self._create_fallback_clip(prompt_data, animation_id, i)
                    clips.append(fallback_clip)
                    print(f"    📦 Clip {i+1} fallback créé")
                
                # Attendre entre les générations pour respecter les limites
                if i < len(video_prompts) - 1:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"    ❌ Erreur clip {i+1}: {e}")
                fallback_clip = self._create_fallback_clip(prompt_data, animation_id, i)
                clips.append(fallback_clip)
        
        print(f"✅ {len(clips)} clips générés (durée totale: {total_duration}s)")
        return clips
    
    async def _generate_single_clip(self, prompt_data: Dict, animation_id: str, clip_index: int) -> Dict[str, Any]:
        """Générer un seul clip vidéo"""
        
        # Préparer les paramètres
        main_prompt = prompt_data.get('main_prompt', '')
        negative_prompt = prompt_data.get('negative_prompt', '')
        technical_params = prompt_data.get('technical_params', {})
        
        # Configuration pour l'API
        config = {
            **self.default_config,
            **technical_params
        }
        
        # Optimiser le prompt pour SD3-Turbo
        optimized_prompt = self._optimize_prompt_for_api(main_prompt)
        
        # Nom du fichier
        clip_filename = f"{animation_id}_clip_{clip_index:03d}.mp4"
        clip_path = self.video_dir / clip_filename
        
        print(f"    📝 Prompt: {optimized_prompt[:80]}...")
        
        try:
            # Préparer la requête à l'API Stability
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Pour l'instant, nous utilisons un endpoint simulé car l'API SD3-Turbo video
            # n'est pas encore disponible publiquement
            # TODO: Remplacer par l'API réelle quand disponible
            
            # Simulation de génération
            await self._simulate_video_generation(optimized_prompt, clip_path, config)
            
            # Métadonnées du clip
            clip_data = {
                "clip_id": f"{animation_id}_clip_{clip_index:03d}",
                "scene_id": prompt_data.get('scene_id', clip_index + 1),
                "filename": clip_filename,
                "path": str(clip_path),
                "url": f"/static/animations/{clip_filename}",
                "duration": config.get('duration', technical_params.get('duration', 5)),
                "width": config['width'],
                "height": config['height'],
                "fps": config['fps'],
                "prompt": optimized_prompt,
                "negative_prompt": negative_prompt,
                "technical_params": technical_params,
                "generation_config": config,
                "status": "generated",
                "timestamp": time.time()
            }
            
            return clip_data
            
        except Exception as e:
            print(f"    ❌ Erreur génération API: {e}")
            return None
    
    async def _simulate_video_generation(self, prompt: str, output_path: Path, config: Dict):
        """
        Simuler la génération vidéo (à remplacer par l'API réelle)
        """
        # Pour la démo, créer un fichier placeholder
        placeholder_content = f"""# Video Placeholder
Prompt: {prompt}
Config: {json.dumps(config, indent=2)}
Duration: {config.get('duration', 5)}s
Resolution: {config['width']}x{config['height']}
Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Créer un fichier texte temporaire
        text_path = output_path.with_suffix('.txt')
        async with aiofiles.open(text_path, 'w', encoding='utf-8') as f:
            await f.write(placeholder_content)
        
        # Simuler le temps de génération
        await asyncio.sleep(1)
        
        print(f"    🎬 Placeholder créé: {text_path.name}")
    
    def _optimize_prompt_for_api(self, prompt: str) -> str:
        """Optimiser le prompt pour l'API Stability"""
        
        # Mots-clés recommandés pour la génération vidéo
        video_keywords = [
            "smooth animation",
            "high quality",
            "cinematic",
            "fluid motion"
        ]
        
        optimized = prompt
        
        # Ajouter des mots-clés vidéo si nécessaire
        for keyword in video_keywords:
            if keyword not in optimized.lower():
                optimized = f"{optimized}, {keyword}"
        
        # Limiter la longueur pour l'API
        if len(optimized) > 400:
            optimized = optimized[:397] + "..."
        
        return optimized
    
    def _create_fallback_clip(self, prompt_data: Dict, animation_id: str, clip_index: int) -> Dict[str, Any]:
        """Créer un clip de fallback si la génération échoue"""
        
        clip_filename = f"{animation_id}_fallback_{clip_index:03d}.txt"
        clip_path = self.video_dir / clip_filename
        
        # Créer un fichier de fallback
        fallback_content = f"""# Fallback Clip
Scene ID: {prompt_data.get('scene_id', clip_index + 1)}
Prompt: {prompt_data.get('main_prompt', 'No prompt')}
Duration: {prompt_data.get('technical_params', {}).get('duration', 5)}s
Status: Fallback (generation failed)
Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        try:
            with open(clip_path, 'w', encoding='utf-8') as f:
                f.write(fallback_content)
        except Exception as e:
            print(f"    ❌ Erreur création fallback: {e}")
        
        return {
            "clip_id": f"{animation_id}_fallback_{clip_index:03d}",
            "scene_id": prompt_data.get('scene_id', clip_index + 1),
            "filename": clip_filename,
            "path": str(clip_path),
            "url": f"/static/animations/{clip_filename}",
            "duration": prompt_data.get('technical_params', {}).get('duration', 5),
            "width": 1024,
            "height": 576,
            "fps": 24,
            "prompt": prompt_data.get('main_prompt', ''),
            "status": "fallback",
            "is_fallback": True,
            "timestamp": time.time()
        }
    
    async def check_api_status(self) -> Dict[str, Any]:
        """Vérifier le statut de l'API Stability"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Endpoint pour vérifier le statut (à adapter selon l'API)
            status_url = "https://api.stability.ai/v1/user/account"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(status_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "available",
                            "credits": data.get("credits", 0),
                            "api_key_valid": True
                        }
                    else:
                        return {
                            "status": "unavailable",
                            "error": f"HTTP {response.status}",
                            "api_key_valid": False
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "api_key_valid": False
            }
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """Retourner les formats supportés"""
        return {
            "video_formats": ["mp4", "webm"],
            "resolutions": [
                {"width": 1024, "height": 576, "aspect_ratio": "16:9"},
                {"width": 768, "height": 768, "aspect_ratio": "1:1"},
                {"width": 576, "height": 1024, "aspect_ratio": "9:16"}
            ],
            "durations": {
                "min": 1,
                "max": 30,
                "recommended": 5
            },
            "fps_options": [24, 30],
            "motion_levels": ["low", "medium", "high"]
        }
