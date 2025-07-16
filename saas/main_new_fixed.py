#!/usr/bin/env python3
"""
🎯 SOLUTION FINALE - Serveur corrigé et fonctionnel
Remplace complètement main_new.py
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import traceback
import os
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Configuration FastAPI
app = FastAPI(
    title="API Histoires et Coloriages", 
    version="2.0", 
    description="API pour générer des histoires et des coloriages personnalisés"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fichiers statiques
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

cache_dir = Path("cache")
cache_dir.mkdir(exist_ok=True)
app.mount("/cache", StaticFiles(directory="cache"), name="cache")

# Modèles Pydantic
class AnimationRequest(BaseModel):
    story: str
    duration: int = 30
    style: Optional[str] = "cartoon"
    theme: Optional[str] = None
    mode: Optional[str] = "demo"

class StoryRequest(BaseModel):
    topic: str
    age: Optional[int] = 5
    length: Optional[str] = "short"

# Endpoints principaux
@app.get("/")
async def root():
    return {
        "message": "API Dessins Animés IA", 
        "version": "2.0",
        "status": "operational",
        "endpoints": [
            "/health",
            "/generate_animation/",
            "/generate_story/",
            "/generate_coloring/"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "API Dessins Animés IA",
        "version": "2.0",
        "pipeline": "GPT-4o-mini + SD3-Turbo",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/generate_animation/")
async def generate_animation(request: AnimationRequest):
    """Génération de dessins animés IA avec pipeline optimisée"""
    try:
        print(f"🎬 NOUVELLE REQUÊTE ANIMATION")
        print(f"   Histoire: {request.story[:50]}...")
        print(f"   Durée: {request.duration}s")
        print(f"   Mode: {request.mode}")
        print(f"   Style: {request.style}")
        
        # Vérifier les clés API
        openai_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not openai_key or openai_key.startswith("sk-votre"):
            return {
                "status": "error",
                "error": "OPENAI_API_KEY non configurée",
                "message": "Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            }
        
        if not stability_key or stability_key.startswith("sk-votre"):
            print("⚠️ STABILITY_API_KEY non configurée - mode démo uniquement")
        
        # Valider les paramètres
        duration = max(20, min(300, request.duration))  # Entre 20s et 5min
        story = request.story.strip()
        
        if len(story) < 5:
            return {
                "status": "error",
                "error": "Histoire trop courte",
                "message": "L'histoire doit contenir au moins 5 caractères"
            }
        
        print(f"✅ Paramètres validés")
        
        # Importer et utiliser le pipeline
        print(f"📦 Import du pipeline...")
        from services.pipeline_dessin_anime_v2 import creer_dessin_anime
        print(f"✅ Pipeline importé")
        
        # Générer l'animation complète
        print(f"🚀 Début génération...")
        result = await creer_dessin_anime(
            histoire=story,
            duree=duration,
            openai_key=openai_key,
            stability_key=stability_key,
            mode=request.mode
        )
        print(f"✅ Génération terminée")
        
        # Ajouter des métadonnées pour l'interface
        result.update({
            "theme": request.theme or "histoire",
            "original_request": {
                "story": story,
                "duration": duration,
                "style": request.style,
                "theme": request.theme,
                "mode": request.mode
            },
            "api_version": "2.0",
            "pipeline": "GPT-4o-mini + SD3-Turbo",
            "server": "corrected"
        })
        
        print(f"🎉 SUCCÈS - Retour de {len(result.get('scenes', []))} scènes")
        return result
        
    except Exception as e:
        print(f"❌ ERREUR GÉNÉRATION: {e}")
        import traceback
        error_traceback = traceback.format_exc()
        print(f"📋 TRACEBACK:")
        print(error_traceback)
        
        # Retourner l'erreur détaillée pour le debug
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": error_traceback.split('\n')[-3:-1],  # Dernières lignes importantes
            "debug_info": "Erreur lors de la génération",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/generate_story/")
async def generate_story(request: StoryRequest):
    """Génération d'histoires (placeholder)"""
    return {
        "status": "not_implemented",
        "message": "Utilisez /generate_animation/ pour créer des dessins animés",
        "suggestion": f"Histoire suggérée pour '{request.topic}': Un petit héros découvre {request.topic} et vit une aventure magique."
    }

@app.post("/generate_coloring/")
async def generate_coloring(request: dict):
    """Génération de coloriages (placeholder)"""
    return {
        "status": "not_implemented", 
        "message": "Utilisez /generate_animation/ pour créer des dessins animés",
        "suggestion": "Le mode demo génère des images SVG que vous pouvez utiliser comme coloriages."
    }

# Endpoint de diagnostic
@app.get("/diagnostic")
async def diagnostic():
    """Diagnostic de l'état du système"""
    try:
        from services.pipeline_dessin_anime_v2 import DessinAnimePipeline
        
        openai_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        config_status = {
            "openai_configured": bool(openai_key and not openai_key.startswith("sk-votre")),
            "stability_configured": bool(stability_key and not stability_key.startswith("sk-votre")),
            "pipeline_importable": True
        }
        
        return {
            "status": "healthy",
            "configuration": config_status,
            "timestamp": datetime.now().isoformat(),
            "message": "Système opérationnel"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
