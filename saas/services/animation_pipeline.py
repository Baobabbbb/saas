"""
Pipeline complète de génération de dessins animés
Transforme une histoire en vidéo animée cohérente
"""
import os
import json
import time
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class AnimationPipeline:
    """Pipeline principal pour la génération de dessins animés"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.cache_dir = Path("cache/animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration par défaut
        self.min_duration = 30  # 30 secondes minimum
        self.max_duration = 300  # 5 minutes maximum
        self.scene_min_duration = 5  # 5 secondes minimum par scène
        self.scene_max_duration = 15  # 15 secondes maximum par scène
        
        print(f"🎬 Pipeline Animation initialisée")
        print(f"   📁 Cache: {self.cache_dir}")
        print(f"   ⏱️ Durée: {self.min_duration}s - {self.max_duration}s")
    
    async def generate_animation(self, story: str, target_duration: int = 60, style_hint: str = "cartoon") -> Dict[str, Any]:
        """
        Pipeline complète de génération d'animation
        
        Args:
            story: Histoire à transformer en animation
            target_duration: Durée cible en secondes (30-300)
            style_hint: Style visuel souhaité
            
        Returns:
            Dictionnaire avec le résultat de l'animation
        """
        animation_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        print(f"🎬 === DÉBUT PIPELINE ANIMATION {animation_id} ===")
        print(f"📖 Histoire: {story[:100]}...")
        print(f"⏱️ Durée cible: {target_duration}s")
        print(f"🎨 Style: {style_hint}")
        
        try:
            # Étape 1: Analyse et découpage de l'histoire
            print(f"\n📝 ÉTAPE 1: Analyse et découpage")
            scenes = await self._analyze_and_segment_story(story, target_duration)
            print(f"✅ {len(scenes)} scènes générées")
            
            # Étape 2: Définition du style graphique
            print(f"\n🎨 ÉTAPE 2: Définition du style")
            visual_style = await self._define_visual_style(story, style_hint)
            print(f"✅ Style défini: {visual_style.get('name', 'Unknown')}")
            
            # Étape 3: Génération des prompts vidéo
            print(f"\n🎯 ÉTAPE 3: Génération des prompts")
            video_prompts = await self._generate_video_prompts(scenes, visual_style)
            print(f"✅ {len(video_prompts)} prompts générés")
            
            # Étape 4: Génération des vidéos
            print(f"\n🎥 ÉTAPE 4: Génération des vidéos")
            video_clips = await self._generate_video_clips(video_prompts, animation_id)
            print(f"✅ {len(video_clips)} clips générés")
            
            # Étape 5: Assemblage final
            print(f"\n🎞️ ÉTAPE 5: Assemblage final")
            final_video = await self._assemble_final_video(video_clips, animation_id)
            print(f"✅ Vidéo finale assemblée")
            
            # Calcul du temps total
            total_time = time.time() - start_time
            actual_duration = sum(clip.get('duration', 0) for clip in video_clips)
            
            # Résultat final
            result = {
                "status": "success",
                "animation_id": animation_id,
                "videoUrl": final_video['url'],
                "video_url": final_video['url'],
                "story": story,
                "target_duration": target_duration,
                "actual_duration": actual_duration,
                "scenes": scenes,
                "scenes_details": scenes,
                "video_clips": video_clips,
                "visual_style": visual_style,
                "generation_time": round(total_time, 2),
                "pipeline_type": "custom_animation",
                "quality": "sd3_turbo",
                "total_scenes": len(scenes),
                "note": f"🎬 Animation générée avec pipeline personnalisé"
            }
            
            print(f"\n🎉 === PIPELINE TERMINÉ ===")
            print(f"⏱️ Temps total: {total_time:.1f}s")
            print(f"🎬 Durée vidéo: {actual_duration}s")
            print(f"📊 Scènes: {len(scenes)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur dans le pipeline: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "failed",
                "animation_id": animation_id,
                "error": str(e),
                "story": story,
                "generation_time": round(time.time() - start_time, 2),
                "pipeline_type": "custom_animation"
            }
    
    async def _analyze_and_segment_story(self, story: str, target_duration: int) -> List[Dict[str, Any]]:
        """
        Étape 1: Analyser et découper l'histoire en scènes
        """
        from services.story_analyzer import StoryAnalyzer
        analyzer = StoryAnalyzer(self.openai_api_key)
        return await analyzer.segment_story(story, target_duration, self.scene_min_duration, self.scene_max_duration)
    
    async def _define_visual_style(self, story: str, style_hint: str) -> Dict[str, Any]:
        """
        Étape 2: Définir le style visuel cohérent
        """
        from services.visual_style_generator import VisualStyleGenerator
        style_generator = VisualStyleGenerator(self.openai_api_key)
        return await style_generator.generate_visual_style(story, style_hint)
    
    async def _generate_video_prompts(self, scenes: List[Dict], visual_style: Dict) -> List[Dict[str, Any]]:
        """
        Étape 3: Générer des prompts vidéo détaillés
        """
        from services.video_prompt_generator import VideoPromptGenerator
        prompt_generator = VideoPromptGenerator(self.openai_api_key)
        return await prompt_generator.generate_prompts(scenes, visual_style)
    
    async def _generate_video_clips(self, video_prompts: List[Dict], animation_id: str) -> List[Dict[str, Any]]:
        """
        Étape 4: Générer les clips vidéo avec SD3-Turbo
        """
        from services.video_generator import VideoGenerator
        video_generator = VideoGenerator(self.stability_api_key, self.cache_dir)
        return await video_generator.generate_clips(video_prompts, animation_id)
    
    async def _assemble_final_video(self, video_clips: List[Dict], animation_id: str) -> Dict[str, Any]:
        """
        Étape 5: Assembler la vidéo finale
        """
        from services.video_assembler import VideoAssembler
        assembler = VideoAssembler(self.cache_dir)
        return await assembler.assemble_video(video_clips, animation_id)

# Instance globale
animation_pipeline = AnimationPipeline()
