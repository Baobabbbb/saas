"""
Service DiffRhythm - Génération de comptines musicales
Utilise l'API GoAPI DiffRhythm pour créer des comptines avec de la musique
"""

import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from config import GOAPI_API_KEY, DIFFRHYTHM_MODEL, DIFFRHYTHM_TASK_TYPE

# Configuration optimisée pour la vitesse des comptines
NURSERY_RHYME_STYLES = {
    "lullaby": {
        "style": "simple lullaby, soft voice, short melody",
        "tempo": "slow",
        "mood": "calm"
    },
    "counting": {
        "style": "simple counting song, clear voice, basic rhythm",
        "tempo": "medium",
        "mood": "educational"
    },
    "animal": {
        "style": "simple animal song, basic sounds, short tune",
        "tempo": "medium",
        "mood": "playful"
    },
    "seasonal": {
        "style": "simple seasonal song, basic melody",
        "tempo": "medium",
        "mood": "festive"
    },
    "educational": {
        "style": "simple educational song, clear voice, basic tune",
        "tempo": "medium",
        "mood": "educational"
    },
    "movement": {
        "style": "simple dance song, basic beat, short duration",
        "tempo": "fast",
        "mood": "energetic"
    },
    "custom": {
        "style": "simple children's song, basic melody, short",
        "tempo": "medium",
        "mood": "joyful"
    }
}

