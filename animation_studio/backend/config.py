import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    # ==========================================
    # API KEYS
    # ==========================================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY", "1611882205be3979e2cc2c83a5265c1882838dd59ce222f77b3cd4cfc2ac6dea")
    
    # ==========================================
    # VEO 3.1 FAST CONFIGURATION (Runway ML)
    # ==========================================
    VEO31_MODEL = "veo3.1_fast"
    VEO31_BASE_URL = "https://api.runwayml.com/v1"
    VEO31_MAX_DURATION = 60  # Durée maximale par clip (jusqu'à 60s)
    VEO31_MIN_DURATION = 5   # Durée minimale par clip

    # Résolutions supportées par Veo 3.1 Fast
    VEO31_RESOLUTIONS = {
        "720p": "1280*720",
        "1080p": "1920*1080",
        "720p_vertical": "720*1280",
        "1080p_vertical": "1080*1920"
    }
    VEO31_DEFAULT_RESOLUTION = "720p"

    # Audio intégré dans Veo 3.1 Fast
    VEO31_AUDIO_INTEGRATED = True
    VEO31_AUDIO_MAX_LENGTH = 60  # secondes

    # Style optimisé pour Veo 3.1 Fast
    VEO31_PROMPT_STYLE = os.getenv("VEO31_PROMPT_STYLE",
        "2D cartoon animation, Disney Pixar style, child-friendly, vibrant colors, smooth fluid animation, expressive characters")

    VEO31_NEGATIVE_PROMPT = os.getenv("VEO31_NEGATIVE_PROMPT",
        "blurry, low quality, distorted, violent, scary, static, motionless, dark, horror")

    # Style pour les enfants
    CARTOON_STYLE = "2D cartoon animation, Disney style, vibrant colors, smooth animation, child-friendly"
    DEFAULT_DURATION = int(os.getenv("DEFAULT_DURATION", "30"))

    # ==========================================
    # GENERATION SETTINGS
    # ==========================================
    TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
    
    # ==========================================
    # SCENE DISTRIBUTION (Veo 3.1 Fast optimisé)
    # ==========================================
    # Mapping durée totale → liste de durées de clips
    DURATION_CLIP_MAPPING = {
        30: [10, 10, 10],                    # 3 clips de 10s
        60: [15, 15, 15, 15],               # 4 clips de 15s (Veo 3.1 Fast optimisé)
        120: [20, 20, 20, 20, 20, 20],      # 6 clips de 20s
        180: [30, 30, 30, 30, 30, 30],      # 6 clips de 30s
        240: [40, 40, 40, 40, 40, 40],      # 6 clips de 40s
        300: [50, 50, 50, 50, 50, 50]       # 6 clips de 50s
    }
    
    # ==========================================
    # SERVER SETTINGS
    # ==========================================
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", "8007"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    
    # JWT Authentication
    JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
    
    # ==========================================
    # CACHE SETTINGS
    # ==========================================
    CACHE_DIR = Path(os.getenv("CACHE_DIR", "../cache"))
    MAX_CACHE_SIZE_GB = int(os.getenv("MAX_CACHE_SIZE_GB", "10"))
    CACHE_CLEANUP_HOURS = int(os.getenv("CACHE_CLEANUP_HOURS", "24"))
    
    @classmethod
    def validate_api_keys(cls):
        """Valide que les clés API essentielles sont configurées"""
        missing_keys = []

        if not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")

        # Vérifier si au moins une plateforme de génération vidéo est disponible
        runway_key = os.getenv("RUNWAY_API_KEY")
        if not runway_key:
            missing_keys.append("RUNWAY_API_KEY")

        if missing_keys:
            raise ValueError(f"Clés API manquantes: {', '.join(missing_keys)}")

        return True
    
    @classmethod
    def get_clip_durations(cls, total_duration: int) -> list:
        """Retourne la distribution optimale des clips pour une durée donnée"""
        if total_duration in cls.DURATION_CLIP_MAPPING:
            return cls.DURATION_CLIP_MAPPING[total_duration]
        
        # Si durée personnalisée, créer des clips de 10s
        num_clips = total_duration // cls.WAN25_MAX_DURATION
        remaining = total_duration % cls.WAN25_MAX_DURATION
        
        clips = [cls.WAN25_MAX_DURATION] * num_clips
        if remaining >= cls.WAN25_MIN_DURATION:
            clips.append(remaining)
        
        return clips

# Instance globale de configuration
config = Config() 