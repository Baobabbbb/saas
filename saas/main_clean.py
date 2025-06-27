from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import time

# Configuration
app = FastAPI(title="API Dessins Animés", version="1.0", description="API pour générer des dessins animés")

# Configuration des fichiers statiques
cache_dir = Path("cache/crewai_animations")
cache_dir.mkdir(parents=True, exist_ok=True)

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/cache", StaticFiles(directory="cache"), name="cache")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "API Dessins Animés",
        "version": "1.0",
        "endpoints": {
            "animation": "/api/animations/test-duration",
            "docs": "/docs"
        }
    }

# --- Endpoint principal pour le frontend ---
@app.post("/api/animations/test-duration")
async def generate_animation_duration(data: dict):
    """
    Endpoint principal pour générer des animations
    """
    try:
        story = data.get('story', 'Une histoire magique')
        duration = data.get('duration', 10)
        style = data.get('style', 'cartoon')
        theme = data.get('theme', 'adventure')
        
        print(f"🎬 Génération animation: {duration}s - {story[:50]}...")
        
        # Service de test avec vraie vidéo
        from services.simple_duration_service import SimpleDurationService
        service = SimpleDurationService()
        
        style_preferences = {
            'style': style,
            'theme': theme,
            'duration': duration
        }
        
        result = await service.generate_simple_animation(story, style_preferences)
        
        print(f"✅ Animation générée: {result.get('total_duration')}s")
        return result
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
