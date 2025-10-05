"""
Service Suno AI - Génération de comptines musicales avec Suno API
Utilise l'API Suno officielle pour créer des comptines avec musique de haute qualité
Documentation: https://docs.sunoapi.org/suno-api/generate-music
"""

import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from config import SUNO_API_KEY, SUNO_BASE_URL

# Configuration optimisée pour les comptines enfant avec Suno
NURSERY_RHYME_STYLES = {
    "lullaby": {
        "style": "gentle French lullaby, soft children's melody, clear French female voice, articulated pronunciation, soothing, calming",
        "tempo": "slow",
        "mood": "calm",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "aggressive, loud, fast, rock, metal, scary"
    },
    "counting": {
        "style": "educational French children's song, clear French singing voice, pedagogical rhythm, articulated French pronunciation, playful, fun",
        "tempo": "medium",
        "mood": "educational",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "complex, adult, serious, slow"
    },
    "animal": {
        "style": "playful French children's song with animal sounds, happy French voice, clear articulation, fun, energetic, joyful",
        "tempo": "medium",
        "mood": "playful",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "sad, slow, serious, adult"
    },
    "seasonal": {
        "style": "festive French children's song, joyful French melody, clear French pronunciation, celebratory, cheerful",
        "tempo": "medium",
        "mood": "festive",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "sad, dark, slow, serious"
    },
    "educational": {
        "style": "educational French children's song, clear French voice, learning melody, articulated pronunciation, pedagogical, fun",
        "tempo": "medium",
        "mood": "educational",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "complex, fast, aggressive, adult"
    },
    "movement": {
        "style": "energetic French children's dance song, upbeat rhythm, clear French pronunciation, dynamic, fun, active",
        "tempo": "fast",
        "mood": "energetic",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "slow, calm, sad, quiet"
    },
    "custom": {
        "style": "French children's song, happy voice, simple melody, clear pronunciation, joyful, fun",
        "tempo": "medium",
        "mood": "joyful",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "adult, complex, serious, sad"
    }
}

