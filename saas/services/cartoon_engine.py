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

# Import uniqueness service to avoid duplicates
from services.uniqueness_service import uniqueness_service

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
        clip_duration: Duration per clip in seconds (always 10s with Wan 2.5 Standard)
    """
    
    # API Configuration
    WAVESPEED_BASE_URL = "https://api.wavespeed.ai/api/v3"
    # Modèle standard uniquement - supporte 10 secondes par clip
    WAN25_ENDPOINT = "/alibaba/wan-2.5/text-to-video"
    FAL_FFMPEG_URL = "https://queue.fal.run/fal-ai/ffmpeg-api/compose"
    
    # Default settings optimized for Disney/Pixar quality animation
    DEFAULT_NEGATIVE_PROMPT = "nsfw, distorted, morphing, text, watermark, scary, horror, violence, blood, dark, creepy, blurry, low quality, bad anatomy, deformed, ugly, amateur, inconsistent style, different art style, changing appearance, jump cut, abrupt transition"
    DEFAULT_STYLE = "Disney Pixar animated movie, consistent character design throughout, seamless continuous animation, same art style and lighting in every frame, professional 3D animation, cinematic composition, warm soft lighting, rich vibrant colors, smooth fluid motion, highly detailed expressive characters, beautiful detailed backgrounds, 4K movie quality"
    
    def __init__(
        self,
        wavespeed_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        fal_api_key: Optional[str] = None,
        supabase_client: Optional[Any] = None,
        max_concurrent_clips: int = 5,
        clip_duration: int = 10  # Toujours 10s avec Wan 2.5 Standard
    ):
        """
        Initialize the WanVideoOrchestrator.
        
        Args:
            wavespeed_api_key: WaveSpeed API key (or from env WAVESPEED_API_KEY)
            openai_api_key: OpenAI API key (or from env OPENAI_API_KEY)
            fal_api_key: FAL AI API key (or from env FAL_API_KEY)
            supabase_client: Supabase client for database updates
            max_concurrent_clips: Max concurrent video generations (default: 5)
            clip_duration: Duration per clip in seconds (always 10s with Wan 2.5 Standard)
        """
        # Load API keys from environment or parameters
        self.wavespeed_api_key = wavespeed_api_key or os.getenv("WAVESPEED_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.fal_api_key = fal_api_key or os.getenv("FAL_API_KEY")
        self.supabase = supabase_client
        
        # Configuration
        self.max_concurrent_clips = max_concurrent_clips
        self.clip_duration = clip_duration  # Toujours 10s par scène avec Wan 2.5 Standard
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
        character_name: Optional[str] = None,
        user_history: Optional[List[Dict[str, Any]]] = None
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
            user_history: Optional list of user's previous animations to avoid duplicates
            
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
            
            # Enrich prompt with user history to avoid duplicates
            if user_history and len(user_history) > 0:
                user_prompt = uniqueness_service.enrich_prompt_with_history(
                    user_prompt, user_history, "animation"
                )
                logger.info(f"🔄 Prompt enrichi avec {len(user_history)} animation(s) précédente(s) pour éviter les doublons")
            
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
        
        # Map style to specific visual instructions
        style_mapping = {
            "3d": "High-quality 3D CGI animation like Pixar/DreamWorks, smooth plastic-like textures, volumetric lighting, ray-traced reflections",
            "cartoon": "Classic 2D cartoon animation like Disney classics, bold outlines, flat colors, squash and stretch animation",
            "anime": "Japanese anime style like Studio Ghibli, large expressive eyes, detailed backgrounds, soft color gradients",
            "realistic": "Photorealistic CGI animation, lifelike textures, natural lighting, cinematic depth of field"
        }
        style_description = style_mapping.get(style.lower(), style_mapping["3d"])
        
        return f"""You are a PROFESSIONAL ANIMATION DIRECTOR creating a {num_scenes}-scene animated short film.

═══════════════════════════════════════════════════════════════════════════════
🎬 ANIMATION STYLE: {style.upper()}
═══════════════════════════════════════════════════════════════════════════════
Visual Style: {style_description}

