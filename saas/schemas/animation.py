# Animation models for CrewAI integration
from pydantic import BaseModel, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

class AnimationStyle(str, Enum):
    CARTOON = "cartoon"
    FAIRY_TALE = "fairy_tale"
    ANIME = "anime"
    REALISTIC = "realistic"
    PAPER_CRAFT = "paper_craft"
    WATERCOLOR = "watercolor"

class AnimationOrientation(str, Enum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"

class AnimationTheme(str, Enum):
    ADVENTURE = "adventure"
    MAGIC = "magic"
    ANIMALS = "animals"
    FRIENDSHIP = "friendship"
    SPACE = "space"
    UNDERWATER = "underwater"
    FOREST = "forest"
    SUPERHERO = "superhero"
    CUSTOM = "custom"

class AnimationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnimationRequest(BaseModel):
    style: AnimationStyle
    theme: AnimationTheme
    orientation: AnimationOrientation
    prompt: Optional[str] = ""
    title: Optional[str] = "Mon Dessin Animé"
    description: Optional[str] = "Dessin animé créé avec CrewAI"

    @validator('prompt')
    def validate_prompt(cls, v):
        if v and len(v) > 500:
            raise ValueError('La description ne peut pas dépasser 500 caractères')
        return v

class AnimationResponse(BaseModel):
    id: str
    title: str
    description: str
    style: AnimationStyle
    theme: AnimationTheme
    orientation: AnimationOrientation
    status: AnimationStatus
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class AnimationStatusResponse(BaseModel):
    status: AnimationStatus
    progress: Optional[int] = None  # Pourcentage de progression
    estimated_time_remaining: Optional[int] = None  # Secondes restantes
    error_message: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class AnimationListResponse(BaseModel):
    animations: List[AnimationResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# SEEDANCE specific schemas
class SeedanceTheme(str, Enum):
    SPACE = "space"
    NATURE = "nature"
    ANIMALS = "animals"
    FRIENDSHIP = "friendship"
    EDUCATION = "education"
    ADVENTURE = "adventure"
    MAGIC = "magic"
    OCEAN = "ocean"
    FOREST = "forest"
    MUSIC = "music"

class SeedanceAgeTarget(str, Enum):
    TODDLER = "2-3 ans"
    PRESCHOOL = "3-5 ans"
    KINDERGARTEN = "5-7 ans"
    PRIMARY = "7-10 ans"

class SeedanceRequest(BaseModel):
    theme: SeedanceTheme
    story_title: str  # Titre de l'histoire sélectionnée
    age_target: Optional[SeedanceAgeTarget] = None  # Optionnel, déduit de l'histoire
    duration: int = 45  # Durée en secondes
    style: str = "cartoon"
    
    @validator('duration')
    def validate_duration(cls, v):
        if v < 30 or v > 180:
            raise ValueError('La durée doit être entre 30 et 180 secondes')
        return v

class SeedanceResponse(BaseModel):
    status: str
    animation_id: str
    video_url: Optional[str] = None
    video_path: Optional[str] = None
    total_duration: int
    actual_duration: int
    scenes_count: int
    generation_time: float
    pipeline_type: str
    scenes: List[dict] = []
    metadata: dict = {}
