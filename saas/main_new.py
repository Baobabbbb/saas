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

# Schemas
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
    title="API Histoires et Coloriages", 
    version="2.0", 
    description="API pour générer des histoires et des coloriages personnalisés"
)

# Configuration des fichiers statiques
from pathlib import Path

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
            "story": "/generate_story/",
            "coloring": "/generate_coloring/",
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
        "pipeline": "story_coloring_api",
        "services": {
            "story_generator": "ready",
            "coloring_generator": "ready",
            "tts_service": "ready"
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

class StoryRequest(BaseModel):
    story_type: str
    voice: str
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

@app.post("/generate_story/")
async def generate_story(request: StoryRequest):
    """Génération d'histoires pour enfants"""
    try:
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        prompt = f"Écris une courte histoire pour enfants sur le thème : {request.story_type}.\n"
        if request.custom_request:
            prompt += f"Demande spécifique : {request.custom_request}\n"
        prompt += f"""L'histoire doit être racontée par un {request.voice}. Adapte le style de narration en conséquence :
- grand-pere : ton bienveillant et sage, avec des anecdotes
- grand-mere : ton chaleureux et maternel, avec de la tendresse
- pere : ton protecteur et aventurier, avec de l'enthousiasme
- mere : ton doux et rassurant, avec de l'amour
- petit-garcon : ton espiègle et curieux, avec de l'émerveillement
- petite-fille : ton joyeux et imaginatif, avec de la fantaisie

L'histoire doit être en français, adaptée aux enfants de 3 à 8 ans, avec un message positif et éducatif.

IMPORTANT : Génère aussi un titre court et attractif pour cette histoire (maximum 4-5 mots), qui plaira aux enfants de 3-8 ans.

Format de réponse attendu :
TITRE: [titre de l'histoire]
HISTOIRE: [texte de l'histoire]"""

        client = AsyncOpenAI(api_key=openai_key)
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un conteur expert pour enfants. Tu écris des histoires captivantes, éducatives et adaptées à l'âge."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
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
        story_text = ""
        
        for line in lines:
            if line.startswith("TITRE:"):
                title = line.replace("TITRE:", "").strip()
            elif line.startswith("HISTOIRE:"):
                story_text = line.replace("HISTOIRE:", "").strip()
            elif not title and not story_text:
                # Si pas de format, prendre la première ligne comme titre
                title = line.strip()
            else:
                story_text += line + "\n"
        
        # Nettoyer le texte
        story_text = story_text.strip()
        
        # Générer l'audio avec la voix sélectionnée
        audio_path = None
        try:
            if story_text:
                audio_path = generate_speech(story_text, voice=request.voice)
        except Exception as audio_error:
            print(f"⚠️ Erreur génération audio: {audio_error}")
            # On continue sans audio si erreur
        
        return {
            "title": title if title else "Histoire merveilleuse",
            "content": story_text if story_text else content,
            "theme": request.story_type,
            "voice": request.voice,
            "audio_path": audio_path,
            "model_used": TEXT_MODEL
        }
        
    except Exception as e:
        print(f"❌ Erreur génération histoire: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"❌ Erreur lors de la génération de l'histoire: {str(e)}"
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
        
        generator = ColoringGenerator()
        
        theme = request.get("theme", "animal")
        style = request.get("style", "simple")
        age_group = request.get("age_group", "3-6")
        
        result = await generator.generate_coloring_pages(theme)
        
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
    """Informations sur l'API d'histoires et coloriages"""
    return {
        "name": "API Histoires et Coloriages v2.0",
        "description": "API personnalisée pour la génération d'histoires et de coloriages",
        "framework": "FastAPI + OpenAI + DALL-E",
        "features": [
            "1. Génération d'histoires personnalisées (GPT-4o-mini)",
            "2. Synthèse vocale pour narration",
            "3. Génération de coloriages thématiques (DALL-E)",
            "4. Support multilingue et personnalisation"
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