═══════════════════════════════════════════════════════════════════════════════
📖 CRITICAL: CREATE A COHERENT, FLUID, REALISTIC STORY!
═══════════════════════════════════════════════════════════════════════════════

Your animation MUST tell ONE CONTINUOUS STORY where each scene is the DIRECT CONTINUATION of the previous one.

**NARRATIVE STRUCTURE for {num_scenes} scenes:**

Scene 1 (INTRODUCTION): 
- Establish the situation, setting and main character
- Show WHERE they are and WHAT they're about to do
- Example: "The team walks onto the field, crowd cheering"

Scene 2 (ACTION BEGINS):
- The main activity/action starts
- Direct continuation from Scene 1
- Example: "Players position themselves, referee blows whistle, match begins"

{"Scene 3 (DEVELOPMENT): " + chr(10) + "- The action continues and intensifies" + chr(10) + "- Build tension or excitement" + chr(10) + "- Example: 'Intense back-and-forth play, near misses'" if num_scenes >= 3 else ""}

Scene {num_scenes} (CLIMAX & RESOLUTION):
- The exciting conclusion
- A triumphant or satisfying ending moment
- Example: "Hero scores the winning goal, team celebrates together"

═══════════════════════════════════════════════════════════════════════════════
🎨 VISUAL CONSISTENCY - ABSOLUTELY CRITICAL!
═══════════════════════════════════════════════════════════════════════════════

1. **SAME CHARACTER in EVERY scene**: 
   - Create ONE detailed character description
   - COPY-PASTE the EXACT SAME description word-for-word in every scene
   - Include: hair color, eye color, skin tone, clothing, distinctive features
   - Example: "A young boy with short brown hair, blue eyes, wearing a red #10 jersey, white shorts, red socks and white cleats"

2. **SAME SETTING throughout**:
   - All scenes happen in the SAME location (or clearly connected locations)
   - Same lighting, same time of day, same weather
   - Example: "A sunny football stadium with green grass, white lines, and packed stands"

3. **CONTINUOUS ACTION**:
   - Each scene picks up EXACTLY where the previous ended
   - No random jumps or unrelated scenes
   - The story flows like watching a real video

═══════════════════════════════════════════════════════════════════════════════
📋 OUTPUT FORMAT (JSON)
═══════════════════════════════════════════════════════════════════════════════

