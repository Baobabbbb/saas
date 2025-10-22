from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
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
from services.comics_generator_gpt4o import ComicsGeneratorGPT4o
from services.real_animation_generator import RealAnimationGenerator
from services.local_animation_generator import LocalAnimationGenerator
from services.sora2_zseedance_generator import Sora2ZseedanceGenerator
from services.sora2_generator import Sora2Generator
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

# Test immédiat de la configuration Runway
runway_key = os.getenv('RUNWAY_API_KEY')
print(f"🔑 TEST RUNWAY_API_KEY: {'présente' if runway_key else 'ABSENTE'}")
if runway_key:
    print(f"🔑 TEST Format: {'✅ OK' if runway_key.startswith('key_') else '❌ ERREUR'}")
    print(f"🔑 TEST Longueur: {len(runway_key)}")
    print(f"🔑 TEST Préfixe: {runway_key[:15]}...")

    # Test de l'import du générateur
    try:
        from services.sora2_zseedance_generator import sora2_zseedance_generator
        print("✅ TEST Générateur importé avec succès")
        print(f"✅ TEST Plateforme sélectionnée: {sora2_zseedance_generator.selected_platform}")
        print(f"✅ TEST Plateformes disponibles: {[name for name, config in sora2_zseedance_generator.sora_platforms.items() if config['available']]}")
    except Exception as e:
        print(f"❌ TEST ERREUR import générateur: {e}")
else:
    print("❌ TEST Runway API key manquante - vérifiez Railway Variables")

print("=" * 60)
print(f"📝 TEXT_MODEL: {TEXT_MODEL}")
print(f"🌐 BASE_URL: {BASE_URL}")
print(f"✅ OPENAI_API_KEY: {'Configurée' if os.getenv('OPENAI_API_KEY') else '❌ NON CONFIGURÉE'}")
print(f"🎵 SUNO_API_KEY: {'Configurée' if os.getenv('SUNO_API_KEY') else '❌ NON CONFIGURÉE'}")
print(f"🎨 STABILITY_API_KEY: {'Configurée' if os.getenv('STABILITY_API_KEY') else '❌ NON CONFIGURÉE'}")

        # Vérification des clés API pour l'animation
runway_key = os.getenv('RUNWAY_API_KEY')
fal_key = os.getenv('FAL_API_KEY')

print(f"🎬 RUNWAY_API_KEY: {'Configurée' if runway_key else '❌ NON CONFIGURÉE'}")
if runway_key:
    print(f"   🔑 Format: {'✅ OK' if runway_key.startswith('key_') else '❌ ERREUR - doit commencer par key_'}")
    print(f"   📏 Longueur: {len(runway_key)} caractères")
    print(f"   👁️  Aperçu: {runway_key[:20]}...{runway_key[-10:] if len(runway_key) > 30 else runway_key}")

    # Afficher la clé complète pour vérification
    print(f"   🔐 CLÉ COMPLÈTE (pour vérification): {runway_key}")
    print("   ⚠️  ATTENTION: Cette clé sera visible dans les logs Railway !")

print(f"🔧 FAL_API_KEY: {'Configurée' if fal_key else '❌ NON CONFIGURÉE'}")
if fal_key:
    print(f"   📏 Longueur: {len(fal_key)} caractères")

print("=" * 60)

app = FastAPI(title="API FRIDAY - Contenu Créatif IA", version="2.0", description="API pour générer du contenu créatif pour enfants : BD, coloriages, histoires, comptines")

# Modèles pour l'API Animation
class AnimationRequest(BaseModel):
    theme: str
    duration: Optional[int] = 30
    style: Optional[str] = "cartoon"
    custom_prompt: Optional[str] = None

class GenerateQuickRequest(BaseModel):
    theme: str = "space"
    duration: int = 30
    style: str = "cartoon"
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

# Sécurité des cookies et protection contre les attaques Host Header
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "herbbie.com",
        "www.herbbie.com",
        "*.railway.app",  # Pour Railway
        "localhost",
        "127.0.0.1"
    ]
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

