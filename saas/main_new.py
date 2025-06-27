"""
Backend principal pour la génération de dessins animés
Pipeline personnalisé sans CrewAI - utilise GPT-4o-mini + SD3-Turbo
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import traceback
import os
import json
import time
import uuid
from fastapi import Form

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

# Import du nouveau pipeline
from services.animation_pipeline import animation_pipeline

# Schemas
from schemas.animation import AnimationRequest, AnimationResponse, AnimationStatusResponse, AnimationStatus
from datetime import datetime

# Services utilitaires
from services.tts import generate_speech
from services.stt import transcribe_audio
from services.coloring_generator import ColoringGenerator
from utils.translate import translate_text

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")

app = FastAPI(
    title="API Dessins Animés", 
    version="2.0", 
    description="API pour générer des dessins animés avec pipeline personnalisé (GPT-4o-mini + SD3-Turbo)"
)

# Configuration des fichiers statiques
from pathlib import Path
cache_dir = Path("cache/animations")
cache_dir.mkdir(parents=True, exist_ok=True)

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Monter les répertoires statiques
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/cache", StaticFiles(directory="cache"), name="cache")

# CORS avec support UTF-8
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour afficher les erreurs
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        print("🔥 Exception occurred during request:")
        traceback.print_exc()
        raise

# === ROUTES DE BASE ===

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🎬 API Dessins Animés v2.0",
        "description": "Pipeline personnalisé pour la génération de dessins animés",
        "pipeline": "GPT-4o-mini + SD3-Turbo",
        "status": "ready",
        "endpoints": {
            "animation": "/api/animations/generate",
            "diagnostic": "/diagnostic",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Vérification de l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "pipeline": "animation_pipeline_v2",
        "services": {
            "animation_pipeline": "ready",
            "story_analyzer": "ready",
            "style_generator": "ready",
            "prompt_generator": "ready",
            "video_generator": "ready",
            "video_assembler": "ready"
        }
    }

@app.get("/diagnostic")
async def diagnostic():
    """Route de diagnostic pour vérifier la configuration des clés API"""
    openai_key = os.getenv("OPENAI_API_KEY")
    stability_key = os.getenv("STABILITY_API_KEY")
    
    return {
        "openai_configured": openai_key is not None and not openai_key.startswith("sk-votre"),
        "stability_configured": stability_key is not None and not stability_key.startswith("sk-votre"),
        "text_model": TEXT_MODEL,
        "openai_key_preview": f"{openai_key[:10]}..." if openai_key else "Non configurée",
        "stability_key_preview": f"{stability_key[:10]}..." if stability_key else "Non configurée",
        "pipeline_version": "2.0",
        "framework": "Custom (sans CrewAI)"
    }

# === NOUVEAU PIPELINE D'ANIMATION ===

class AnimationGenerateRequest(BaseModel):
    story: str
    target_duration: Optional[int] = 60  # Durée en secondes (30-300)
    style_hint: Optional[str] = "cartoon"  # Style visuel souhaité
    
class AnimationGenerateResponse(BaseModel):
    status: str
    animation_id: str
    videoUrl: str
    video_url: str
    story: str
    target_duration: int
    actual_duration: float
    scenes: list
    scenes_details: list
    video_clips: list
    visual_style: dict
    generation_time: float
    pipeline_type: str
    quality: str
    total_scenes: int
    note: str

@app.post("/api/animations/generate", response_model=AnimationGenerateResponse)
async def generate_animation(request: AnimationGenerateRequest):
    """
    🎬 Endpoint principal pour générer un dessin animé complet
    
    Transforme une histoire en vidéo animée en 5 étapes :
    1. Analyse et découpage de l'histoire
    2. Définition du style visuel
    3. Génération des prompts vidéo
    4. Génération des clips avec SD3-Turbo
    5. Assemblage final
    """
    print(f"\n🎬 === GÉNÉRATION ANIMATION ===")
    print(f"📖 Histoire: {request.story[:100]}...")
    print(f"⏱️ Durée cible: {request.target_duration}s")
    print(f"🎨 Style: {request.style_hint}")
    
    try:
        # Vérifier les clés API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        # Valider les paramètres
        if not request.story or len(request.story.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="❌ L'histoire doit contenir au moins 10 caractères"
            )
        
        if request.target_duration < 30 or request.target_duration > 300:
            raise HTTPException(
                status_code=400,
                detail="❌ La durée doit être entre 30 et 300 secondes (5 minutes)"
            )
        
        # Générer l'animation avec le nouveau pipeline
        result = await animation_pipeline.generate_animation(
            story=request.story,
            target_duration=request.target_duration,
            style_hint=request.style_hint
        )
        
        # Vérifier le résultat
        if result.get("status") == "failed":
            raise HTTPException(
                status_code=500,
                detail=f"❌ Échec de la génération: {result.get('error', 'Erreur inconnue')}"
            )
        
        print(f"✅ Animation générée avec succès: {result.get('animation_id')}")
        
        return AnimationGenerateResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"❌ Erreur interne: {str(e)}"
        )

# === ENDPOINT DE COMPATIBILITÉ FRONTEND ===

@app.post("/api/animations/test-duration")
async def test_duration_endpoint(request: dict):
    """
    🔧 Endpoint de compatibilité pour les tests de durée
    Redirige vers le nouveau pipeline
    """
    try:
        story = request.get("story", "")
        target_duration = request.get("target_duration", 60)
        
        # Rediriger vers le nouveau pipeline
        animation_request = AnimationGenerateRequest(
            story=story,
            target_duration=target_duration,
            style_hint="cartoon"
        )
        
        return await generate_animation(animation_request)
        
    except Exception as e:
        print(f"❌ Erreur test-duration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === SERVICES UTILITAIRES (TTS, STT, etc.) ===

@app.post("/tts")
async def tts_endpoint(data: dict):
    """Génération de synthèse vocale"""
    try:
        text = data["text"]
        path = generate_speech(text)
        return {"audio_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    """Reconnaissance vocale"""
    try:
        temp_path = f"static/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        transcription = transcribe_audio(temp_path)
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === GÉNÉRATION DE COMPTINES ===

class RhymeRequest(BaseModel):
    rhyme_type: str
    custom_request: Optional[str] = None

@app.post("/generate_rhyme/")
async def generate_rhyme(request: RhymeRequest):
    """Génération de comptines pour enfants"""
    try:
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        prompt = f"Écris une comptine courte, joyeuse et rythmée pour enfants sur le thème : {request.rhyme_type}.\n"
        if request.custom_request:
            prompt += f"Demande spécifique : {request.custom_request}\n"
        prompt += """La comptine doit être en français, adaptée aux enfants de 3 à 8 ans, avec des rimes simples et un rythme enjoué.

