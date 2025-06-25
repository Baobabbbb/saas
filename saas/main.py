from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from unidecode import unidecode
import traceback
import os
import json
import time
from fastapi import Form

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from schemas.animation import AnimationRequest, AnimationResponse, AnimationStatusResponse, AnimationStatus
from datetime import datetime
from services.tts import generate_speech
from services.stt import transcribe_audio
from services.runway_story import runway_story_service
from services.runway_gen4_new import runway_gen4_service
# from services.integrated_animation_service import integrated_animation_service  # Temporairement désactivé
from services.coloring_generator import ColoringGenerator
from utils.translate import translate_text

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")

app = FastAPI(title="API Dessins Animés", version="1.0", description="API pour générer des dessins animés avec Runway Gen-4 Turbo")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        
        content = response.choices[0].message.content.strip()
        
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
        
        content = response.choices[0].message.content.strip()
        
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
    Génère un dessin animé avec Runway Gen-4 Turbo
    """
    try:
        print(f"🎬 Génération animation: {request.style} / {request.theme}")
        
        # Convertir les enum en chaînes
        style_str = request.style.value
        theme_str = request.theme.value
        orientation_str = request.orientation.value
        
        # Générer un titre attractif avec l'IA
        animation_title = await _generate_animation_title(theme_str, style_str)
        
        # Générer l'animation avec le service Runway Gen-4 Turbo
        result = await runway_gen4_service.generate_animation({
            'style': style_str,
            'theme': theme_str,
            'orientation': orientation_str,
            'prompt': request.prompt,
            'title': animation_title,
            'description': f"Animation {style_str} sur le thème {theme_str}"
        })
        
        # Ajuster le statut et la description selon le mode utilisé
        response_status = AnimationStatus.COMPLETED
        
        # Si c'est une simulation à cause des crédits, l'indiquer
        if result.get('simulation_reason'):
            result['description'] += f" (Mode simulation: {result['simulation_reason']})"
        
        return AnimationResponse(
            id=result['id'],
            title=result['title'],
            description=result['description'],
            video_url=result['video_url'],
            thumbnail_url=result.get('thumbnail_url'),
            status=response_status,
            created_at=datetime.fromisoformat(result['created_at']),
            style=request.style,
            theme=request.theme,
            orientation=request.orientation
        )
        
    except Exception as e:
        print(f"❌ Erreur génération animation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}/status", response_model=AnimationStatusResponse)
async def get_animation_status(animation_id: str):
    """
    Récupère le statut d'une animation
    """
    try:
        # Pour Runway Gen-4 Turbo, les animations sont générées avec polling
        # Cette route est maintenue pour la compatibilité
        return AnimationStatusResponse(
            status=AnimationStatus.COMPLETED,
            progress=100
        )
    except Exception as e:
        print(f"❌ Erreur récupération statut: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Status et monitoring ---
@app.get("/api/runway/credits")
async def get_runway_credits_status():
    """
    Vérifie l'état des crédits Runway
    """
    try:
        # status = await runway_simple_service.check_credits_status()
        return {
            "service": "runway_simple",
            "timestamp": datetime.now().isoformat(),
            "status": "available",
            "message": "Service simplifié - vérification des crédits non implémentée"
        }
    except Exception as e:
        return {
            "service": "runway_gen4",
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "credits_available": False
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
    Génère un dessin animé avec Runway Gen-4 Turbo (mode optimisé pour la vitesse)
    """
    try:
        print(f"⚡ Génération animation RAPIDE: {request.style} / {request.theme}")
        
        # Convertir les enum en chaînes
        style_str = request.style.value
        theme_str = request.theme.value
        orientation_str = request.orientation.value
        
        # Générer un titre attractif avec l'IA
        animation_title = await _generate_animation_title(theme_str, style_str)
        
        # Générer l'animation avec le service Runway Gen-4 Turbo (mode rapide)
        result = await runway_gen4_service.generate_animation_fast({
            'style': style_str,
            'theme': theme_str,
            'orientation': orientation_str,
            'prompt': request.prompt,
            'title': animation_title,
            'description': f"Animation {style_str} sur le thème {theme_str} (optimisée)"
        })
        
        # Ajuster le statut et la description selon le mode utilisé
        response_status = AnimationStatus.COMPLETED
        
        # Si c'est une simulation à cause des crédits, l'indiquer
        if result.get('simulation_reason'):
            result['description'] += f" (Mode simulation: {result['simulation_reason']})"
        
        return AnimationResponse(
            id=result['id'],
            title=result['title'],
            description=result['description'],
            video_url=result['video_url'],
            thumbnail_url=result.get('thumbnail_url'),
            status=response_status,
            created_at=datetime.fromisoformat(result['created_at']),
            style=request.style,
            theme=request.theme,
            orientation=request.orientation
        )
        
    except Exception as e:
        print(f"❌ Erreur génération animation rapide: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/animations/generate-async", response_model=AnimationResponse)
