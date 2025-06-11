import asyncio
import aiohttp
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
import logging
import sys
sys.path.append('..')
from schemas.animation import AnimationRequest, AnimationResponse, AnimationStatus, AnimationStatusResponse

logger = logging.getLogger(__name__)

class Veo3Service:
    def __init__(self):
        self.api_key = os.getenv("VEO3_API_KEY")
        self.base_url = os.getenv("VEO3_BASE_URL", "https://api.veo3.ai/v1")
        self.session = None
        self.animations_storage: Dict[str, Dict] = {}

    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    def _create_optimized_prompt(self, style: str, theme: str, orientation: str, custom_prompt: str = "") -> str:
        style_prompts = {
            "cartoon": "vibrant cartoon animation style, colorful and playful, Disney-Pixar inspired",
            "fairy_tale": "magical fairy tale animation, enchanted atmosphere with sparkles and soft lighting",
            "anime": "anime animation style, expressive characters, Japanese animation inspired",
            "realistic": "semi-realistic animation style, detailed but child-friendly",
            "paper_craft": "paper craft stop-motion animation style, layered paper cutout effect",
            "watercolor": "watercolor animation style, soft painted textures, artistic brush strokes"
        }

        theme_prompts = {
            "adventure": "exciting adventure scene with exploration and discovery",
            "magic": "magical scene with sparkles, spell effects, and wonder",
            "animals": "cute animals in their natural habitat, friendly and endearing",
            "friendship": "heartwarming scene showing friendship and companionship",
            "space": "space adventure with stars, planets, and cosmic elements",
            "underwater": "underwater scene with marine life and coral reefs",
            "forest": "enchanted forest with magical creatures and nature",
            "superhero": "child-friendly superhero adventure with positive themes"
        }

        orientation_prompts = {
            "landscape": "horizontal composition, wide cinematic view, 16:9 aspect ratio",
            "portrait": "vertical composition, mobile-friendly format, 9:16 aspect ratio"
        }

        base_prompt = f"{style_prompts.get(style, 'cartoon animation style')}, {theme_prompts.get(theme, 'adventure scene')}, {orientation_prompts.get(orientation, 'horizontal composition')}"
        
        if custom_prompt.strip():
            base_prompt += f", {custom_prompt.strip()}"

        base_prompt += ", suitable for children, bright colors, positive atmosphere, high quality animation"
        
        return base_prompt

    async def generate_animation(self, request: AnimationRequest) -> AnimationResponse:
        try:
            animation_id = str(uuid.uuid4())
            
            optimized_prompt = self._create_optimized_prompt(
                request.style, 
                request.theme, 
                request.orientation,
                request.prompt
            )

            aspect_ratio = "16:9" if request.orientation == "landscape" else "9:16"

            veo3_payload = {
                "prompt": optimized_prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": "720p",
                "fps": 24,
                "style": request.style,
                "seed": None
            }

            if self.api_key:
                session = await self._get_session()
                async with session.post(
                    f"{self.base_url}/generate",
                    json=veo3_payload,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status == 200:
                        veo3_response = await response.json()
                        job_id = veo3_response.get("job_id")
                    else:
                        raise Exception(f"Erreur API Veo3: {response.status}")
            else:
                job_id = f"veo3_job_{animation_id}"

            animation_response = AnimationResponse(
                id=animation_id,
                title=request.title,
                description=request.description,
                style=request.style,
                theme=request.theme,
                orientation=request.orientation,
                status=AnimationStatus.PROCESSING,
                created_at=datetime.now()
            )

            self.animations_storage[animation_id] = {
                "response": animation_response,
                "job_id": job_id,
                "veo3_payload": veo3_payload
            }

            asyncio.create_task(self._monitor_animation_job(animation_id, job_id))

            return animation_response

        except Exception as e:
            logger.error(f"Erreur lors de la génération d'animation: {str(e)}")
            return AnimationResponse(
                id=str(uuid.uuid4()),
                title=request.title,
                description=request.description,
                style=request.style,
                theme=request.theme,
                orientation=request.orientation,
                status=AnimationStatus.FAILED,
                error_message=str(e),
                created_at=datetime.now()
            )

    async def _monitor_animation_job(self, animation_id: str, job_id: str):
        try:
            max_attempts = 60
            attempt = 0
            
            while attempt < max_attempts:
                await asyncio.sleep(10)
                
                status_response = await self._check_veo3_job_status(job_id)
                
                if status_response.status == AnimationStatus.COMPLETED:
                    if animation_id in self.animations_storage:
                        stored_animation = self.animations_storage[animation_id]
                        stored_animation["response"].status = AnimationStatus.COMPLETED
                        stored_animation["response"].completed_at = datetime.now()
                        stored_animation["response"].video_url = status_response.video_url
                        stored_animation["response"].thumbnail_url = status_response.thumbnail_url
                    break
                elif status_response.status == AnimationStatus.FAILED:
                    if animation_id in self.animations_storage:
                        stored_animation = self.animations_storage[animation_id]
                        stored_animation["response"].status = AnimationStatus.FAILED
                        stored_animation["response"].error_message = status_response.error_message
                    break
                
                attempt += 1

            if attempt >= max_attempts:
                if animation_id in self.animations_storage:
                    stored_animation = self.animations_storage[animation_id]
                    stored_animation["response"].status = AnimationStatus.FAILED
                    stored_animation["response"].error_message = "Timeout: génération trop longue"

        except Exception as e:
            logger.error(f"Erreur lors du monitoring du job {job_id}: {str(e)}")
            if animation_id in self.animations_storage:
                stored_animation = self.animations_storage[animation_id]
                stored_animation["response"].status = AnimationStatus.FAILED
                stored_animation["response"].error_message = f"Erreur monitoring: {str(e)}"

    async def _check_veo3_job_status(self, job_id: str) -> AnimationStatusResponse:
        if self.api_key:
            try:
                session = await self._get_session()
                async with session.get(
                    f"{self.base_url}/jobs/{job_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return AnimationStatusResponse(
                            status=AnimationStatus(data.get("status", "processing")),
                            progress=data.get("progress"),
                            estimated_time_remaining=data.get("estimated_time_remaining"),
                            video_url=data.get("video_url"),
                            thumbnail_url=data.get("thumbnail_url")
                        )
                    else:
                        return AnimationStatusResponse(
                            status=AnimationStatus.FAILED,
                            error_message=f"Erreur API: {response.status}"
                        )
            except Exception as e:
                return AnimationStatusResponse(
                    status=AnimationStatus.FAILED,
                    error_message=str(e)
                )
        else:
            return AnimationStatusResponse(
                status=AnimationStatus.COMPLETED,
                progress=100,
                video_url="https://example.com/video.mp4",
                thumbnail_url="https://example.com/thumbnail.jpg"
            )

    async def get_animation_status(self, animation_id: str) -> Optional[AnimationStatusResponse]:
        if animation_id in self.animations_storage:
            stored_animation = self.animations_storage[animation_id]
            response = stored_animation["response"]
            
            return AnimationStatusResponse(
                status=response.status,
                progress=100 if response.status == AnimationStatus.COMPLETED else 50,
                error_message=response.error_message
            )
        return None

    async def get_animation(self, animation_id: str) -> Optional[AnimationResponse]:
        if animation_id in self.animations_storage:
            return self.animations_storage[animation_id]["response"]
        return None

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

veo3_service = Veo3Service()
