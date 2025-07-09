#!/usr/bin/env python3
"""Simple test server for SEEDANCE stories endpoint"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.seedance_stories import SEEDANCE_STORIES, get_story_by_theme_and_title

app = FastAPI(title="SEEDANCE Stories Test API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SEEDANCE Stories Test API", "status": "running"}

@app.get("/api/seedance/stories")
async def get_seedance_stories():
    """Récupère toutes les histoires disponibles organisées par thème"""
    try:
        return {
            "status": "success",
            "stories": SEEDANCE_STORIES
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/seedance/stories/{theme}")
async def get_stories_by_theme(theme: str):
    """Récupère les histoires d'un thème spécifique"""
    try:
        if theme in SEEDANCE_STORIES:
            return {
                "status": "success",
                "theme": theme,
                "stories": SEEDANCE_STORIES[theme]
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Thème '{theme}' non trouvé"
            )
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/seedance/test-story")
async def test_story_retrieval(request: dict):
    """Test de récupération d'histoire par thème et titre"""
    try:
        theme = request.get("theme")
        story_title = request.get("story_title")
        
        if not theme or not story_title:
            raise HTTPException(
                status_code=400,
                detail="Les paramètres 'theme' et 'story_title' sont obligatoires"
            )
        
        story_data = get_story_by_theme_and_title(theme, story_title)
        if not story_data:
            raise HTTPException(
                status_code=404,
                detail=f"Histoire '{story_title}' introuvable dans le thème '{theme}'"
            )
        
        return {
            "status": "success",
            "theme": theme,
            "story_title": story_title,
            "story_data": story_data
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    print("🚀 Démarrage du serveur de test SEEDANCE Stories...")
    print("📡 API disponible sur: http://localhost:8001")
    print("🔗 Endpoints:")
    print("   GET  /api/seedance/stories")
    print("   GET  /api/seedance/stories/{theme}")
    print("   POST /api/seedance/test-story")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
