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

class AnimationOrientation(str, Enum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"

class AnimationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnimationRequest(BaseModel):
    style: AnimationStyle
    theme: AnimationTheme
    duration: int
    orientation: AnimationOrientation = AnimationOrientation.LANDSCAPE
    prompt: Optional[str] = ""
    title: Optional[str] = "Mon Dessin Animé"
    description: Optional[str] = "Dessin animé créé avec CrewAI"

    @validator('duration')
    def validate_duration(cls, v):
        if v < 5 or v > 20:
            raise ValueError('La durée doit être entre 5 et 20 secondes')
        return v

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
    duration: int
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

class AnimationListResponse(BaseModel):
    animations: List[AnimationResponse]
    total: int
    page: int
    limit: int
    total_pages: int
