"""
Backend principal pour la génération de dessins animés
Pipeline personnalisé sans CrewAI - utilise GPT-4o-mini + SD3-Turbo
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
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
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177"],
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
async def health_check():
    """Endpoint de santé pour vérifier que l'API fonctionne"""
    return {
        "status": "healthy",
        "service": "API Dessins Animés IA",
        "version": "2.0",
        "pipeline": "GPT-4o-mini + SD3-Turbo",
        "timestamp": datetime.now().isoformat()
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
    generate_music: Optional[bool] = True  # Générer la musique ou seulement les paroles
    custom_style: Optional[str] = None  # Style musical personnalisé

class StoryRequest(BaseModel):
    story_type: str
    voice: str
    custom_request: Optional[str] = None

# === MODÈLES POUR LES COMPTINES ===

class RhymeTaskStatusRequest(BaseModel):
    """Requête pour vérifier le statut d'une tâche de comptine"""
    task_id: str
    style_used: Optional[str] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None
    demo_message: Optional[str] = None  # Message informatif pour le mode démo
    suggestions: Optional[list] = None  # Suggestions pour l'utilisateur

@app.post("/generate_rhyme/")
async def generate_rhyme(request: RhymeRequest):
    """Génération de comptines pour enfants avec capacités musicales"""
    try:
        print(f"🎵 Génération comptine: {request.rhyme_type}, Musique: {request.generate_music}")
        
        # Si la musique est demandée, utiliser le service musical complet
        if request.generate_music:
            # Générer la comptine complète (paroles + musique)
            result = await musical_nursery_rhyme_service.generate_complete_nursery_rhyme(
                rhyme_type=request.rhyme_type,
                custom_request=request.custom_request,
                generate_music=request.generate_music or True,
                custom_style=request.custom_style,
                language=getattr(request, 'language', 'fr')
            )
            
            # Ajouter des messages informatifs si la musique a échoué
            if result.get("music_status") == "failed":
                if "demo_message" not in result:
                    result["demo_message"] = (
                        "🎵 Comptine générée avec succès ! "
                        "La génération musicale est en cours de développement - "
                        "pour l'instant, profitez du magnifique texte créé pour votre enfant !"
                    )
            
            return result
        
        # Sinon, génération simple (texte seulement)
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

# === COMPTINES MUSICALES AVEC UDIO ===

from services.musical_nursery_rhyme_service import musical_nursery_rhyme_service
from services.udio_service import udio_service

@app.post("/check_rhyme_task_status/")
async def check_rhyme_task_status(request: RhymeTaskStatusRequest):
    """Vérifier le statut d'une tâche de génération musicale"""
    try:
        print(f"🔍 Vérification statut tâche: {request.task_id}")
        
        # Vérifier le statut de la tâche Udio
        result = await udio_service.check_task_status(request.task_id)
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur vérification statut: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"❌ Erreur lors de la vérification du statut: {str(e)}"
        )

@app.get("/check_task_status/{task_id}")
async def check_task_status_get(task_id: str):
    """Vérifier le statut d'une tâche de génération musicale via GET"""
    try:
        print(f"🔍 Vérification statut tâche GET: {task_id}")
        
        # Vérifier le statut de la tâche Udio
        result = await udio_service.check_task_status(task_id)
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur vérification statut GET: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"❌ Erreur lors de la vérification du statut: {str(e)}"
        )

@app.get("/rhyme_styles/")
async def get_available_rhyme_styles():
    """Récupérer les styles de comptines disponibles"""
    try:
        from services.udio_service import NURSERY_RHYME_STYLES
        
        styles = {}
        for style_key, style_info in NURSERY_RHYME_STYLES.items():
            styles[style_key] = {
                "name": style_key.replace("_", " ").title(),
                "description": style_info["style"],
                "tempo": style_info["tempo"],
                "mood": style_info["mood"]
            }
        
        return styles
        
    except Exception as e:
        print(f"❌ Erreur récupération styles: {e}")
        return {
            "status": "error",
            "error": str(e),
            "styles": {}
        }

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

# === GÉNÉRATION D'ANIMATIONS IA ===

class AnimationRequest(BaseModel):
    story: str
    duration: Optional[int] = 60  # Durée en secondes (30-300)
    style: Optional[str] = "cartoon"  # Style: cartoon, anime, realistic
    theme: Optional[str] = None  # Thème optionnel
    mode: Optional[str] = "demo"  # Mode: "demo" ou "production"

