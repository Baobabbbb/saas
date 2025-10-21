import asyncio
import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any

from config import config
from models.schemas import (
    AnimationRequest, AnimationResult, AnimationProgress, 
    DiagnosticResponse, AnimationTheme, AnimationDuration
)
from services.animation_pipeline import AnimationPipeline

# Import des modules d'authentification JWT
try:
    from utils.jwt_auth import jwt_auth, JWTBearer, get_current_user
    from services.auth_service import auth_service
    from schemas.auth import (
        LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest,
        RefreshTokenResponse, LogoutRequest, UserProfile, PasswordResetRequest,
        ProfileUpdateRequest
    )
except ImportError:
    # Fallback si les modules ne sont pas disponibles
    jwt_auth = None
    auth_service = None
    JWTBearer = None
    get_current_user = None
    # Créer des classes factices pour éviter les erreurs
    from pydantic import BaseModel
    class TokenResponse(BaseModel):
        pass
    class RefreshTokenResponse(BaseModel):
        pass
    class LoginRequest(BaseModel):
        pass
    class RegisterRequest(BaseModel):
        pass
    class RefreshTokenRequest(BaseModel):
        pass
    class LogoutRequest(BaseModel):
        pass
    class UserProfile(BaseModel):
        pass
    class PasswordResetRequest(BaseModel):
        pass
    class ProfileUpdateRequest(BaseModel):
        pass
    
    # Fonction factice pour get_current_user
    def get_current_user(request):
        return {"sub": "dummy", "email": "dummy@example.com"}

# Pipeline global
pipeline = AnimationPipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application (Wan 2.5)"""
    # Startup
    print("🎬 Animation Studio Veo 3.1 Fast - Démarrage du serveur...")
    
    # Mode rapide par défaut
    print("⚡ Mode démarrage rapide")
    # Validation ultra-rapide des clés
    if config.OPENAI_API_KEY:
        print("✅ Clé OpenAI détectée (génération idées)")
    runway_key = os.getenv("RUNWAY_API_KEY")
    if runway_key and runway_key != "your-runway-api-key-here":
        print(f"✅ Clé Runway détectée (Veo 3.1 Fast: {config.VEO31_MODEL})")
    else:
        print("⚠️ Clé Runway non configurée ou invalide")

    print(f"🎨 Résolution par défaut: {config.VEO31_DEFAULT_RESOLUTION}")
    print(f"🎵 Audio intégré: {config.VEO31_AUDIO_INTEGRATED}")
    print("🚀 Prêt pour génération Veo 3.1 Fast!")
    
    yield
    
    # Shutdown
    print("🛑 Arrêt du serveur Veo 3.1 Fast...")
    pipeline.cleanup_old_animations()

# Création de l'app FastAPI
app = FastAPI(
    title="Animation Studio API (Veo 3.1 Fast)",
    description="API de génération de dessins animés pour enfants avec Veo 3.1 Fast (Runway ML) - Audio intégré",
    version="2.0.0-veo31",
    lifespan=lifespan
)

# Configuration CORS (assouplie pour déploiement Railway)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache pour stocker les callbacks de progression
progress_callbacks: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API"""
    return {
        "name": "Animation Studio API",
        "version": "1.0.0",
        "description": "Génération de dessins animés pour enfants via IA",
        "endpoints": {
            "diagnostic": "/diagnostic",
            "generate": "/generate",
            "status": "/status/{animation_id}",
            "themes": "/themes"
        }
    }

