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

# Configuration par défaut pour les comptines
NURSERY_RHYME_STYLES = {
    "lullaby": {
        "style": "gentle lullaby, soft and soothing, quiet vocals, peaceful melody",
        "tempo": "slow",
        "mood": "calm and peaceful"
    },
    "counting": {
        "style": "upbeat children's song, clear vocals, educational and fun",
        "tempo": "medium",
        "mood": "cheerful and educational"
    },
    "animal": {
        "style": "playful children's song with animal sounds, bouncy rhythm",
        "tempo": "medium-fast",
        "mood": "playful and fun"
    },
    "seasonal": {
        "style": "festive children's song, warm and joyful melody",
        "tempo": "medium",
        "mood": "festive and warm"
    },
    "educational": {
        "style": "educational children's song, clear pronunciation, memorable tune",
        "tempo": "medium",
        "mood": "educational and engaging"
    },
    "movement": {
        "style": "energetic children's song with dance rhythm, upbeat and active",
        "tempo": "fast",
        "mood": "energetic and active"
    },
    "custom": {
        "style": "children's song with simple melody, clear vocals",
        "tempo": "medium",
        "mood": "joyful and child-friendly"
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
        custom_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une comptine musicale avec DiffRhythm
        
        Args:
            lyrics: Les paroles de la comptine
            rhyme_type: Type de comptine (lullaby, counting, animal, etc.)
            custom_style: Style personnalisé optionnel
            
        Returns:
            Dict contenant les informations de la tâche
        """
        try:
            if not self.api_key or self.api_key.startswith("votre_cle"):
                raise ValueError("❌ Clé API GoAPI non configurée")
            
            # Récupérer le style prédéfini ou utiliser le style personnalisé
            style_config = NURSERY_RHYME_STYLES.get(rhyme_type, NURSERY_RHYME_STYLES["custom"])
            style_prompt = custom_style or style_config["style"]
            
            # Préparer le payload pour l'API
            payload = {
                "model": self.model,
                "task_type": self.task_type,
                "input": {
                    "lyrics": lyrics[:10000],  # Limite de 10000 caractères
                    "style_prompt": style_prompt,
                    "style_audio": ""  # Pas d'audio de référence
                },
                "config": {
                    "service_mode": ""
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
                            status = task_data.get("status")
                            
                            return {
                                "status": "success",
                                "task_status": status,
                                "task_data": task_data
                            }
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
