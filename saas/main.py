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

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from datetime import datetime
from services.tts import generate_speech
from services.stt import transcribe_audio

# Authentification gérée par Supabase - modules supprimés car inutiles avec Vercel
from services.coloring_generator import ColoringGenerator
from services.comic_generator import ComicGenerator
from utils.translate import translate_text
# Validation et sécurité supprimées car gérées automatiquement par Vercel + Supabase

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")

app = FastAPI(title="API FRIDAY - Contenu Créatif IA", version="2.0", description="API pour générer du contenu créatif pour enfants : BD, coloriages, histoires, comptines")

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

# CORS avec support UTF-8
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Frontend HTTP (développement)
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", 
        "http://localhost:5176", "http://localhost:5177", "http://localhost:5178", 
        "http://localhost:5179", "http://localhost:5180",
        # Frontend HTTPS (sécurisé)
        "https://localhost:5173", "https://localhost:5174", "https://localhost:5175",
        "https://localhost:5176", "https://localhost:5177", "https://localhost:5178",
        "https://localhost:5179", "https://localhost:5180",
        # Autres origins communs
        "http://127.0.0.1:5173", "https://127.0.0.1:5173",
        "http://localhost:3000", "https://localhost:3000",
        # Adresse IP locale pour le développement
        "http://192.168.1.19:5173", "https://192.168.1.19:5173",
        "http://192.168.1.19:5174", "https://192.168.1.19:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# === ROUTE DES FONCTIONNALITÉS ===

@app.get("/api/features")
async def get_features():
    """Route pour récupérer l'état des fonctionnalités du site"""
    return {
        "animation": {"enabled": True, "name": "Dessin animé", "icon": "🎬"},
        "comic": {"enabled": True, "name": "Bande dessinée", "icon": "💬"},
        "coloring": {"enabled": True, "name": "Coloriage", "icon": "🎨"},
        "audio": {"enabled": True, "name": "Histoire", "icon": "📖"},
        "rhyme": {"enabled": True, "name": "Comptine", "icon": "🎵"}
    }

@app.put("/api/features/{feature_key}")
async def update_feature(feature_key: str, request: dict):
    """Route pour mettre à jour l'état d'une fonctionnalité"""
    enabled = request.get("enabled", True)
    # Ici vous pourriez sauvegarder en base de données
    return {
        "success": True,
        "feature": feature_key,
        "enabled": enabled,
        "features": {
            "animation": {"enabled": True, "name": "Dessin animé", "icon": "🎬"},
            "comic": {"enabled": True, "name": "Bande dessinée", "icon": "💬"},
            "coloring": {"enabled": True, "name": "Coloriage", "icon": "🎨"},
            "audio": {"enabled": True, "name": "Histoire", "icon": "📖"},
            "rhyme": {"enabled": True, "name": "Comptine", "icon": "🎵"}
        }
    }

@app.post("/api/features/reset")
async def reset_features():
    """Route pour réinitialiser toutes les fonctionnalités"""
    return {
        "success": True,
        "features": {
            "animation": {"enabled": True, "name": "Dessin animé", "icon": "🎬"},
            "comic": {"enabled": True, "name": "Bande dessinée", "icon": "💬"},
            "coloring": {"enabled": True, "name": "Coloriage", "icon": "🎨"},
            "audio": {"enabled": True, "name": "Histoire", "icon": "📖"},
            "rhyme": {"enabled": True, "name": "Comptine", "icon": "🎵"}
        }
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
from services.udio_service import udio_service

# Ancien modèle remplacé par ValidatedRhymeRequest dans validators.py

@app.post("/generate_rhyme/")
async def generate_rhyme(request: dict):
    try:
        # Validation des données d'entrée
        # Vérifier la clé API OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API OpenAI non configurée. Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            )
        
        # Vérifier la clé API Udio
        goapi_key = os.getenv("GOAPI_API_KEY")
        if not goapi_key or goapi_key.startswith("votre_cle"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API GoAPI Udio non configurée. Veuillez configurer GOAPI_API_KEY dans le fichier .env"
            )
        
        # 1. Générer les paroles avec OpenAI
        theme = request.get("theme", "animaux")
        custom_request = request.get("custom_request", "")
        
        prompt = f"Écris une comptine courte, joyeuse et rythmée pour enfants sur le thème : {theme}.\n"
        if custom_request:
            prompt += f"Demande spécifique : {custom_request}\n"
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
        title = f"Comptine {theme}"  # Titre par défaut
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
        
        # 2. Lancer la génération musicale avec Udio
        print(f"🎵 Lancement génération musicale pour: {title}")
        udio_result = await udio_service.generate_musical_nursery_rhyme(
            lyrics=rhyme_content,
            rhyme_type=theme
        )
        
        if udio_result.get("status") == "success":
            task_id = udio_result.get("task_id")
            print(f"✅ Tâche musicale créée: {task_id}")
            
            return {
                "title": title,
                "content": rhyme_content,
                "type": "rhyme",
                "music_task_id": task_id,
                "music_status": "processing",
                "message": "Comptine générée, musique en cours de création..."
            }
        else:
            # Si la génération musicale échoue, retourner une erreur HTTP
            error_message = udio_result.get("error", "Erreur inconnue lors de la génération musicale")
            print(f"❌ Erreur génération musicale: {error_message}")
            raise HTTPException(
                status_code=500, 
                detail=f"❌ La création de l'audio a échoué : {error_message}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur génération comptine: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")

@app.get("/check_task_status/{task_id}")
async def check_task_status(task_id: str):
    """
    Vérifie le statut d'une tâche musicale Udio
    """
    try:
        result = await udio_service.check_task_status(task_id)
        return result
    except Exception as e:
        print(f"❌ Erreur vérification statut: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification : {str(e)}")

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

# Instance globale du générateur de coloriage
coloring_generator_instance = ColoringGenerator()

@app.post("/generate_coloring/")
async def generate_coloring(request: dict):
    """
    Génère un coloriage basé sur un thème
    """
    try:
        # Validation des données d'entrée
        theme = request.get("theme", "animaux")
        print(f"🎨 Génération coloriage: {theme}")
        
        # Vérifier la clé API Stability AI
        stability_key = os.getenv("STABILITY_API_KEY")
        if not stability_key or stability_key.startswith("sk-votre"):
            raise HTTPException(
                status_code=400, 
                detail="❌ Clé API Stability AI non configurée. Veuillez configurer STABILITY_API_KEY dans le fichier .env"
            )
        
        # Générer le coloriage
        result = await coloring_generator_instance.generate_coloring_pages(theme)
        
        if result.get("success") == True:  # Le service retourne "success" au lieu de "status"
            return {
                "status": "success",
                "theme": theme,
                "images": result.get("images", []),
                "message": "Coloriage généré avec succès !",
                "type": "coloring"
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