@app.get("/diagnostic", response_model=DiagnosticResponse)
async def diagnostic():
    """Diagnostic complet de l'état des APIs et services (Wan 2.5)"""
    try:
        health = await pipeline.validate_pipeline_health()
        
        return DiagnosticResponse(
            openai_configured=bool(config.OPENAI_API_KEY),
            wavespeed_configured=bool(config.WAVESPEED_API_KEY),
            wan25_model=config.WAN25_MODEL,
            all_systems_operational=health["pipeline_operational"],
            details=health
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur diagnostic Wan 2.5: {str(e)}")

@app.get("/themes")
async def get_themes():
    """Récupère la liste des thèmes disponibles avec descriptions"""
    try:
        themes = pipeline.get_supported_themes()
        
        # Formater pour l'interface utilisateur
        formatted_themes = {}
        for theme_key, theme_data in themes.items():
            formatted_themes[theme_key] = {
                "name": theme_key.title(),
                "description": theme_data["base_concept"],
                "elements": theme_data["elements"],
                "mood": theme_data["mood"],
                "icon": {
                    "space": "🚀",
                    "nature": "🌳", 
                    "adventure": "🏰",
                    "animals": "🐾",
                    "magic": "✨",
                    "friendship": "🤝"
                }.get(theme_key, "🎬")
            }
        
        return {
            "themes": formatted_themes,
            "durations": [30, 60, 120, 180, 240, 300],
            "default_duration": config.DEFAULT_DURATION
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération thèmes: {str(e)}")

@app.post("/generate")
async def generate_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    """Démarre la génération et retourne immédiatement un animation_id pour polling."""
    try:
        if request.duration not in [30, 60, 120, 180, 240, 300]:
            raise HTTPException(status_code=400, detail="Durée non supportée")

        # Callback de progression
        def progress_callback(progress: AnimationProgress):
            progress_callbacks[progress.animation_id] = progress

        # Démarrer la génération asynchrone et obtenir l'id immédiatement
        animation_id = await pipeline.start_generation_async(request, progress_callback)

        return JSONResponse(status_code=202, content={
            "animation_id": animation_id,
            "status": "pending"
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération: {str(e)}")

@app.get("/status/{animation_id}")
async def get_animation_status(animation_id: str):
    """Récupère le statut d'une animation en cours"""
    try:
        # Chercher dans le cache de progression d'abord
        if animation_id in progress_callbacks:
            progress = progress_callbacks[animation_id]
            return {
                "type": "progress",
                "data": progress
            }
        
        # Sinon chercher dans les animations terminées
        result = pipeline.get_animation_status(animation_id)
        if result:
            return {
                "type": "result",
                "data": result
            }
        
        raise HTTPException(status_code=404, detail="Animation non trouvée")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statut: {str(e)}")

@app.post("/generate-quick")
async def generate_quick_animation(theme: str, duration: int):
    """Endpoint simplifié pour génération rapide"""
    try:
        # Valider les paramètres
        if theme not in ["space", "nature", "adventure", "animals", "magic", "friendship"]:
            raise HTTPException(status_code=400, detail="Thème non supporté")
        
        if duration not in [30, 60, 120, 180, 240, 300]:
            raise HTTPException(status_code=400, detail="Durée non supportée")
        
        # Créer la requête
        request = AnimationRequest(
            theme=AnimationTheme(theme),
            duration=AnimationDuration(duration)
        )
        
        # Générer
        result = await pipeline.generate_animation(request)
        
        return {
            "animation_id": result.animation_id,
            "status": result.status.value,
            "final_video_url": result.final_video_url,
            "processing_time": result.processing_time,
            "story_idea": result.story_idea.dict() if result.story_idea else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapide: {str(e)}")

@app.get("/health")
async def health_check():
    """Vérification rapide de santé du service"""
    try:
        health = await pipeline.validate_pipeline_health()
        return {
            "status": "healthy" if health["pipeline_operational"] else "degraded",
            "services": health["services"],
            "timestamp": pipeline.active_animations
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.delete("/cleanup")
async def cleanup_old_animations():
    """Nettoie les anciennes animations (endpoint admin)"""
    try:
        initial_count = len(pipeline.active_animations)
        pipeline.cleanup_old_animations(max_age_hours=6)  # 6 heures
        final_count = len(pipeline.active_animations)
        
        return {
            "message": "Nettoyage effectué",
            "animations_removed": initial_count - final_count,
            "remaining_animations": final_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur nettoyage: {str(e)}")

# === ROUTES D'AUTHENTIFICATION JWT ===

@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Connexion utilisateur avec JWT tokens"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    return await auth_service.authenticate_user(login_data)

@app.post("/auth/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest):
    """Inscription utilisateur avec JWT tokens"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    return await auth_service.register_user(register_data)

@app.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Rafraîchir un access token avec un refresh token"""
    if not jwt_auth:
        raise HTTPException(status_code=500, detail="Service JWT non disponible")
    
    return jwt_auth.refresh_access_token(refresh_data.refresh_token)

@app.post("/auth/logout")
async def logout(logout_data: LogoutRequest):
    """Déconnexion utilisateur en révoquant les tokens"""
    if not jwt_auth:
        raise HTTPException(status_code=500, detail="Service JWT non disponible")
    
    try:
        # Vérifier le refresh token pour obtenir l'user_id
        payload = jwt_auth.verify_token(logout_data.refresh_token)
        user_id = payload.get("sub")
        
        if user_id:
            jwt_auth.revoke_refresh_token(user_id)
        
        return {"message": "Déconnexion réussie"}
    except Exception as e:
        # Même en cas d'erreur, on considère la déconnexion comme réussie
        return {"message": "Déconnexion réussie"}

@app.get("/auth/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Récupérer le profil de l'utilisateur connecté"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    user_id = current_user.get("sub")
    return await auth_service.get_user_profile(user_id)

@app.put("/auth/profile", response_model=UserProfile)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour le profil de l'utilisateur connecté"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    user_id = current_user.get("sub")
    update_data = {}
    
    if profile_data.first_name is not None:
        update_data["first_name"] = profile_data.first_name
    if profile_data.last_name is not None:
        update_data["last_name"] = profile_data.last_name
    
    return await auth_service.update_user_profile(user_id, update_data)

@app.post("/auth/reset-password")
async def reset_password(reset_data: PasswordResetRequest):
    """Demander une réinitialisation de mot de passe"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    await auth_service.reset_password(reset_data.email)
    return {"message": "Email de réinitialisation envoyé"}

@app.get("/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Vérifier la validité d'un token"""
    return {
        "valid": True,
        "user_id": current_user.get("sub"),
        "email": current_user.get("email")
    }

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Ajouter le répertoire backend au PYTHONPATH
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    print(f"🚀 Démarrage sur http://{config.HOST}:{config.PORT}")
    uvicorn.run(
        app,  # Utiliser l'objet app directement
        host=config.HOST,
        port=config.PORT,
        reload=False,  # Désactivé pour éviter les conflits d'imports
        log_level="warning",  # Mode rapide
        access_log=False      # Désactiver logs d'accès
    ) 