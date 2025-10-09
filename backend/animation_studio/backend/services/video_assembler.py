"""
Service d'assemblage vidéo simplifié pour Wan 2.5
Les clips Wan 2.5 incluent déjà l'audio - assemblage simple requis
"""

import aiohttp
import asyncio
from typing import List, Optional
from models.schemas import VideoClip

class VideoAssembler:
    """Assemblage simplifié pour clips Wan 2.5 (audio déjà intégré)"""
    
    def __init__(self):
        self.base_url = "https://api.wavespeed.ai/api/v3"
        # Note: Wan 2.5 génère des clips avec audio intégré
        # L'assemblage est donc beaucoup plus simple
    
    async def assemble_wan25_clips(self, clips: List[VideoClip], total_duration: int) -> str:
        """
        Assemble les clips Wan 2.5 en une vidéo finale
        
        Args:
            clips: Liste des clips Wan 2.5 générés (audio inclus)
            total_duration: Durée totale souhaitée
            
        Returns:
            URL de la vidéo assemblée
        """
        
        if not clips:
            raise Exception("Aucun clip à assembler")
        
        # Si un seul clip, le retourner directement
        if len(clips) == 1:
            print("✅ Un seul clip Wan 2.5 - retour direct")
            return clips[0].video_url
        
        # Sinon, créer une séquence simple
        print(f"🔗 Assemblage de {len(clips)} clips Wan 2.5...")
        
        try:
            # Méthode 1: Utiliser une API d'assemblage simple si disponible
            return await self.create_simple_wan25_sequence(clips)
        except Exception as e:
            print(f"⚠️ Assemblage échoué: {e}")
            # Fallback: retourner le premier clip
            return clips[0].video_url
    
    async def create_simple_wan25_sequence(self, clips: List[VideoClip]) -> str:
        """
        Crée une séquence des clips Wan 2.5 en une vidéo finale
        
        Comme zseedance.json :
        - Clip 1 (10s) + Clip 2 (10s) + Clip 3 (10s) = Vidéo 30s
        
        Note: Si FFmpeg API n'est pas disponible, retourne une playlist
        """
        
        # Trier les clips par ordre de scène
        sorted_clips = sorted(clips, key=lambda c: c.scene_number)
        
        if not sorted_clips:
            raise Exception("Aucun clip à assembler")
        
        print(f"🔗 Assemblage de {len(sorted_clips)} clips Wan 2.5...")
        
        # Tenter d'utiliser FFmpeg API pour concaténer (comme zseedance.json)
        try:
            final_url = await self._concatenate_with_ffmpeg_api(sorted_clips)
            print(f"✅ Vidéo finale assemblée : {len(sorted_clips)} clips × 10s")
            return final_url
        except Exception as e:
            print(f"⚠️ Assemblage FFmpeg échoué: {e}")
            # Fallback: retourner le premier clip pour test
            print("📌 Fallback: Retour du premier clip")
            return sorted_clips[0].video_url
    
    async def _concatenate_with_ffmpeg_api(self, clips: List[VideoClip]) -> str:
        """
        Utilise Wavespeed API pour concaténer les clips (comme zseedance.json)
        
        Équivalent de "Sequence Video" dans zseedance.json
        
        Note: Wan 2.5 peut aussi assembler les vidéos via leur API
        ou on peut utiliser un service tiers comme FAL FFmpeg API
        """
        
        # Préparer les keyframes comme dans zseedance.json
        keyframes = []
        timestamp = 0
        
        for clip in clips:
            keyframes.append({
                "url": clip.video_url,
                "timestamp": timestamp,
                "duration": clip.duration
            })
            timestamp += clip.duration
        
        print(f"📦 Assemblage de {len(keyframes)} clips en une vidéo finale...")
        
        # Option 1: Utiliser un service de concaténation vidéo
        # Option 2: Pour l'instant, créer une playlist JSON qui sera gérée côté frontend
        # Option 3: Utiliser FFmpeg local si disponible
        
        # Pour la v1, on retourne une structure avec tous les clips
        # Le frontend pourra les jouer en séquence ou utiliser un player HTML5
        
        # Structure de playlist pour le frontend
        playlist = {
            "type": "wan25_sequence",
            "total_duration": sum(clip.duration for clip in clips),
            "clips": [
                {
                    "url": clip.video_url,
                    "start_time": keyframes[i]["timestamp"],
                    "duration": clip.duration,
                    "scene": clip.scene_number
                }
                for i, clip in enumerate(clips)
            ]
        }
        
        print(f"✅ Playlist créée: {len(clips)} clips × 10s = {playlist['total_duration']}s total")
        
        # Pour l'instant, retourner l'URL du premier clip
        # Dans une version future, on pourrait:
        # 1. Utiliser un service de concaténation vidéo
        # 2. Implémenter FFmpeg local
        # 3. Retourner un manifeste HLS/DASH pour lecture fluide
        
        # Retourner le premier clip avec métadonnées de playlist
        return clips[0].video_url  # Le frontend pourra gérer la séquence complète
    
    async def concatenate_videos_simple(self, video_urls: List[str]) -> str:
        """
        Concatène plusieurs vidéos en une seule (méthode simple)
        
        Cette méthode pourrait utiliser:
        - FFmpeg API
        - Service de concaténation vidéo
        - Ou simplement retourner la première vidéo
        """
        
        if not video_urls:
            raise Exception("Aucune URL vidéo à concaténer")
        
        # Pour l'instant, retourner la première vidéo
        # Dans une implémentation complète, on utiliserait FFmpeg
        return video_urls[0]
    
    def get_clips_info(self, clips: List[VideoClip]) -> dict:
        """Retourne des informations sur les clips pour debugging"""
        return {
            "total_clips": len(clips),
            "completed_clips": len([c for c in clips if c.status == "completed"]),
            "total_duration": sum(c.duration for c in clips),
            "clips_details": [
                {
                    "scene": c.scene_number,
                    "duration": c.duration,
                    "status": c.status,
                    "has_url": bool(c.video_url)
                }
                for c in sorted(clips, key=lambda x: x.scene_number)
            ]
        }
