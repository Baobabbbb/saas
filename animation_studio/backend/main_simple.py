#!/usr/bin/env python3
"""
Serveur FastAPI simplifié pour génération d'animations - Version FRIDAY
Basé sur fixed_server.py mais adapté pour l'intégration FRIDAY
"""

import os
import json
import time
import asyncio
import threading
import requests
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import openai

# Charger les variables d'environnement
load_dotenv()

# Configuration depuis .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY") 
FAL_API_KEY = os.getenv("FAL_API_KEY")

# Configuration par défaut
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
WAVESPEED_MODEL = os.getenv("WAVESPEED_MODEL", "seedance-v1-pro")
CARTOON_STYLE = os.getenv("CARTOON_STYLE", "2D cartoon animation, Disney style, vibrant colors")

# Vérification des clés API
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY manquante dans le fichier .env")
if not WAVESPEED_API_KEY:
    raise ValueError("WAVESPEED_API_KEY manquante dans le fichier .env")
if not FAL_API_KEY:
    raise ValueError("FAL_API_KEY manquante dans le fichier .env")

# Configuration OpenAI
openai.api_key = OPENAI_API_KEY

# --- SCHEMAS ---
class AnimationRequest(BaseModel):
    theme: str
    duration: int
    custom_prompt: Optional[str] = None

class StoryIdea(BaseModel):
    caption: str
    idea: str
    environment: str
    sound: str
    status: str = "for production"

class Scene(BaseModel):
    scene_number: int
    description: str
    duration: int
    prompt: str

class VideoClip(BaseModel):
    scene_number: int
    video_url: str = ""
    duration: int
    status: str = "pending"

class AnimationResult(BaseModel):
    animation_id: str
    status: str
    story_idea: Optional[StoryIdea] = None
    scenes: Optional[List[Scene]] = None
    video_clips: Optional[List[VideoClip]] = None
    audio_track: Optional[str] = None
    final_video_url: Optional[str] = None
    created_at: str
    processing_time: Optional[float] = None
    error_message: Optional[str] = None

# --- STOCKAGE EN MÉMOIRE ---
animations_store: Dict[str, AnimationResult] = {}

# --- CONFIGURATION FASTAPI ---
app = FastAPI(
    title="Animation Studio Backend - FRIDAY",
    description="Backend simplifié pour génération d'animations",
    version="1.0.0"
)

# Configuration CORS pour FRIDAY
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- UTILITAIRES ---
def generate_animation_id() -> str:
    """Génère un ID unique pour l'animation"""
    return str(uuid.uuid4())

# --- THÈMES ET DURÉES ---
ANIMATION_THEMES = {
    "space": {
        "name": "Space",
        "description": "a visually compelling space adventure for children",
        "elements": "spacecraft, planets, astronauts, friendly aliens, space stations",
        "mood": "adventurous, wonder-filled, educational, exciting",
        "icon": "🚀"
    },
    "nature": {
        "name": "Nature", 
        "description": "a magical nature adventure for children",
        "elements": "talking animals, magical trees, flowers, butterflies, forest creatures",
        "mood": "peaceful, magical, educational, harmonious",
        "icon": "🌳"
    },
    "adventure": {
        "name": "Adventure",
        "description": "a heroic adventure quest for children",
        "elements": "brave heroes, treasure maps, castles, dragons, magical artifacts", 
        "mood": "brave, exciting, inspiring, triumphant",
        "icon": "🏰"
    },
    "animals": {
        "name": "Animals",
        "description": "an animal friendship story for children",
        "elements": "cute animals, farms, jungles, oceans, animal families",
        "mood": "heartwarming, educational, funny, caring",
        "icon": "🐾"
    },
    "magic": {
        "name": "Magic",
        "description": "a magical fairy tale for children", 
        "elements": "fairies, wizards, magic wands, potions, enchanted objects",
        "mood": "whimsical, magical, wonder-filled, sparkling",
        "icon": "✨"
    },
    "friendship": {
        "name": "Friendship",
        "description": "a heartwarming friendship story for children",
        "elements": "diverse characters, cooperation, helping others, sharing, kindness",
        "mood": "warm, caring, inspiring, joyful", 
        "icon": "🤝"
    }
}

ANIMATION_DURATIONS = [30, 60, 120, 180, 240, 300]

