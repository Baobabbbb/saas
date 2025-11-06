import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# --- Modèles par tâche ---
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "stability-ai")
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
STT_MODEL = os.getenv("STT_MODEL", "gpt-4o-mini-transcribe")

# --- Clés API ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# --- Suno AI (Comptines musicales) ---
SUNO_API_KEY = os.getenv("SUNO_API_KEY")
SUNO_BASE_URL = os.getenv("SUNO_BASE_URL", "https://api.sunoapi.org/api/v1")

# --- Wan 2.5 (Animations intégrées avec audio) ---
WAN25_MODEL = os.getenv("WAN25_MODEL", "alibaba/wan-2.5/text-to-video-fast")
WAN25_BASE_URL = os.getenv("WAN25_BASE_URL", "https://api.wavespeed.ai")
WAN25_DEFAULT_RESOLUTION = os.getenv("WAN25_DEFAULT_RESOLUTION", "720p")
WAN25_MAX_DURATION = int(os.getenv("WAN25_MAX_DURATION", "10"))

# --- Sora 2 (Animations avancées) ---
SORA2_PLATFORMS = {
    "openai": {
        "enabled": bool(os.getenv("OPENAI_API_KEY")),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "model": "sora-2",
        "priority": 1
    },
    "runway": {
        "enabled": bool(os.getenv("RUNWAY_API_KEY")),
        "api_key": os.getenv("RUNWAY_API_KEY"),
        "base_url": "https://api.dev.runwayml.com",
        "model": "veo3.1_fast",  # Modèle Veo 3.1 Fast pour text-to-video
        "priority": 1  # Priorité la plus haute
    },
    "pika": {
        "enabled": bool(os.getenv("PIKA_API_KEY")),
        "api_key": os.getenv("PIKA_API_KEY"),
        "base_url": "https://api.pika.art/v1",
        "model": "pika-1.0",
        "priority": 3
    },
    "luma": {
        "enabled": bool(os.getenv("LUMA_API_KEY")),
        "api_key": os.getenv("LUMA_API_KEY"),
        "base_url": "https://api.luma.ai/v1",
        "model": "dream-machine",
        "priority": 4
    }
}

# Configuration Sora 2 optimisée pour enfants
SORA2_CONFIG = {
    "max_duration": 60,  # Sora 2 peut gérer des vidéos plus longues
    "aspect_ratio": "16:9",
    "resolution": "1080p",
    "style": "2D cartoon animation, Disney Pixar style, child-friendly, vibrant colors, smooth fluid animation, expressive characters",
    "negative_prompt": "blurry, low quality, distorted, violent, scary, static, motionless, dark, horror, realistic, 3D, adult themes",
    "target_audience": "children aged 4-10, family-friendly, educational, joyful"
}

# Sélection automatique de la meilleure plateforme Sora 2 disponible
def get_best_sora2_platform():
    """Sélectionne la plateforme Sora 2 disponible avec la priorité la plus haute"""
    available_platforms = [
        (name, config) for name, config in SORA2_PLATFORMS.items()
        if config["enabled"]
    ]

    if not available_platforms:
        return None

    # Trier par priorité
    available_platforms.sort(key=lambda x: x[1]["priority"])
    return available_platforms[0][0]

SORA2_BEST_PLATFORM = get_best_sora2_platform()

# Export all variables
__all__ = [
    'TEXT_MODEL', 'IMAGE_MODEL', 'TTS_MODEL', 'STT_MODEL',
    'OPENAI_API_KEY', 'STABILITY_API_KEY',
    'SUNO_API_KEY', 'SUNO_BASE_URL',
    'WAN25_MODEL', 'WAN25_BASE_URL', 'WAN25_DEFAULT_RESOLUTION', 'WAN25_MAX_DURATION',
    'SORA2_PLATFORMS', 'SORA2_CONFIG', 'SORA2_BEST_PLATFORM'
]