"""
Service Udio - Génération de comptines musicales
Utilise l'API GoAPI Udio pour créer des comptines avec de la musique réaliste
"""

import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from config import GOAPI_API_KEY, UDIO_MODEL, UDIO_TASK_TYPE

# Configuration optimisée pour les comptines enfant avec Udio
NURSERY_RHYME_STYLES = {
    "lullaby": {
        "style": "gentle French lullaby, clear French female voice, soft children's melody, articulated pronunciation",
        "tempo": "slow",
        "mood": "calm"
    },
    "counting": {
        "style": "educational French children's song, clear French singing voice, pedagogical rhythm, articulated French pronunciation",
        "tempo": "medium",
        "mood": "educational"
    },
    "animal": {
        "style": "playful French children's song with animal sounds, happy French voice, clear articulation",
        "tempo": "medium",
        "mood": "playful"
    },
    "seasonal": {
        "style": "festive French children's song, joyful French melody, clear French pronunciation",
        "tempo": "medium",
        "mood": "festive"
    },
    "educational": {
        "style": "educational French children's song, clear French voice, learning melody, articulated pronunciation",
        "tempo": "medium",
        "mood": "educational"
    },
    "movement": {
        "style": "energetic French children's dance song, upbeat rhythm, clear French pronunciation",
        "tempo": "fast",
        "mood": "energetic"
    },
    "custom": {
        "style": "French children's song, happy voice, simple melody",
        "tempo": "medium",
        "mood": "joyful"
    }
}