# --- SERVICES ---
async def generate_story_idea(theme: str, duration: int, custom_prompt: Optional[str] = None) -> StoryIdea:
    """Génère une idée d'histoire avec OpenAI"""
    try:
        theme_data = ANIMATION_THEMES.get(theme, ANIMATION_THEMES["animals"])
        
        if custom_prompt:
            user_prompt = f"""Adapte cette histoire pour un dessin animé de {duration} secondes sur le thème "{theme}": {custom_prompt}

L'histoire doit être:
- Adaptée aux enfants de 3-8 ans
- Visuellement engageante pour l'animation
- Éducative et positive
- Complète avec début, milieu et fin
- Parfaite pour une durée de {duration} secondes

Format de sortie JSON:
{{
  "caption": "🌟 Titre accrocheur avec emoji et hashtags #enfants #animation",
  "idea": "Histoire complète en une phrase d'action claire",
  "environment": "Description de l'environnement en moins de 20 mots",
  "sound": "Description audio adaptée aux enfants",
  "status": "for production"
}}"""
        else:
            user_prompt = f"""Génère une idée de dessin animé sur le thème "{theme}" d'une durée de {duration} secondes.

Thème: {theme_data['description']}
Éléments: {theme_data['elements']}
Ambiance: {theme_data['mood']}

L'histoire doit être:
- Adaptée aux enfants de 3-8 ans
- Visuellement engageante pour l'animation
- Éducative et positive
- Complète avec début, milieu et fin
- Parfaite pour une durée de {duration} secondes

Format de sortie JSON:
{{
  "caption": "🌟 Titre accrocheur avec emoji et hashtags #enfants #animation",
  "idea": "Histoire complète en une phrase d'action claire",
  "environment": "Description de l'environnement en moins de 20 mots", 
  "sound": "Description audio adaptée aux enfants",
  "status": "for production"
}}"""

        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un générateur d'idées créatives pour dessins animés enfants. Réponds uniquement en JSON valide."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Nettoyer le JSON
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        idea_data = json.loads(content)
        return StoryIdea(**idea_data)
        
    except Exception as e:
        # Fallback en cas d'erreur
        theme_data = ANIMATION_THEMES.get(theme, ANIMATION_THEMES["animals"])
        return StoryIdea(
            caption=f"{theme_data['icon']} Nouvelle aventure {theme}! #enfants #animation #{theme}",
            idea=f"Une histoire magique de {duration} secondes sur {theme_data['description']}",
            environment=f"Environnement coloré style cartoon pour enfants",
            sound="Musique douce et effets sonores mélodieux pour enfants",
            status="for production"
        )

