# Models package for the animation service

# Cartoon generation schemas (Wan 2.5 via WaveSpeed)
from .cartoon import (
    CharacterSheet,
    Scene,
    Script,
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
    ProgressUpdate,
    AspectRatio,
    Resolution
)

__all__ = [
    "CharacterSheet",
    "Scene",
    "Script",
    "GenerationRequest",
    "GenerationResult",
    "GenerationStatus",
    "ProgressUpdate",
    "AspectRatio",
    "Resolution"
]