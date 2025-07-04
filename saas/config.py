import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# --- Modèles par tâche ---
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "stability-ai")  # ← mise à jour par défaut
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
STT_MODEL = os.getenv("STT_MODEL", "gpt-4o-mini-transcribe")

# --- Clés API ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")  # ← ajout pour Stability AI

# --- GoAPI Udio (Comptines musicales) ---
GOAPI_API_KEY = os.getenv("GOAPI_API_KEY")
UDIO_MODEL = os.getenv("UDIO_MODEL", "music-u")
UDIO_TASK_TYPE = os.getenv("UDIO_TASK_TYPE", "generate_music")

# Configuration file for the SAAS application
# Only CrewAI and essential services
