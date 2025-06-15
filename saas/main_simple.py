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
        prompt = f"Écris une comptine courte, joyeuse et rythmée pour enfants sur le thème : {request.rhyme_type}.\n"
        if request.custom_request:
            prompt += f"Détails supplémentaires : {request.custom_request}"

        client = AsyncOpenAI()

        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        content = response.choices[0].message.content.strip()

        # Extraire un titre nettoyé depuis le contenu si possible
        final_title = "audio_story"
        if content.startswith("**") and "**" in content[2:]:
            final_title = content.split("**")[1].strip()        # Nettoyer pour un nom de fichier
        safe_filename = unidecode(final_title.lower().replace(" ", "_"))

        # Pas de génération audio pour les comptines dans cette version simplifiée
        # audio_path = generate_speech(content, voice=request.voice, filename=safe_filename)

        return {
            "title": final_title,
            "content": content,
            "audio_path": None  # Pas d'audio pour le moment
        }

    except Exception as e:
        import traceback
        print("❌ Erreur dans /generate_rhyme/ :", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# --- Histoire / Conte ---
class AudioStoryRequest(BaseModel):
    story_type: str
    voice: Optional[str] = None
    custom_request: Optional[str] = None

# --- Coloriage ---
class ColoringRequest(BaseModel):
    theme: str

@app.post("/generate_audio_story/")
async def generate_audio_story(request: AudioStoryRequest):
    try:
        print("📥 Requête reçue sur /generate_audio_story/")
        print("🧾 Données reçues :", request)

        prompt = f"Raconte un conte original pour enfant sur le thème : {request.story_type}. "
        prompt += "Utilise un ton bienveillant, imagé et adapté à un enfant de 4 à 8 ans. "
        if request.custom_request:
            prompt += f"Détails supplémentaires : {request.custom_request}"

        print("💡 Prompt généré :", prompt)

        client = AsyncOpenAI()

        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )

        content = response.choices[0].message.content.strip()
        print("📝 Conte généré :", content[:200], "...")  # Affiche un extrait

        audio_path = None
        if request.voice:
            print("🔊 Génération audio activée avec la voix :", request.voice)
            audio_path = generate_speech(content, voice=request.voice)
            print("✅ Audio généré :", audio_path)
        else:
            print("ℹ️ Aucune voix spécifiée, audio non généré.")

        return {
            "title": f"L'histoire de {request.story_type.capitalize()}",
            "content": content,
            "audio_path": audio_path
        }

    except Exception as e:
        print("❌ Erreur lors de la génération du conte audio :")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint Coloriage ---
@app.post("/generate_coloring/")
async def generate_coloring(request: ColoringRequest):
    try:
        print("📥 Requête reçue sur /generate_coloring/")
        print("🎨 Données reçues :", request.dict())

        # Initialiser le générateur de coloriages
        coloring_generator = ColoringGenerator()        # Générer les images de coloriage
        result = await coloring_generator.generate_coloring_pages(
            theme=request.theme
        )
        
        print("✅ Coloriages générés avec succès")
        return result

    except Exception as e:
        print("❌ Erreur lors de la génération des coloriages :")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINTS POUR LES ANIMATIONS ===

@app.post("/api/animations/generate", response_model=AnimationResponse)
async def generate_animation(request: AnimationRequest):
    """Génère une nouvelle animation avec Veo3 via fal-ai"""
    try:
        print(f"🎬 Génération d'animation demandée: {request.style} - {request.theme}")
        
        # Construction du prompt pour fal-ai
        style_map = {
            "cartoon": "style cartoon coloré",
            "fairy_tale": "style conte de fées magique",
            "anime": "style anime japonais",
            "realistic": "style réaliste cinématique",
            "paper_craft": "style papier découpé artisanal",
            "watercolor": "style aquarelle artistique"
        }
        
        theme_map = {
            "adventure": "aventure épique avec des héros",
            "magic": "monde magique avec des sortilèges",
            "animals": "animaux mignons et amicaux",
            "friendship": "amitié et entraide",
            "space": "exploration spatiale futuriste",
            "underwater": "monde sous-marin coloré",
            "forest": "forêt enchantée mystérieuse",
            "superhero": "super-héros sauvant le monde"
        }
        
        prompt_parts = [
            f"Animation courte {style_map.get(request.style, request.style)}",
            f"sur le thème: {theme_map.get(request.theme, request.theme)}",
            "Adapté aux enfants, couleurs vives, mouvements fluides",
            "Qualité professionnelle haute définition"
        ]
        
        if request.prompt:
            prompt_parts.append(f"Histoire: {request.prompt}")
        
        animation_prompt = ". ".join(prompt_parts)
        
        # Détermination de l'aspect ratio
        aspect_ratio = "9:16" if request.orientation == "portrait" else "16:9"
        
        # Génération avec le service fal-ai
        result = await veo3_fal_service.generate_video(
            prompt=animation_prompt,
            aspect_ratio=aspect_ratio,
            generate_audio=True
        )
        
        # Création de la réponse
        import uuid
        animation_id = str(uuid.uuid4())
        
        animation = AnimationResponse(
            id=animation_id,
            title=request.title or "Mon Dessin Animé",
            description=request.description or "Dessin animé créé avec Veo3",
            style=request.style,
            theme=request.theme,
            orientation=request.orientation,
            status=AnimationStatus.COMPLETED,
            video_url=result["video_url"],
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        print(f"✅ Animation créée avec l'ID: {animation.id}")
        print(f"🎥 URL vidéo: {animation.video_url}")
        
        return animation
        
    except Exception as e:
        print("❌ Erreur lors de la génération d'animation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}/status", response_model=AnimationStatusResponse)
async def get_animation_status(animation_id: str):
    """Récupère le statut d'une animation (pour compatibilité)"""
    try:
        # Avec fal-ai, les animations sont synchrones donc toujours completed
        return AnimationStatusResponse(
            status=AnimationStatus.COMPLETED,
            progress=100
        )
        
    except Exception as e:
        print("❌ Erreur lors de la récupération du statut:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}", response_model=AnimationResponse)
async def get_animation(animation_id: str):
    """Récupère une animation complète (pour compatibilité)"""
    try:
        # Dans cette version simplifiée, on ne stocke pas les animations
        # On retourne une animation d'exemple ou une erreur 404
        raise HTTPException(status_code=404, detail="Animation non trouvée")
        
    except HTTPException:
        raise
    except Exception as e:
        print("❌ Erreur lors de la récupération de l'animation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations")
async def get_user_animations(page: int = 1, limit: int = 10):
    """Récupère les animations d'un utilisateur (version simplifiée)"""
    try:
        # Version simplifiée - retourne une liste vide
        # Dans un vrai projet, on aurait une base de données
        return {
            "animations": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0
        }
        
    except Exception as e:
        print("❌ Erreur lors de la récupération des animations:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Cleanup à la fermeture
@app.on_event("shutdown")
async def shutdown_event():
    """Nettoie les ressources à la fermeture"""
    if hasattr(veo3_fal_service, 'close'):
        await veo3_fal_service.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
