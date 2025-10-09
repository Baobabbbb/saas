from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ValidationError
from typing import Optional, List, Dict, Any
from unidecode import unidecode
import traceback
import os
import json
import time
import uuid
from fastapi import Form
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from datetime import datetime
# from services.tts import generate_speech
# from services.stt import transcribe_audio

# Authentification gérée par Supabase - modules supprimés car inutiles avec Vercel
from services.coloring_generator_gpt4o import ColoringGeneratorGPT4o
from services.comic_generator import ComicGenerator
from services.real_animation_generator import RealAnimationGenerator
from services.local_animation_generator import LocalAnimationGenerator
from utils.translate import translate_text
from routes.admin_features import router as admin_features_router, load_features_config, CONFIG_FILE
# from models.animation import AnimationRequest
# Validation et sécurité supprimées car gérées automatiquement par Vercel + Supabase

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
BASE_URL = os.getenv("BASE_URL", "https://herbbie.com")

# Logging des variables d'environnement au démarrage
print("=" * 60)
print("🚀 DÉMARRAGE API FRIDAY - Contenu Créatif IA")
print("=" * 60)
print(f"📝 TEXT_MODEL: {TEXT_MODEL}")
print(f"🌐 BASE_URL: {BASE_URL}")
print(f"✅ OPENAI_API_KEY: {'Configurée' if os.getenv('OPENAI_API_KEY') else '❌ NON CONFIGURÉE'}")
print(f"🎵 SUNO_API_KEY: {'Configurée' if os.getenv('SUNO_API_KEY') else '❌ NON CONFIGURÉE'}")
print(f"🎨 STABILITY_API_KEY: {'Configurée' if os.getenv('STABILITY_API_KEY') else '❌ NON CONFIGURÉE'}")
print("=" * 60)

app = FastAPI(title="API FRIDAY - Contenu Créatif IA", version="2.0", description="API pour générer du contenu créatif pour enfants : BD, coloriages, histoires, comptines")

# Modèles pour l'API Animation
class AnimationRequest(BaseModel):
    theme: str
    duration: Optional[int] = 30
    style: Optional[str] = "cartoon"
    mode: Optional[str] = "demo"
    custom_prompt: Optional[str] = None

# Modèle pour le formulaire de contact
class ContactForm(BaseModel):
    firstName: str
    lastName: str
    email: str
    subject: str
    message: str

# Gestionnaire d'erreurs pour la validation Pydantic
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Gestionnaire pour les erreurs de validation Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    return HTTPException(
        status_code=422,
        detail={
            "message": "Erreur de validation des données d'entrée",
            "errors": errors
        }
    )

# Gestionnaire d'erreurs pour les erreurs de validation personnalisées
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Gestionnaire pour les erreurs de validation personnalisées"""
    return HTTPException(
        status_code=400,
        detail={
            "message": "Erreur de validation",
            "error": str(exc)
        }
    )

# Rate limiting et HTTPS supprimés car gérés automatiquement par Vercel

# Configuration des fichiers statiques
from pathlib import Path
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Monter le répertoire static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Servir les animations générées localement
@app.get("/static/generated/{filename}")
async def serve_generated_video(filename: str):
    """Sert les vidéos générées localement"""
    file_path = os.path.join("static", "generated", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4")
    else:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
# Monter aussi /assets pour les fichiers générés par Vite (JS/CSS)
assets_dir = static_dir / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# CORS avec support UTF-8
app.add_middleware(
    CORSMiddleware,
    # Autoriser les domaines spécifiques du panneau et d'Herbbie
    allow_origins=[
        "https://panneau-production.up.railway.app",
        "https://herbbie.com",
        "https://www.herbbie.com",
        "http://localhost:3000",  # Pour le développement local
        "http://localhost:5173"    # Pour Vite en développement
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Inclusion des routes d'administration
app.include_router(admin_features_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint de santé pour vérifier si le serveur répond"""
    return {
        "status": "healthy",
        "service": "herbbie-backend",
        "base_url": BASE_URL,
        "timestamp": datetime.now().isoformat()
    }

# Validation des requêtes supprimée car gérée automatiquement par Vercel

