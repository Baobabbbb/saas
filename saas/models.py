from pydantic import BaseModel
from typing import List

class Dialogue(BaseModel):
    character: str
    text: str

class Scene(BaseModel):
    description: str
    dialogues: List[Dialogue]

class ComicScenario(BaseModel):
    title: str
    scenes: List[Scene]

class ComicRequest(BaseModel):
    style: str
    hero_name: str
    story_type: str
    custom_request: str