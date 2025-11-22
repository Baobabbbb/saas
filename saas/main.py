from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Header, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ValidationError
from typing import Optional, List, Dict, Any
from unidecode import unidecode

# Modèles Pydantic pour la validation des requêtes
class ColoringRequest(BaseModel):
    theme: str
    with_colored_model: Optional[bool] = True
    custom_prompt: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        allow_none_optional = True
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
import jwt
import httpx
from fastapi import status

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from datetime import datetime
from services.tts import generate_speech
from services.stt import transcribe_audio

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

# Service d'unicité pour éviter les doublons
from services.uniqueness_service import uniqueness_service

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
BASE_URL = os.getenv("BASE_URL", "https://herbbie.com")

# Client Supabase pour le service d'unicité et Storage
from supabase import create_client, Client
from services.supabase_storage import init_storage_service, get_storage_service
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xfbmdeuzuyixpmouhqcv.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_AUTH_API_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
supabase_client: Client = None
if SUPABASE_SERVICE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    # Initialiser le service Storage
    init_storage_service(supabase_client, SUPABASE_URL)
    print("✅ Service Supabase Storage initialisé")

# Service de nettoyage automatique des fichiers locaux
from services.file_cleanup import run_scheduled_cleanup
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Démarrage silencieux - pas de logs sensibles

app = FastAPI(title="API FRIDAY - Contenu Créatif IA", version="2.0", description="API pour générer du contenu créatif pour enfants : BD, coloriages, histoires, comptines")

# Initialiser le scheduler pour le nettoyage automatique
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=run_scheduled_cleanup,
    trigger="interval",
    hours=1,  # Exécuter toutes les heures
    id="file_cleanup_job",
    name="Nettoyage automatique des fichiers locaux",
    replace_existing=True
)
scheduler.start()
print("✅ Scheduler de nettoyage automatique démarré (toutes les heures)")

# Arrêter le scheduler proprement lors de la fermeture
atexit.register(lambda: scheduler.shutdown())

# ============================================
# FONCTIONS D'AUTHENTIFICATION ET SÉCURITÉ
# ============================================

async def fetch_user_id_from_supabase(token: str) -> Optional[str]:
    """
    Valide le JWT via l'API Supabase et retourne l'identifiant utilisateur.
    Utilise l'endpoint /auth/v1/user pour garantir la vérification côté serveur.
    """
    if not token or not SUPABASE_URL or not SUPABASE_AUTH_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_AUTH_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("id") or data.get("user", {}).get("id")

        print(f"[SECURITY] JWT invalide (status={response.status_code}) : {response.text}")
    except httpx.HTTPError as exc:
        print(f"[SECURITY] Erreur lors de la validation JWT : {exc}")

    return None

async def extract_user_id_from_jwt(
    auth_token: Optional[str] = None,
    request: Optional[Request] = None
) -> Optional[str]:
    """
    Extrait le user_id depuis le JWT Supabase.
    Retourne None si le JWT n'est pas présent ou invalide.
    Compatible avec les JWT Supabase qui ont 'sub' comme claim du user_id.
    """
    if not auth_token or not auth_token.startswith("Bearer "):
        return None

    token = auth_token.split(" ")[1]
    return await fetch_user_id_from_supabase(token)


async def get_current_user_id(
    auth_token: Optional[str] = None,
    request_body: Optional[Dict[str, Any]] = None,
    request_obj: Optional[Request] = None
) -> Optional[str]:
    """
    Récupère le user_id depuis le JWT (prioritaire) ou depuis le body (fallback pour rétrocompatibilité).
    Utilisé pour les endpoints de génération pour éviter de casser le fonctionnement actuel.
    
    Args:
        auth_token: Header Authorization avec le JWT (Bearer token)
        request_body: Le body de la requête (dict) - utilisé dans les endpoints POST
        request_obj: Objet Request FastAPI - utilisé pour lire les headers si request_body n'est pas disponible
    
    Returns:
        user_id ou None si non trouvé
    """
    return await extract_user_id_from_jwt(auth_token, request_obj)


