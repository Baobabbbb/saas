from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from unidecode import unidecode
import traceback
import os
import json
from fastapi import Form

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from schemas.animation import AnimationRequest, AnimationResponse, AnimationStatusResponse, AnimationStatus
from datetime import datetime
from services.tts import generate_speech
from services.stt import transcribe_audio
from services.veo3_fal import veo3_fal_service
from services.coloring_generator import ColoringGenerator
from utils.translate import translate_text

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
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

@app.post("/generate_coloring/")
async def generate_coloring(request: ColoringRequest):
    try:
        print(f"🎨 Génération coloriage theme: {request.theme}")
        
        # Générer un titre attractif avec l'IA
        title = await _generate_coloring_title(request.theme)
        
        coloring_generator = ColoringGenerator()
        result = await coloring_generator.generate_coloring(request.theme)
        
        # Ajouter le titre généré au résultat
        if result.get("success"):
            result["title"] = title
            result["type"] = "coloring"
        
        return result
    except Exception as e:
        print(f"❌ Erreur génération coloriage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_coloring_title(theme: str) -> str:
    """Génère un titre attractif pour un coloriage selon le thème"""
    try:
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            # Fallback si pas d'API
            return f"Coloriage {theme.title()}"
        
        prompt = f"""Génère un titre court et attractif pour un coloriage sur le thème : {theme}

Le titre doit être :
- Court (maximum 3-4 mots)
- Adapté aux enfants de 3-8 ans
- Joyeux et imaginatif  
- En français
- Sans ponctuation spéciale

Exemples de bons titres :
- "Princesse Magique"
- "Super Héros Volant"
- "Animaux Rigolos"
- "Licorne Arc-en-ciel"

Titre uniquement (sans autre texte) :"""

        client = AsyncOpenAI(api_key=openai_key)
        
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un spécialiste des activités créatives pour enfants. Tu génères des titres courts et attractifs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,
            temperature=0.7
        )
        
        title = response.choices[0].message.content.strip()
        
        # Nettoyer le titre (enlever guillemets éventuels)
        title = title.replace('"', '').replace("'", '').strip()
        
        return title if title else f"Coloriage {theme.title()}"
        
    except Exception as e:
        print(f"⚠️ Erreur génération titre coloriage: {e}")
        return f"Coloriage {theme.title()}"

# --- Dessins Animés ---
@app.post("/api/animations/generate", response_model=AnimationResponse)
async def generate_animation(request: AnimationRequest):
    """
    Génère un dessin animé avec Veo3 via fal-ai
    """
    try:
        print(f"🎬 Génération animation: {request.style} / {request.theme}")
        
        # Générer un titre attractif avec l'IA
        animation_title = await _generate_animation_title(request.theme, request.style)
        
        # Générer l'animation avec le service Veo3
        result = await veo3_fal_service.generate_animation({
            'style': request.style,
            'theme': request.theme,
            'orientation': request.orientation,
            'prompt': request.prompt,
            'title': animation_title,
            'description': f"Animation {request.style} sur le thème {request.theme}"
        })
        
        return AnimationResponse(
            id=result['id'],
            title=result['title'],
            description=result['description'],
            video_url=result['video_url'],
            thumbnail_url=result.get('thumbnail_url'),
            status=AnimationStatus.COMPLETED,
            created_at=result['created_at'],
            style=request.style,
            theme=request.theme,
            duration=8
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
        # Pour Veo3, les animations sont générées immédiatement
        # Cette route est maintenue pour la compatibilité
        return AnimationStatusResponse(
            id=animation_id,
            status=AnimationStatus.COMPLETED,
            progress=100
        )
    except Exception as e:
        print(f"❌ Erreur récupération statut: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
            temperature=0.7
        )
        
        title = response.choices[0].message.content.strip()
        
        # Nettoyer le titre (enlever guillemets éventuels)
        title = title.replace('"', '').replace("'", '').strip()
        
        return title if title else f"Animation {theme.title()}"
        
    except Exception as e:
        print(f"⚠️ Erreur génération titre animation: {e}")
        return f"Animation {theme.title()}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