# Route pour servir le favicon.ico
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon.ico"""
    favicon_path = static_dir / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    # Fallback vers le logo si favicon n'existe pas
    logo_path = static_dir / "logo_v.png"
    if logo_path.exists():
        return FileResponse(logo_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Favicon not found")

# Endpoint pour fournir les variables d'environnement au frontend
@app.get("/api/config")
async def get_config():
    """Fournit les variables de configuration nécessaires au frontend"""
    return {
        "supabase_url": os.getenv("SUPABASE_URL", "https://xfbmdeuzuyixpmouhqcv.supabase.co"),
        "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw"),
        "base_url": BASE_URL
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
    Génère un coloriage basé sur un thème avec GPT-4o-mini + gpt-image-1-mini-mini
    Supporte deux formats d'URL pour compatibilité frontend
    Organisation OpenAI vérifiée requise pour gpt-image-1-mini-mini
    """
    try:
        # Validation des données d'entrée
        theme = request.get("theme", "animaux")
        custom_prompt = request.get("custom_prompt")  # Prompt personnalisé optionnel
        with_colored_model = request.get("with_colored_model", True)  # Par défaut avec modèle
        
        if custom_prompt:
            print(f"[COLORING] Generation coloriage personnalisé gpt-image-1-mini-mini: '{custom_prompt}' ({'avec' if with_colored_model else 'sans'} modèle coloré)")
        else:
            print(f"[COLORING] Generation coloriage gpt-image-1-mini-mini: {theme} ({'avec' if with_colored_model else 'sans'} modèle coloré) (content_type_id={content_type_id})")
        
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
        
        # Générer le coloriage avec GPT-4o-mini (analyse) + gpt-image-1-mini-mini (génération)
        result = await generator.generate_coloring_from_theme(theme, with_colored_model, custom_prompt)
        
        print(f"[DEBUG] Resultat recu: {result.get('success', False)}")
        
        if result.get("success") == True:
            return {
                "status": "success",
                "theme": theme,
                "images": result.get("images", []),
                "message": "Coloriage généré avec succès avec gpt-image-1-mini-mini !",
                "type": "coloring",
                "model": "gpt-image-1-mini"
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
    Convertit une photo uploadée en coloriage avec GPT-4o-mini + gpt-image-1-mini
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
        print(f"[COLORING] Conversion photo en coloriage avec gpt-image-1-mini ({'avec' if with_colored_model else 'sans'} modèle coloré): {photo_path}")
        
        # Vérifier que le fichier existe
        if not photo_path_obj.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Photo introuvable: {photo_path}"
            )
        
        # Obtenir l'instance du générateur
        generator = get_coloring_generator()
        
        # Convertir avec GPT-4o-mini (analyse) + gpt-image-1-mini (génération)
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
                "model": "gpt-image-1-mini"
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

# Instance globale du générateur de BD (lazy initialization)
comics_generator_instance = None

def get_comics_generator():
    """Obtient l'instance du générateur de BD (lazy initialization)"""
    global comics_generator_instance
    if comics_generator_instance is None:
        comics_generator_instance = ComicsGeneratorGPT4o()
    return comics_generator_instance

@app.post("/generate_comic/")
async def generate_comic(request: dict):
    """
    Lance la génération d'une bande dessinée en arrière-plan
    Retourne immédiatement un task_id pour éviter les timeouts
    """
    try:
        # Récupérer les paramètres
        theme = request.get("theme", "espace")
        art_style = request.get("art_style", "cartoon")
        num_pages = request.get("num_pages", 1)
        custom_prompt = request.get("custom_prompt")
        character_photo_path = request.get("character_photo_path")
        
        print(f"📚 Lancement génération BD: thème={theme}, style={art_style}, pages={num_pages}")
        
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400,
                detail="❌ Clé API OpenAI non configurée"
            )
        
        # Créer un task_id unique
        task_id = str(uuid.uuid4())
        print(f"📋 Task BD créé: {task_id}")
        
        # Stocker les informations de la tâche
        comic_task_storage[task_id] = {
            "start_time": time.time(),
            "theme": theme,
            "art_style": art_style,
            "num_pages": num_pages,
            "custom_prompt": custom_prompt,
            "character_photo_path": character_photo_path,
            "status": "processing"
        }
        
        # Lancer la génération en arrière-plan
        import asyncio
        asyncio.create_task(generate_comic_task(task_id, theme, art_style, num_pages, custom_prompt, character_photo_path))
        
        # Retourner immédiatement le task_id
        estimated_time = f"{num_pages * 1.2:.0f}-{num_pages * 1.5:.0f} minutes"
        result = {
            "task_id": task_id,
            "status": "processing",
            "message": f"Bande dessinée en cours de création...",
            "estimated_time": estimated_time,
            "theme": theme,
            "art_style": art_style,
            "num_pages": num_pages
        }
        
        print(f"✅ Task BD lancée: {result}")
        return result
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lancement BD: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors du lancement: {str(e)}")