{{
    "title": "Short, catchy title",
    "synopsis": "Complete story summary in one paragraph",
    "setting": "The main location (be specific)",
    "mood": "Overall feeling",
    "visual_style": "{style_description}",
    "main_character": {{
        "name": "Character name",
        "visual_description": "ULTRA-DETAILED: [Age/type] with [hair color/style], [eye color], [skin tone], wearing [specific clothing with colors]. [Any distinctive features].",
        "role": "Their role in the story"
    }},
    "scenes": [
        {{
            "scene_number": 1,
            "story_beat": "What happens (narrative)",
            "visual_description": "[COPY EXACT CHARACTER DESCRIPTION]. [SPECIFIC ACTION with movement verbs]. [EMOTION through facial expression and body language]. [ENVIRONMENT: same setting]. [LIGHTING: consistent]. {style_description}.",
            "character_emotion": "Primary emotion",
            "camera_angle": "wide/medium/close-up"
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
        
        # Map theme to CONCRETE story scenarios with clear scene progressions
        theme_scenarios = {
            "sport": {
                "story": "a young athlete competing in an exciting sports match",
                "example_3_scenes": [
                    "Scene 1: The player and their team walk onto the field/court, crowd cheering, excited faces",
                    "Scene 2: The match begins, intense action, players running and competing",
                    "Scene 3: The hero scores/wins, jumps in celebration, teammates rush to hug them"
                ],
                "setting": "a sports stadium/arena with cheering crowd"
            },
            "space": {
                "story": "a young astronaut on an exciting space exploration mission",
                "example_3_scenes": [
                    "Scene 1: The astronaut boards their rocket, waves goodbye, rocket launches into space",
                    "Scene 2: Flying through colorful nebulas, discovering a new planet, landing on surface",
                    "Scene 3: Meeting friendly aliens, exchanging gifts, celebrating new friendship"
                ],
                "setting": "outer space with stars, planets and a spaceship"
            },
            "ocean": {
                "story": "a young diver exploring the magical underwater world",
                "example_3_scenes": [
                    "Scene 1: Diver jumps into crystal blue water, descends into the ocean depths",
                    "Scene 2: Swimming among colorful coral reefs, discovering hidden treasure chest",
                    "Scene 3: Swimming back to surface with treasure, emerging triumphant, dolphins celebrating"
                ],
                "setting": "a vibrant underwater ocean with coral reefs and sea life"
            },
            "forest": {
                "story": "a young adventurer exploring a magical enchanted forest",
                "example_3_scenes": [
                    "Scene 1: Hero enters the mystical forest, sunlight filtering through tall trees",
                    "Scene 2: Discovering magical glowing flowers, meeting forest creatures",
                    "Scene 3: Finding the heart of the forest, magical transformation, triumphant celebration"
                ],
                "setting": "an enchanted forest with tall trees, magical plants and mystical creatures"
            },
            "animals": {
                "story": "adorable animal friends going on an adventure together",
                "example_3_scenes": [
                    "Scene 1: Animal friends gather together, planning their adventure, excited faces",
                    "Scene 2: Journeying through beautiful landscape, helping each other over obstacles",
                    "Scene 3: Reaching their destination, celebrating together, group hug"
                ],
                "setting": "a beautiful natural landscape with meadows and hills"
            },
            "magic": {
                "story": "a young wizard learning to master their magical powers",
                "example_3_scenes": [
                    "Scene 1: Young wizard opens a magical spellbook, wand glowing with power",
                    "Scene 2: Practicing spells, magical effects swirling, initial struggles then success",
                    "Scene 3: Casting a perfect spell, magical fireworks, celebration dance"
                ],
                "setting": "a magical wizard tower with floating books and glowing crystals"
            },
            "adventure": {
                "story": "a brave explorer on a treasure hunting expedition",
                "example_3_scenes": [
                    "Scene 1: Explorer studies ancient map, packs backpack, sets off on journey",
                    "Scene 2: Navigating through jungle/caves, solving puzzles, overcoming obstacles",
                    "Scene 3: Discovering the legendary treasure, holding it up triumphantly, celebrating"
                ],
                "setting": "an exotic adventure location with ancient ruins"
            },
            "friendship": {
                "story": "two characters meeting and becoming best friends",
                "example_3_scenes": [
                    "Scene 1: Two characters meet for the first time, shy but curious",
                    "Scene 2: Playing together, sharing, laughing, having fun activities",
                    "Scene 3: Best friends forever moment, pinky promise, happy hug"
                ],
                "setting": "a colorful playground or park setting"
            },
            "dinosaur": {
                "story": "a baby dinosaur on an adventure in the prehistoric world",
                "example_3_scenes": [
                    "Scene 1: Baby dinosaur hatches from egg, takes first steps, curious about world",
                    "Scene 2: Exploring prehistoric landscape, meeting other dinosaurs, playing",
                    "Scene 3: Finding dinosaur family, happy reunion, nuzzling together"
                ],
                "setting": "a prehistoric landscape with volcanoes, ferns and dinosaurs"
            },
            "circus": {
                "story": "a performer preparing for and delivering an amazing circus show",
                "example_3_scenes": [
                    "Scene 1: Performer practices backstage, nervously peeks at the crowd",
                    "Scene 2: Steps into spotlight, begins performance, audience gasping",
                    "Scene 3: Grand finale, perfect landing, standing ovation, bowing"
                ],
                "setting": "a colorful big top circus tent with spotlights"
            }
        }
        
        # Get theme scenario or create generic one
        scenario = theme_scenarios.get(theme.lower(), {
            "story": f"an exciting adventure about {theme}",
            "example_3_scenes": [
                f"Scene 1: Hero prepares for their {theme} adventure",
                f"Scene 2: Exciting {theme} action and challenges",
                f"Scene 3: Triumphant conclusion and celebration"
            ],
            "setting": f"a location fitting for {theme}"
        })
        
        # Build scene example based on num_scenes
        if num_scenes == 3:
            scene_examples = "\n".join(scenario["example_3_scenes"])
        elif num_scenes < 3:
            scene_examples = "\n".join(scenario["example_3_scenes"][:num_scenes])
        else:
            # For more scenes, expand the middle
            scene_examples = scenario["example_3_scenes"][0] + "\n"
            scene_examples += f"Scenes 2-{num_scenes-1}: Extended action sequence building up to the climax\n"
            scene_examples += scenario["example_3_scenes"][2].replace("Scene 3:", f"Scene {num_scenes}:")
        
        prompt = f"""Create a COHERENT, FLUID, REALISTIC animated short film ({num_scenes} scenes × {self.clip_duration}s each).

═══════════════════════════════════════════════════════════════════════════════
🎬 THEME: {theme.upper()}
📖 STORY: {scenario["story"]}
🏠 SETTING: {scenario["setting"]}
🎨 STYLE: {style.upper()}
═══════════════════════════════════════════════════════════════════════════════

**SCENE STRUCTURE EXAMPLE** (follow this type of progression):
{scene_examples}

═══════════════════════════════════════════════════════════════════════════════
⚠️ CRITICAL REQUIREMENTS FOR COHERENCE:
═══════════════════════════════════════════════════════════════════════════════

1. **ONE CONTINUOUS STORY**: Each scene must be the DIRECT continuation of the previous one. 
   No random jumps. The viewer should feel like watching ONE video, not separate clips.

2. **SAME CHARACTER ALWAYS**: Create ONE character with SPECIFIC details (hair color, eye color, 
   clothing colors) and COPY-PASTE that exact description in EVERY scene visual_description.

3. **SAME LOCATION**: All scenes happen in the SAME place or clearly connected locations.
   Same lighting, same weather, same time of day throughout.

4. **LOGICAL PROGRESSION**: 
   - Scene 1 → leads directly to → Scene 2 → leads directly to → Scene 3...
   - Actions flow naturally: walk in → start activity → climax → celebration

5. **REALISTIC TIMING**: What you describe in each scene should be achievable in {self.clip_duration} seconds.
   Don't describe too much action for one scene.

═══════════════════════════════════════════════════════════════════════════════
The result should feel like watching a real Disney/Pixar short film - fluid, coherent, and emotionally satisfying!"""
        
        if character_name:
            prompt += f"\n\n👤 MAIN CHARACTER NAME: {character_name}"
        
        if custom_prompt:
            prompt += f"\n\n💡 USER'S SPECIFIC STORY REQUEST: {custom_prompt}\n(Incorporate this into the {theme} theme while keeping the coherent scene structure)"
        
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
                
                # Prepare WaveSpeed API request - Wan 2.5 Standard (10s clips)
                # Toutes les scènes sont de 10 secondes
                payload = {
                    "prompt": styled_prompt,
                    "negative_prompt": self.DEFAULT_NEGATIVE_PROMPT,
                    "size": size,  # WaveSpeed format: "1280*720" ou "1920*1080"
                    "duration": 10,  # Toujours 10 secondes par scène
                    "enable_prompt_expansion": False,
                    "seed": -1
                }
                
                headers = {
                    "Authorization": f"Bearer {self.wavespeed_api_key}",
                    "Content-Type": "application/json"
                }
                
                api_url = f"{self.WAVESPEED_BASE_URL}{self.WAN25_ENDPOINT}"
                logger.info(f"📡 POST {api_url} [Wan 2.5 Standard - 10s]")
                logger.info(f"📦 Payload: size={size}, duration=10s")
                
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
        max_wait: int = 600,  # 10 minutes max for standard model (10s clips take longer)
        poll_interval: int = 8
    ) -> str:
        """
        Poll WaveSpeed API until video generation is complete.
        
        Args:
            prediction_id: WaveSpeed prediction ID
            max_wait: Maximum wait time in seconds (600s for standard 10s model)
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
    ) -> Tuple[str, List[str]]:
        """
        Télécharge et assemble les clips vidéo en une seule vidéo avec moviepy.
        
        Args:
            video_urls: List of video clip URLs from WaveSpeed
            output_format: Output format (mp4)
            normalize_audio: Whether to normalize audio loudness
            
        Returns:
            Tuple of (path to assembled video file, list of temp clip paths for cleanup)
        """
        import tempfile
        import httpx
        
        logger.info(f"🎬 Assemblage de {len(video_urls)} clips vidéo...")
        
        if not video_urls:
            raise ValueError("No video URLs to stitch")
        
        temp_dir = tempfile.mkdtemp(prefix="cartoon_")
        temp_clips = []
        
        try:
            # Step 1: Download all clips
            logger.info(f"📥 Téléchargement de {len(video_urls)} clips...")
            async with httpx.AsyncClient(timeout=120.0) as client:
                for idx, url in enumerate(video_urls):
                    logger.info(f"📥 Téléchargement clip {idx + 1}/{len(video_urls)}...")
                    response = await client.get(url)
                    
                    if response.status_code != 200:
                        logger.warning(f"⚠️ Échec téléchargement clip {idx + 1}: HTTP {response.status_code}")
                        continue
                    
                    clip_path = os.path.join(temp_dir, f"clip_{idx:03d}.mp4")
                    with open(clip_path, 'wb') as f:
                        f.write(response.content)
                    temp_clips.append(clip_path)
                    logger.info(f"✅ Clip {idx + 1} téléchargé: {len(response.content) / 1024:.1f} KB")
            
            if len(temp_clips) == 0:
                raise ValueError("Aucun clip n'a pu être téléchargé")
            
            if len(temp_clips) == 1:
                logger.info("✅ Un seul clip, pas d'assemblage nécessaire")
                return temp_clips[0], temp_clips
            
            # Step 2: Concatenate with moviepy
            logger.info(f"🔧 Assemblage de {len(temp_clips)} clips avec moviepy...")
            
            from moviepy.editor import VideoFileClip, concatenate_videoclips
            
            # Load all clips
            clips = []
            for clip_path in temp_clips:
                try:
                    clip = VideoFileClip(clip_path)
                    clips.append(clip)
                except Exception as e:
                    logger.warning(f"⚠️ Erreur chargement clip {clip_path}: {e}")
            
            if len(clips) == 0:
                raise ValueError("Aucun clip n'a pu être chargé pour l'assemblage")
            
            # Concatenate all clips
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Export final video
            output_path = os.path.join(temp_dir, f"animation_complete.{output_format}")
            logger.info(f"📼 Export de la vidéo finale ({final_clip.duration:.1f}s)...")
            
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='medium',
                threads=4,
                logger=None  # Disable moviepy's verbose logging
            )
            
            # Close all clips to free memory
            for clip in clips:
                clip.close()
            final_clip.close()
            
            logger.info(f"✅ Vidéo assemblée: {output_path}")
            logger.info(f"📺 Durée totale: {len(temp_clips) * self.clip_duration}s")
            
            return output_path, temp_clips
            
        except Exception as e:
            logger.error(f"❌ Erreur assemblage vidéo: {e}")
            import traceback
            traceback.print_exc()
            # Cleanup on error
            for clip_path in temp_clips:
                try:
                    os.remove(clip_path)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
            raise
    
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
            
            # Step 1.5: Get user history to avoid duplicates
            user_history = []
            if request.user_id and self.supabase:
                try:
                    user_history = await uniqueness_service.get_user_history(
                        self.supabase,
                        request.user_id,
                        "animation",
                        theme=request.theme,
                        limit=5
                    )
                    if user_history:
                        logger.info(f"📜 Found {len(user_history)} previous animations for user on theme '{request.theme}'")
                except Exception as e:
                    logger.warning(f"⚠️ Could not fetch user history: {e}")
            
            # Step 2: Generate script
            result.status = GenerationStatus.GENERATING_SCRIPT
            await self._update_progress(result, 10, "Création du scénario...", on_progress)
            
            script = await self.generate_script(
                theme=request.theme,
                duration_seconds=request.duration_seconds,
                style=request.style,
                custom_prompt=request.custom_prompt,
                character_name=request.character_name,
                user_history=user_history
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
            result.successful_clips = len(video_urls)
            result.failed_clips = result.total_clips - result.successful_clips
            
            await self._update_progress(result, 70, f"Clips générés: {len(video_urls)}/{result.total_clips}", on_progress)
            
            # Step 4: Assemble all clips into one video
            result.status = GenerationStatus.STITCHING
            await self._update_progress(result, 75, "Assemblage de la vidéo...", on_progress)
            
            assembled_video_path, temp_clips = await self.stitch_videos(video_urls, normalize_audio=True)
            result.duration_seconds = len(video_urls) * self.clip_duration
            
            await self._update_progress(result, 85, "Vidéo assemblée, upload en cours...", on_progress)
            
            # Step 5: Upload assembled video to Supabase Storage
            final_url = await self._upload_final_video_to_supabase(
                video_path=assembled_video_path,
                user_id=request.user_id,
                creation_id=task_id,
                duration_seconds=result.duration_seconds
            )
            
            result.final_video_url = final_url
            result.video_urls = [final_url]  # Single assembled video
            
            # Cleanup temp files
            await self._cleanup_temp_files(assembled_video_path, temp_clips)
            
            await self._update_progress(result, 95, "Animation sauvegardée!", on_progress)
            
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
    
    async def _upload_final_video_to_supabase(
        self,
        video_path: str,
        user_id: str,
        creation_id: str,
        duration_seconds: int
    ) -> str:
        """
        Upload the assembled final video to Supabase Storage.
        
        Args:
            video_path: Local path to the assembled video file
            user_id: User ID for storage path
            creation_id: Animation ID for storage path
            duration_seconds: Duration of the final video
            
        Returns:
            Public URL of the uploaded video
        """
        from services.supabase_storage import get_storage_service
        
        storage = get_storage_service()
        if not storage:
            logger.warning("⚠️ Supabase Storage non disponible")
            raise ValueError("Supabase Storage is not configured")
        
        try:
            logger.info(f"📤 Upload vidéo assemblée vers Supabase Storage...")
            logger.info(f"   - Fichier: {video_path}")
            logger.info(f"   - Durée: {duration_seconds}s")
            
            # Upload the assembled video file
            result = await storage.upload_file(
                file_path=video_path,
                user_id=user_id or "anonymous",
                content_type="animation",
                creation_id=creation_id,
                custom_filename=f"animation_{creation_id}.mp4"
            )
            
            if result.get("success"):
                public_url = result.get("public_url")
                logger.info(f"✅ Vidéo uploadée vers Supabase: {public_url[:80]}...")
                return public_url
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"❌ Échec upload Supabase: {error}")
                raise ValueError(f"Failed to upload to Supabase: {error}")
                
        except Exception as e:
            logger.error(f"❌ Erreur upload vidéo finale: {e}")
            raise
    
    async def _cleanup_temp_files(self, assembled_path: str, clip_paths: List[str]) -> None:
        """
        Clean up temporary video files after upload.
        
        Args:
            assembled_path: Path to the assembled video
            clip_paths: List of paths to individual clip files
        """
        import shutil
        
        try:
            # Get the temp directory from the assembled path
            temp_dir = os.path.dirname(assembled_path)
            
            # Remove all files in the temp directory
            for clip_path in clip_paths:
                try:
                    if os.path.exists(clip_path):
                        os.remove(clip_path)
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de supprimer {clip_path}: {e}")
            
            # Remove assembled video
            try:
                if os.path.exists(assembled_path):
                    os.remove(assembled_path)
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer {assembled_path}: {e}")
            
            # Remove temp directory
            try:
                if os.path.exists(temp_dir) and temp_dir.startswith(os.path.join(os.sep, "tmp")) or "cartoon_" in temp_dir:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.info(f"🗑️ Dossier temporaire nettoyé: {temp_dir}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer le dossier temp: {e}")
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur nettoyage fichiers temp: {e}")

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

