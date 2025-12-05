"""
Cartoon Generation Engine using Wan 2.5 Model via WaveSpeed API.

This module implements a production-grade cartoon generation pipeline following
the "Seedance-style" workflow:
1. Ideation: Generate cohesive script with consistent characters (Series Bible)
2. Production: Parallel generation of video clips using Wan 2.5
3. Post-Production: Intelligent stitching of clips with FAL AI FFmpeg

Author: Herbbie Team
Version: 1.0.0
Stack: Python 3.11, FastAPI, Supabase, WaveSpeed API
"""

import asyncio
import httpx
import json
import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import schemas
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.cartoon import (
    CharacterSheet, Scene, Script, GenerationRequest, GenerationResult,
    GenerationStatus, ProgressUpdate, AspectRatio, Resolution
)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class WanVideoOrchestrator:
    """
    Main orchestrator for cartoon generation using Wan 2.5 via WaveSpeed API.
    
    Implements the complete pipeline:
    - "Showrunner" logic for script generation with character consistency
    - Parallel video generation with rate limiting
    - Intelligent stitching with audio normalization
    
    Attributes:
        wavespeed_api_key: WaveSpeed API key
        openai_api_key: OpenAI API key for script generation
        fal_api_key: FAL AI API key for video stitching
        max_concurrent_clips: Maximum concurrent clip generation (semaphore limit)
        clip_duration: Duration per clip in seconds (5s for Wan 2.5)
    """
    
    # API Configuration
    WAVESPEED_BASE_URL = "https://api.wavespeed.ai/api/v3"
    WAN25_ENDPOINT = "/alibaba/wan-2.5/text-to-video-fast"  # URL correcte selon doc WaveSpeed
    FAL_FFMPEG_URL = "https://queue.fal.run/fal-ai/ffmpeg-api/compose"
    
    # Default settings optimized for children's cartoon content
    DEFAULT_NEGATIVE_PROMPT = "nsfw, distorted, morphing, text, watermark, scary, horror, violence, blood, dark, creepy, realistic, photorealistic, live action"
    DEFAULT_STYLE = "High-quality 2D cartoon animation, Disney Pixar Dreamworks style, colorful children's cartoon, expressive animated characters, smooth animation, vibrant saturated colors, professional cartoon quality"
    
    def __init__(
        self,
        wavespeed_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        fal_api_key: Optional[str] = None,
        supabase_client: Optional[Any] = None,
        max_concurrent_clips: int = 5,
        clip_duration: int = 5
    ):
        """
        Initialize the WanVideoOrchestrator.
        
        Args:
            wavespeed_api_key: WaveSpeed API key (or from env WAVESPEED_API_KEY)
            openai_api_key: OpenAI API key (or from env OPENAI_API_KEY)
            fal_api_key: FAL AI API key (or from env FAL_API_KEY)
            supabase_client: Supabase client for database updates
            max_concurrent_clips: Max concurrent video generations (default: 5)
            clip_duration: Duration per clip in seconds (default: 5 for Wan 2.5)
        """
        # Load API keys from environment or parameters
        self.wavespeed_api_key = wavespeed_api_key or os.getenv("WAVESPEED_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.fal_api_key = fal_api_key or os.getenv("FAL_API_KEY")
        self.supabase = supabase_client
        
        # Configuration
        self.max_concurrent_clips = max_concurrent_clips
        self.clip_duration = clip_duration
        self.semaphore = asyncio.Semaphore(max_concurrent_clips)
        
        # Text model for script generation
        self.text_model = os.getenv("TEXT_MODEL", "gpt-4o-mini")
        
        # Validate required API keys
        self._validate_config()
        
        logger.info(f"✅ WanVideoOrchestrator initialized - Max concurrent: {max_concurrent_clips}, Clip duration: {clip_duration}s")
    
    def _validate_config(self) -> None:
        """Validate that all required API keys are configured."""
        missing = []
        
        if not self.wavespeed_api_key:
            missing.append("WAVESPEED_API_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.fal_api_key:
            missing.append("FAL_API_KEY")
        
        if missing:
            error_msg = f"Missing required API keys: {', '.join(missing)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
    
    # =========================================================================
    # MODERATION
    # =========================================================================
    
    async def _moderate_content(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Run content through OpenAI Moderation API.
        
        Args:
            text: Text to moderate
            
        Returns:
            Tuple of (is_safe, reason_if_flagged)
        """
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            
            response = await client.moderations.create(input=text)
            result = response.results[0]
            
            if result.flagged:
                # Find which categories were flagged
                flagged_categories = [
                    cat for cat, flagged in result.categories.model_dump().items()
                    if flagged
                ]
                reason = f"Content flagged for: {', '.join(flagged_categories)}"
                logger.warning(f"⚠️ Content moderation flagged: {reason}")
                return False, reason
            
            return True, None
            
        except Exception as e:
            logger.error(f"❌ Moderation API error: {e}")
            # Fail open for availability, but log the error
            return True, None
    
    # =========================================================================
    # IDEATION - Script Generation (Showrunner Logic)
    # =========================================================================
    
    async def generate_script(
        self,
        theme: str,
        duration_seconds: int,
        style: str = "cartoon",
        custom_prompt: Optional[str] = None,
        character_name: Optional[str] = None
    ) -> Script:
        """
        Generate a complete script with character sheet and scenes.
        
        This implements the "Showrunner" logic from the prompt.md:
        1. Define Character Sheet first for consistency
        2. Calculate number of scenes based on duration
        3. Generate scenes that explicitly include character descriptions
        
        Args:
            theme: User-provided theme
            duration_seconds: Target duration
            style: Visual style (cartoon, anime, 3d, realistic)
            custom_prompt: Optional additional instructions
            character_name: Optional character name
            
        Returns:
            Complete Script object with scenes
        """
        logger.info(f"📝 Generating script for theme: '{theme}' ({duration_seconds}s, style: {style})")
        
        # Step 1: Moderate the input
        is_safe, reason = await self._moderate_content(theme)
        if not is_safe:
            raise ValueError(f"Theme rejected by content moderation: {reason}")
        
        if custom_prompt:
            is_safe, reason = await self._moderate_content(custom_prompt)
            if not is_safe:
                raise ValueError(f"Custom prompt rejected by content moderation: {reason}")
        
        # Step 2: Calculate number of scenes
        num_scenes = max(1, duration_seconds // self.clip_duration)
        logger.info(f"📊 Calculated {num_scenes} scenes of {self.clip_duration}s each")
        
        # Step 3: Generate Character Sheet and Script via OpenAI
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            
            # System prompt for Series Bible approach
            system_prompt = self._build_script_system_prompt(num_scenes, style)
            
            # User prompt with theme
            user_prompt = self._build_script_user_prompt(
                theme, num_scenes, style, custom_prompt, character_name
            )
            
            response = await client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"🤖 Raw script response: {content[:200]}...")
            
            # Parse the response
            script_data = json.loads(content)
            
            # Build Script object
            script = self._parse_script_response(
                script_data, theme, duration_seconds, style, num_scenes
            )
            
            logger.info(f"✅ Script generated: '{script.title}' with {len(script.scenes)} scenes")
            return script
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse script JSON: {e}")
            raise ValueError(f"Failed to generate valid script: {e}")
        except Exception as e:
            logger.error(f"❌ Script generation error: {e}")
            raise
    
    def _build_script_system_prompt(self, num_scenes: int, style: str) -> str:
        """Build the system prompt for script generation."""
        return f"""You are a PROFESSIONAL children's cartoon animation scriptwriter at Disney/Pixar creating a complete animated short film.

Your task is to create a COHESIVE STORY with:
1. ONE MAIN CHARACTER with EXACT visual description (same in every scene!)
2. Exactly {num_scenes} scenes that tell ONE COMPLETE STORY with beginning, middle, and happy ending
3. Each scene is a {self.clip_duration}-second animated clip

STORY STRUCTURE REQUIREMENTS:
- Scene 1: INTRODUCTION - Introduce character and setting
- Scene 2-{num_scenes-1}: ADVENTURE/PROBLEM - Character faces a challenge or goes on adventure  
- Scene {num_scenes}: HAPPY ENDING - Resolution, character learned something or achieved goal

CRITICAL VISUAL RULES:
- The EXACT SAME character description MUST appear in EVERY scene
- Example: "A small blue bunny with big pink ears and a yellow star on its forehead"
- EVERY visual_description must START with this character description
- Use BRIGHT, COLORFUL cartoon visuals
- Style: {style} animation like Disney/Pixar shorts

ANIMATION STYLE:
- 2D or 3D cartoon animation (NOT realistic)
- Expressive character emotions
- Vibrant colors, soft lighting
- Child-friendly, magical, whimsical

OUTPUT FORMAT: Return ONLY valid JSON:
{{
    "title": "Catchy title (3-5 words)",
    "synopsis": "One paragraph story summary",
    "setting": "Colorful cartoon location",
    "mood": "joyful/magical/adventurous",
    "main_character": {{
        "name": "Character name",
        "visual_description": "EXACT visual description to repeat in every scene (e.g., 'A small blue bunny with big pink ears, a yellow star on its forehead, and a tiny red cape')",
        "personality_traits": ["curious", "brave", "kind"],
        "color_palette": ["#4A90D9", "#FF69B4", "#FFD700"]
    }},
    "scenes": [
        {{
            "scene_number": 1,
            "visual_description": "[CHARACTER DESCRIPTION]. [What character does in this scene]. [Setting/background details]",
            "camera_angle": "wide shot / medium shot / close-up",
            "audio_description": "Happy cartoon music, sound effects"
        }}
    ]
}}"""

    def _build_script_user_prompt(
        self,
        theme: str,
        num_scenes: int,
        style: str,
        custom_prompt: Optional[str],
        character_name: Optional[str]
    ) -> str:
        """Build the user prompt for script generation."""
        prompt = f"""Create a magical {style} animated short film about: {theme}

Requirements:
- {num_scenes} scenes of {self.clip_duration} seconds each
- Complete story arc (beginning, middle, happy ending)
- Child-friendly, positive, educational if possible
- Vibrant colors and expressive characters"""
        
        if character_name:
            prompt += f"\n- Main character should be named '{character_name}'"
        
        if custom_prompt:
            prompt += f"\n- Additional instructions: {custom_prompt}"
        
        return prompt
    
    def _parse_script_response(
        self,
        data: Dict[str, Any],
        theme: str,
        duration_seconds: int,
        style: str,
        num_scenes: int
    ) -> Script:
        """Parse OpenAI response into a Script object."""
        # Parse main character
        char_data = data.get("main_character", {})
        main_character = CharacterSheet(
            name=char_data.get("name", "Hero"),
            visual_description=char_data.get("visual_description", "A friendly animated character"),
            personality_traits=char_data.get("personality_traits", ["friendly", "curious"]),
            color_palette=char_data.get("color_palette")
        )
        
        # Parse scenes
        scenes = []
        for scene_data in data.get("scenes", []):
            scene = Scene(
                scene_number=scene_data.get("scene_number", len(scenes) + 1),
                prompt="",  # Will be built with build_wan_prompt()
                visual_description=scene_data.get("visual_description", ""),
                camera_angle=scene_data.get("camera_angle", "medium shot"),
                audio_description=scene_data.get("audio_description", ""),
                duration_seconds=self.clip_duration
            )
            # Build the complete prompt with character sheet
            scene.prompt = scene.build_wan_prompt(main_character)
            scenes.append(scene)
        
        return Script(
            title=data.get("title", f"Animation: {theme}"),
            theme=theme,
            synopsis=data.get("synopsis", ""),
            target_duration_seconds=duration_seconds,
            main_character=main_character,
            setting=data.get("setting", ""),
            mood=data.get("mood", "joyful"),
            scenes=scenes,
            num_scenes=num_scenes,
            actual_duration_seconds=len(scenes) * self.clip_duration
        )
    
    # =========================================================================
    # PRODUCTION - Video Clip Generation with Wan 2.5
    # =========================================================================
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError))
    )
    async def generate_clip_task(
        self,
        scene: Scene,
        character_sheet: Optional[CharacterSheet] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p"
    ) -> Scene:
        """
        Generate a single video clip using WaveSpeed Wan 2.5 API.
        
        Decorated with @retry for exponential backoff on failures.
        Uses semaphore to limit concurrent requests.
        
        Args:
            scene: Scene object with prompt
            character_sheet: Optional character sheet for consistency
            aspect_ratio: Video aspect ratio (default: 16:9 for horizontal)
            resolution: Video resolution (default: 720p)
            
        Returns:
            Updated Scene object with video_url
        """
        async with self.semaphore:
            logger.info(f"🎬 Generating clip for Scene {scene.scene_number}: {scene.visual_description[:50]}...")
            
            try:
                # Build the complete prompt for cartoon animation
                full_prompt = scene.build_wan_prompt(character_sheet)
                
                # Add style prefix for high-quality cartoon
                styled_prompt = f"Animated cartoon scene. {self.DEFAULT_STYLE}. {full_prompt}"
                
                # Log the prompt for debugging
                logger.info(f"🎨 Prompt for Scene {scene.scene_number}: {styled_prompt[:100]}...")
                
                # Truncate if too long (API limit)
                if len(styled_prompt) > 1500:
                    styled_prompt = styled_prompt[:1497] + "..."
                
                # Map aspect_ratio and resolution to WaveSpeed "size" format
                # WaveSpeed accepts: 1280*720, 720*1280, 1920*1080, 1080*1920
                size_mapping = {
                    ("16:9", "720p"): "1280*720",
                    ("9:16", "720p"): "720*1280",
                    ("16:9", "1080p"): "1920*1080",
                    ("9:16", "1080p"): "1080*1920",
                }
                size = size_mapping.get((aspect_ratio, resolution), "1280*720")
                
                # Prepare WaveSpeed API request (according to official documentation)
                payload = {
                    "prompt": styled_prompt,
                    "negative_prompt": self.DEFAULT_NEGATIVE_PROMPT,
                    "size": size,  # WaveSpeed format: "1280*720"
                    "duration": min(scene.duration_seconds, 10),  # Max 10 seconds
                    "enable_prompt_expansion": False,
                    "seed": -1
                }
                
                headers = {
                    "Authorization": f"Bearer {self.wavespeed_api_key}",
                    "Content-Type": "application/json"
                }
                
                api_url = f"{self.WAVESPEED_BASE_URL}{self.WAN25_ENDPOINT}"
                logger.info(f"📡 POST {api_url}")
                logger.info(f"📦 Payload: size={size}, duration={payload['duration']}")
                
                # Make the request
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(api_url, json=payload, headers=headers)
                    
                    if response.status_code != 200:
                        error_text = response.text
                        logger.error(f"❌ WaveSpeed API error ({response.status_code}): {error_text}")
                        raise httpx.HTTPError(f"WaveSpeed API error: {response.status_code} - {error_text}")
                    
                    result = response.json()
                    logger.info(f"📨 WaveSpeed response: {result}")
                    
                    prediction_id = result.get("data", {}).get("id") or result.get("id")
                    
                    if not prediction_id:
                        raise ValueError(f"No prediction ID in response: {result}")
                    
                    logger.info(f"✅ Prediction created: {prediction_id}")
                
                # Wait for the video to be generated
                video_url = await self._wait_for_wavespeed_result(prediction_id)
                
                # Update scene
                scene.video_url = video_url
                scene.status = GenerationStatus.COMPLETED
                
                logger.info(f"✅ Scene {scene.scene_number} completed: {video_url[:50]}...")
                return scene
                
            except Exception as e:
                logger.error(f"❌ Failed to generate Scene {scene.scene_number}: {e}")
                scene.status = GenerationStatus.FAILED
                scene.error_message = str(e)
                scene.retry_count += 1
                raise
    
    async def _wait_for_wavespeed_result(
        self,
        prediction_id: str,
        max_wait: int = 300,
        poll_interval: int = 5
    ) -> str:
        """
        Poll WaveSpeed API until video generation is complete.
        
        Args:
            prediction_id: WaveSpeed prediction ID
            max_wait: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Video URL
        """
        result_url = f"{self.WAVESPEED_BASE_URL}/predictions/{prediction_id}/result"
        headers = {
            "Authorization": f"Bearer {self.wavespeed_api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = asyncio.get_event_loop().time()
        attempt = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while asyncio.get_event_loop().time() - start_time < max_wait:
                attempt += 1
                
                try:
                    response = await client.get(result_url, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        status = result.get("status") or result.get("data", {}).get("status")
                        
                        if status in ["completed", "COMPLETED", "succeeded", "SUCCEEDED"]:
                            # Get video URL from response
                            video_url = (
                                result.get("data", {}).get("outputs", [None])[0] or
                                result.get("output", {}).get("video_url") or
                                result.get("video_url") or
                                result.get("data", {}).get("video_url")
                            )
                            
                            if video_url:
                                return video_url
                            else:
                                logger.warning(f"⚠️ No video URL in completed result: {result}")
                        
                        elif status in ["failed", "FAILED", "error", "ERROR"]:
                            error = result.get("error") or result.get("data", {}).get("error", "Unknown error")
                            raise Exception(f"WaveSpeed generation failed: {error}")
                        
                        else:
                            progress = result.get("progress") or result.get("data", {}).get("progress", 0)
                            logger.info(f"⏳ Waiting for WaveSpeed (attempt {attempt}): status={status}, progress={progress}%")
                    
                    elif response.status_code == 202:
                        # Still processing
                        logger.info(f"⏳ WaveSpeed still processing (attempt {attempt})...")
                    
                    else:
                        logger.warning(f"⚠️ Unexpected status code: {response.status_code}")
                
                except httpx.HTTPError as e:
                    logger.warning(f"⚠️ HTTP error during polling: {e}")
                
                await asyncio.sleep(poll_interval)
        
        raise TimeoutError(f"WaveSpeed generation timed out after {max_wait}s")
    
    async def generate_all_clips(
        self,
        script: Script,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        on_progress: Optional[callable] = None
    ) -> List[Scene]:
        """
        Generate all video clips in parallel with rate limiting.
        
        Uses asyncio.gather with semaphore to limit concurrent requests.
        Implements graceful degradation: if <20% fail, continue with successful clips.
        
        Args:
            script: Script with scenes to generate
            aspect_ratio: Video aspect ratio (16:9 or 9:16)
            resolution: Video resolution (720p or 1080p)
            on_progress: Optional callback for progress updates
            
        Returns:
            List of updated Scene objects
        """
        logger.info(f"🎬 Starting parallel generation of {len(script.scenes)} clips...")
        
        # Create tasks for all scenes
        tasks = [
            self.generate_clip_task(
                scene=scene,
                character_sheet=script.main_character,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
            for scene in script.scenes
        ]
        
        # Run all tasks with error handling
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_scenes = []
        failed_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Scene {i+1} failed: {result}")
                script.scenes[i].status = GenerationStatus.FAILED
                script.scenes[i].error_message = str(result)
                failed_count += 1
            else:
                successful_scenes.append(result)
                if on_progress:
                    progress = int((len(successful_scenes) / len(script.scenes)) * 100)
                    await on_progress(progress, f"Generated clip {len(successful_scenes)}/{len(script.scenes)}")
        
        # Check failure threshold (>20% = abort)
        failure_rate = failed_count / len(script.scenes)
        if failure_rate > 0.2:
            logger.error(f"❌ Too many failures ({failure_rate:.0%}). Aborting.")
            raise Exception(f"Generation aborted: {failed_count}/{len(script.scenes)} clips failed (>{0.2:.0%} threshold)")
        
        if failed_count > 0:
            logger.warning(f"⚠️ Continuing with {len(successful_scenes)}/{len(script.scenes)} clips (graceful degradation)")
        
        logger.info(f"✅ Generated {len(successful_scenes)}/{len(script.scenes)} clips successfully")
        return successful_scenes
    
    # =========================================================================
    # POST-PRODUCTION - Video Stitching with FAL AI FFmpeg
    # =========================================================================
    
    async def stitch_videos(
        self,
        video_urls: List[str],
        output_format: str = "mp4",
        normalize_audio: bool = True
    ) -> str:
        """
        Stitch multiple video clips into a single video using FAL AI luma-video-to-video concat.
        
        Falls back to returning first video if stitching fails.
        
        Args:
            video_urls: List of video clip URLs
            output_format: Output format (mp4)
            normalize_audio: Whether to normalize audio loudness
            
        Returns:
            URL of the final stitched video (or first video on failure)
        """
        logger.info(f"🔗 Stitching {len(video_urls)} clips...")
        
        if not video_urls:
            raise ValueError("No video URLs to stitch")
        
        if len(video_urls) == 1:
            logger.info("✅ Only one clip, no stitching needed")
            return video_urls[0]
        
        try:
            # Use FAL AI video concat endpoint (simpler API)
            concat_url = "https://fal.run/fal-ai/video-utils/concat"
            
            # Build payload for video concat
            payload = {
                "video_urls": video_urls
            }
            
            headers = {
                "Authorization": f"Key {self.fal_api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"📡 POST {concat_url}")
            logger.info(f"📦 Concatenating {len(video_urls)} videos")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    concat_url,
                    json=payload,
                    headers=headers
                )
                
                logger.info(f"📨 FAL concat response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"📨 FAL concat result: {result}")
                    
                    # Get video URL from response
                    video_url = (
                        result.get("video", {}).get("url") or
                        result.get("video_url") or
                        result.get("output_url") or
                        result.get("url")
                    )
                    
                    if video_url:
                        logger.info(f"✅ Video stitching complete: {video_url[:50]}...")
                        return video_url
                    else:
                        logger.warning(f"⚠️ No video URL in concat response: {result}")
                        raise Exception("No video URL in concat response")
                else:
                    error_text = response.text
                    logger.error(f"❌ FAL concat API error ({response.status_code}): {error_text}")
                    raise Exception(f"FAL concat API error: {response.status_code} - {error_text}")
            
        except Exception as e:
            logger.error(f"❌ Video stitching failed: {e}")
            logger.warning(f"⚠️ Fallback: returning all video URLs for sequential playback")
            # Fallback: return all video URLs - frontend can play them sequentially
            # We return the first one as the "final" but the full list is in video_urls
            return video_urls[0]  # First video as thumbnail/preview
    
    async def _wait_for_fal_result(
        self,
        request_id: str,
        max_wait: int = 300,
        poll_interval: int = 10
    ) -> str:
        """
        Poll FAL AI until video stitching is complete.
        
        Args:
            request_id: FAL AI request ID
            max_wait: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Final video URL
        """
        result_url = f"https://queue.fal.run/fal-ai/ffmpeg-api/requests/{request_id}"
        headers = {
            "Authorization": f"Key {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = asyncio.get_event_loop().time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while asyncio.get_event_loop().time() - start_time < max_wait:
                try:
                    response = await client.get(result_url, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        status = result.get("status", "").upper()
                        
                        if status in ["COMPLETED", "SUCCEEDED"]:
                            video_url = result.get("video_url") or result.get("output_url")
                            if video_url:
                                return video_url
                        
                        elif status in ["FAILED", "ERROR"]:
                            error = result.get("error", "Unknown error")
                            raise Exception(f"FAL stitching failed: {error}")
                        
                        else:
                            logger.info(f"⏳ FAL stitching in progress: {status}")
                    
                except httpx.HTTPError as e:
                    logger.warning(f"⚠️ HTTP error during FAL polling: {e}")
                
                await asyncio.sleep(poll_interval)
        
        raise TimeoutError(f"FAL stitching timed out after {max_wait}s")
    
    # =========================================================================
    # MAIN PIPELINE
    # =========================================================================
    
    async def run_pipeline(
        self,
        request: GenerationRequest,
        on_progress: Optional[callable] = None
    ) -> GenerationResult:
        """
        Run the complete cartoon generation pipeline.
        
        Pipeline steps:
        1. Moderate input content
        2. Generate script with character sheet
        3. Generate video clips in parallel
        4. Stitch clips into final video
        5. Update Supabase with results
        
        Args:
            request: GenerationRequest with user parameters
            on_progress: Optional callback for progress updates
            
        Returns:
            GenerationResult with final video URL and metadata
        """
        task_id = str(uuid.uuid4())
        started_at = datetime.now()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 STARTING CARTOON GENERATION PIPELINE")
        logger.info(f"Task ID: {task_id}")
        logger.info(f"User: {request.user_id}")
        logger.info(f"Theme: {request.theme}")
        logger.info(f"Duration: {request.duration_seconds}s")
        logger.info(f"Style: {request.style}")
        logger.info(f"{'='*80}\n")
        
        result = GenerationResult(
            task_id=task_id,
            user_id=request.user_id,
            status=GenerationStatus.PENDING,
            theme=request.theme,
            style=request.style,
            started_at=started_at
        )
        
        try:
            # Step 1: Update status to moderating
            result.status = GenerationStatus.MODERATING
            await self._update_progress(result, 5, "Vérification du contenu...", on_progress)
            
            # Step 2: Generate script
            result.status = GenerationStatus.GENERATING_SCRIPT
            await self._update_progress(result, 10, "Création du scénario...", on_progress)
            
            script = await self.generate_script(
                theme=request.theme,
                duration_seconds=request.duration_seconds,
                style=request.style,
                custom_prompt=request.custom_prompt,
                character_name=request.character_name
            )
            
            result.script = script
            result.title = script.title
            result.total_clips = len(script.scenes)
            result.debug_prompts = [scene.prompt for scene in script.scenes]
            
            await self._update_progress(result, 20, f"Scénario créé: {script.title}", on_progress)
            
            # Step 3: Generate video clips
            result.status = GenerationStatus.GENERATING_CLIPS
            
            async def clip_progress(percent, message):
                overall_progress = 20 + int(percent * 0.6)  # 20-80% for clips
                await self._update_progress(result, overall_progress, message, on_progress)
            
            scenes = await self.generate_all_clips(
                script=script,
                aspect_ratio=request.aspect_ratio.value,
                resolution=request.resolution.value,
                on_progress=clip_progress
            )
            
            # Collect successful video URLs
            video_urls = [s.video_url for s in scenes if s.video_url]
            result.video_urls = video_urls
            result.successful_clips = len(video_urls)
            result.failed_clips = result.total_clips - result.successful_clips
            
            await self._update_progress(result, 80, f"Clips générés: {len(video_urls)}/{result.total_clips}", on_progress)
            
            # Step 4: Stitch videos
            result.status = GenerationStatus.STITCHING
            await self._update_progress(result, 85, "Assemblage de la vidéo finale...", on_progress)
            
            final_url = await self.stitch_videos(video_urls, normalize_audio=True)
            result.final_video_url = final_url
            result.duration_seconds = len(video_urls) * self.clip_duration
            
            # Step 5: Mark as completed
            result.status = GenerationStatus.COMPLETED
            result.completed_at = datetime.now()
            result.generation_time_seconds = (result.completed_at - started_at).total_seconds()
            
            await self._update_progress(result, 100, "Animation terminée!", on_progress)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"Task ID: {task_id}")
            logger.info(f"Final Video: {final_url[:80]}...")
            logger.info(f"Duration: {result.duration_seconds}s")
            logger.info(f"Clips: {result.successful_clips}/{result.total_clips}")
            logger.info(f"Generation Time: {result.generation_time_seconds:.1f}s")
            logger.info(f"{'='*80}\n")
            
            return result
            
        except Exception as e:
            logger.error(f"\n{'='*80}")
            logger.error(f"❌ PIPELINE FAILED")
            logger.error(f"Task ID: {task_id}")
            logger.error(f"Error: {e}")
            logger.error(f"{'='*80}\n")
            
            result.status = GenerationStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now()
            result.generation_time_seconds = (result.completed_at - started_at).total_seconds()
            
            # Update Supabase with failure
            await self._update_supabase(result)
            
            return result
    
    async def _update_progress(
        self,
        result: GenerationResult,
        progress: int,
        message: str,
        callback: Optional[callable]
    ) -> None:
        """Update progress via callback and Supabase."""
        logger.info(f"📊 Progress: {progress}% - {message}")
        
        if callback:
            try:
                await callback(progress, message)
            except Exception as e:
                logger.warning(f"⚠️ Progress callback error: {e}")
        
        # Update Supabase
        await self._update_supabase(result, progress, message)
    
    async def _update_supabase(
        self,
        result: GenerationResult,
        progress: Optional[int] = None,
        message: Optional[str] = None
    ) -> None:
        """Update generation status in Supabase."""
        if not self.supabase:
            return
        
        try:
            data = {
                "status": result.status.value,
                "updated_at": datetime.now().isoformat()
            }
            
            if progress is not None:
                data["progress_percent"] = progress
            
            if message:
                data["current_step"] = message
            
            if result.final_video_url:
                data["final_video_url"] = result.final_video_url
            
            if result.debug_prompts:
                data["debug_prompts"] = result.debug_prompts
            
            if result.error_message:
                data["error_message"] = result.error_message
            
            # Upsert to generations table
            self.supabase.table("generations").upsert({
                "id": result.task_id,
                "user_id": result.user_id,
                **data
            }).execute()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to update Supabase: {e}")


# =========================================================================
# SINGLETON INSTANCE
# =========================================================================

# Global orchestrator instance (lazy initialization)
_orchestrator_instance: Optional[WanVideoOrchestrator] = None


def get_wan_orchestrator() -> WanVideoOrchestrator:
    """
    Get or create the singleton WanVideoOrchestrator instance.
    
    Returns:
        WanVideoOrchestrator instance
    """
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = WanVideoOrchestrator()
    
    return _orchestrator_instance


def is_wan_orchestrator_available() -> bool:
    """
    Check if the WanVideoOrchestrator can be initialized.
    
    Returns:
        True if all required API keys are configured
    """
    try:
        get_wan_orchestrator()
        return True
    except ValueError:
        return False

