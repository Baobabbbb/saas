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

# --- Wan 2.5 via WaveSpeed API (Animations intégrées avec audio) ---
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY")
WAN25_MODEL = os.getenv("WAN25_MODEL", "alibaba/alibaba-wan-2.5-text-to-video-fast")
WAN25_BASE_URL = os.getenv("WAN25_BASE_URL", "https://api.wavespeed.ai/api/v3")
WAN25_ENDPOINT = "/alibaba/alibaba-wan-2.5-text-to-video-fast"
WAN25_DEFAULT_RESOLUTION = os.getenv("WAN25_DEFAULT_RESOLUTION", "720p")
WAN25_DEFAULT_ASPECT_RATIO = os.getenv("WAN25_DEFAULT_ASPECT_RATIO", "9:16")  # Vertical pour TikTok/Reels
WAN25_CLIP_DURATION = int(os.getenv("WAN25_CLIP_DURATION", "5"))  # 5 secondes par clip
WAN25_MAX_DURATION = int(os.getenv("WAN25_MAX_DURATION", "120"))  # Max 2 minutes total
WAN25_MAX_CONCURRENT = int(os.getenv("WAN25_MAX_CONCURRENT", "5"))  # Max clips en parallèle

# --- FAL AI (pour assemblage vidéo) ---
FAL_API_KEY = os.getenv("FAL_API_KEY")

# Export all variables
__all__ = [
    'TEXT_MODEL', 'IMAGE_MODEL', 'TTS_MODEL', 'STT_MODEL',
    'OPENAI_API_KEY', 'STABILITY_API_KEY',
    'SUNO_API_KEY', 'SUNO_BASE_URL',
    # Wan 2.5 via WaveSpeed (dessins animés)
    'WAVESPEED_API_KEY', 'WAN25_MODEL', 'WAN25_BASE_URL', 'WAN25_ENDPOINT',
    'WAN25_DEFAULT_RESOLUTION', 'WAN25_DEFAULT_ASPECT_RATIO',
    'WAN25_CLIP_DURATION', 'WAN25_MAX_DURATION', 'WAN25_MAX_CONCURRENT',
    # FAL AI
    'FAL_API_KEY'
]