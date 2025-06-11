# Service Veo3 simplifié pour test
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
import os
from schemas.animation import AnimationRequest, AnimationResponse, AnimationStatus

class Veo3Service:
    def __init__(self):
        self.api_key = os.getenv("VEO3_API_KEY")
        self.animations_storage: Dict[str, Dict] = {}

    def validate_animation_data(self, data: dict) -> dict:
        errors = []
        
        if not data.get('style'):
            errors.append("Le style est requis")
        
        if not data.get('theme'):
            errors.append("Le thème est requis")
            
        if not data.get('orientation'):
            errors.append("L'orientation est requise")
        
        if data.get('theme') == 'custom' and not data.get('prompt', '').strip():
            errors.append("Une description est requise pour un thème personnalisé")
        
        return {
            'isValid': len(errors) == 0,
            'errors': errors
        }

    async def generate_animation(self, request: AnimationRequest) -> AnimationResponse:
        animation_id = str(uuid.uuid4())
        
        animation_response = AnimationResponse(
            id=animation_id,
            title=request.title,
            description=request.description,
            style=request.style,
            theme=request.theme,
            orientation=request.orientation,
            status=AnimationStatus.COMPLETED,
            video_url="https://example.com/video.mp4",
            thumbnail_url="https://example.com/thumbnail.jpg",
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        return animation_response

# Instance globale
veo3_service = Veo3Service()