# Middleware pour afficher les erreurs (avec gestion des déconnexions client)
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except ConnectionResetError:
        # Ignorer silencieusement les déconnexions client (streaming audio/vidéo)
        pass
    except OSError as e:
        if "WinError 10054" in str(e) or "connexion existante" in str(e).lower():
            # Ignorer silencieusement les erreurs de connexion fermée par le client
            pass
        else:
            print(f"🔥 OS Error during request: {e}")
            traceback.print_exc()
            raise
    except Exception as e:
        # Afficher les autres erreurs importantes
        if "connection" not in str(e).lower():
            print(f"🔥 Exception occurred during request: {e}")
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

# === ROUTES DES FONCTIONNALITÉS GÉRÉES PAR LE ROUTEUR ADMIN_FEATURES ===
# Les routes /api/features sont maintenant gérées par le routeur admin_features_router

# === ENDPOINT DE TEST POUR LES FONCTIONNALITÉS ===
@app.get("/test-features")
async def test_features():
    """Test endpoint pour vérifier les fonctionnalités"""
    try:
        features = load_features_config()
        return {
            "status": "success",
            "features": features,
            "config_file_exists": os.path.exists(CONFIG_FILE)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "config_file_exists": os.path.exists(CONFIG_FILE)
        }

# === ENDPOINTS VALIDÉS ===