async def generate_animation_async(request: AnimationRequest):
    """
    Démarre une génération d'animation asynchrone (retour immédiat)
    """
    try:
        print(f"🔄 Génération animation ASYNCHRONE: {request.style} / {request.theme}")
        
        # Convertir les enum en chaînes
        style_str = request.style.value
        theme_str = request.theme.value
        orientation_str = request.orientation.value
        
        # Générer un titre attractif avec l'IA
        animation_title = await _generate_animation_title(theme_str, style_str)
        
        # Démarrer la génération avec le service story
        result = await runway_story_service.generate_animation({
            'style': style_str,
            'theme': theme_str,
            'orientation': orientation_str,
            'prompt': request.prompt,
            'title': animation_title,
            'description': f"Animation {style_str} sur le thème {theme_str}"
        })
        
        # Déterminer le statut
        status = AnimationStatus.PROCESSING if result.get('status') == 'processing' else AnimationStatus.COMPLETED
        
        return AnimationResponse(
            id=result['id'],
            title=result['title'],
            description=result['description'],
            video_url=result.get('video_url'),
            thumbnail_url=result.get('thumbnail_url'),
            status=status,
            created_at=datetime.fromisoformat(result['created_at']),
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
        
        # Service temporairement désactivé
        return {
            "status": "error", 
            "message": "Service intégré temporairement désactivé",
            "error": "integrated_animation_service non disponible"
        }
        
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
        
        print(f"🧪 Test pipeline CrewAI")
        print(f"📝 Histoire de test: {test_story}")
        
        # Service temporairement désactivé  
        return {
            "status": "test_completed",
            "message": "Service intégré temporairement désactivé pour les tests",
            "error": "integrated_animation_service non disponible"
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
    Génère un dessin animé narratif complet avec CrewAI + Runway
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
        
        # Générer l'animation narrative avec CrewAI + Runway
        result = await runway_gen4_service.generate_narrative_animation({
            'story': story,
            'style': style,
            'theme': theme,
            'orientation': orientation
        })
        
        return {
            "status": "success",
            "message": "Animation narrative générée avec succès !",
            "animation": result,
            "type": "narrative",
            "scenes_count": result.get("total_scenes", 1),
            "duration": result.get("total_duration", 10)
        }
        
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
        story_data = {
            "story": request.story,
            "style": request.style,
            "theme": request.theme,
            "orientation": request.orientation,
            "duration": request.duration,
            "quality": request.quality,
            "title": request.title
        }
        
        # Lancer le pipeline CrewAI complet
        start_time = time.time()
        
        result = await runway_gen4_service.generate_narrative_animation(story_data)
        
        generation_time = time.time() - start_time
        
        # Ajouter les métadonnées de performance
        result.update({
            "generation_time": round(generation_time, 2),
            "endpoint": "cohesive",
            "pipeline_type": "crewai_multi_agent",
            "success": True
        })
        
        print(f"✅ Animation cohérente générée en {generation_time:.2f}s")
        print(f"🎯 Score continuité: {result.get('visual_consistency_score', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur génération cohérente: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Erreur lors de la génération de l'animation cohérente",
            "fallback_suggestion": "Essayer le mode génération simple"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur FastAPI...")
    print("📍 Backend accessible sur: http://localhost:8000")
    print("🎬 Endpoints disponibles:")
    print("   • /api/animations/generate (Génération simple)")
    print("   • /api/animations/generate-fast (Génération rapide)")
    print("   • /api/animations/generate-narrative (Multi-scènes)")
    print("   • /api/animations/generate-cohesive (🆕 CrewAI cohérent)")
    print("📱 Frontend accessible sur: http://localhost:5173")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
