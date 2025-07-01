from pydantic import BaseModel
from typing import List, Optional

# === MODÈLES POUR LES COMPTINES MUSICALES ===

class MusicalRhymeRequest(BaseModel):
    """Requête pour générer une comptine musicale"""
    rhyme_type: str  # lullaby, counting, animal, seasonal, educational, movement, custom
    custom_request: Optional[str] = None  # Demande personnalisée
    generate_music: Optional[bool] = True  # Générer la musique ou seulement les paroles
    custom_style: Optional[str] = None  # Style musical personnalisé
    language: Optional[str] = "fr"  # Langue (français par défaut)

class RhymeTaskStatusRequest(BaseModel):
    """Requête pour vérifier le statut d'une tâche de comptine"""
    task_id: str

class MusicalRhymeResponse(BaseModel):
    """Réponse pour une comptine musicale"""
    status: str
    title: Optional[str] = None
    lyrics: Optional[str] = None
    rhyme_type: Optional[str] = None
    has_music: Optional[bool] = False
    music_status: Optional[str] = None  # pending, completed, failed
    music_task_id: Optional[str] = None
    audio_url: Optional[str] = None
    style_used: Optional[str] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None
