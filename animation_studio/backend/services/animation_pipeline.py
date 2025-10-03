import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from config import config
from models.schemas import (
    AnimationRequest, AnimationResult, AnimationProgress, AnimationStatus,
    StoryIdea, Scene, VideoClip, AudioTrack, AnimationTheme
)
from .idea_generator import IdeaGenerator
from .scene_creator import SceneCreator
from .wan25_generator import Wan25Generator
from .video_assembler import VideoAssembler

class AnimationPipeline:
    """
    Pipeline 100% Wan 2.5 pour génération de dessins animés
    Basé sur zseedance.json mais adapté pour Wan 2.5 (Alibaba)
    Audio intégré automatiquement - pas besoin de génération séparée
    """
    
    def __init__(self):
        self.idea_generator = IdeaGenerator()
        self.scene_creator = SceneCreator()
        self.wan25_generator = Wan25Generator()  # Remplace VideoGenerator
        self.video_assembler = VideoAssembler()
        # Plus besoin d'AudioGenerator - audio intégré dans Wan 2.5
        
        # Cache pour suivre les animations en cours
        self.active_animations: Dict[str, AnimationResult] = {}
        
        print("🎬 Pipeline Wan 2.5 initialisé (audio intégré)")
    
    async def generate_animation(
        self,
        request: AnimationRequest,
        progress_callback: Optional[Callable[[AnimationProgress], None]] = None,
        forced_animation_id: Optional[str] = None,
    ) -> AnimationResult:
        """
        Génère un dessin animé complet avec Wan 2.5
        
        Workflow inspiré de zseedance.json mais adapté:
        1. Ideas AI Agent (OpenAI) → Génération idée
        2. Prompts AI Agent (OpenAI) → Création scènes cohérentes
        3. Wan 2.5 Generation → Clips vidéo avec audio intégré
        4. Video Assembly → Assemblage final simple
        
        Note: Pas besoin d'audio séparé - Wan 2.5 l'intègre automatiquement
        """
        
        # Initialiser le résultat
        animation_id = forced_animation_id or str(uuid.uuid4())
        start_time = time.time()
        
        result = AnimationResult(
            animation_id=animation_id,
            status=AnimationStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        self.active_animations[animation_id] = result
        
        try:
            # Étape 1: Génération d'idée (équivalent "Ideas AI Agent" dans n8n)
            await self._update_progress(animation_id, AnimationStatus.GENERATING_IDEA, 10, 
                                      "Génération de l'idée d'histoire...", progress_callback)
            
            story_idea = await self.idea_generator.generate_story_idea(request.theme, request.duration)
            
            # Valider l'idée pour les enfants
            if not await self.idea_generator.validate_idea(story_idea):
                raise Exception("L'idée générée n'est pas appropriée pour les enfants")
            
            result.story_idea = story_idea
            
            # Étape 2: Création des scènes (équivalent "Prompts AI Agent" dans n8n)
            await self._update_progress(animation_id, AnimationStatus.CREATING_SCENES, 25,
                                      "Création des scènes détaillées...", progress_callback)
            
            scenes = await self.scene_creator.create_scenes_from_idea(story_idea, request.duration)
            result.scenes = scenes
            
            # Étape 3: Génération des clips Wan 2.5 avec audio intégré
            await self._update_progress(animation_id, AnimationStatus.GENERATING_CLIPS, 40,
                                      f"Génération de {len(scenes)} clips Wan 2.5 avec audio intégré...", 
                                      progress_callback)
            
            # Générer tous les clips avec Wan 2.5 (audio inclus automatiquement)
            video_clips = await self.wan25_generator.generate_all_clips(scenes)
            result.video_clips = video_clips
            
            # Vérifier qu'au moins un clip a été généré avec succès
            valid_clips = [clip for clip in video_clips if clip.status == "completed"]
            if not valid_clips:
                # Agréger les erreurs pour diagnostic
                failed_details = "; ".join(
                    [f"scene {c.scene_number}: {c.status}" for c in video_clips if c.status and c.status.startswith("failed")]
                ) or "aucun détail"
                hints = "Vérifiez WAVESPEED_API_KEY et la connexion à l'API Wan 2.5"
                result.error_message = f"Aucun clip Wan 2.5 n'a pu être généré ({failed_details}). {hints}"
                raise Exception(result.error_message)
            
            print(f"✅ {len(valid_clips)}/{len(scenes)} clips Wan 2.5 générés avec succès (audio inclus)")
            
            # Note: Pas d'étape audio séparée - Wan 2.5 l'intègre automatiquement
            
            # Étape 4: Assemblage final simplifié (clips Wan 2.5 déjà complets avec audio)
            await self._update_progress(animation_id, AnimationStatus.ASSEMBLING_VIDEO, 85,
                                      "Assemblage de la vidéo finale...", progress_callback)
            
            try:
                # Assemblage simple - clips Wan 2.5 ont déjà l'audio intégré
                final_video_url = await self.video_assembler.assemble_wan25_clips(
                    valid_clips, request.duration
                )
            except Exception as e:
                # Fallback: créer une séquence simple des clips
                print(f"Échec assemblage complet, essai séquence simple: {e}")
                final_video_url = await self.video_assembler.create_simple_wan25_sequence(valid_clips)
            
            if not final_video_url:
                # Dernière solution: retourner le premier clip valide
                print("⚠️ Assemblage impossible, retour du premier clip")
                final_video_url = next((clip.video_url for clip in valid_clips), "")
            
            result.final_video_url = final_video_url
            result.audio_track = None  # Pas d'audio séparé avec Wan 2.5
            
            # Finalisation
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.status = AnimationStatus.COMPLETED
            
            await self._update_progress(animation_id, AnimationStatus.COMPLETED, 100,
                                      "Animation terminée!", progress_callback)
            
            return result
            
        except Exception as e:
            # Gestion d'erreur
            result.status = AnimationStatus.FAILED
            result.error_message = str(e)
            
            await self._update_progress(animation_id, AnimationStatus.FAILED, 0,
                                      f"Erreur: {str(e)}", progress_callback)
            
            return result
        
        finally:
            # Nettoyer le cache
            if animation_id in self.active_animations:
                self.active_animations[animation_id] = result

    async def start_generation_async(
        self,
        request: AnimationRequest,
        progress_callback: Optional[Callable[[AnimationProgress], None]] = None
    ) -> str:
        """Crée un job PENDING et démarre la génération en tâche de fond.
        Retourne immédiatement l'animation_id à utiliser pour le polling.
        """
        animation_id = str(uuid.uuid4())
        result_placeholder = AnimationResult(
            animation_id=animation_id,
            status=AnimationStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        self.active_animations[animation_id] = result_placeholder

        async def run_job():
            try:
                # Lancer la génération complète en imposant le même id
                final_result = await self.generate_animation(request, progress_callback, forced_animation_id=animation_id)
                self.active_animations[animation_id] = final_result
            except Exception as e:
                failed = self.active_animations.get(animation_id, result_placeholder)
                failed.status = AnimationStatus.FAILED
                failed.error_message = str(e)
                self.active_animations[animation_id] = failed

        # Planifier sans attendre
        asyncio.create_task(run_job())

        return animation_id

    async def _update_progress(
        self, 
        animation_id: str, 
        status: AnimationStatus, 
        percentage: int,
        current_step: str,
        callback: Optional[Callable[[AnimationProgress], None]] = None
    ):
        """Met à jour la progression et appelle le callback si fourni"""
        
        progress = AnimationProgress(
            animation_id=animation_id,
            status=status,
            progress_percentage=percentage,
            current_step=current_step
        )
        
        # Estimer le temps restant
        if status != AnimationStatus.COMPLETED and status != AnimationStatus.FAILED:
            estimated_total_time = self.estimate_total_generation_time()
            remaining_time = int(estimated_total_time * (100 - percentage) / 100)
            progress.estimated_remaining_time = remaining_time
        
        if callback:
            callback(progress)

    def get_animation_status(self, animation_id: str) -> Optional[AnimationResult]:
        """Récupère le statut d'une animation en cours"""
        return self.active_animations.get(animation_id)

    def estimate_total_generation_time(self) -> int:
        """
        Estime le temps total de génération en secondes (Wan 2.5)
        
        Wan 2.5 est plus rapide que Seedance et inclut l'audio
        """
        
        idea_time = 30          # Génération d'idée: 30s
        scenes_time = 45        # Création scènes: 45s
        video_time = 240        # Génération Wan 2.5: 4 minutes (plus rapide que Seedance)
        # Plus d'audio séparé - intégré dans Wan 2.5
        assembly_time = 60      # Assemblage simple: 1 minute
        
        return idea_time + scenes_time + video_time + assembly_time  # ~6 minutes total

    async def validate_pipeline_health(self) -> Dict[str, Any]:
        """Valide que tous les services du pipeline sont opérationnels"""
        
        health_check = {
            "pipeline_operational": True,
            "services": {},
            "estimated_generation_time": self.estimate_total_generation_time()
        }
        
        # Tester OpenAI (génération idées)
        try:
            if config.OPENAI_API_KEY and config.OPENAI_API_KEY.startswith("sk-"):
                health_check["services"]["idea_generator"] = {"status": "configured", "model": config.TEXT_MODEL}
            else:
                raise ValueError("Clé OpenAI invalide ou manquante")
        except Exception as e:
            health_check["services"]["idea_generator"] = {"status": "failed", "error": str(e)}
            health_check["pipeline_operational"] = False
        
        # Tester Wan 2.5 (génération vidéo avec audio intégré)
        try:
            if config.WAVESPEED_API_KEY:
                health_check["services"]["wan25_generator"] = {
                    "status": "configured",
                    "model": config.WAN25_MODEL,
                    "max_duration": config.WAN25_MAX_DURATION,
                    "resolution": config.WAN25_DEFAULT_RESOLUTION,
                    "audio_integrated": True
                }
            else:
                raise ValueError("Clé Wavespeed manquante")
        except Exception as e:
            health_check["services"]["wan25_generator"] = {"status": "failed", "error": str(e)}
            health_check["pipeline_operational"] = False
        
        # Tester Video Assembler (assemblage simple pour Wan 2.5)
        health_check["services"]["video_assembler"] = {
            "status": "ready",
            "type": "wan25_simple_assembly",
            "note": "Assemblage simplifié - audio déjà intégré dans clips Wan 2.5"
        }
        
        return health_check

    def get_supported_themes(self) -> Dict[str, Dict[str, str]]:
        """Retourne les thèmes supportés avec leurs descriptions"""
        return self.idea_generator.get_theme_prompts()

    def cleanup_old_animations(self, max_age_hours: int = 24):
        """Nettoie les anciennes animations du cache"""
        current_time = time.time()
        
        to_remove = []
        for animation_id, result in self.active_animations.items():
            creation_time = datetime.fromisoformat(result.created_at).timestamp()
            if current_time - creation_time > (max_age_hours * 3600):
                to_remove.append(animation_id)
        
        for animation_id in to_remove:
            del self.active_animations[animation_id] 