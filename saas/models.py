from pydantic import BaseModel
from typing import List, Optional

class Dialogue(BaseModel):
    character: str
    text: str

class Scene(BaseModel):
    description: str
    dialogues: List[Dialogue]

class ComicScenario(BaseModel):
    title: str
    scenes: List[Scene]
    seed: Optional[int] = None  # ← Nouveau champ pour la cohérence des images

class ComicRequest(BaseModel):
    style: str
    hero_name: str
    story_type: str
    custom_request: str