class SunoService:
    def __init__(self):
        self.api_key = SUNO_API_KEY
        self.base_url = SUNO_BASE_URL or "https://api.sunoapi.org/api/v1"
        
        if not self.api_key or self.api_key.startswith("your_suno") or self.api_key == "None":
            print("⚠️ ATTENTION: Clé API Suno non configurée correctement")
            print(f"   SUNO_API_KEY actuel: {self.api_key}")
            print(f"   SUNO_BASE_URL actuel: {self.base_url}")
            print("   ❌ Veuillez configurer SUNO_API_KEY dans les variables d'environnement Railway")
        else:
            print(f"✅ Service Suno initialisé avec succès")
            print(f"   Base URL: {self.base_url}")
        
    async def generate_musical_nursery_rhyme(
        self, 
        lyrics: str, 
        rhyme_type: str = "custom",
        custom_style: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une comptine musicale avec Suno AI
        
        Args:
            lyrics: Les paroles de la comptine (utilisées comme prompt en mode custom)
            rhyme_type: Type de comptine (lullaby, counting, animal, etc.)
            custom_style: Style musical personnalisé optionnel
            title: Titre de la comptine
            
        Returns:
            Dict contenant les informations de la tâche
        """
        try:
            if not self.api_key or self.api_key.startswith("your_suno"):
                raise ValueError("❌ Clé API Suno non configurée. Veuillez configurer SUNO_API_KEY dans le fichier .env")

            # Récupérer le style prédéfini ou utiliser le style personnalisé
            style_config = NURSERY_RHYME_STYLES.get(rhyme_type, NURSERY_RHYME_STYLES["custom"])
            base_style = custom_style or style_config["style"]
            
            # Préparer le titre
            if not title:
                title = f"Comptine {rhyme_type.capitalize()}"
            
            # Limiter la longueur selon les specs de l'API
            # V4_5 supporte jusqu'à 5000 caractères pour le prompt
            lyrics_truncated = lyrics[:5000] if len(lyrics) > 5000 else lyrics
            style_truncated = base_style[:1000] if len(base_style) > 1000 else base_style
            title_truncated = title[:80] if len(title) > 80 else title
            
            # Préparer le payload pour l'API Suno
            # Documentation: https://docs.sunoapi.org/suno-api/generate-music
            payload = {
                "prompt": lyrics_truncated,  # Les paroles de la comptine
                "style": style_truncated,  # Le style musical
                "title": title_truncated,  # Le titre
                "customMode": True,  # Mode custom pour contrôler les paroles
                "instrumental": style_config["instrumental"],  # False pour avoir des paroles
                "model": style_config["model"],  # V4_5 pour meilleure qualité
                "vocalGender": style_config["vocal_gender"],  # Voix féminine
                "negativeTags": style_config.get("negative_tags", ""),  # Styles à éviter
                "styleWeight": 0.7,  # Poids du style (0.7 = bon équilibre)
                "weirdnessConstraint": 0.3,  # Contrainte de créativité (0.3 = pas trop bizarre)
                "audioWeight": 0.6  # Poids de l'influence audio
            }
            
            print(f"🎵 Génération Suno lancée:")
            print(f"   - Titre: {title_truncated}")
            print(f"   - Style: {style_config['mood']}")
            print(f"   - Modèle: {style_config['model']}")
            print(f"   - Paroles: {len(lyrics_truncated)} caractères")
            
            # Faire la requête à l'API Suno
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            
                            if data.get("code") == 200:
                                task_id = data["data"]["taskId"]
                                
                                print(f"✅ Tâche Suno créée avec succès: {task_id}")
                                
                                return {
                                    "status": "success",
                                    "task_id": task_id,
                                    "message": "Génération musicale lancée avec Suno AI",
                                    "style_used": base_style,
                                    "model_used": style_config["model"],
                                    "service": "suno"
                                }
                            else:
                                error_msg = data.get("msg", "Erreur inconnue de l'API Suno")
                                print(f"❌ Erreur API Suno (code {data.get('code')}): {error_msg}")
                                return {
                                    "status": "error",
                                    "error": f"Erreur API Suno: {error_msg}",
                                    "code": data.get("code")
                                }
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur parsing JSON: {e}")
                            print(f"   Réponse brute: {response_text[:500]}")
                            return {
                                "status": "error",
                                "error": f"Erreur parsing réponse: {str(e)}"
                            }
                    else:
                        print(f"❌ Erreur HTTP {response.status}")
                        print(f"   Réponse: {response_text[:500]}")
                        return {
                            "status": "error",
                            "error": f"Erreur HTTP {response.status}: {response_text[:200]}"
                        }
            
        except asyncio.TimeoutError:
            print("❌ Timeout lors de la requête à l'API Suno")
            return {
                "status": "error",
                "error": "Timeout lors de la requête à l'API Suno (30s)"
            }
        except Exception as e:
            print(f"❌ Erreur génération musicale Suno: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Vérifie le statut d'une tâche Suno
        Documentation: https://docs.sunoapi.org/suno-api/generate-music
        
        Args:
            task_id: ID de la tâche
            
        Returns:
            Dict contenant le statut et les URLs si terminé
        """
        try:
            if not self.api_key or self.api_key.startswith("your_suno"):
                raise ValueError("❌ Clé API Suno non configurée")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/get/{task_id}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            
                            if data.get("code") == 200:
                                task_data = data.get("data", {})
                                
                                # L'API Suno retourne une liste de clips (généralement 2)
                                clips = task_data if isinstance(task_data, list) else [task_data]
                                
                                # Analyser le statut de tous les clips
                                all_completed = all(clip.get("status") == "completed" for clip in clips if clip)
                                any_failed = any(clip.get("status") == "error" for clip in clips if clip)
                                
                                if all_completed and len(clips) > 0:
                                    # Tous les clips sont terminés
                                    songs = []
                                    for clip in clips:
                                        if clip and clip.get("status") == "completed":
                                            songs.append({
                                                "id": clip.get("id"),
                                                "title": clip.get("title", "Comptine"),
                                                "audio_url": clip.get("audio_url"),
                                                "video_url": clip.get("video_url"),
                                                "image_url": clip.get("image_url") or clip.get("image_large_url"),
                                                "duration": clip.get("duration"),
                                                "model_name": clip.get("model_name"),
                                                "tags": clip.get("tags", ""),
                                                "prompt": clip.get("prompt", "")
                                            })
                                    
                                    return {
                                        "status": "completed",
                                        "task_id": task_id,
                                        "songs": songs,
                                        "total_songs": len(songs),
                                        "message": f"✅ {len(songs)} chanson(s) générée(s) avec succès"
                                    }
                                elif any_failed:
                                    # Au moins un clip a échoué
                                    error_messages = [
                                        clip.get("error_message", "Erreur inconnue") 
                                        for clip in clips 
                                        if clip and clip.get("status") == "error"
                                    ]
                                    return {
                                        "status": "failed",
                                        "task_id": task_id,
                                        "error": "; ".join(error_messages),
                                        "message": "❌ La génération a échoué"
                                    }
                                else:
                                    # Génération en cours
                                    # Calculer la progression moyenne
                                    total_progress = sum(
                                        clip.get("progress", 0) 
                                        for clip in clips 
                                        if clip
                                    )
                                    avg_progress = total_progress / len(clips) if clips else 0
                                    
                                    return {
                                        "status": "processing",
                                        "task_id": task_id,
                                        "progress": int(avg_progress),
                                        "clips_count": len(clips),
                                        "message": f"🔄 Génération en cours... ({int(avg_progress)}%)"
                                    }
                            else:
                                error_msg = data.get("msg", "Erreur inconnue")
                                return {
                                    "status": "error",
                                    "error": f"Erreur API Suno: {error_msg}",
                                    "code": data.get("code")
                                }
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur parsing JSON status: {e}")
                            print(f"   Réponse brute: {response_text[:500]}")
                            return {
                                "status": "error",
                                "error": f"Erreur parsing réponse: {str(e)}"
                            }
                    else:
                        print(f"❌ Erreur HTTP {response.status} lors de la vérification")
                        return {
                            "status": "error",
                            "error": f"Erreur HTTP {response.status}: {response_text[:200]}"
                        }
                        
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "error": "Timeout lors de la vérification du statut"
            }
        except Exception as e:
            print(f"❌ Erreur vérification statut Suno: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

# Instance globale du service
suno_service = SunoService()