@app.post("/upload_character_photo/")
async def upload_character_photo(file: UploadFile = File(...)):
    """
    Upload une photo de personnage pour l'intégrer dans une BD
    """
    try:
        print(f"📸 Upload photo personnage: {file.filename}")
        
        # Vérifier le type de fichier
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
            )
        
        # Créer un nom unique
        unique_filename = f"character_{uuid.uuid4().hex[:8]}{file_ext}"
        upload_path = Path("static/uploads/comics") / unique_filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder
        with open(upload_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
        
        print(f"✅ Photo personnage sauvegardée: {unique_filename}")
        
        return {
            "status": "success",
            "message": "Photo uploadée avec succès",
            "file_path": str(upload_path),
            "filename": unique_filename,
            "url": f"{BASE_URL}/static/uploads/comics/{unique_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur upload photo: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur upload: {str(e)}")

@app.get("/status_comic/{task_id}")
async def get_comic_status(task_id: str):
    """
    Récupère le statut d'une tâche de génération de BD
    """
    try:
        # Vérifier si la tâche existe
        if task_id not in comic_task_storage:
            print(f"❌ Task BD {task_id} non trouvé")
            raise HTTPException(status_code=404, detail="Tâche non trouvée")
        
        task_info = comic_task_storage[task_id]
        status = task_info.get("status", "processing")
        
        print(f"📊 Statut BD demandé pour {task_id}: {status}")
        
        if status == "processing" or status == "generating":
            # Encore en traitement
            current_time = time.time()
            elapsed_seconds = current_time - task_info["start_time"]
            
            # Estimation temps selon le nombre de pages (70s par page)
            num_pages = task_info.get("num_pages", 1)
            estimated_duration = num_pages * 70
            progress = min(int((elapsed_seconds / estimated_duration) * 100), 95)
            
            result = {
                "type": "result", 
                "data": {
                    "task_id": task_id,
                    "status": "processing",
                    "progress": progress,
                    "message": f"Génération de la BD en cours... {progress}%",
                    "estimated_remaining": max(int(estimated_duration - elapsed_seconds), 10)
                }
            }
            print(f"⏳ Task BD {task_id} en cours: {progress}%")
            
        elif status == "completed":
            # BD terminée !
            comic_result = task_info.get("result", {})
            result = {
                "type": "result",
                "data": comic_result
            }
            print(f"✅ BD {task_id} terminée et retournée!")
            
        elif status == "failed":
            # Erreur de génération
            error_msg = task_info.get("error", "Erreur inconnue")
            result = {
                "type": "result",
                "data": {
                    "status": "failed",
                    "error": error_msg
                }
            }
            print(f"❌ Task BD {task_id} échouée: {error_msg}")
        else:
            result = {
                "type": "result",
                "data": {
                    "status": status,
                    "message": "Statut inconnu"
                }
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur récupération statut BD: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur statut: {str(e)}")


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
async def generate_animation_post(
    request: AnimationRequest
):
    """
    Génère une animation via POST avec body JSON
    """
    return await _generate_animation_logic(
        theme=request.theme,
        duration=request.duration or 30,
        style=request.style or "cartoon",
        custom_prompt=request.custom_prompt
    )

@app.post("/generate-quick-json")
async def generate_quick_json(
    request: GenerateQuickRequest
):
    """
    Génère une animation via POST avec body JSON uniquement (nouvelle route)
    """
    return await _generate_animation_logic(
        theme=request.theme,
        duration=request.duration,
        style=request.style,
        custom_prompt=request.custom_prompt
    )

@app.get("/generate-quick")   # Ajouter support GET pour compatibilité
async def generate_animation(
    theme: str = "space",
    duration: int = 30,
    style: str = "cartoon",
    custom_prompt: str = None
):
    """
    Génère une VRAIE animation avec Runway ML Veo 3.1 Fast (workflow zseedance)
    Supporte les requêtes GET avec query parameters - PLUS DE MODE, toujours vrai pipeline
    """
    return await _generate_animation_logic(theme, duration, style, custom_prompt)

async def _generate_animation_logic(
    theme: str,
    duration: int,
    style: str,
    custom_prompt: str = None
):
    """
    Logique commune de génération d'animation
    """
    try:
        # Nettoyer et valider le thème (gérer le cas "null")
        if isinstance(theme, str):
            theme = theme.strip().lower()
            if theme == "null" or theme == "" or not theme:
                theme = "space"

        # Valider et corriger les autres paramètres
        valid_themes = ["space", "ocean", "forest", "city", "adventure", "fantasy", "cartoon"]
        if theme not in valid_themes:
            print(f"⚠️ Thème invalide '{theme}', utilisation de 'space' par défaut")
            theme = "space"

        # Valider la durée
        try:
            duration = int(duration)
            if duration < 30 or duration > 300:
                duration = 30
        except:
            duration = 30

        # Valider le style
        valid_styles = ["cartoon", "3d", "manga", "comics", "realistic", "watercolor"]
        if style not in valid_styles:
            style = "cartoon"

        print(f"🎬 VRAIE Génération animation: {theme} / {style} / {duration}s / workflow: ZSEEDANCE")

        task_id = str(uuid.uuid4())
        print(f"📋 Task ID créé: {task_id}")

        # Stocker les informations de la tâche
        task_storage[task_id] = {
            "start_time": time.time(),
            "theme": theme,
            "duration": duration,
            "style": style,
            "workflow": "zseedance",
            "status": "processing"
        }

        # Génération selon le workflow zseedance.json (toujours le même pipeline)
        import asyncio
        asyncio.create_task(generate_zseedance_animation_task(task_id, theme, duration, style))

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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération de l'animation : {str(e)}")

# Stockage temporaire des tâches en cours (en production, utiliser Redis/DB)
task_storage = {}
comic_task_storage = {}

async def generate_zseedance_animation_task(task_id: str, theme: str, duration: int, style: str = "cartoon"):
    """
    Tâche en arrière-plan pour la génération selon le workflow zseedance.json
    Pipeline complet : Ideas → Prompts → Create Clips (Veo 3.1) → Create Sounds → Sequence Video
    """
    try:
        print(f"🚀 Démarrage génération ZSEEDANCE pour {task_id} (thème: {theme}, durée: {duration}s, style: {style})")

        # Mettre à jour le statut
        task_storage[task_id]["status"] = "generating"

        # Utiliser le générateur Sora2ZseedanceGenerator (workflow fidèle à zseedance.json)
        print(f"🔧 Initialisation du générateur Sora2ZseedanceGenerator...")
        try:
            generator = Sora2ZseedanceGenerator()
            print(f"✅ Générateur initialisé avec succès")
        except Exception as init_error:
            print(f"❌ ERREUR lors de l'initialisation du générateur: {init_error}")
            import traceback
            traceback.print_exc()
            raise init_error
        print(f"🎬 Utilisation du workflow ZSEEDANCE (n8n identique)")

        # Calculer le nombre de scènes selon la durée (comme zseedance : 10s par scène)
        num_scenes = max(3, duration // 10)  # Minimum 3 scènes, 10s par scène
        print(f"📊 Génération de {num_scenes} scènes de 10 secondes chacune")

        # Générer l'animation complète selon le workflow zseedance
        print(f"🚀 Appel generate_complete_animation_zseedance avec thème: {theme}")
        try:
            animation_result = await generator.generate_complete_animation_zseedance(theme)
            print(f"✅ generate_complete_animation_zseedance terminé avec résultat: {animation_result.get('status', 'unknown')}")
        except Exception as gen_error:
            print(f"❌ ERREUR lors de l'appel generate_complete_animation_zseedance: {gen_error}")
            import traceback
            traceback.print_exc()
            raise gen_error

        # Vérifier que nous avons bien une vidéo finale
        if animation_result.get("status") == "completed" and animation_result.get("final_video_url"):
            print(f"✅ Animation ZSEEDANCE {task_id} générée avec succès!")
            print(f"🎬 Vidéo finale: {animation_result['final_video_url'][:50]}...")
        else:
            print(f"⚠️ Animation générée mais pas de vidéo finale: {animation_result.get('status')}")

        # Stocker le résultat
        task_storage[task_id]["result"] = animation_result
        task_storage[task_id]["status"] = "completed"

    except Exception as e:
        print(f"❌ Erreur génération ZSEEDANCE {task_id}: {e}")
        import traceback
        traceback.print_exc()

        task_storage[task_id]["status"] = "failed"
        task_storage[task_id]["error"] = str(e)

async def generate_comic_task(task_id: str, theme: str, art_style: str, num_pages: int, custom_prompt: str, character_photo_path: str):
    """
    Tâche en arrière-plan pour la génération de BD
    """
    try:
        print(f"🚀 Démarrage génération BD pour {task_id}")
        
        # Mettre à jour le statut
        comic_task_storage[task_id]["status"] = "generating"
        
        # Obtenir le générateur
        generator = get_comics_generator()
        
        # Générer la BD complète
        result = await generator.create_complete_comic(
            theme=theme,
            num_pages=num_pages,
            art_style=art_style,
            custom_prompt=custom_prompt,
            character_photo_path=character_photo_path
        )
        
        # Stocker le résultat
        if result.get("success"):
            comic_task_storage[task_id]["result"] = {
                "status": "success",
                "comic_id": result["comic_id"],
                "title": result["title"],
                "synopsis": result["synopsis"],
                "pages": result["pages"],
                "total_pages": result["total_pages"],
                "theme": result["theme"],
                "art_style": result["art_style"],
                "generation_time": result["generation_time"]
            }
            comic_task_storage[task_id]["status"] = "completed"
            print(f"✅ BD {task_id} générée avec succès!")
        else:
            error_msg = result.get("error", "Erreur inconnue")
            comic_task_storage[task_id]["status"] = "failed"
            comic_task_storage[task_id]["error"] = error_msg
            print(f"❌ Échec BD {task_id}: {error_msg}")
        
    except Exception as e:
        print(f"❌ Erreur génération BD {task_id}: {e}")
        import traceback
        traceback.print_exc()
        comic_task_storage[task_id]["status"] = "failed" 
        comic_task_storage[task_id]["error"] = str(e)

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


async def generate_sora2_animation_task(task_id: str, theme: str, duration: int):
    """
    Tâche en arrière-plan pour la génération Sora 2 d'animation
    """
    try:
        print(f"🚀 Démarrage génération Sora 2 pour {task_id}")

        # Mettre à jour le statut
        task_storage[task_id]["status"] = "generating"

        # Utiliser le générateur Sora 2
        generator = Sora2Generator()
        print(f"🎬 Utilisation de SORA 2 (plateforme: {generator.selected_platform})")

        # Générer l'animation Sora 2
        animation_result = await generator.generate_complete_animation(theme, duration)

        # Stocker le résultat
        task_storage[task_id]["result"] = animation_result
        task_storage[task_id]["status"] = "completed"

        print(f"✅ Animation Sora 2 {task_id} générée avec succès!")

    except Exception as e:
        print(f"❌ Erreur génération Sora 2 {task_id}: {e}")
        task_storage[task_id]["status"] = "failed"
        task_storage[task_id]["error"] = str(e)

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
                    "from": "Herbbie <contact@herbbie.com>",
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
