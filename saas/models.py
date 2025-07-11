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

# === MODÈLES POUR LES BANDES DESSINÉES ===

class ComicRequest(BaseModel):
    """Requête pour générer une bande dessinée"""
    theme: str  # adventure, animals, space, magic, friendship, etc.
    story_length: Optional[str] = "short"  # short, medium, long (4-6, 8-10, 12-16 pages)
    art_style: Optional[str] = "cartoon"  # cartoon, realistic, manga, comics, watercolor
    target_age: Optional[str] = "6-12"  # 3-6, 6-12, 12+
    custom_request: Optional[str] = None  # Demande personnalisée
    characters: Optional[List[str]] = None  # Personnages principaux
    setting: Optional[str] = None  # Lieu de l'action
    
class ComicPage(BaseModel):
    """Modèle pour une page de bande dessinée"""
    page_number: int
    image_url: str
    description: str
    dialogues: List[dict]  # [{"character": "nom", "text": "dialogue", "bubble_type": "normal"}]
    panels: Optional[List[dict]] = None  # Informations sur les cases
    
class ComicResponse(BaseModel):
    """Réponse pour une bande dessinée générée"""
    status: str
    comic_id: str
    title: str
    pages: List[ComicPage]
    total_pages: int
    theme: str
    art_style: str
    generation_time: Optional[float] = None
    comic_metadata: Optional[dict] = None
    error: Optional[str] = None
