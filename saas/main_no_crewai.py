from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import time
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'application
app = FastAPI(
    title="API Dessins Animés", 
    version="2.0", 
    description="API pour générer des dessins animés sans CrewAI"
)

# Configuration des fichiers statiques
cache_dir = Path("cache")
cache_dir.mkdir(parents=True, exist_ok=True)

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/cache", StaticFiles(directory="cache"), name="cache")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175", 
        "http://localhost:5177"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "API Dessins Animés - Version sans CrewAI",
        "version": "2.0",
        "status": "ready",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "message": "API opérationnelle"
    }

# Endpoint temporaire pour le frontend en attendant la nouvelle implémentation
@app.post("/api/animations/test-duration")
async def placeholder_animation(data: dict):
    """
    Endpoint temporaire pour maintenir la compatibilité du frontend
    """
    story = data.get('story', 'Histoire temporaire')
    duration = data.get('duration', 10)
    style = data.get('style', 'cartoon')
    theme = data.get('theme', 'adventure')
    
    print(f"📝 Demande d'animation reçue: {story[:50]}...")
    
    # Réponse temporaire
    return {
        "status": "success",
        "message": "CrewAI supprimé - En attente de la nouvelle implémentation",
        "videoUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "story": story,
        "duration": duration,
        "style": style,
        "theme": theme,
        "total_duration": duration,
        "scenes": [
            {
                "scene_number": 1,
                "description": f"Scène temporaire: {story[:30]}...",
                "duration": duration,
                "action": "En attente de nouvelle implémentation",
                "setting": "Placeholder",
                "status": "placeholder"
            }
        ],
        "scenes_details": [
            {
                "scene_number": 1,
                "description": f"Scène temporaire: {story[:30]}...",
                "duration": duration,
                "action": "En attente de nouvelle implémentation",
                "setting": "Placeholder",
                "status": "placeholder"
            }
        ],
        "generation_time": 0.1,
        "pipeline_type": "placeholder",
        "note": "🚧 CrewAI supprimé - Prêt pour nouvelle implémentation"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