IMPORTANT : Génère aussi un titre court et attractif pour cette comptine (maximum 4-5 mots), qui plaira aux enfants de 3-8 ans. Le titre doit être simple et joyeux.

Format de réponse attendu :
TITRE: [titre de la comptine]
COMPTINE: [texte de la comptine]"""

        client = AsyncOpenAI(api_key=openai_key)
        
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un spécialiste des comptines pour enfants. Tu écris des textes courts, amusants et éducatifs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        if content:
            content = content.strip()
        else:
            content = ""
        
        # Extraire le titre et le contenu
        lines = content.split('\n')
        title = ""
        rhyme_text = ""
        
        for line in lines:
            if line.startswith("TITRE:"):
                title = line.replace("TITRE:", "").strip()
            elif line.startswith("COMPTINE:"):
                rhyme_text = line.replace("COMPTINE:", "").strip()
            elif not title and not rhyme_text:
                # Si pas de format, prendre la première ligne comme titre
                title = line.strip()
            else:
                rhyme_text += line + "\n"
        
        # Nettoyer le texte
        rhyme_text = rhyme_text.strip()
        
        return {
            "title": title if title else "Comptine joyeuse",
            "rhyme": rhyme_text if rhyme_text else content,
            "theme": request.rhyme_type,
            "model_used": TEXT_MODEL
        }
        
    except Exception as e:
        print(f"❌ Erreur génération comptine: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"❌ Erreur lors de la génération de la comptine: {str(e)}"
        )

# === GÉNÉRATEUR DE COLORIAGES ===

@app.post("/generate_coloring/")
async def generate_coloring(request: dict):
    """Génération de pages de coloriage"""
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        generator = ColoringGenerator(openai_key)
        
        theme = request.get("theme", "animal")
        style = request.get("style", "simple")
        age_group = request.get("age_group", "3-6")
        
        result = await generator.generate_coloring_page(theme, style, age_group)
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur génération coloriage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === TRADUCTION ===

@app.post("/translate/")
async def translate_endpoint(request: dict):
    """Service de traduction"""
    try:
        text = request.get("text", "")
        target_language = request.get("target_language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="Texte requis")
        
        translated = translate_text(text, target_language)
        
        return {
            "original_text": text,
            "translated_text": translated,
            "target_language": target_language,
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Erreur traduction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === INFORMATIONS PIPELINE ===

@app.get("/api/pipeline/info")
async def pipeline_info():
    """Informations sur le pipeline d'animation"""
    return {
        "name": "Custom Animation Pipeline v2.0",
        "description": "Pipeline personnalisé pour la génération de dessins animés",
        "framework": "FastAPI + OpenAI + SD3-Turbo",
        "stages": [
            "1. Analyse et découpage de l'histoire (GPT-4o-mini)",
            "2. Définition du style visuel cohérent (GPT-4o-mini)",
            "3. Génération des prompts vidéo optimisés (GPT-4o-mini)",
            "4. Génération des clips vidéo (SD3-Turbo)",
            "5. Assemblage de la vidéo finale"
        ],
        "supported_durations": "30-300 secondes",
        "supported_styles": ["cartoon", "anime", "realistic"],
        "max_scenes": 10,
        "quality": "HD (1024x576)",
        "features": [
            "Style visuel cohérent",
            "Durée personnalisable",
            "Assemblage automatique",
            "Fallback robuste",
            "Cache optimisé"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