class UdioService:
    def __init__(self):
        self.api_key = GOAPI_API_KEY
        self.base_url = "https://api.goapi.ai/api/v1/task"
        self.model = UDIO_MODEL
        self.task_type = UDIO_TASK_TYPE
        
    async def generate_musical_nursery_rhyme(
        self, 
        lyrics: str, 
        rhyme_type: str = "custom",
        custom_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une comptine musicale avec Udio
        
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
            base_style = custom_style or style_config["style"]
            
            # Style description pour Udio - français clair et compréhensible
            gpt_description_prompt = f"{base_style}, comptine française pour enfants, voix féminine française native, prononciation française impeccable, accent français parisien standard, diction claire et articulée, chanteuse française professionnelle, paroles françaises bien articulées"
            
            # Préparer le payload pour l'API Udio
            payload = {
                "model": self.model,
                "task_type": self.task_type,
                "input": {
                    "lyrics": self.format_lyrics_for_udio(lyrics)[:1000],  # Formatage optimisé pour le français
                    "gpt_description_prompt": gpt_description_prompt,
                    "negative_tags": "adult content, explicit, violent, english lyrics, unclear voice",
                    "lyrics_type": "user",  # Nous fournissons les paroles
                    "seed": -1  # Aléatoire
                },
                "config": {
                    "service_mode": "public"
                }
            }
            
            # Headers pour l'API
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            }
            
            print(f"🎵 Génération comptine musicale avec Udio...")
            print(f"   📝 Paroles: {lyrics[:100]}...")
            print(f"   🎨 Style: {gpt_description_prompt}")
            
            # Appel à l'API Udio
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("code") == 200:
                            task_data = result.get("data", {})
                            task_id = task_data.get("task_id")
                            
                            print(f"✅ Tâche Udio créée: {task_id}")
                            print(f"   📊 Statut: {task_data.get('status')}")
                            
                            return {
                                "status": "success",
                                "task_id": task_id,
                                "task_data": task_data,
                                "rhyme_type": rhyme_type,
                                "style_used": gpt_description_prompt,
                                "lyrics": lyrics
                            }
                        else:
                            raise Exception(f"Erreur API Udio: {result}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erreur HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ Erreur génération comptine musicale Udio: {e}")
            return {
                "status": "error",
                "error": str(e),
                "rhyme_type": rhyme_type,
                "lyrics": lyrics
            }
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Vérifie le statut d'une tâche Udio
        
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
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("code") == 200:
                            task_data = result.get("data", {})
                            task_status = task_data.get("status")
                            
                            # Mapper le statut de GoAPI vers notre format
                            status_mapping = {
                                "pending": "pending",
                                "starting": "processing",
                                "processing": "processing", 
                                "success": "completed",
                                "completed": "completed",
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
                                # Pour Udio, chercher dans task_result puis output
                                output = task_data.get("output", {})
                                
                                print(f"🔍 DEBUG Udio - Output structure: {json.dumps(output, indent=2) if output else 'None'}")
                                
                                audio_url = None
                                
                                # Udio retourne les chansons dans output.songs[]
                                if output and "songs" in output:
                                    songs = output["songs"]
                                    if songs and len(songs) > 0:
                                        # Prendre la première chanson
                                        first_song = songs[0]
                                        audio_url = first_song.get("song_path")
                                        print(f"🔍 DEBUG Udio - Première chanson: {first_song.get('title')}")
                                        print(f"🔍 DEBUG Udio - URL audio: {audio_url}")
                                
                                # Fallback sur d'autres formats possibles
                                if not audio_url and output:
                                    audio_url = (
                                        output.get("audio_url") or 
                                        output.get("url") or 
                                        output.get("music_url") or
                                        output.get("song_url") or
                                        output.get("file_url")
                                    )
                                
                                # Legacy fallback
                                if not audio_url:
                                    legacy_output = task_data.get("task_result", {}).get("task_output", {})
                                    if legacy_output:
                                        audio_url = (
                                            legacy_output.get("audio_url") or 
                                            legacy_output.get("url") or
                                            legacy_output.get("music_url")
                                        )
                                
                                print(f"🔍 DEBUG Udio - URL audio extraite: {audio_url}")
                                
                                if audio_url:
                                    response_data["audio_url"] = audio_url
                                    response_data["audio_path"] = audio_url
                                    response_data["audio_generated"] = True
                                    response_data["status"] = "completed"
                                    print(f"✅ Comptine Udio prête: {audio_url}")
                                else:
                                    print(f"⚠️ Aucune URL audio Udio trouvée")
                                    print(f"   Task data complet: {json.dumps(task_data, indent=2)}")
                                    response_data["status"] = "completed"
                                    response_data["audio_generated"] = False
                                    response_data["warning"] = "Audio généré mais URL introuvable"
                            
                            return response_data
                        else:
                            raise Exception(f"Erreur API Udio: {result}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erreur HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ Erreur vérification statut Udio: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def wait_for_completion(
        self, 
        task_id: str, 
        max_wait_time: int = None,  # Pas de limite
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Attend la completion d'une tâche Udio
        
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
            
            print(f"🔄 Statut tâche Udio {task_id}: {task_status}")
            
            # Si la tâche est terminée
            if task_status in ["completed", "success"]:
                audio_url = status_result.get("audio_url")
                if audio_url:
                    print(f"✅ Comptine musicale Udio générée!")
                    return {
                        "status": "completed",
                        "task_data": task_data,
                        "audio_url": audio_url,
                        "audio_path": audio_url,
                        "audio_generated": True
                    }
                else:
                    print(f"⚠️ Udio terminé mais pas d'URL audio")
                    return {
                        "status": "completed",
                        "task_data": task_data,
                        "audio_generated": False,
                        "warning": "Pas d'URL audio dans la réponse"
                    }
            
            # Si la tâche a échoué
            elif task_status in ["failed", "error"]:
                task_result = task_data.get("task_result", {})
                error_messages = task_result.get("error_messages", [])
                error_msg = ", ".join(error_messages) if error_messages else "Génération Udio échouée"
                
                return {
                    "status": "failed",
                    "error": error_msg,
                    "task_data": task_data
                }
            
            # Vérifier le timeout seulement si max_wait_time est défini
            if max_wait_time:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > max_wait_time:
                    return {
                        "status": "timeout",
                        "error": f"Timeout après {max_wait_time} secondes",
                        "task_data": task_data
                    }
            
            # Attendre avant le prochain poll (Udio prend plus de temps)
            await asyncio.sleep(poll_interval)

    def format_lyrics_for_udio(self, lyrics: str) -> str:
        """
        Formate les paroles pour Udio avec optimisation pour la prononciation française
        Udio préfère des paroles structurées avec [Verse], [Chorus], etc.
        
        Args:
            lyrics: Paroles brutes
            
        Returns:
            Paroles formatées pour Udio avec indications de prononciation
        """
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        if not lines:
            return lyrics
        
        # Si les paroles sont courtes (comptine), les formater simplement
        if len(lines) <= 6:
            # Ajouter des indications pour une meilleure prononciation française
            formatted_lyrics = f"[Verse - French pronunciation, clear articulation]\n" + '\n'.join(lines)
        else:
            # Pour des paroles plus longues, essayer de structurer
            middle = len(lines) // 2
            verse1 = '\n'.join(lines[:middle])
            verse2 = '\n'.join(lines[middle:])
            formatted_lyrics = f"[Verse - French pronunciation, clear articulation]\n{verse1}\n\n[Verse 2 - French pronunciation, clear articulation]\n{verse2}"
        
        return formatted_lyrics

# Instance globale du service
udio_service = UdioService()
