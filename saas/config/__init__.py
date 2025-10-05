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

# --- Suno AI (Comptines musicales - PRINCIPAL) ---
SUNO_API_KEY = os.getenv("SUNO_API_KEY")
SUNO_BASE_URL = os.getenv("SUNO_BASE_URL", "https://api.sunoapi.org/api/v1")

# --- GoAPI Udio (Comptines musicales - LEGACY/BACKUP) ---
GOAPI_API_KEY = os.getenv("GOAPI_API_KEY")
UDIO_MODEL = os.getenv("UDIO_MODEL", "music-u")
UDIO_TASK_TYPE = os.getenv("UDIO_TASK_TYPE", "generate_music")

# Export all variables
__all__ = [
    'TEXT_MODEL', 'IMAGE_MODEL', 'TTS_MODEL', 'STT_MODEL',
    'OPENAI_API_KEY', 'STABILITY_API_KEY',
    'SUNO_API_KEY', 'SUNO_BASE_URL',
    'GOAPI_API_KEY', 'UDIO_MODEL', 'UDIO_TASK_TYPE'
]