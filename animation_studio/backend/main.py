#!/usr/bin/env python3
"""
Serveur Animation Studio - Version Simplifiée pour FRIDAY
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer l'app FastAPI
app = FastAPI(title="Animation Studio - FRIDAY", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Schemas simples
class AnimationRequest(BaseModel):
    theme: str
    duration: int
    custom_prompt: Optional[str] = None

class AnimationResult(BaseModel):
    animation_id: str
    status: str
    error_message: Optional[str] = None

# Thèmes disponibles
THEMES = {
    "space": {"name": "Space", "description": "Aventure spatiale", "icon": "🚀"},
    "nature": {"name": "Nature", "description": "Aventure nature", "icon": "🌳"},
    "adventure": {"name": "Adventure", "description": "Quête héroïque", "icon": "🏰"},
    "animals": {"name": "Animals", "description": "Histoire d'animaux", "icon": "🐾"},
    "magic": {"name": "Magic", "description": "Conte magique", "icon": "✨"},
    "friendship": {"name": "Friendship", "description": "Histoire d'amitié", "icon": "🤝"}
}

DURATIONS = [30, 60, 120, 180, 240, 300]

# Endpoints
@app.get("/")
async def root():
    return {"message": "Animation Studio Backend - FRIDAY", "status": "running"}

@app.get("/themes")
async def get_themes():
    return {"themes": THEMES, "durations": DURATIONS}

@app.post("/generate")
async def generate_animation(request: AnimationRequest):
    print(f"🎬 Demande d'animation: {request.theme}, {request.duration}s")
    return {
        "animation_id": "test-123",
        "status": "generating_idea",
        "message": f"Animation {request.theme} en cours de génération ({request.duration}s)"
    }

@app.get("/status/{animation_id}")
async def get_status(animation_id: str):
    return {
        "animation_id": animation_id,
        "status": "completed",
        "final_video_url": "https://exemple.com/video.mp4"
    }

@app.get("/diagnostic")
async def diagnostic():
    return {
        "status": "operational",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "wavespeed_configured": bool(os.getenv("WAVESPEED_API_KEY")),
        "fal_configured": bool(os.getenv("FAL_API_KEY"))
    }

if __name__ == "__main__":
    print("🚀 Animation Studio Backend - FRIDAY (Version Simplifiée)")
    uvicorn.run(app, host="0.0.0.0", port=8007, log_level="info")