@app.post("/generate_animation/")
async def generate_animation(request: AnimationRequest):
    """Génération de dessins animés IA avec pipeline optimisée"""
    try:
        # Vérifier les clés API
        openai_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400,
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        if not stability_key or stability_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400,
                detail="❌ Clé API Stability AI non configurée. Veuillez configurer STABILITY_API_KEY dans le fichier .env"
            )
        
        # Valider les paramètres
        duration = max(30, min(300, request.duration))  # Entre 30s et 5min
        story = request.story.strip()
        
        if len(story) < 10:
            raise HTTPException(
                status_code=400,
                detail="L'histoire doit contenir au moins 10 caractères"
            )
        
        print(f"🎬 Génération animation: {story[:50]}... ({duration}s, {request.style}, mode: {request.mode})")
        
        # Importer et utiliser le nouveau pipeline conforme à la spécification
        from services.pipeline_dessin_anime_v2 import creer_dessin_anime
        
        # Générer l'animation complète avec le nouveau pipeline
        result = await creer_dessin_anime(
            histoire=story,
            duree=duration,
            openai_key=openai_key,
            stability_key=stability_key,
            mode=request.mode
        )
        
        # Ajouter des métadonnées pour l'interface
        result.update({
            "theme": request.theme or "histoire",
            "original_request": {
                "story": story,
                "duration": duration,
                "style": request.style,
                "theme": request.theme
            },
            "api_version": "2.0",
            "pipeline": "GPT-4o-mini + SD3-Turbo"
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération animation: {e}")
        import traceback
        error_traceback = traceback.format_exc()
        print(f"📋 TRACEBACK COMPLET:")
        print(error_traceback)
        
        # Retourner les détails de l'erreur pour le debug
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": error_traceback,
            "debug_info": "Erreur lors de la génération"
        }

# Endpoint compatible avec l'ancien système pour maintenir la compatibilité
@app.post("/api/animations/test-duration")
async def legacy_animation_endpoint(data: dict):
    """Endpoint de compatibilité avec l'ancien système frontend"""
    try:
        # Extraire les paramètres avec plusieurs formats possibles
        story = data.get('story', data.get('prompt', ''))
        duration = data.get('duration', data.get('total_duration', 60))
        style = data.get('style', data.get('visual_style', 'cartoon'))
        theme = data.get('theme', 'histoire')
        
        # Créer une requête compatible
        request = AnimationRequest(
            story=story,
            duration=duration,
            style=style,
            theme=theme
        )
        
        # Utiliser l'endpoint principal
        return await generate_animation(request)
        
    except Exception as e:
        print(f"❌ Erreur endpoint legacy: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Erreur lors de la génération de l'animation"
        }

# Endpoint de test pour valider les corrections frontend
@app.post("/test_animation/")
async def test_animation(request: AnimationRequest):
    """Endpoint de test rapide pour valider la logique frontend"""
    try:
        story = request.story.strip()
        
        # Validation identique à celle de l'endpoint principal
        if len(story) < 10:
            raise HTTPException(
                status_code=400,
                detail="L'histoire doit contenir au moins 10 caractères"
            )
        
        # Retourner un résultat de test immédiat
        return {
            "status": "test_success",
            "message": "✅ Test réussi - Histoire valide",
            "received_story": story,
            "story_length": len(story),
            "duration": request.duration,
            "style": request.style,
            "theme": request.theme,
            "test_note": "Ceci est un test - pas de vraie génération"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de test: {str(e)}"
        )

# ===== DÉMARRAGE DU SERVEUR =====

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur FRIDAY Backend...")
    print("📁 Répertoire de travail:", os.getcwd())
    print("🔑 Variables d'environnement:")
    print(f"   - OPENAI_API_KEY: {'✅ CONFIGURÉE' if os.getenv('OPENAI_API_KEY') else '❌ MANQUANTE'}")
    print(f"   - STABILITY_API_KEY: {'✅ CONFIGURÉE' if os.getenv('STABILITY_API_KEY') else '❌ MANQUANTE'}")
    print(f"   - TEXT_MODEL: {os.getenv('TEXT_MODEL', 'Non défini')}")
    print(f"   - VIDEO_MODEL: {os.getenv('VIDEO_MODEL', 'Non défini')}")
    print("\n🎬 Services disponibles:")
    print("   - ✅ Génération d'histoires")
    print("   - ✅ Génération de comptines")
    print("   - ✅ Génération de coloriages")
    print("   - ✅ Génération d'animations IA (GPT-4o-mini + SD3-Turbo)")
    print("   - ✅ Synthèse vocale (TTS)")
    print("   - ✅ Reconnaissance vocale (STT)")
    print("\n🌐 API Documentation: http://localhost:8000/docs")
    print("🔗 Frontend: http://localhost:5173")
    print("=" * 60)
    
    uvicorn.run(
        "main_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

from fastapi.responses import StreamingResponse
import httpx

@app.get("/download_audio/{filename}")
async def download_audio_proxy(filename: str, url: str):
    """Proxy pour télécharger des fichiers audio avec le bon nom"""
    try:
        print(f"🎵 Téléchargement proxy demandé: {filename} depuis {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Erreur de téléchargement")
            
            # Retourner le fichier avec le bon nom
            return StreamingResponse(
                iter([response.content]),
                media_type="audio/mpeg",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    except Exception as e:
        print(f"❌ Erreur téléchargement proxy: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléchargement: {str(e)}")