async def verify_admin(
    user_id: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    request: Optional[Request] = None,
    body: Optional[Dict[str, Any]] = None
) -> str:
    """
    Vérifie que l'utilisateur est admin.
    Extrait le user_id depuis le JWT ou le body, puis vérifie le rôle dans Supabase.
    Lève une HTTPException si l'utilisateur n'est pas admin.
    """
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Supabase non disponible"
        )
    
    # Récupérer le user_id depuis JWT uniquement
    if not user_id:
        user_id = await extract_user_id_from_jwt(authorization, request)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise. Fournissez un JWT valide dans le header Authorization."
        )
    
    # Vérifier le rôle admin dans la table profiles
    try:
        response = supabase_client.table('profiles').select('role').eq('id', user_id).single().execute()
        
        if not response.data or response.data.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux administrateurs"
            )
        
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        # Si l'utilisateur n'existe pas ou erreur de base, refuser l'accès
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )


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

# Pas de modèle Pydantic strict - on accepte n'importe quel dict

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
    # Sécurisation contre path traversal
    safe_filename = os.path.basename(filename)
    if safe_filename != filename or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")
    
    file_path = os.path.join("static", "generated", safe_filename)
    # Vérifier que le chemin résolu est bien dans le répertoire autorisé
    resolved_path = os.path.abspath(file_path)
    base_dir = os.path.abspath("static/generated")
    if not resolved_path.startswith(base_dir):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
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
    # Retirer la clé hardcodée en fallback pour sécurité
    # Les variables d'environnement doivent être configurées sur Railway
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_anon_key:
        raise HTTPException(
            status_code=500,
            detail="Configuration Supabase manquante. Vérifiez les variables d'environnement SUPABASE_URL et SUPABASE_ANON_KEY sur Railway."
        )
    
    return {
        "supabase_url": supabase_url,
        "supabase_anon_key": supabase_anon_key,
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
async def diagnostic(authorization: Optional[str] = Header(None)):
    """Route de diagnostic pour vérifier la configuration des clés API"""
    await verify_admin(authorization=authorization)

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
async def test_features(authorization: Optional[str] = Header(None)):
    """Test endpoint pour vérifier les fonctionnalités"""
    await verify_admin(authorization=authorization)

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
async def test_rhyme_simple(authorization: Optional[str] = Header(None)):
    """
    Endpoint de test ultra-simple pour diagnostiquer les erreurs
    """
    await verify_admin(authorization=authorization)

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
async def diagnostic_suno(authorization: Optional[str] = Header(None)):
    """
    Endpoint de diagnostic pour vérifier la configuration Suno
    """
    await verify_admin(authorization=authorization)

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
async def test_suno(authorization: Optional[str] = Header(None)):
    """
    Endpoint de test pour vérifier l'appel direct à l'API Suno
    """
    await verify_admin(authorization=authorization)

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

# --- Test Runway API ---
# --- Audio Streaming ---
@app.get("/audio/{filename}")
async def stream_audio(filename: str, download: bool = False):
    """
    Endpoint pour servir les fichiers audio avec FileResponse optimisé
    """
    import os
    # Empêcher toute tentative de traversal en normalisant le nom de fichier
    safe_filename = os.path.basename(filename)
    if safe_filename != filename or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")

    file_path = os.path.join("static", safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    if download:
        # Pour le téléchargement : forcer le téléchargement avec Content-Disposition
        headers = {
            "Content-Type": "audio/mpeg",
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        }

        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            headers=headers
        )
    else:
        # Pour la lecture : servir normalement avec headers optimisés
        headers = {
            "Content-Type": "audio/mpeg",
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",  # Cache 1 heure pour la lecture
        }

        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            headers=headers
        )

# Endpoint Runway supprimé - retour à OpenAI TTS

# --- Histoire Audio ---
# Ancien modèle remplacé par ValidatedAudioStoryRequest dans validators.py

