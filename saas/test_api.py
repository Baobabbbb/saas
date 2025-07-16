#!/usr/bin/env python3
"""
🚀 Solution rapide : API simplifiée pour tester la génération
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le chemin
sys.path.insert(0, str(Path(__file__).parent))

app = FastAPI(title="API Test Génération", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnimationRequest(BaseModel):
    story: str
    duration: int = 30
    style: Optional[str] = "cartoon"
    theme: Optional[str] = None
    mode: Optional[str] = "demo"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "API Test"}

@app.post("/generate_animation/")
async def generate_animation_test(request: AnimationRequest):
    """Test de génération simplifié avec logs détaillés"""
    try:
        print("🚀 DÉBUT TEST GÉNÉRATION")
        print(f"   Histoire: {request.story}")
        print(f"   Durée: {request.duration}")
        print(f"   Mode: {request.mode}")
        
        # Test 1: Import
        print("📦 Test import...")
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv OK")
        
        # Test 2: Configuration
        print("🔧 Test configuration...")
        openai_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not openai_key:
            raise Exception("OPENAI_API_KEY manquante")
        if not stability_key:
            raise Exception("STABILITY_API_KEY manquante")
        
        print("✅ Clés API OK")
        
        # Test 3: Import pipeline
        print("🎬 Test import pipeline...")
        from services.pipeline_dessin_anime_v2 import creer_dessin_anime
        print("✅ Import pipeline OK")
        
        # Test 4: Génération
        print("🎯 Test génération...")
        result = await creer_dessin_anime(
            histoire=request.story,
            duree=request.duration,
            openai_key=openai_key,
            stability_key=stability_key,
            mode=request.mode
        )
        print("✅ Génération OK")
        
        return {
            "status": "success",
            "message": "Génération réussie!",
            "result": result
        }
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Erreur lors de la génération"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
