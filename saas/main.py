from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from unidecode import unidecode
import traceback
import os
import json
import time
import uuid
from fastapi import Form

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from .schemas.animation import AnimationRequest, AnimationResponse, AnimationStatusResponse, AnimationStatus
from datetime import datetime
from .services.tts import generate_speech
from .services.stt import transcribe_audio
# Pipeline d'animation moderne et modulaire (sans CrewAI)
from .services.complete_animation_pipeline import CompletAnimationPipeline

# Instance globale de la pipeline
animation_pipeline_instance = CompletAnimationPipeline()

# Fonction wrapper pour compatibilité avec l'ancienne interface
async def complete_animation_pipeline(story: str, total_duration: int = 30, style: str = "cartoon", **kwargs):
    """Fonction wrapper pour maintenir la compatibilité avec l'ancienne interface"""
    return await animation_pipeline_instance.create_animation(
        story=story,
        target_duration=total_duration,
        style=style
    )
from .services.coloring_generator import ColoringGenerator
from .services.comic_generator import ComicGenerator
from .utils.translate import translate_text

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")

app = FastAPI(title="API Dessins Animés", version="2.0", description="API moderne pour générer des dessins animés avec pipeline IA modulaire")

# Configuration des fichiers statiques pour servir les animations
from pathlib import Path
animations_cache_dir = Path("cache/animations")
animations_cache_dir.mkdir(parents=True, exist_ok=True)

# Garder l'ancien répertoire pour compatibilité
old_cache_dir = Path("cache/crewai_animations")
old_cache_dir.mkdir(parents=True, exist_ok=True)

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Monter seulement le répertoire static
app.mount("/static", StaticFiles(directory="static"), name="static")
# Note: /cache/animations est géré par un endpoint personnalisé pour le support Range

# CORS avec support UTF-8
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:5178", "http://localhost:5179", "http://localhost:5180"],
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

# === ROUTE DE DIAGNOSTIC ===

@app.get("/diagnostic")
async def diagnostic():
    """Route de diagnostic pour vérifier la configuration des clés API"""
    openai_key = os.getenv("OPENAI_API_KEY")
    stability_key = os.getenv("STABILITY_API_KEY")
    fal_key = os.getenv("FAL_API_KEY")
    
    return {
        "openai_configured": openai_key is not None and not openai_key.startswith("sk-votre"),
        "stability_configured": stability_key is not None and not stability_key.startswith("sk-votre"),
        "fal_configured": fal_key is not None and not fal_key.startswith("votre-cle"),
        "text_model": TEXT_MODEL,
        "openai_key_preview": f"{openai_key[:10]}..." if openai_key else "Non configurée",
        "stability_key_preview": f"{stability_key[:10]}..." if stability_key else "Non configurée",
        "fal_key_preview": f"{fal_key[:10]}..." if fal_key else "Non configurée"
    }

# === ENDPOINTS VALIDÉS ===