@app.post("/generate_audio_story/")
async def generate_audio_story(req: Request, authorization: Optional[str] = Header(None)):
    try:
        # Extraire user_id depuis JWT - AUTHENTIFICATION REQUISE
        user_id = await extract_user_id_from_jwt(authorization, None)
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Authentification requise pour générer une histoire audio"
            )
        
        # Parser le body JSON - essayer req.json() d'abord (plus simple)
        try:
            request_dict = await req.json()
            print(f"[DEBUG generate_audio_story] JSON parsé avec succès via req.json(). Clés: {list(request_dict.keys())}")
        except Exception as json_error:
            # Fallback: parser manuellement
            print(f"[DEBUG] req.json() a échoué: {json_error}, tentative parsing manuel...")
            try:
                body_bytes = await req.body()
                print(f"[DEBUG] Body reçu: {len(body_bytes)} bytes")
                if not body_bytes:
                    raise HTTPException(
                        status_code=422,
                        detail="Body vide"
                    )
                
                body_str = body_bytes.decode('utf-8')
                print(f"[DEBUG] Body string (premiers 200 chars): {body_str[:200]}")
                
                request_dict = json.loads(body_str)
                print(f"[DEBUG] JSON parsé avec succès manuellement. Clés: {list(request_dict.keys())}")
                
            except json.JSONDecodeError as e:
                print(f"[DEBUG] Erreur JSON: {e}")
                raise HTTPException(
                    status_code=422,
                    detail=f"JSON invalide: {str(e)}"
                )
            except Exception as e:
                print(f"[DEBUG] Erreur inattendue: {e}")
                import traceback
                print(f"[DEBUG] Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=422,
                    detail=f"Erreur parsing body: {str(e)}"
                )
        
        # Validation précoce des données d'entrée
        if not request_dict or not isinstance(request_dict, dict):
            print(f"[DEBUG] request_dict invalide: type={type(request_dict)}, valeur={request_dict}")
            raise HTTPException(
                status_code=422,
                detail="Données d'entrée invalides: doit être un objet JSON"
            )

        request_dict["user_id"] = user_id

        # Validation des données d'entrée
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre") or openai_key.startswith("your-"):
            raise HTTPException(
                status_code=400,
                detail="❌ Clé API OpenAI non configurée ou invalide"
            )

        story_type = request_dict.get("story_type", "aventure")
        custom_request = request_dict.get("custom_request", "")

        # Validation du type d'histoire
        if not isinstance(story_type, str) or len(story_type) > 50:
            story_type = "aventure"

        # Validation de la demande personnalisée
        if not isinstance(custom_request, str) or len(custom_request) > 200:
            custom_request = ""
        
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
            temperature=0.7,
            timeout=30  # Timeout de 30 secondes pour éviter les erreurs 520
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
        
        # 🆕 VÉRIFICATION UNICITÉ (non-bloquante, ne casse rien si erreur)
        uniqueness_metadata = {}
        try:
            if supabase_client and request_dict.get("user_id"):
                # Vérifier l'unicité du contenu généré
                uniqueness_check = await uniqueness_service.ensure_unique_content(
                    supabase_client=supabase_client,
                    user_id=request_dict.get("user_id"),
                    content_type="histoire",
                    theme=story_type,
                    generated_content=story_content,
                    custom_data={"custom_request": custom_request if custom_request else None}
                )
                
                # Si c'est un doublon exact, régénérer UNE SEULE FOIS
                if uniqueness_check.get("should_regenerate"):
                    print(f"🔄 Doublon détecté pour histoire {story_type}, régénération...")
                    
                    # Enrichir le prompt avec l'historique
                    enhanced_prompt = uniqueness_service.enrich_prompt_with_history(
                        prompt, 
                        uniqueness_check.get("history", []),
                        "histoire"
                    )
                    
                    # Régénérer avec prompt enrichi et température légèrement plus élevée
                    response = await client.chat.completions.create(
                        model=TEXT_MODEL,
                        messages=[
                            {"role": "system", "content": "Tu es un conteur spécialisé dans les histoires pour enfants. Tu écris des histoires engageantes avec des valeurs positives."},
                            {"role": "user", "content": enhanced_prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.85,  # Légèrement plus créatif
                        timeout=30
                    )
                    
                    content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
                    
                    # Ré-extraire titre et contenu
                    if "TITRE:" in content and "HISTOIRE:" in content:
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith("TITRE:"):
                                title = line.replace("TITRE:", "").strip()
                                break
                        histoire_start = content.find("HISTOIRE:")
                        if histoire_start != -1:
                            story_content = content[histoire_start + 9:].strip()
                    
                    # Recalculer les métadonnées avec le nouveau contenu
                    uniqueness_check = await uniqueness_service.ensure_unique_content(
                        supabase_client=supabase_client,
                        user_id=request_dict.get("user_id"),
                        content_type="histoire",
                        theme=story_type,
                        generated_content=story_content,
                        custom_data={"custom_request": custom_request if custom_request else None}
                    )
                
                # Stocker les métadonnées d'unicité
                uniqueness_metadata = {
                    "content_hash": uniqueness_check.get("content_hash"),
                    "summary": uniqueness_check.get("summary"),
                    "variation_tags": uniqueness_check.get("variation_tags")
                }
        except Exception as uniqueness_error:
            # En cas d'erreur, continuer normalement sans métadonnées
            print(f"⚠️ Service unicité non disponible (non-bloquant): {uniqueness_error}")
            pass
        
        # Génération de l'audio si une voix est spécifiée
        audio_path = None
        voice = request_dict.get("voice")

        # Validation de la voix
        if voice and isinstance(voice, str) and voice in ["male", "female"]:
            try:
                # Timeout pour éviter les erreurs 520 lors de la génération audio
                import asyncio
                audio_path = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, generate_speech, story_content, voice, title),
                    timeout=60  # 60 secondes maximum pour la génération audio
                )
            except asyncio.TimeoutError:
                # Timeout dépassé, continuer sans audio
                audio_path = None
            except Exception as audio_error:
                # Erreur lors de la génération audio, continuer sans audio
                audio_path = None
        elif voice and voice not in ["male", "female"]:
            # Voix invalide, ignorer l'audio
            voice = None
        
        result = {
            "title": title,
            "content": story_content,
            "audio_path": audio_path,
            "audio_generated": audio_path is not None,
            "type": "audio",
            # Métadonnées d'unicité (optionnelles, pour stockage dans la base)
            "uniqueness_metadata": uniqueness_metadata if uniqueness_metadata else None
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Log détaillé pour debug mais pas d'exposition en production
        import traceback
        error_details = traceback.format_exc()
        print(f"Erreur génération audio story: {str(e)}")
        print(f"Details: {error_details}")
        # Retourner une réponse valide même en cas d'erreur pour éviter l'erreur 520
        return {
            "title": f"Histoire {request_dict.get('story_type', 'aventure')}",
            "content": "Une erreur est survenue lors de la génération. Veuillez réessayer.",
            "audio_path": None,
            "audio_generated": False,
            "type": "audio",
            "error": True
        }

# --- Coloriage ---
# Ancien modèle remplacé par ValidatedColoringRequest dans validators.py

# Instance globale du générateur de coloriage (GPT-4o-mini + DALL-E 3)
# Utilisation de l'initialisation paresseuse pour éviter les erreurs au démarrage
coloring_generator_instance = None

def get_coloring_generator():
    """Obtient l'instance du générateur de coloriage (lazy initialization)"""
    from services.coloring_generator_gpt4o import coloring_generator

    if coloring_generator is None:
        try:
            from services.coloring_generator_gpt4o import ColoringGeneratorGPT4o
            # Assigner à la variable globale du module
            import services.coloring_generator_gpt4o
            services.coloring_generator_gpt4o.coloring_generator = ColoringGeneratorGPT4o()
            return services.coloring_generator_gpt4o.coloring_generator
        except ValueError as e:
            # Clé API manquante ou invalide
            print(f"[ERROR] Impossible d'initialiser ColoringGeneratorGPT4o: {e}")
            return None
        except Exception as e:
            # Autres erreurs d'initialisation
            print(f"[ERROR] Erreur inattendue lors de l'initialisation ColoringGeneratorGPT4o: {e}")
            return None
    return coloring_generator

@app.post("/generate_coloring/")
@app.post("/generate_coloring/{content_type_id}")
async def generate_coloring(
    request: ColoringRequest = Body(...),
    content_type_id: int = None,
    authorization: Optional[str] = Header(None)
):
    """
    Génère un coloriage basé sur un thème avec GPT-4o-mini + gpt-image-1-mini
    Supporte deux formats d'URL pour compatibilité frontend
    Organisation OpenAI vérifiée requise pour gpt-image-1-mini
    """
    try:
        # Extraire user_id depuis JWT - AUTHENTIFICATION REQUISE
        user_id = await extract_user_id_from_jwt(authorization, None)
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Authentification requise pour générer un coloriage"
            )

        # Validation des données d'entrée
        theme = request.theme
        custom_prompt = request.custom_prompt  # Prompt personnalisé optionnel
        with_colored_model = request.with_colored_model  # Par défaut avec modèle
        
        if custom_prompt:
            print(f"[COLORING] Generation coloriage personnalisé gpt-image-1-mini: '{custom_prompt}' ({'avec' if with_colored_model else 'sans'} modèle coloré)")
        else:
            print(f"[COLORING] Generation coloriage gpt-image-1-mini: {theme} ({'avec' if with_colored_model else 'sans'} modèle coloré) (content_type_id={content_type_id})")
        
        # Vérifier la clé API OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        # Obtenir l'instance du générateur
        generator = get_coloring_generator()

        if generator is None:
            raise HTTPException(
                status_code=500,
                detail="Service de génération de coloriage non disponible. Clé API OpenAI manquante ou invalide."
            )

        # 🆕 Enrichir le prompt avec l'historique pour éviter doublons (non-bloquant)
        try:
            if supabase_client and user_id:
                # Récupérer l'historique des coloriages de l'utilisateur
                history = await uniqueness_service.get_user_history(
                    supabase_client=supabase_client,
                    user_id=user_id,
                    content_type="coloriage",
                    theme=theme,
                    limit=5
                )
                
                # Si l'utilisateur a déjà des coloriages sur ce thème, enrichir le prompt
                if history and len(history) > 0:
                    variations_used = [h.get("variation_tags", {}) for h in history]
                    # Ajouter une suggestion de variation au custom_prompt
                    if not custom_prompt:
                        variation_hints = f" (variation #{len(history) + 1})"
                        custom_prompt = f"{theme}{variation_hints}"
        except Exception as history_error:
            print(f"⚠️ Historique non disponible (non-bloquant): {history_error}")
            pass
        
        # Générer le coloriage avec GPT-4o-mini (analyse) + gpt-image-1-mini (génération)
        result = await generator.generate_coloring_from_theme(theme, with_colored_model, custom_prompt, user_id=user_id)
        
        # 🆕 Stocker les métadonnées d'unicité (non-bloquant)
        uniqueness_metadata = {}
        try:
            if result.get("success") and supabase_client and user_id:
                # Créer un "contenu" textuel pour le hash (le prompt utilisé)
                content_for_hash = f"{theme}_{custom_prompt}_{with_colored_model}"
                
                uniqueness_check = await uniqueness_service.ensure_unique_content(
                    supabase_client=supabase_client,
                    user_id=user_id,
                    content_type="coloriage",
                    theme=theme,
                    generated_content=content_for_hash,
                    custom_data={
                        "custom_prompt": custom_prompt,
                        "with_colored_model": with_colored_model
                    }
                )
                
                uniqueness_metadata = {
                    "content_hash": uniqueness_check.get("content_hash"),
                    "summary": uniqueness_check.get("summary"),
                    "variation_tags": uniqueness_check.get("variation_tags")
                }
        except Exception as uniqueness_error:
            print(f"⚠️ Service unicité non disponible (non-bloquant): {uniqueness_error}")
            pass
        
        if result.get("success") == True:
            return {
                "status": "success",
                "theme": theme,
                "images": result.get("images", []),
                "message": "Coloriage généré avec succès avec gpt-image-1-mini !",
                "type": "coloring",
                "model": "gpt-image-1-mini",
                # Métadonnées d'unicité (optionnelles)
                "uniqueness_metadata": uniqueness_metadata if uniqueness_metadata else None
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
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ Erreur génération coloriage: {e}")
        print(f"❌ Traceback complet:\n{error_traceback}")
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
            with_colored_model=with_colored_model,
            user_id=request.get("user_id")  # Passer user_id pour Supabase Storage
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
async def generate_comic(
    request: dict,
    authorization: Optional[str] = Header(None)
):
    """
    Lance la génération d'une bande dessinée en arrière-plan
    Retourne immédiatement un task_id pour éviter les timeouts
    """
    try:
        # Extraire user_id depuis JWT - AUTHENTIFICATION REQUISE
        user_id = await extract_user_id_from_jwt(authorization, None)
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Authentification requise pour générer une bande dessinée"
            )
        
        request["user_id"] = user_id
        
        # Récupérer les paramètres
        theme = request.get("theme", "espace")
        art_style = request.get("art_style", "cartoon")
        num_pages = request.get("num_pages", 1)
        custom_prompt = request.get("custom_prompt")
        character_photo_path = request.get("character_photo_path")
        user_id = user_id or request.get("user_id")  # Pour unicité
        
        print(f"📚 Lancement génération BD: thème={theme}, style={art_style}, pages={num_pages}")
        
        # 🆕 Enrichir avec l'historique (non-bloquant)
        try:
            if supabase_client and user_id:
                history = await uniqueness_service.get_user_history(
                    supabase_client, user_id, "bd", theme, limit=3
                )
                if history and len(history) > 0 and not custom_prompt:
                    custom_prompt = f"Variation #{len(history) + 1} - éviter: {', '.join([h.get('title', '') for h in history[:2]])}"
        except Exception:
            pass
        
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
            "user_id": user_id,  # Stocker pour utilisation ultérieure
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
    request: AnimationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Génère une animation via POST avec body JSON
    """
    # Extraire user_id depuis JWT - AUTHENTIFICATION REQUISE
    user_id = await extract_user_id_from_jwt(authorization, None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise pour générer une animation"
        )
    
    return await _generate_animation_logic(
        theme=request.theme,
        duration=request.duration or 30,
        style=request.style or "cartoon",
        custom_prompt=request.custom_prompt,
        user_id=user_id
    )

@app.post("/generate-quick-json")
async def generate_quick_json(
    request: GenerateQuickRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Génère une animation via POST avec body JSON uniquement (nouvelle route)
    """
    # Extraire user_id depuis JWT - AUTHENTIFICATION REQUISE
    user_id = await extract_user_id_from_jwt(authorization, None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise pour générer une animation rapide"
        )

    return await _generate_animation_logic(
        theme=request.theme,
        duration=request.duration,
        style=request.style,
        custom_prompt=request.custom_prompt,
        user_id=user_id
    )

