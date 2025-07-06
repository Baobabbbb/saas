"""
Configuration centralisée pour l'application FRIDAY
Charge les variables d'environnement depuis .env
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")
STT_MODEL = os.getenv("STT_MODEL", "whisper-1")

# Configuration Stability AI
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "stability-ai")

# Configuration FAL
FAL_API_KEY = os.getenv("FAL_API_KEY")
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "sd3-large-turbo")

# Configuration Udio et services externes
GOAPI_API_KEY = os.getenv("GOAPI_API_KEY")
UDIO_MODEL = os.getenv("UDIO_MODEL", "udio-130")
UDIO_TASK_TYPE = os.getenv("UDIO_TASK_TYPE", "udio_gen")

# Configuration DiffRhythm
DIFFRHYTHM_MODEL = os.getenv("DIFFRHYTHM_MODEL", "diffrhythm-1.0")
DIFFRHYTHM_TASK_TYPE = os.getenv("DIFFRHYTHM_TASK_TYPE", "diffrhythm_gen")

# Configuration Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Configuration ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Validation des clés API critiques
def validate_config():
    """Valide que les clés API essentielles sont configurées"""
    issues = []
    
    if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-votre"):
        issues.append("OPENAI_API_KEY non configurée")
    
    if not STABILITY_API_KEY or STABILITY_API_KEY.startswith("sk-votre"):
        issues.append("STABILITY_API_KEY non configurée")
    
    return issues

def get_config_status():
    """Retourne le statut de configuration des API"""
    return {
        "openai_configured": OPENAI_API_KEY is not None and not OPENAI_API_KEY.startswith("sk-votre"),
        "stability_configured": STABILITY_API_KEY is not None and not STABILITY_API_KEY.startswith("sk-votre"),
        "fal_configured": FAL_API_KEY is not None,
        "goapi_configured": GOAPI_API_KEY is not None,
        "elevenlabs_configured": ELEVENLABS_API_KEY is not None,
        "huggingface_configured": HUGGINGFACE_API_KEY is not None,
    }