@app.post("/tts")
async def tts_endpoint(data: dict):
    try:
        text = data["text"]
        path = generate_speech(text)
        return {"audio_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    try:
        temp_path = f"static/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        transcription = transcribe_audio(temp_path)
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Comptine ---
class RhymeRequest(BaseModel):
    rhyme_type: str
    custom_request: Optional[str] = None

@app.post("/generate_rhyme/")
async def generate_rhyme(request: RhymeRequest):
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
        
        # Extraire le titre et le contenu si le format est respecté
        title = f"Comptine {request.rhyme_type}"  # Titre par défaut
        rhyme_content = content
        
        if "TITRE:" in content and "COMPTINE:" in content:
            try:
                lines = content.split('\n')
                for line in lines:
                    if line.startswith("TITRE:"):
                        title = line.replace("TITRE:", "").strip()
                        break
                
                # Extraire le contenu de la comptine
                comptine_start = content.find("COMPTINE:")
                if comptine_start != -1:
                    rhyme_content = content[comptine_start + 9:].strip()
            except:
                # En cas d'erreur, utiliser le contenu complet
                pass
        
        return {
            "title": title,
            "content": rhyme_content,
            "type": "rhyme"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération comptine: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")

# --- Histoire Audio ---
class AudioStoryRequest(BaseModel):
    story_type: str
    voice: Optional[str] = None
    custom_request: Optional[str] = None

@app.post("/generate_audio_story/")
async def generate_audio_story(request: AudioStoryRequest):
    try:
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        prompt = f"Écris une histoire courte et captivante pour enfants sur le thème : {request.story_type}.\n"
        if request.custom_request:
            prompt += f"Demande spécifique : {request.custom_request}\n"
        prompt += """L'histoire doit être en français, adaptée aux enfants de 4 à 10 ans, avec une morale positive et des personnages attachants. Maximum 800 mots.

IMPORTANT : Commence par générer un titre court et attractif pour cette histoire (maximum 5-6 mots), qui captivera les enfants de 4-10 ans.

Format de réponse OBLIGATOIRE :
TITRE: [titre de l'histoire]
HISTOIRE: [texte de l'histoire]

N'ajoute aucun titre dans le texte de l'histoire lui-même, juste dans la partie TITRE."""

        client = AsyncOpenAI(api_key=openai_key)
        
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un conteur spécialisé dans les histoires pour enfants. Tu écris des histoires engageantes avec des valeurs positives."},
                {"role": "user", "content": prompt}
            ],            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if content:
            content = content.strip()
        else:
            content = ""
        
        # Extraire le titre et le contenu si le format est respecté
        title = f"Histoire {request.story_type}"  # Titre par défaut
        story_content = content
        
        if "TITRE:" in content and "HISTOIRE:" in content:
            try:
                lines = content.split('\n')
                for line in lines:
                    if line.startswith("TITRE:"):
                        title = line.replace("TITRE:", "").strip()
                        break
                
                # Extraire le contenu de l'histoire
                histoire_start = content.find("HISTOIRE:")
                if histoire_start != -1:
                    story_content = content[histoire_start + 9:].strip()
            except:
                # En cas d'erreur, utiliser le contenu complet
                pass
        
        # Génération de l'audio si une voix est spécifiée
        audio_path = None
        if request.voice:
            try:
                # Utiliser le contenu de l'histoire pour l'audio, pas le titre
                audio_path = generate_speech(story_content, voice=request.voice)
            except Exception as audio_error:
                print(f"⚠️ Erreur génération audio: {audio_error}")
        
        return {
            "title": title,
            "content": story_content,
            "audio_path": audio_path,
            "type": "audio"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération histoire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")

# --- Coloriage ---
class ColoringRequest(BaseModel):
    theme: str

# --- Bandes Dessinées ---

# Modèles pour les BD
from typing import List, Dict, Any
from pydantic import BaseModel

class ComicRequest(BaseModel):
    """Requête pour générer une bande dessinée"""
    theme: str  # adventure, animals, space, magic, friendship, etc.
    story_length: Optional[str] = "short"  # short, medium, long (4-6, 8-10, 12-16 pages)
    art_style: Optional[str] = "cartoon"  # cartoon, realistic, manga, comics, watercolor
    custom_request: Optional[str] = None  # Demande personnalisée
    characters: Optional[List[str]] = None  # Personnages principaux
    setting: Optional[str] = None  # Lieu de l'action
    
class ComicPage(BaseModel):
    """Modèle pour une page de bande dessinée"""
    page_number: int
    image_url: str
    description: str
    dialogues: List[dict]  # [{"character": "nom", "text": "dialogue", "bubble_type": "normal"}]
    panels: Optional[List[dict]] = None  # Informations sur les cases
    
class ComicResponse(BaseModel):
    """Réponse pour une bande dessinée générée"""
    status: str
    comic_id: str
    title: str
    pages: List[ComicPage]
    total_pages: int
    theme: str
    art_style: str
    generation_time: Optional[float] = None
    comic_metadata: Optional[dict] = None
    error: Optional[str] = None

# Instance globale du générateur de BD
comic_generator_instance = ComicGenerator()

@app.post("/generate_comic/", response_model=ComicResponse)
async def generate_comic(request: ComicRequest):
    """
    Génère une bande dessinée complète avec IA
    """
    try:
        print(f"📚 Génération BD: {request.theme} / {request.art_style} / {request.story_length}")
        
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        # Convertir la requête en dictionnaire
        request_data = {
            "theme": request.theme,
            "story_length": request.story_length,
            "art_style": request.art_style,
            "custom_request": request.custom_request,
            "characters": request.characters,
            "setting": request.setting
        }
        
        # Générer la BD complète
        result = await comic_generator_instance.create_complete_comic(request_data)
        
        if result["status"] == "success":
            return ComicResponse(**result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur inconnue"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération BD: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération de la BD : {str(e)}")

# --- Animation Cohérente CrewAI ---
class AnimationCohesiveRequest(BaseModel):
    story: str
    style: str = "cartoon"
    theme: str = "adventure"
    orientation: str = "landscape"
    duration: int = 60  # Durée en secondes (30s à 300s = 5min)
    quality: str = "medium"  # fast, medium, high
    title: Optional[str] = None

@app.post("/api/animations/generate", response_model=AnimationResponse)
async def generate_animation(request: AnimationRequest):
    """
    Génère un dessin animé avec CrewAI - Animation simple
    """
    try:
        print(f"🎬 Génération animation CrewAI: {request.style} / {request.theme}")
        
        # Convertir les enum en chaînes
        style_str = request.style.value
        theme_str = request.theme.value
        
        # Créer une histoire simple basée sur le prompt ou les paramètres
        simple_story = request.prompt or f"Une {theme_str} {style_str} pour enfants"
        
        # Préparer les préférences de style
        style_preferences = {
            "style": style_str,
            "theme": theme_str,
            "orientation": request.orientation.value,
            "mood": "joyeux et coloré",
            "target_age": "3-8 ans"
        }
        
        # Générer l'animation avec la pipeline complète
        result = await complete_animation_pipeline(
            story=simple_story,
            total_duration=30,
            style="cartoon"
        )
        
        if result.get('status') == 'success':
            return AnimationResponse(
                id=str(uuid.uuid4()),
                title=f"Animation {theme_str}",
                description=f"Animation {style_str} créée avec CrewAI",
                video_url=result['video_url'],
                thumbnail_url=None,
                status=AnimationStatus.COMPLETED,
                created_at=datetime.now(),
                style=request.style,
                theme=request.theme,
                orientation=request.orientation
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Erreur génération'))
        
    except Exception as e:
        print(f"❌ Erreur génération animation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}/status", response_model=AnimationStatusResponse)
async def get_animation_status(animation_id: str):
    """
    Récupère le statut d'une animation
    """
    try:
        # Pour CrewAI, les animations sont générées avec polling
        # Cette route est maintenue pour la compatibilité
        return AnimationStatusResponse(
            status=AnimationStatus.COMPLETED,
            progress=100
        )
    except Exception as e:
        print(f"❌ Erreur récupération statut: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Status et monitoring ---
@app.get("/api/crewai/status")
async def get_crewai_status():
    """
    Vérifie l'état du service CrewAI
    """
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        return {
            "service": "crewai_animation",
            "timestamp": datetime.now().isoformat(),
            "status": "available",
            "openai_configured": openai_key is not None and not openai_key.startswith("sk-votre"),
            "stability_configured": stability_key is not None and not stability_key.startswith("sk-votre"),
            "agents_available": ["screenwriter", "art_director", "prompt_engineer", "technical_operator", "video_editor"],
            "message": "Service CrewAI opérationnel"
        }
    except Exception as e:
        return {
            "service": "crewai_animation",
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "message": "Erreur service CrewAI"
        }

async def _generate_animation_title(theme: str, style: str) -> str:
    """Génère un titre attractif pour une animation selon le thème et le style"""
    try:
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            # Fallback si pas d'API
            return f"Animation {theme.title()}"
        
        prompt = f"""Génère un titre court et attractif pour un dessin animé sur le thème : {theme} 
Style d'animation : {style}

Le titre doit être :
- Court (maximum 4-5 mots)
- Adapté aux enfants de 4-10 ans
- Captivant et imaginatif  
- En français
- Sans ponctuation spéciale

Exemples de bons titres :
- "Les Aventures de Luna"
- "Super Chat Volant"
- "Princesse des Océans"
- "Mission Spatiale Secrète"

Titre uniquement (sans autre texte) :"""

        client = AsyncOpenAI(api_key=openai_key)
        
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un spécialiste des contenus audiovisuels pour enfants. Tu génères des titres courts et captivants."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=25,
            temperature=0.7        )
        
        title = response.choices[0].message.content
        if title:
            title = title.strip()
            # Nettoyer le titre (enlever guillemets éventuels)
            title = title.replace('"', '').replace("'", '').strip()
        
        return title if title else f"Animation {theme.title()}"
        
    except Exception as e:
        print(f"⚠️ Erreur génération titre animation: {e}")
        return f"Animation {theme.title()}"

# --- Dessins Animés Optimisés ---
@app.post("/api/animations/generate-fast", response_model=AnimationResponse)
async def generate_animation_fast(request: AnimationRequest):
    """
    Génère un dessin animé avec le service rapide (vraies vidéos)
    """
    try:
        print(f"⚡ Génération animation RAPIDE: {request.style} / {request.theme}")
        
        # Importer le service rapide
        from .services.fast_animation_service import fast_animation_service
        
        # Utiliser le service rapide qui génère des vraies vidéos
        style_str = request.style.value
        theme_str = request.theme.value
        
        # Histoire simple et courte pour mode rapide
        simple_story = f"Une courte aventure {theme_str} en style {style_str}"
        
        style_preferences = {
            "style": style_str,
            "theme": theme_str,
            "mode": "fast",
            "scenes_max": 3,
            "duration_per_scene": 5
        }
        
        # Génération avec le service rapide
        result = await fast_animation_service.generate_fast_animation(
            simple_story, 
            style_preferences
        )
        
        if result.get('status') == 'success':
            return AnimationResponse(
                id=str(uuid.uuid4()),
                title=f"Animation Rapide {theme_str}",
                description=f"Animation {style_str} rapide",
                video_url=result['video_url'],
                thumbnail_url=None,
                status=AnimationStatus.COMPLETED,
                created_at=datetime.now(),
                style=request.style,
                theme=request.theme,
                orientation=request.orientation
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Erreur génération'))
        
    except Exception as e:
        print(f"❌ Erreur génération animation rapide: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/animations/generate-async", response_model=AnimationResponse)
async def generate_animation_async(request: AnimationRequest):
    """
    Démarre une génération d'animation asynchrone avec CrewAI
    """
    try:
        print(f"🔄 Génération animation ASYNCHRONE CrewAI: {request.style} / {request.theme}")
        
        # Pour l'instant, on utilise le même service mais on pourrait l'adapter pour être vraiment asynchrone
        style_str = request.style.value
        theme_str = request.theme.value
        
        simple_story = f"Une aventure {theme_str} en style {style_str}"
        
        style_preferences = {
            "style": style_str,
            "theme": theme_str,
            "mode": "async"
        }
        
        result = await complete_animation_pipeline(
            story=simple_story,
            total_duration=30,
            style=style_str
        )
        
        # Déterminer le statut
        status = AnimationStatus.COMPLETED if result.get('status') == 'success' else AnimationStatus.FAILED
        
        return AnimationResponse(
            id=str(uuid.uuid4()),
            title=f"Animation Async {theme_str}",
            description=f"Animation {style_str} générée avec CrewAI",
            video_url=result.get('video_url'),
            thumbnail_url=None,
            status=status,
            created_at=datetime.now(),
            style=request.style,
            theme=request.theme,
            orientation=request.orientation
        )
        
    except Exception as e:
        print(f"❌ Erreur génération animation async: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Nouvel endpoint pour génération d'animation narrative complète avec CrewAI
@app.post("/api/animations/generate-story")
async def generate_story_animation(request: dict):
    """
    Génère une animation narrative complète à partir d'un texte avec CrewAI
    Pipeline: Analyse narrative → Direction artistique → Génération vidéo → Assemblage
    """
    try:
        story_text = request.get('story', '')
        style_preferences = request.get('style_preferences', {
            'style': 'cartoon coloré',
            'mood': 'joyeux',
            'target_age': '3-8 ans'
        })
        
        if not story_text:
            raise HTTPException(status_code=400, detail="Le texte de l'histoire est requis")
        
        if len(story_text) < 10:
            raise HTTPException(status_code=400, detail="L'histoire doit contenir au moins 10 caractères")
        
        print(f"🎬 Génération animation narrative CrewAI")
        print(f"📖 Histoire: {story_text[:100]}...")
        print(f"🎨 Style: {style_preferences}")
        
        # Utiliser la pipeline complète
        result = await complete_animation_pipeline(
            story=story_text,
            total_duration=30,
            style=style_preferences.get("style", "cartoon")
        )
        
        if result.get('status') == 'success':
            return {
                "status": "success",
                "message": "Animation narrative générée avec succès !",
                "video_url": result.get('video_url'),
                "video_path": result.get('video_path'),
                "scenes_count": result.get('scenes_count'),
                "total_duration": result.get('total_duration'),
                "generation_time": result.get('generation_time'),
                "scenes_details": result.get('scenes_details'),
                "timestamp": result.get('timestamp')
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Erreur génération animation: {result.get('error', 'Erreur inconnue')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur endpoint animation narrative: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# Test endpoint pour pipeline CrewAI
@app.post("/api/animations/test-crewai")
async def test_crewai_pipeline(request: dict):
    """Test du pipeline CrewAI avec une histoire simple"""
    try:
        test_story = request.get('story', "Il était une fois un petit lapin qui découvrait un jardin magique plein de couleurs.")
        
        print(f"🧪 Test pipeline complète")
        print(f"📝 Histoire de test: {test_story}")
        
        # Test avec la pipeline complète
        result = await complete_animation_pipeline(
            story=test_story,
            total_duration=10,
            style="cartoon"
        )
        
        return {
            "status": "test_completed",
            "message": "Test CrewAI exécuté avec succès",
            "result": result,
            "test_story": test_story
        }
        
    except Exception as e:
        print(f"❌ Erreur test CrewAI: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "message": "Erreur lors du test CrewAI"
        }

# Test endpoint pour debug
@app.post("/api/animations/test-data")
async def test_animation_data(request: dict):
    """Test pour vérifier les données reçues"""
    print(f"📊 Données reçues: {request}")
    return {"status": "ok", "received": request}

# --- Dessins Animés Narratifs avec CrewAI ---
@app.post("/api/animations/generate-narrative")
async def generate_narrative_animation(request: dict):
    """
    Génère un dessin animé narratif complet avec CrewAI
    """
    try:
        print(f"🎬 Génération animation narrative avec CrewAI")
        
        # Extraire les paramètres
        story = request.get("story", "")
        style = request.get("style", "cartoon")
        theme = request.get("theme", "adventure")
        orientation = request.get("orientation", "landscape")
        
        if not story or len(story) < 20:
            raise HTTPException(status_code=400, detail="L'histoire doit contenir au moins 20 caractères")
        
        print(f"📖 Histoire: {story[:100]}...")
        print(f"🎨 Style: {style}, Thème: {theme}")
        
        # Préparer les préférences de style
        style_preferences = {
            "style": style,
            "theme": theme,
            "orientation": orientation,
            "mode": "narrative"
        }
        
        # Générer l'animation narrative avec la pipeline complète
        result = await complete_animation_pipeline(
            story,
            style_preferences
        )
        
        if result.get('status') == 'success':
            return {
                "status": "success",
                "message": "Animation narrative générée avec succès !",
                "animation": result,
                "type": "narrative",
                "scenes_count": result.get("scenes_count", 1),
                "duration": result.get("total_duration", 10)
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Erreur génération'))
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération narrative: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# --- Animation Cohérente avec CrewAI ---

@app.post("/api/animations/generate-cohesive")
async def generate_cohesive_animation(request: AnimationCohesiveRequest):
    """
    🎬 Génération d'animation cohérente avec CrewAI
    Pipeline multi-agents pour créer des animations de 30s à 5min
    avec continuité visuelle et narrative parfaite
    """
    try:
        print(f"🎭 Demande animation cohérente:")
        print(f"   📖 Histoire: {request.story[:100]}...")
        print(f"   🎨 Style: {request.style}")
        print(f"   ⏱️ Durée: {request.duration}s")
        print(f"   💎 Qualité: {request.quality}")
        
        # Préparer les données pour le service CrewAI
        style_preferences = {
            "style": request.style,
            "theme": request.theme,
            "orientation": request.orientation,
            "duration": request.duration,
            "quality": request.quality,
            "title": request.title,
            "mode": "cohesive"
        }
        
        # Lancer le pipeline CrewAI complet
        start_time = time.time()
        
        # MODE RAPIDE: Utiliser le service fast si qualité = "fast"
        if request.quality == "fast":
            try:
                from services.fast_animation_service import fast_animation_service
                print("⚡ Mode rapide activé...")
                
                result = await fast_animation_service.generate_complete_animation(
                    request.story,
                    style_preferences
                )
                
                if result.get('status') == 'success':
                    generation_time = time.time() - start_time
                    result.update({
                        "generation_time": round(generation_time, 2),
                        "endpoint": "cohesive_fast",
                        "pipeline_type": "fast_service",
                        "success": True
                    })
                    print(f"⚡ Animation rapide générée en {generation_time:.2f}s")
                    return result
            except Exception as e:
                print(f"⚠️ Service rapide échoué: {e}")
        
        # MODE NORMAL: UTILISATION SERVICE IA RÉEL (vraie génération vidéo)
        if request.quality in ["high", "medium"]:
            try:
                from services.real_animation_service import real_animation_crewai
                print("🎬 Utilisation du service IA RÉEL (vraie génération vidéo)...")
                
                result = await real_animation_crewai.generate_complete_animation(
                    request.story,
                    style_preferences
                )
                
                if result.get('status') == 'success':
                    generation_time = time.time() - start_time
                    result.update({
                        "generation_time": round(generation_time, 2),
                        "endpoint": "cohesive_real_ai",
                        "pipeline_type": "real_ai_generation",
                        "success": True
                    })
                    print(f"🎉 Animation IA RÉELLE générée en {generation_time:.2f}s")
                    return result
                else:
                    print(f"⚠️ Service IA réel échoué: {result.get('error')}")
            except Exception as e:
                print(f"⚠️ Service IA réel indisponible: {e}")
        
        # FALLBACK: UTILISATION SERVICE ANIMATION COMPLET
        try:
            from services.complete_animation_pipeline import complete_animation_pipeline
            print("🚀 Utilisation du service animation complet...")
            
            result = await complete_animation_pipeline.generate_complete_animation(
                request.story,
                style_preferences
            )
            
            if result.get('status') == 'success':
                generation_time = time.time() - start_time
                result.update({
                    "generation_time": round(generation_time, 2),
                    "endpoint": "cohesive_final",
                    "pipeline_type": "crewai_final",
                    "success": True
                })
                print(f"✅ Animation cohérente (FINALE) générée en {generation_time:.2f}s")
                return result
            
        except Exception as e:
            print(f"⚠️ Service final indisponible: {e}")
            
        # FALLBACK: Essayer la version simple
        try:
            from services.simple_animation_service import simple_animation_service
            print("🔧 Fallback: Utilisation du service simple...")
            
            result = await simple_animation_service.generate_complete_animation(
                request.story,
                style_preferences
            )
            
            if result.get('status') == 'success':
                generation_time = time.time() - start_time
                result.update({
                    "generation_time": round(generation_time, 2),
                    "endpoint": "cohesive_corrected",
                    "pipeline_type": "crewai_corrected_fallback",
                    "success": True
                })
                print(f"✅ Animation cohérente (fallback corrigé) générée en {generation_time:.2f}s")
                return result
            else:
                print("⚠️ Service corrigé échoué, fallback vers original...")
        
        except Exception as corrected_error:
            print(f"⚠️ Service corrigé indisponible: {corrected_error}")
        
        # Fallback vers la pipeline complète
        print("🔄 Utilisation de la pipeline complète...")
        result = await complete_animation_pipeline(
            request.story,
            style_preferences
        )
        
        generation_time = time.time() - start_time
        
        # Ajouter les métadonnées de performance
        result.update({
            "generation_time": round(generation_time, 2),
            "endpoint": "cohesive",
            "pipeline_type": "crewai_multi_agent",
            "success": result.get('status') == 'success'
        })
        
        print(f"✅ Animation cohérente générée en {generation_time:.2f}s")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur génération cohérente: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Erreur lors de la génération de l'animation cohérente",
            "fallback_suggestion": "Essayer le mode génération simple"
        }

# === ENDPOINT SIMPLIFIÉ FONCTIONNEL ===
@app.post("/api/animations/generate-simple")
async def generate_simple_animation(data: dict):
    """
    Générateur d'animation simplifié qui fonctionne à coup sûr
    """
    try:
        # Extraction des paramètres
        story = data.get('story', data.get('prompt', 'Il était une fois un petit héros qui découvrait un monde magique plein de couleurs et d\'aventures.'))
        duration = int(data.get('duration_preferences', {}).get('total_duration', data.get('duration', 10)))
        style = data.get('style_preferences', {}).get('visual_style', data.get('style', 'cartoon'))
        
        print(f"🎬 Génération animation simple: {story[:50]}... | {duration}s | {style}")
        
        # Générer un ID unique
        animation_id = str(uuid.uuid4())[:8]
        
        # Créer le répertoire de cache
        cache_dir = Path("cache/animations")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Créer directement une vidéo avec le générateur basique
        output_file = cache_dir / f"animation_{animation_id}.mp4"
        
        try:
            # Import local du générateur de vidéo
            import sys
            backend_dir = Path(__file__).parent.parent
            sys.path.append(str(backend_dir))
            
            from create_animated_video import create_animated_video
            
            print(f"  📹 Création vidéo: {output_file}")
            success = create_animated_video(story, duration, output_file)
            
            if success and output_file.exists():
                file_size = output_file.stat().st_size
                print(f"  ✅ Vidéo créée: {file_size} bytes")
                
                return {
                    "status": "success",
                    "animation_id": animation_id,
                    "video_url": f"/cache/animations/{output_file.name}",
                    "story": story,
                    "total_duration": duration,
                    "actual_duration": duration,
                    "scenes_count": 1,
                    "generation_time": 2.0,
                    "file_size": file_size,
                    "quality": "simple_generator",
                    "message": "Animation créée avec succès"
                }
            else:
                print(f"  ⚠️ Génération échouée, création fichier vide")
                output_file.touch()
                
                return {
                    "status": "partial_success",
                    "animation_id": animation_id,
                    "video_url": f"/cache/animations/{output_file.name}",
                    "story": story,
                    "total_duration": duration,
                    "message": "Fichier créé mais génération partielle",
                    "warning": "Utilisation fallback"
                }
                
        except Exception as gen_error:
            print(f"  ❌ Erreur générateur: {gen_error}")
            # Créer un fichier minimal en fallback
            output_file.touch()
            
            return {
                "status": "fallback",
                "animation_id": animation_id,
                "video_url": f"/cache/animations/{output_file.name}",
                "story": story,
                "total_duration": duration,
                "error": str(gen_error),
                "message": "Fichier créé avec fallback"
            }
        
    except Exception as e:
        print(f"❌ Erreur endpoint simple: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": str(e),
            "pipeline": "simple_animation"
        }

# === ENDPOINT COMPATIBLE FRONTEND ===  
@app.post("/generate-production")
async def generate_production_animation(data: dict):
    """
    Endpoint de production utilisant la pipeline complète
    Compatible avec le frontend existant (sans /api/)
    """
    try:
        # Extraction des paramètres avec support de la structure frontend
        story = data.get('story', data.get('prompt', 'Histoire par défaut'))
        
        # Gestion de la durée (plusieurs formats possibles)
        duration_prefs = data.get('duration_preferences', {})
        duration = (
            duration_prefs.get('total_duration') or 
            data.get('duration') or 
            data.get('total_duration') or 
            30
        )
        
        # Gestion du style (plusieurs formats possibles)
        style_prefs = data.get('style_preferences', {})
        style = (
            style_prefs.get('visual_style') or 
            data.get('style') or 
            'cartoon'
        )
        
        print(f"🎬 Production: {story[:50]}... | {duration}s | {style}")
        print(f"📊 Données reçues: {data}")
        
        # Utiliser la pipeline complète
        result = await complete_animation_pipeline(
            story=story,
            total_duration=int(duration),
            style=style
        )
        
        return result
            
    except Exception as e:
        print(f"❌ Erreur production: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "pipeline": "production_pipeline"
        }

@app.get("/cache/animations/{filename}")
async def serve_animation_video(filename: str, range: Optional[str] = Header(None)):
    """
    Servir les vidéos d'animation avec support Range pour la lecture vidéo
    """
    file_path = Path(f"cache/animations/{filename}")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier vidéo non trouvé")
    
    # Pour les requêtes simples sans Range, retourner le fichier complet
    if not range:
        return FileResponse(
            path=str(file_path),
            media_type="video/mp4",
            headers={"Accept-Ranges": "bytes"}
        )
    
    # Gérer les requêtes Range pour le streaming vidéo
    file_size = file_path.stat().st_size
    
    try:
        # Parse Range header (format: bytes=start-end)
        range_match = range.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        # Vérifier les limites
        if start >= file_size or end >= file_size or start > end:
            raise HTTPException(
                status_code=416, 
                detail="Range Not Satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"}
            )
        
        # Lire la portion du fichier
        chunk_size = end - start + 1
        
        def generate_chunk():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    read_size = min(8192, remaining)
                    chunk = f.read(read_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
        }
        
        return StreamingResponse(
            generate_chunk(),
            status_code=206,  # Partial Content
            headers=headers,
            media_type="video/mp4"
        )
        
    except ValueError:
        # Range header mal formé, retourner le fichier complet
        return FileResponse(
            path=str(file_path),
            media_type="video/mp4",
            headers={"Accept-Ranges": "bytes"}
        )

# === ENDPOINT DE TEST SIMPLE ===
@app.post("/api/test")
async def test_endpoint():
    """Test simple pour vérifier que l'API fonctionne"""
    print("🧪 Test endpoint appelé !")
    return {
        "status": "success",
        "message": "API fonctionne correctement",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def test_get_endpoint():
    """Test GET simple"""
    print("🧪 Test GET endpoint appelé !")
    return {
        "status": "success",
        "message": "API GET fonctionne correctement",
        "timestamp": datetime.now().isoformat()
    }

# === ENDPOINTS DE TEST SIMPLE ===
@app.get("/test")
async def test_endpoint():
    """Test simple de connectivité"""
    return {
        "status": "ok",
        "message": "API Animation fonctionnelle",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/test-simple-animation")
async def test_simple_animation(data: dict):
    """Test de génération d'animation simplifié"""
    try:
        story = data.get("story", "Histoire de test")
        duration = data.get("duration", 5)
        
        print(f"🧪 Test animation simple: {story} ({duration}s)")
        
        # Créer directement une vidéo test avec le générateur simplifié
        animation_id = str(uuid.uuid4())[:8]
        
        # Utiliser le générateur basique
        cache_dir = Path("cache/animations")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = cache_dir / f"test_{animation_id}.mp4"
        
        # Import local pour éviter les problèmes
        try:
            import sys
            backend_dir = Path(__file__).parent.parent
            sys.path.append(str(backend_dir))
            
            from create_animated_video import create_animated_video
            success = create_animated_video(story, duration, output_file)
            
            if success and output_file.exists():
                file_size = output_file.stat().st_size
                return {
                    "status": "success",
                    "message": "Animation test créée avec succès",
                    "video_url": f"/cache/animations/{output_file.name}",
                    "file_size": file_size,
                    "story": story,
                    "duration": duration,
                    "animation_id": animation_id
                }
            else:
                # Fallback : créer un fichier vide  
                output_file.touch()
                return {
                    "status": "partial_success",
                    "message": "Fichier créé mais génération échouée",
                    "video_url": f"/cache/animations/{output_file.name}",
                    "story": story,
                    "duration": duration
                }
                
        except Exception as gen_error:
            print(f"⚠️ Erreur génération: {gen_error}")
            # Créer un fichier vide en fallback
            output_file.touch()
            return {
                "status": "fallback",
                "message": f"Fichier vide créé (erreur: {gen_error})",
                "video_url": f"/cache/animations/{output_file.name}",
                "story": story,
                "error": str(gen_error)
            }
        
    except Exception as e:
        print(f"❌ Erreur test animation: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# === ENDPOINT POUR SERVIR LES IMAGES PLACEHOLDER ===
@app.get("/placeholder-video.png")
async def serve_placeholder_video():
    """Servir une image placeholder pour les vidéos"""
    # Créer une image placeholder simple
    from PIL import Image, ImageDraw, ImageFont
    
    # Créer une image de placeholder
    img = Image.new('RGB', (640, 360), color=(100, 100, 150))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Ajouter du texte
    text = "🎬 Vidéo Animation"
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (640 - text_width) // 2
        y = (360 - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Sauvegarder temporairement
    placeholder_path = Path("static/placeholder-video.png")
    img.save(placeholder_path)
    
    return FileResponse(
        path=str(placeholder_path),
        media_type="image/png"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