class DiffRhythmService:
    def __init__(self):
        self.api_key = GOAPI_API_KEY
        self.base_url = "https://api.goapi.ai/api/v1/task"
        self.model = DIFFRHYTHM_MODEL
        self.task_type = DIFFRHYTHM_TASK_TYPE
        
    async def generate_musical_nursery_rhyme(
        self, 
        lyrics: str, 
        rhyme_type: str = "custom",
        custom_style: Optional[str] = None,
        fast_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Génère une comptine musicale avec DiffRhythm
        
        Args:
            lyrics: Les paroles de la comptine
            rhyme_type: Type de comptine (lullaby, counting, animal, etc.)
            custom_style: Style personnalisé optionnel
            fast_mode: Mode rapide pour optimiser la vitesse
            
        Returns:
            Dict contenant les informations de la tâche
        """
        try:
            if not self.api_key or self.api_key.startswith("votre_cle"):
                raise ValueError("❌ Clé API GoAPI non configurée")
            
            # Récupérer le style prédéfini ou utiliser le style personnalisé
            style_config = NURSERY_RHYME_STYLES.get(rhyme_type, NURSERY_RHYME_STYLES["custom"])
            base_style = custom_style or style_config["style"]
            
            # Adapter le style selon le mode
            if fast_mode:
                style_prompt = f"{base_style}, short simple song, under 30 seconds, minimal complexity"
            else:
                style_prompt = f"{base_style}, full children's song, up to 60 seconds"
            
            # Préparer le payload pour l'API avec optimisations selon le mode
            payload = {
                "model": self.model,
                "task_type": self.task_type,
                "input": {
                    "lyrics": lyrics[:1000 if fast_mode else 2000],
                    "style_prompt": style_prompt,
                    "style_audio": ""  # Pas d'audio de référence
                },
                "config": {
                    "service_mode": "fast" if fast_mode else "standard",
                    "duration": "short" if fast_mode else "medium",
                    "quality": "fast" if fast_mode else "standard"
                }
            }
            
            # Headers pour l'API
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            }
            
            print(f"🎵 Génération comptine musicale...")
            print(f"   📝 Paroles: {lyrics[:100]}...")
            print(f"   🎨 Style: {style_prompt}")
            
            # Appel à l'API DiffRhythm
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("code") == 200:
                            task_data = result.get("data", {})
                            task_id = task_data.get("task_id")
                            
                            print(f"✅ Tâche créée: {task_id}")
                            print(f"   📊 Statut: {task_data.get('status')}")
                            
                            return {
                                "status": "success",
                                "task_id": task_id,
                                "task_data": task_data,
                                "rhyme_type": rhyme_type,
                                "style_used": style_prompt,
                                "lyrics": lyrics
                            }
                        else:
                            raise Exception(f"Erreur API: {result}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erreur HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ Erreur génération comptine musicale: {e}")
            return {
                "status": "error",
                "error": str(e),
                "rhyme_type": rhyme_type,
                "lyrics": lyrics
            }
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Vérifie le statut d'une tâche DiffRhythm
        
        Args:
            task_id: ID de la tâche à vérifier
            
        Returns:
            Dict contenant les informations de statut
        """
        try:
            if not self.api_key or self.api_key.startswith("votre_cle"):
                raise ValueError("❌ Clé API GoAPI non configurée")
            
            headers = {
                "x-api-key": self.api_key
            }
            
            # URL pour récupérer le statut de la tâche
            status_url = f"https://api.goapi.ai/api/v1/task/{task_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    status_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("code") == 200:
                            task_data = result.get("data", {})
                            task_status = task_data.get("status")
                            
                            # Mapper le statut de GoAPI vers notre format
                            status_mapping = {
                                "pending": "pending",
                                "processing": "processing", 
                                "completed": "completed",
                                "success": "completed",
                                "failed": "failed",
                                "error": "failed"
                            }
                            
                            mapped_status = status_mapping.get(task_status, "pending")
                            
                            response_data = {
                                "status": mapped_status,
                                "task_status": task_status,
                                "task_data": task_data
                            }
                            
                            # Si la tâche est terminée, extraire l'URL audio
                            if task_status in ["completed", "success"]:
                                output = task_data.get("output")
                                if output:
                                    # Extraire l'URL audio depuis la réponse
                                    audio_url = None
                                    if isinstance(output, dict):
                                        audio_url = output.get("audio_url") or output.get("url")
                                    elif isinstance(output, str):
                                        audio_url = output
                                    
                                    if audio_url:
                                        response_data["audio_url"] = audio_url
                                        response_data["audio_path"] = audio_url
                                        response_data["status"] = "completed"
                                        print(f"✅ Audio prêt: {audio_url}")
                            
                            return response_data
                        else:
                            raise Exception(f"Erreur API: {result}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erreur HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ Erreur vérification statut: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def wait_for_completion(
        self, 
        task_id: str, 
        max_wait_time: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Attend la completion d'une tâche DiffRhythm
        
        Args:
            task_id: ID de la tâche
            max_wait_time: Temps d'attente maximal en secondes
            poll_interval: Intervalle de polling en secondes
            
        Returns:
            Dict contenant le résultat final
        """
        start_time = datetime.now()
        
        while True:
            # Vérifier le statut
            status_result = await self.check_task_status(task_id)
            
            if status_result["status"] == "error":
                return status_result
            
            task_status = status_result.get("task_status")
            task_data = status_result.get("task_data", {})
            
            print(f"🔄 Statut tâche {task_id}: {task_status}")
            
            # Si la tâche est terminée
            if task_status in ["completed", "success"]:
                output = task_data.get("output")
                if output:
                    print(f"✅ Comptine musicale générée!")
                    return {
                        "status": "completed",
                        "task_data": task_data,
                        "audio_url": output.get("audio_url") if isinstance(output, dict) else None,
                        "output": output
                    }
            
            # Si la tâche a échoué
            elif task_status in ["failed", "error"]:
                error_info = task_data.get("error", {})
                return {
                    "status": "failed",
                    "error": error_info.get("message", "Génération échouée"),
                    "task_data": task_data
                }
            
            # Vérifier le timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_wait_time:
                return {
                    "status": "timeout",
                    "error": f"Timeout après {max_wait_time} secondes",
                    "task_data": task_data
                }
            
            # Attendre avant le prochain poll
            await asyncio.sleep(poll_interval)

    def format_lyrics_with_timing(self, lyrics: str, estimated_duration: int = 30) -> str:
        """
        Formate les paroles avec des timestamps pour DiffRhythm
        
        Args:
            lyrics: Paroles brutes
            estimated_duration: Durée estimée en secondes
            
        Returns:
            Paroles formatées avec timestamps
        """
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        if not lines:
            return lyrics
        
        # Calculer les intervalles de temps
        time_per_line = estimated_duration / len(lines)
        formatted_lyrics = []
        
        current_time = 0
        for line in lines:
            # Format timestamp [MM:SS.ss]
            minutes = int(current_time // 60)
            seconds = current_time % 60
            timestamp = f"[{minutes:02d}:{seconds:05.2f}]"
            
            formatted_lyrics.append(f"{timestamp} {line}")
            current_time += time_per_line
        
        return '\n'.join(formatted_lyrics)

# Instance globale du service
diffrhythm_service = DiffRhythmService()