@app.post("/tts")
async def tts_endpoint(request: dict):
    try:
        path = generate_speech(request["text"])
        return {"audio_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    try:
        # Validation du fichier audio
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")
        
        # Lire le contenu
        content = await file.read()
        
        # Sécuriser le nom de fichier
        import uuid
        safe_filename = f"{uuid.uuid4()}_{file.filename.replace(' ', '_')}"
        temp_path = f"static/{safe_filename}"
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        transcription = transcribe_audio(temp_path)
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(temp_path)
        except:
            pass
        
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Comptine ---
from services.suno_service import suno_service
from routes.rhyme_routes import router as rhyme_router
app.include_router(rhyme_router)

# ANCIEN ENDPOINT COMPTINE SUPPRIMÉ
# Voir routes/rhyme_routes.py pour le nouveau code propre

@app.get("/check_task_status/{task_id}")
async def check_task_status(task_id: str):
    """
    Vérifie le statut d'une tâche musicale Suno AI
    """
    try:
        result = await suno_service.check_task_status(task_id)
        return result
    except Exception as e:
        print(f"❌ Erreur vérification statut Suno: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification : {str(e)}")

@app.post("/test_rhyme_simple/")
async def test_rhyme_simple():
    """
    Endpoint de test ultra-simple pour diagnostiquer les erreurs
    """
    try:
        return {
            "status": "ok",
            "message": "Test endpoint fonctionne",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/diagnostic/suno")
async def diagnostic_suno():
    """
    Endpoint de diagnostic pour vérifier la configuration Suno
    """
    suno_key = os.getenv("SUNO_API_KEY")
    suno_url = os.getenv("SUNO_BASE_URL")
    
    return {
        "service": "Suno AI",
        "api_key_configured": bool(suno_key and suno_key != "None" and not suno_key.startswith("your_suno")),
        "api_key_value": f"{suno_key[:10]}..." if suno_key and len(suno_key) > 10 else suno_key,
        "base_url": suno_url,
        "service_initialized": bool(suno_service.api_key),
        "service_api_key": f"{suno_service.api_key[:10]}..." if suno_service.api_key and len(str(suno_service.api_key)) > 10 else str(suno_service.api_key),
        "service_base_url": suno_service.base_url,
        "status": "ready" if (suno_key and suno_key != "None" and not suno_key.startswith("your_suno")) else "not_configured"
    }

@app.post("/suno-callback")
async def suno_callback(request: Request):
    """
    Endpoint de callback pour recevoir les notifications de Suno AI
    Requis par l'API Suno mais nous utilisons le polling avec check_task_status
    """
    try:
        data = await request.json()
        print(f"📩 Callback Suno reçu: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return {"status": "received"}
    except Exception as e:
        print(f"❌ Erreur callback Suno: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/test-suno")
async def test_suno():
    """
    Endpoint de test pour vérifier l'appel direct à l'API Suno
    """
    try:
        test_lyrics = "Petit escargot, porte sur son dos, sa maisonnette. Aussitôt qu'il pleut, il est tout heureux, il sort sa tête."
        
        result = await suno_service.generate_musical_nursery_rhyme(
            lyrics=test_lyrics,
            rhyme_type="animal",
            title="Test Petit Escargot"
        )
        
        return {
            "test": "Suno API",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        import traceback
        return {
            "test": "Suno API",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }

# --- Histoire Audio ---
# Ancien modèle remplacé par ValidatedAudioStoryRequest dans validators.py

@app.post("/generate_audio_story/")
async def generate_audio_story(request: dict):
    try:
        # Validation des données d'entrée
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        story_type = request.get("story_type", "aventure")
        custom_request = request.get("custom_request", "")
        
        prompt = f"Écris une histoire courte et captivante pour enfants sur le thème : {story_type}.\n"
        if custom_request:
            prompt += f"Demande spécifique : {custom_request}\n"
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
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if content:
            content = content.strip()
        else:
            content = ""
        
        # Extraire le titre et le contenu si le format est respecté
        title = f"Histoire {story_type}"  # Titre par défaut
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
        voice = request.get("voice")
        if voice:
            try:
                # Utiliser le contenu de l'histoire pour l'audio, pas le titre
                # Utiliser le titre comme nom de fichier pour l'audio
                audio_path = generate_speech(story_content, voice=voice, filename=title)
                print(f"✅ Audio généré avec la voix: {voice}")
            except Exception as audio_error:
                print(f"⚠️ Erreur génération audio: {audio_error}")
                audio_path = None
        
        return {
            "title": title,
            "content": story_content,
            "audio_path": audio_path,
            "audio_generated": audio_path is not None,
            "type": "audio"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération histoire: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")

# --- Coloriage ---
# Ancien modèle remplacé par ValidatedColoringRequest dans validators.py

# Instance globale du générateur de coloriage (GPT-4o-mini + DALL-E 3)
# Utilisation de l'initialisation paresseuse pour éviter les erreurs au démarrage
coloring_generator_instance = None

def get_coloring_generator():
    """Obtient l'instance du générateur de coloriage (lazy initialization)"""
    global coloring_generator_instance
    if coloring_generator_instance is None:
        coloring_generator_instance = ColoringGeneratorGPT4o()
    return coloring_generator_instance

@app.post("/generate_coloring/")
@app.post("/generate_coloring/{content_type_id}")
async def generate_coloring(request: dict, content_type_id: int = None):
    """
    Génère un coloriage basé sur un thème avec GPT-4o-mini + gpt-image-1
    Supporte deux formats d'URL pour compatibilité frontend
    Organisation OpenAI vérifiée requise pour gpt-image-1
    """
    try:
        # Validation des données d'entrée
        theme = request.get("theme", "animaux")
        custom_prompt = request.get("custom_prompt")  # Prompt personnalisé optionnel
        with_colored_model = request.get("with_colored_model", True)  # Par défaut avec modèle
        
        if custom_prompt:
            print(f"[COLORING] Generation coloriage personnalisé gpt-image-1: '{custom_prompt}' ({'avec' if with_colored_model else 'sans'} modèle coloré)")
        else:
            print(f"[COLORING] Generation coloriage gpt-image-1: {theme} ({'avec' if with_colored_model else 'sans'} modèle coloré) (content_type_id={content_type_id})")
        
        # Vérifier la clé API OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        # Obtenir l'instance du générateur
        generator = get_coloring_generator()
        
        # Debug: afficher les paramètres
        print(f"[DEBUG] Parametres: theme={theme}, with_colored_model={with_colored_model}, custom_prompt={custom_prompt}")
        
        # Générer le coloriage avec GPT-4o-mini (analyse) + gpt-image-1 (génération)
        result = await generator.generate_coloring_from_theme(theme, with_colored_model, custom_prompt)
        
        print(f"[DEBUG] Resultat recu: {result.get('success', False)}")
        
        if result.get("success") == True:
            return {
                "status": "success",
                "theme": theme,
                "images": result.get("images", []),
                "message": "Coloriage généré avec succès avec gpt-image-1 !",
                "type": "coloring",
                "model": "gpt-image-1"
            }
        else:
            error_message = result.get("error", "Erreur inconnue lors de la génération du coloriage")
            raise HTTPException(
                status_code=500, 
                detail=f"❌ La création du coloriage a échoué : {error_message}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération coloriage: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")


@app.post("/upload_photo_for_coloring/")
async def upload_photo_for_coloring(file: UploadFile = File(...)):
    """
    Upload une photo pour la convertir en coloriage
    """
    try:
        print(f"📸 Upload photo pour coloriage: {file.filename}")
        print(f"   Type MIME: {file.content_type}")
        
        # Vérifier le type de fichier
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Format de fichier non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
            )
        
        # Créer un nom de fichier unique
        unique_filename = f"upload_{uuid.uuid4().hex[:8]}{file_ext}"
        upload_path = Path("static/uploads/coloring") / unique_filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"   Sauvegarde vers: {upload_path}")
        
        # Sauvegarder le fichier en chunks pour éviter timeout
        file_size = 0
        with open(upload_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                buffer.write(chunk)
                file_size += len(chunk)
        
        print(f"   Taille: {file_size} bytes")
        
        print(f"✅ Photo sauvegardée: {unique_filename}")
        
        return {
            "status": "success",
            "message": "Photo uploadée avec succès",
            "file_path": str(upload_path),
            "filename": unique_filename,
            "url": f"{BASE_URL}/static/uploads/coloring/{unique_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur upload photo: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload : {str(e)}")


@app.post("/convert_photo_to_coloring/")
async def convert_photo_to_coloring(request: dict):
    """
    Convertit une photo uploadée en coloriage avec GPT-4o-mini + gpt-image-1
    """
    try:
        # Récupérer les paramètres
        photo_path = request.get("photo_path")
        custom_prompt = request.get("custom_prompt")
        
        if not photo_path:
            raise HTTPException(
                status_code=400,
                detail="Le chemin de la photo est requis (photo_path)"
            )
        
        # Convertir en chemin absolu si c'est un chemin relatif
        photo_path_obj = Path(photo_path)
        if not photo_path_obj.is_absolute():
            photo_path_obj = Path.cwd() / photo_path
        
        photo_path = str(photo_path_obj)
        
        # Récupérer le choix de modèle coloré
        with_colored_model = request.get("with_colored_model", True)  # Par défaut avec modèle
        print(f"[COLORING] Conversion photo en coloriage avec gpt-image-1 ({'avec' if with_colored_model else 'sans'} modèle coloré): {photo_path}")
        
        # Vérifier que le fichier existe
        if not photo_path_obj.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Photo introuvable: {photo_path}"
            )
        
        # Obtenir l'instance du générateur
        generator = get_coloring_generator()
        
        # Convertir avec GPT-4o-mini (analyse) + gpt-image-1 (génération)
        result = await generator.generate_coloring_from_photo(
            photo_path=photo_path,
            custom_prompt=custom_prompt,
            with_colored_model=with_colored_model
        )
        
        if result.get("success") == True:
            return {
                "status": "success",
                "images": result.get("images", []),
                "description": result.get("description"),
                "message": "Photo convertie en coloriage avec succès !",
                "type": "coloring",
                "source": "photo",
                "model": "gpt-image-1"
            }
        else:
            error_message = result.get("error", "Erreur inconnue lors de la conversion")
            print(f"❌ Échec conversion: {error_message}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur conversion : {error_message}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur conversion photo: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la conversion : {str(e)}")

# --- Bandes Dessinées ---

# Modèles pour les BD
from typing import List, Dict, Any
from pydantic import BaseModel

# Ancien modèle remplacé par ValidatedComicRequest dans validators.py
    
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
async def generate_comic(request: dict):
    """
    Génère une bande dessinée complète avec IA
    """
    try:
        # Validation des données d'entrée
        theme = request.get("theme", "aventure")
        art_style = request.get("art_style", "cartoon")
        story_length = request.get("story_length", "court")
        print(f"📚 Génération BD: {theme} / {art_style} / {story_length}")
        
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        # Convertir la requête en dictionnaire
        request_data = {
            "theme": theme,
            "story_length": story_length,
            "art_style": art_style,
            "custom_request": request.get("custom_request", ""),
            "characters": request.get("characters", []),
            "setting": request.get("setting", "")
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

# --- Themes pour l'animation ---
@app.get("/themes")
async def get_themes():
    """
    Retourne la liste des thèmes disponibles pour les animations
    """
    themes = [
        {"id": "space", "name": "Espace", "description": "Aventures dans l'espace"},
        {"id": "ocean", "name": "Océan", "description": "Aventures sous-marines"},
        {"id": "forest", "name": "Forêt", "description": "Aventures dans la nature"},
        {"id": "city", "name": "Ville", "description": "Aventures urbaines"},
        {"id": "adventure", "name": "Aventure", "description": "Aventures génériques"},
        {"id": "fantasy", "name": "Fantasy", "description": "Monde fantastique"},
        {"id": "cartoon", "name": "Cartoon", "description": "Style cartoon classique"}
    ]
    return {"themes": themes}

# --- Animation ---
@app.post("/generate_animation/")
@app.post("/generate-quick")  # Route alternative pour compatibilité frontend
async def generate_animation(request: AnimationRequest):
    """
    Génère une VRAIE animation avec les APIs Wavespeed et Fal AI
    """
    try:
        # Extraire les paramètres depuis le modèle Pydantic
        style = request.style
        theme = request.theme
        duration = request.duration
        mode = request.mode

        print(f"🎬 VRAIE Génération animation: {theme} / {style} / {duration}s / mode: {mode}")

        task_id = str(uuid.uuid4())
        print(f"📋 Task ID créé: {task_id}")

        # Stocker les informations de la tâche
        task_storage[task_id] = {
            "start_time": time.time(),
            "theme": theme,
            "duration": duration,
            "style": style,
            "mode": mode,
            "status": "processing"
        }

        # Lancer la génération en arrière-plan
        import asyncio
        asyncio.create_task(generate_real_animation_task(task_id, theme, duration))

        # Retourner immédiatement le task_id
        result = {
            "task_id": task_id,
            "status": "processing",
            "message": f"Animation '{theme}' en cours de génération RÉELLE...",
            "estimated_time": "5-7 minutes",
            "style": style,
            "theme": theme,
            "duration": duration
        }

        print(f"✅ Task lancée: {result}")
        return result

    except Exception as e:
        print(f"❌ Erreur génération animation: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération de l'animation : {str(e)}")

# Stockage temporaire des tâches en cours (en production, utiliser Redis/DB)
task_storage = {}

async def generate_real_animation_task(task_id: str, theme: str, duration: int):
    """
    Tâche en arrière-plan pour la génération réelle d'animation
    """
    try:
        print(f"🚀 Démarrage génération réelle pour {task_id}")
        
        # Mettre à jour le statut
        task_storage[task_id]["status"] = "generating"
        
        # Vérifier si on a les API keys pour le vrai système
        has_real_apis = bool(os.getenv("WAVESPEED_API_KEY") and os.getenv("FAL_API_KEY"))
        
        if has_real_apis:
            # Utiliser le générateur seedance réel
            generator = RealAnimationGenerator()
            print(f"🎬 Utilisation du VRAI système seedance")
        else:
            # Utiliser le générateur local complet
            generator = LocalAnimationGenerator()
            print(f"🎬 Utilisation du générateur LOCAL complet")
        
        # Générer l'animation complète
        animation_result = await generator.generate_complete_animation(theme, duration)
        
        # Stocker le résultat
        task_storage[task_id]["result"] = animation_result
        task_storage[task_id]["status"] = "completed"
        
        print(f"✅ Animation {task_id} générée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur génération {task_id}: {e}")
        task_storage[task_id]["status"] = "failed" 
        task_storage[task_id]["error"] = str(e)

@app.get("/status/{task_id}")
async def get_animation_status(task_id: str):
    """
    Récupère le statut RÉEL d'une tâche d'animation
    """
    try:
        # Vérifier si la tâche existe dans notre stockage
        if task_id not in task_storage:
            print(f"❌ Task ID {task_id} non trouvé")
            raise HTTPException(status_code=404, detail="Tâche non trouvée")
        
        task_info = task_storage[task_id]
        status = task_info.get("status", "processing")
        
        print(f"📊 Statut RÉEL demandé pour {task_id}: {status}")
        
        if status == "processing" or status == "generating":
            # Encore en traitement RÉEL
            current_time = time.time()
            elapsed_seconds = current_time - task_info["start_time"]
            
            # Estimation temps selon le mode
            estimated_duration = 180  # 3 minutes en mode démo, 6.5 minutes en mode réel
            progress = min(int((elapsed_seconds / estimated_duration) * 100), 95)
            
            result = {
                "type": "result", 
                "data": {
                    "task_id": task_id,
                    "status": "processing",
                    "progress": progress,
                    "message": f"Génération RÉELLE en cours... {progress}%",
                    "estimated_remaining": max(int(estimated_duration - elapsed_seconds), 30)
                }
            }
            print(f"⏳ Task RÉEL {task_id} en cours: {progress}%")
        elif status == "completed":
            # Animation RÉELLE terminée !
            animation_result = task_info.get("result", {})
            result = {
                "type": "result",
                "data": animation_result
            }
            print(f"✅ Animation RÉELLE {task_id} terminée et retournée!")
            
        elif status == "failed":
            # Erreur de génération
            error_msg = task_info.get("error", "Erreur inconnue")
            result = {
                "type": "result",
                "data": {
                    "task_id": task_id,
                    "status": "failed",
                    "error": error_msg,
                    "message": f"Échec de la génération: {error_msg}"
                }
            }
            print(f"❌ Animation {task_id} échouée: {error_msg}")
            
        else:
            # Statut inconnu - fallback
            result = {
                "type": "result", 
                "data": {
                    "task_id": task_id,
                    "status": "unknown",
                    "message": f"Statut inconnu: {status}"
                }
            }
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur récupération statut: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut : {str(e)}")

# === ROUTES D'AUTHENTIFICATION JWT ===

# === ENDPOINTS D'AUTHENTIFICATION ===
# Authentification gérée par Supabase - endpoints supprimés car inutiles avec Vercel

# Configuration pour supprimer les erreurs de connexion dans les logs
import asyncio
import logging

def ignore_connection_errors(loop, context):
    """Gestionnaire pour ignorer les erreurs de connexion fermée"""
    if 'exception' not in context:
        return
        
    exception = context['exception']
    if isinstance(exception, (ConnectionResetError, OSError)):
        # Ignorer silencieusement les erreurs de connexion
        if any(msg in str(exception) for msg in [
            'WinError 10054', 
            'connexion existante', 
            'connection lost',
            'connection reset'
        ]):
            return
    
    # Pour les autres erreurs, utiliser le gestionnaire par défaut
    loop.default_exception_handler(context)

# Appliquer le gestionnaire au loop asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Si le loop est déjà en cours, on ne peut pas définir un gestionnaire
        pass
    else:
        loop.set_exception_handler(ignore_connection_errors)
except RuntimeError:
    # Pas de loop actuel, c'est OK
    pass

# === SERVIR LE FRONTEND (SPA) ===

@app.get("/", include_in_schema=False)
async def serve_root():
    """Servez le build React à la racine."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"detail": "Not Found"}


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    """Fallback pour le routage côté client (évite 404 sur refresh)."""
    # Laisse les routes d'API et les assets gérer leur 404 normalement
    if full_path.startswith(("api", "static", "assets", "docs", "openapi.json", "redoc")):
        raise HTTPException(status_code=404, detail="Not Found")
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Not Found")

# === ENDPOINTS DE TEST RATE LIMITING ===

# Endpoints de test supprimés car inutiles avec Vercel

if __name__ == "__main__":
    import uvicorn
    import threading
    import os.path
    
    # Configuration de base
    config = {
        "app": app,
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8006)),
    }
    
    # Configuration SSL pour le développement
    ssl_keyfile = "../../ssl/dev.key"
    ssl_certfile = "../../ssl/dev.crt"
    
    # Mode debug pour le développement
    if os.getenv("ENVIRONMENT", "development").lower() != "production":
        config["log_level"] = "debug"
        
        # Vérifier si les certificats SSL existent
        if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
            config["ssl_keyfile"] = ssl_keyfile
            config["ssl_certfile"] = ssl_certfile
            print(f"🔒 Démarrage du serveur FRIDAY sur HTTPS://{config['host']}:{config['port']}")
        else:
            print(f"⚠️ Certificats SSL non trouvés, démarrage en HTTP://{config['host']}:{config['port']}")
    else:
        config["log_level"] = "info"
        print(f"🚀 Démarrage du serveur FRIDAY sur HTTP://{config['host']}:{config['port']}")
    
    # En développement, lancer aussi un serveur HTTP sur un port différent si pas de SSL
    if os.getenv("ENVIRONMENT", "development").lower() != "production" and not config.get("ssl_keyfile"):
        def run_http_server():
            http_config = {
                "app": app,
                "host": "0.0.0.0",
                "port": 8007,  # Port HTTP différent
                "log_level": "debug"
            }
            print(f"🌐 Serveur HTTP de secours sur http://{http_config['host']}:{http_config['port']}")
            uvicorn.run(**http_config)

        # Lancer le serveur HTTP en arrière-plan
        http_thread = threading.Thread(target=run_http_server, daemon=True)
        http_thread.start()

    uvicorn.run(**config)

# Fonction asynchrone pour envoyer l'email en arrière-plan
async def send_email_background(contact_form: ContactForm):
    """Envoie un email en arrière-plan (non bloquant)"""
    try:
        # Configuration Resend
        resend_api_key = os.getenv("RESEND_API_KEY")
        receiver_email = os.getenv("CONTACT_EMAIL", "contact@herbbie.com")

        if not resend_api_key:
            print("❌ RESEND_API_KEY non configuré")
            return

        if not receiver_email:
            print("❌ CONTACT_EMAIL non configuré")
            return

        # Création du contenu HTML de l'email
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">HERBBIE</h1>
                <p style="color: #e8e8e8; margin: 10px 0 0 0; font-size: 14px;">Nouveau message de contact</p>
            </div>

            <div style="padding: 40px 30px;">
                <div style="background: #f8f9fa; border-radius: 8px; padding: 30px; margin-bottom: 30px;">
                    <h2 style="color: #333; margin-top: 0; font-size: 20px;">📬 Nouveau message reçu</h2>

                    <div style="margin: 25px 0;">
                        <div style="display: flex; margin-bottom: 15px;">
                            <strong style="width: 100px; color: #666;">Prénom:</strong>
                            <span style="color: #333;">{contact_form.firstName}</span>
                        </div>
                        <div style="display: flex; margin-bottom: 15px;">
                            <strong style="width: 100px; color: #666;">Nom:</strong>
                            <span style="color: #333;">{contact_form.lastName}</span>
                        </div>
                        <div style="display: flex; margin-bottom: 15px;">
                            <strong style="width: 100px; color: #666;">Email:</strong>
                            <span style="color: #333;">{contact_form.email}</span>
                        </div>
                        <div style="display: flex; margin-bottom: 25px;">
                            <strong style="width: 100px; color: #666;">Sujet:</strong>
                            <span style="color: #333;">{contact_form.subject}</span>
                        </div>
                    </div>

                    <div style="border-top: 1px solid #dee2e6; padding-top: 25px;">
                        <h3 style="color: #333; margin-top: 0; font-size: 16px;">💬 Message:</h3>
                        <div style="background: white; border: 1px solid #e9ecef; border-radius: 6px; padding: 20px; margin-top: 10px;">
                            <p style="margin: 0; line-height: 1.6; color: #333; white-space: pre-line;">{contact_form.message}</p>
                        </div>
                    </div>
                </div>

                <div style="text-align: center; color: #666; font-size: 12px; border-top: 1px solid #dee2e6; padding-top: 20px;">
                    <p>Cet email a été envoyé automatiquement depuis le formulaire de contact Herbbie.</p>
                    <p>© 2024 Herbbie - Tous droits réservés</p>
                </div>
            </div>
        </div>
        """

        # Contenu texte brut (fallback)
        text_content = f"""HERBBIE - Nouveau message de contact

Prénom: {contact_form.firstName}
Nom: {contact_form.lastName}
Email: {contact_form.email}
Sujet: {contact_form.subject}

Message:
{contact_form.message}

---
Cet email a été envoyé automatiquement depuis le formulaire de contact Herbbie.
"""

        # Envoi via Resend API
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "Herbbie <noreply@herbbie.com>",
                    "to": [receiver_email],
                    "subject": f"HERBBIE - {contact_form.subject}",
                    "html": html_content,
                    "text": text_content,
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Email envoyé avec succès via Resend - ID: {result.get('id', 'N/A')}")
                print(f"📧 De: {contact_form.email} → À: {receiver_email}")
            else:
                error_msg = response.text
                print(f"❌ Erreur Resend API ({response.status_code}): {error_msg}")
                raise Exception(f"Resend API error: {error_msg}")

    except Exception as e:
        print(f"❌ Erreur envoi email via Resend: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")


# Endpoint pour envoyer un email de contact (réponse immédiate)
@app.post("/api/contact")
async def send_contact_email(contact_form: ContactForm):
    """Envoie un email depuis le formulaire de contact (réponse immédiate)"""
    try:
        # Vérifier la configuration
        if not os.getenv("RESEND_API_KEY"):
            raise HTTPException(status_code=500, detail="Configuration Resend manquante")

        # Lancer l'envoi en arrière-plan (non bloquant)
        asyncio.create_task(send_email_background(contact_form))
        
        # Réponse immédiate au client
        return {"message": "Email en cours d'envoi"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")