@app.get("/generate-quick")   # Ajouter support GET pour compatibilité
async def generate_animation(
    theme: str = "space",
    duration: int = 30,
    style: str = "cartoon",
    custom_prompt: str = None,
    authorization: Optional[str] = Header(None)
):
    """
    Génère une VRAIE animation avec Runway ML Veo 3.1 Fast (workflow zseedance)
    Supporte les requêtes GET avec query parameters - PLUS DE MODE, toujours vrai pipeline
    """
    # Extraire user_id depuis JWT - AUTHENTIFICATION REQUISE
    user_id = await extract_user_id_from_jwt(authorization, None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise pour générer une animation"
        )
    return await _generate_animation_logic(theme, duration, style, custom_prompt, user_id=user_id)

async def _generate_animation_logic(
    theme: str,
    duration: int,
    style: str,
    custom_prompt: str = None,
    user_id: str = None
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
        
        # 🆕 Enrichir avec l'historique (non-bloquant)
        try:
            if supabase_client and user_id:
                history = await uniqueness_service.get_user_history(
                    supabase_client, user_id, "animation", theme, limit=3
                )
                if history and len(history) > 0:
                    variation_hint = f" [Variation #{len(history) + 1}]"
                    if custom_prompt:
                        custom_prompt = f"{custom_prompt}{variation_hint}"
                    else:
                        custom_prompt = variation_hint
        except Exception:
            pass

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
    print(f"\n{'='*80}")
    print(f"🚀🚀🚀 DÉBUT TÂCHE GÉNÉRATION ZSEEDANCE 🚀🚀🚀")
    print(f"Task ID: {task_id}")
    print(f"Thème: {theme}")
    print(f"Durée: {duration}s")
    print(f"Style: {style}")
    print(f"{'='*80}\n")
    
    try:
        # Mettre à jour le statut
        task_storage[task_id]["status"] = "generating"
        print(f"✅ Statut mis à jour: generating")

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

        # Calculer le nombre de scènes selon la durée (8s par scène avec veo3.1_fast)
        # Arrondir pour être plus proche de la durée demandée
        num_scenes = max(3, round(duration / 8))  # Minimum 3 scènes, ~8s par scène
        total_duration = num_scenes * 8
        print(f"📊 Génération de {num_scenes} scènes de 8 secondes chacune (durée totale: {total_duration}s pour {duration}s demandés)")

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

        # Vérifier le statut réel de l'animation
        result_status = animation_result.get("status", "failed")
        final_video_url = animation_result.get("final_video_url")

        if result_status == "completed" and final_video_url:
            print(f"✅ Animation ZSEEDANCE {task_id} générée avec succès!")
            print(f"🎬 Vidéo finale: {final_video_url[:50]}...")
            task_storage[task_id]["status"] = "completed"
        else:
            print(f"❌ Animation ZSEEDANCE {task_id} échouée: {animation_result.get('error', 'Erreur inconnue')}")
            task_storage[task_id]["status"] = "failed"

        # Stocker le résultat dans tous les cas
        task_storage[task_id]["result"] = animation_result

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌❌❌ ERREUR TÂCHE GÉNÉRATION ZSEEDANCE ❌❌❌")
        print(f"Task ID: {task_id}")
        print(f"Erreur: {e}")
        print(f"Type: {type(e).__name__}")
        print(f"{'='*80}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")

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
            character_photo_path=character_photo_path,
            user_id=user_id  # Passer user_id pour Supabase Storage
        )
        
        # Stocker le résultat
        if result.get("success"):
            # 🆕 Métadonnées d'unicité (non-bloquant)
            uniqueness_metadata = {}
            try:
                user_id = comic_task_storage[task_id].get("user_id")
                if supabase_client and user_id:
                    synopsis = result.get("synopsis", "")
                    uniqueness_check = await uniqueness_service.ensure_unique_content(
                        supabase_client, user_id, "bd", theme,
                        synopsis[:200], {"art_style": art_style, "num_pages": num_pages}
                    )
                    uniqueness_metadata = {
                        "content_hash": uniqueness_check.get("content_hash"),
                        "summary": uniqueness_check.get("summary"),
                        "variation_tags": uniqueness_check.get("variation_tags")
                    }
            except Exception:
                pass
            
            comic_task_storage[task_id]["result"] = {
                "status": "success",
                "comic_id": result["comic_id"],
                "title": result["title"],
                "synopsis": result["synopsis"],
                "pages": result["pages"],
                "total_pages": result["total_pages"],
                "theme": result["theme"],
                "art_style": result["art_style"],
                "generation_time": result["generation_time"],
                "uniqueness_metadata": uniqueness_metadata if uniqueness_metadata else None
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
            # LOG DÉTAILLÉ pour déboguer l'affichage frontend
            print(f"✅ Animation RÉELLE {task_id} terminée et retournée!")
            print(f"📦 Données retournées: status={animation_result.get('status')}, final_video_url={'OUI' if animation_result.get('final_video_url') else 'NON'}, video_urls={'OUI' if animation_result.get('video_urls') else 'NON'}, clips={'OUI' if animation_result.get('clips') else 'NON'}")
            
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

@app.get("/sitemap.xml", include_in_schema=False)
async def serve_sitemap():
    """Servez le sitemap.xml pour Google Search Console."""
    sitemap_path = static_dir / "sitemap.xml"
    if sitemap_path.exists():
        return FileResponse(
            sitemap_path,
            media_type="application/xml",
            headers={"Content-Type": "application/xml; charset=utf-8"}
        )
    raise HTTPException(status_code=404, detail="Sitemap not found")


@app.get("/robots.txt", include_in_schema=False)
async def serve_robots():
    """Servez le robots.txt pour les moteurs de recherche."""
    robots_path = static_dir / "robots.txt"
    if robots_path.exists():
        return FileResponse(
            robots_path,
            media_type="text/plain",
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )
    raise HTTPException(status_code=404, detail="Robots.txt not found")


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
    # Servir sitemap.xml et robots.txt s'ils sont demandés (au cas où)
    if full_path == "sitemap.xml":
        sitemap_path = static_dir / "sitemap.xml"
        if sitemap_path.exists():
            return FileResponse(
                sitemap_path,
                media_type="application/xml",
                headers={"Content-Type": "application/xml; charset=utf-8"}
            )
    if full_path == "robots.txt":
        robots_path = static_dir / "robots.txt"
        if robots_path.exists():
            return FileResponse(
                robots_path,
                media_type="text/plain",
                headers={"Content-Type": "text/plain; charset=utf-8"}
            )
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


# ===================================
# ENDPOINT ADMIN - NETTOYAGE FICHIERS
# ===================================

@app.post("/admin/cleanup-files")
async def trigger_file_cleanup(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Endpoint admin pour déclencher manuellement le nettoyage des fichiers locaux.
    Supprime tous les fichiers de plus de 24h dans les dossiers de cache.
    Requiert une authentification admin (JWT dans Authorization header ou user_id dans le body).
    """
    # Vérifier que l'utilisateur est admin
    # On accepte user_id depuis le body pour compatibilité
    body = None
    try:
        body_data = await request.body()
        if body_data:
            try:
                body = json.loads(body_data)
            except:
                pass
    except:
        pass
    
    await verify_admin(authorization=authorization, request=request, body=body)
    
    try:
        from services.file_cleanup import cleanup_service
        
        # Exécuter le nettoyage
        stats = cleanup_service.run_cleanup()
        
        return {
            "success": True,
            "message": "Nettoyage des fichiers locaux effectué",
            "stats": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du nettoyage: {str(e)}"
        )


@app.get("/admin/cleanup-status")
async def get_cleanup_status(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Endpoint admin pour obtenir les informations sur le service de nettoyage.
    Retourne la configuration et l'état du scheduler.
    Requiert une authentification admin (JWT dans Authorization header).
    """
    # Vérifier que l'utilisateur est admin
    await verify_admin(authorization=authorization, request=request)
    
    try:
        from services.file_cleanup import cleanup_service
        
        return {
            "success": True,
            "config": {
                "max_age_hours": cleanup_service.max_age_seconds / 3600,
                "cache_directories": cleanup_service.cache_directories,
                "cleanup_interval": "1 hour"
            },
            "scheduler_running": scheduler.running,
            "next_run": scheduler.get_jobs()[0].next_run_time.isoformat() if scheduler.get_jobs() else None
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du status: {str(e)}"
        )