async def generate_scenes(story_idea: StoryIdea, duration: int) -> List[Scene]:
    """Génère les scènes de l'animation"""
    try:
        num_scenes = max(2, min(5, duration // 10))  # 1 scène toutes les 10 secondes
        scene_duration = duration // num_scenes
        
        user_prompt = f"""Crée {num_scenes} scènes détaillées pour cette histoire:
        
Histoire: {story_idea.idea}
Environnement: {story_idea.environment}
Durée totale: {duration} secondes
Durée par scène: {scene_duration} secondes

Chaque scène doit avoir:
- Une description détaillée avec mouvements de caméra
- Des actions visuelles claires pour l'animation
- Une progression narrative logique

Format JSON:
[
  {{
    "scene_number": 1,
    "description": "Description détaillée avec mouvements de caméra...",
    "duration": {scene_duration},
    "prompt": "VIDEO THEME: {CARTOON_STYLE} | WHAT HAPPENS: Description | WHERE: {story_idea.environment}"
  }}
]"""

        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un expert en storyboard pour animations enfants. Réponds uniquement en JSON valide."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Nettoyer le JSON
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        scenes_data = json.loads(content)
        return [Scene(**scene) for scene in scenes_data]
        
    except Exception as e:
        # Fallback avec scènes basiques
        return [
            Scene(
                scene_number=1,
                description=f"Scène d'ouverture: {story_idea.idea[:100]}...",
                duration=duration // 2,
                prompt=f"VIDEO THEME: {CARTOON_STYLE} | WHAT HAPPENS: {story_idea.idea} | WHERE: {story_idea.environment}"
            ),
            Scene(
                scene_number=2,
                description=f"Scène finale: Conclusion de l'histoire",
                duration=duration // 2,
                prompt=f"VIDEO THEME: {CARTOON_STYLE} | WHAT HAPPENS: Conclusion de {story_idea.idea} | WHERE: {story_idea.environment}"
            )
        ]

def generate_video_with_wavespeed(prompt: str, duration: int) -> str:
    """Génère une vidéo avec Wavespeed API"""
    try:
        print(f"🎬 Génération vidéo Wavespeed - Durée: {duration}s")
        
        # Appel à l'API Wavespeed
        response = requests.post(
            "https://api.wavespeed.ai/v1/video/generate",
            headers={
                "Authorization": f"Bearer {WAVESPEED_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": WAVESPEED_MODEL,
                "prompt": prompt,
                "duration": duration,
                "quality": "high",
                "format": "mp4"
            },
            timeout=120  # Timeout de 2 minutes
        )
        
        if response.status_code == 200:
            result = response.json()
            if "video_url" in result:
                return result["video_url"]
            else:
                return ""
        else:
            print(f"❌ Erreur Wavespeed: {response.status_code}")
            return ""
            
    except Exception as e:
        print(f"❌ Erreur génération vidéo: {e}")
        return ""

# --- ENDPOINTS ---
@app.get("/")
async def root():
    return {"message": "Animation Studio Backend - FRIDAY Integration", "status": "running"}

@app.get("/themes")
async def get_themes():
    """Retourne les thèmes et durées disponibles"""
    return {
        "themes": ANIMATION_THEMES,
        "durations": ANIMATION_DURATIONS
    }

@app.post("/generate")
async def generate_animation(request: AnimationRequest):
    """Lance la génération d'une animation"""
    try:
        print(f"🚀 Nouvelle demande d'animation: {request.theme}, {request.duration}s")
        
        # Créer l'animation
        animation_id = generate_animation_id()
        animation = AnimationResult(
            animation_id=animation_id,
            status="generating_idea",
            created_at=datetime.now().isoformat()
        )
        
        # Stocker l'animation
        animations_store[animation_id] = animation
        
        # Lancer la génération en arrière-plan
        threading.Thread(
            target=process_animation_sync,
            args=(animation_id, request.theme, request.duration, request.custom_prompt)
        ).start()
        
        return animation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")

@app.get("/status/{animation_id}")
async def get_animation_status(animation_id: str):
    """Récupère le statut d'une animation"""
    if animation_id not in animations_store:
        raise HTTPException(status_code=404, detail="Animation non trouvée")
    
    return animations_store[animation_id]

@app.get("/diagnostic")
async def diagnostic():
    """Diagnostic du système"""
    return {
        "status": "operational",
        "openai_configured": bool(OPENAI_API_KEY),
        "wavespeed_configured": bool(WAVESPEED_API_KEY),
        "fal_configured": bool(FAL_API_KEY),
        "active_animations": len(animations_store),
        "themes_available": len(ANIMATION_THEMES),
        "durations_available": len(ANIMATION_DURATIONS)
    }

# --- TRAITEMENT ASYNCHRONE ---
def process_animation_sync(animation_id: str, theme: str, duration: int, custom_prompt: Optional[str] = None):
    """Traite l'animation de manière synchrone (appelé dans un thread)"""
    try:
        animation = animations_store[animation_id]
        
        # Étape 1: Générer l'idée
        print(f"💡 Génération d'idée pour {animation_id}")
        animation.status = "generating_idea"
        
        # Utiliser asyncio pour les fonctions async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        story_idea = loop.run_until_complete(generate_story_idea(theme, duration, custom_prompt))
        animation.story_idea = story_idea
        
        # Étape 2: Créer les scènes  
        print(f"🎬 Création des scènes pour {animation_id}")
        animation.status = "creating_scenes"
        
        scenes = loop.run_until_complete(generate_scenes(story_idea, duration))
        animation.scenes = scenes
        
        # Étape 3: Générer les clips vidéo
        print(f"🎥 Génération des clips pour {animation_id}")
        animation.status = "generating_clips"
        
        video_clips = []
        for scene in scenes:
            print(f"📹 Génération clip {scene.scene_number}")
            
            video_url = generate_video_with_wavespeed(scene.prompt, scene.duration)
            
            clip = VideoClip(
                scene_number=scene.scene_number,
                video_url=video_url,
                duration=scene.duration,
                status="completed" if video_url else "failed: Timeout: La génération vidéo n'a pas abouti dans les temps"
            )
            video_clips.append(clip)
        
        animation.video_clips = video_clips
        
        # Vérifier si au moins un clip a réussi
        successful_clips = [clip for clip in video_clips if clip.status == "completed"]
        
        if successful_clips:
            animation.status = "completed"
            animation.final_video_url = successful_clips[0].video_url  # Pour l'instant, premier clip
        else:
            animation.status = "failed"
            animation.error_message = "Aucun clip vidéo n'a pu être généré"
        
        # Calculer le temps de traitement
        start_time = datetime.fromisoformat(animation.created_at)
        animation.processing_time = (datetime.now() - start_time).total_seconds()
        
        loop.close()
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement {animation_id}: {e}")
        animation.status = "failed"
        animation.error_message = str(e)

if __name__ == "__main__":
    print("🚀 Démarrage Animation Studio Backend - FRIDAY")
    print(f"✅ OpenAI configuré: {bool(OPENAI_API_KEY)}")
    print(f"✅ Wavespeed configuré: {bool(WAVESPEED_API_KEY)}")
    print(f"✅ FAL configuré: {bool(FAL_API_KEY)}")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8007,
        reload=False,
        log_level="info"
    )