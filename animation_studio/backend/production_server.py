from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
import uuid
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les services
sys.path.append(str(Path(__file__).parent))

import os

app = FastAPI(title="Animation Studio - Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models pour les requêtes
class AnimationRequest(BaseModel):
    theme: str
    duration: int

class GenerationStatus(BaseModel):
    animation_id: str
    status: str
    progress: int
    current_step: str
    result: dict = None
    error: str = None

# Stockage en mémoire des tâches de génération
generation_tasks = {}

@app.get("/health")
async def health():
    # Vérifier les clés API
    api_status = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "wavespeed": bool(os.getenv("WAVESPEED_API_KEY")),
        "fal": bool(os.getenv("FAL_API_KEY"))
    }
    return {
        "status": "healthy", 
        "ai_services": api_status,
        "ready_for_production": all(api_status.values())
    }

@app.get("/themes")
async def get_themes():
    return {
        "themes": {
            "space": {
                "name": "Espace", 
                "description": "Aventures spatiales extraordinaires",
                "icon": "🚀",
                "elements": "Fusées, étoiles, planètes magiques"
            },
            "nature": {
                "name": "Nature", 
                "description": "Forêts enchantées et animaux merveilleux",
                "icon": "🌲",
                "elements": "Arbres, fleurs, rivières cristallines"
            },
            "adventure": {
                "name": "Aventure", 
                "description": "Quêtes héroïques et trésors cachés",
                "icon": "⚔️",
                "elements": "Héros, trésors, châteaux mystérieux"
            },
            "animals": {
                "name": "Animaux", 
                "description": "Petites créatures adorables et rigolotes",
                "icon": "🦊",
                "elements": "Animaux mignons, jeux, amitié"
            },
            "magic": {
                "name": "Magie", 
                "description": "Monde fantastique rempli de merveilles",
                "icon": "✨",
                "elements": "Sorciers, potions, sorts magiques"
            },
            "friendship": {
                "name": "Amitié", 
                "description": "Belles histoires d'amitié et de partage",
                "icon": "💖",
                "elements": "Amis, partage, moments joyeux"
            }
        },
        "durations": [30, 60, 120, 180, 240, 300],
        "default_duration": 30
    }

@app.post("/generate")
async def generate_animation(request: AnimationRequest):
    """Générer une animation avec les vraies APIs d'IA"""
    
    # Vérifier les clés API
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="Clé API OpenAI manquante")
    if not os.getenv("WAVESPEED_API_KEY"):
        raise HTTPException(status_code=500, detail="Clé API Wavespeed manquante")
    if not os.getenv("FAL_API_KEY"):
        raise HTTPException(status_code=500, detail="Clé API FAL manquante")
    
    animation_id = str(uuid.uuid4())
    
    # Initialiser le status
    generation_tasks[animation_id] = GenerationStatus(
        animation_id=animation_id,
        status="starting",
        progress=0,
        current_step="🚀 Initialisation des APIs d'IA..."
    )
    
    # Lancer la génération en arrière-plan
    asyncio.create_task(run_real_animation_generation(animation_id, request.theme, request.duration))
    
    return {"animation_id": animation_id, "status": "started"}

@app.get("/status/{animation_id}")
async def get_generation_status(animation_id: str):
    """Obtenir le statut de génération d'une animation"""
    if animation_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Animation ID non trouvé")
    
    return generation_tasks[animation_id]

async def run_real_animation_generation(animation_id: str, theme: str, duration: int):
    """Génération réelle avec les vraies APIs d'IA"""
    try:
        task = generation_tasks[animation_id]
        
        # Import des services (fait ici pour éviter les erreurs d'import au démarrage)
        try:
            from services.idea_generator import IdeaGenerator
            from services.scene_creator import SceneCreator
            from services.video_generator import VideoGenerator
            from services.audio_generator import AudioGenerator
            from services.video_assembler import VideoAssembler
        except ImportError as e:
            task.status = "error"
            task.error = f"Erreur d'import des services: {str(e)}"
            return
        
        # Étape 1: Génération de l'idée avec OpenAI
        task.current_step = "🧠 Génération de l'idée créative avec OpenAI GPT-4..."
        task.progress = 10
        
        idea_generator = IdeaGenerator()
        story_idea = await idea_generator.generate_story_idea(theme, duration)
        print(f"✅ Idée générée: {story_idea.idea[:50]}...")
        
        # Étape 2: Création des scènes avec OpenAI
        task.current_step = "🎬 Création des scènes détaillées avec OpenAI..."
        task.progress = 25
        
        scene_creator = SceneCreator()
        scenes = await scene_creator.create_scenes(story_idea, duration)
        print(f"✅ {len(scenes)} scènes créées")
        
        # Étape 3: Génération des clips vidéo avec Wavespeed AI
        task.current_step = "🎥 Génération des clips vidéo avec Wavespeed AI..."
        task.progress = 40
        
        video_generator = VideoGenerator()
        video_clips = []
        
        for i, scene in enumerate(scenes):
            task.current_step = f"🎥 Génération du clip {i+1}/{len(scenes)} avec Wavespeed AI..."
            task.progress = 40 + (i * 30 // len(scenes))
            
            clip = await video_generator.generate_clip(scene)
            video_clips.append(clip)
            print(f"✅ Clip {i+1} généré: {clip.video_url}")
        
        # Étape 4: Génération de l'audio avec FAL AI
        task.current_step = "🎵 Création de la bande sonore avec FAL AI..."
        task.progress = 75
        
        audio_generator = AudioGenerator()
        audio_track = await audio_generator.generate_audio(story_idea, duration)
        print(f"✅ Audio généré: {audio_track.audio_url}")
        
        # Étape 5: Assemblage final avec FAL AI FFmpeg
        task.current_step = "🎞️ Assemblage final avec FAL AI FFmpeg..."
        task.progress = 90
        
        video_assembler = VideoAssembler()
        final_video = await video_assembler.assemble_video(video_clips, audio_track, duration)
        print(f"✅ Vidéo finale assemblée: {final_video}")
        
        # Finalisation
        task.current_step = "✨ Animation terminée avec succès !"
        task.progress = 100
        task.status = "completed"
        task.result = {
            "final_video_url": final_video.get("video_url"),
            "download_url": final_video.get("download_url"),
            "story_idea": {
                "idea": story_idea.idea,
                "caption": story_idea.caption,
                "environment": story_idea.environment,
                "sound": story_idea.sound
            },
            "scenes_count": len(scenes),
            "clips_count": len(video_clips),
            "theme": theme,
            "duration": duration,
            "ai_models_used": [
                f"OpenAI {os.getenv('TEXT_MODEL', 'gpt-4o-mini')}",
                f"Wavespeed {os.getenv('WAVESPEED_MODEL', 'bytedance/seedance-v1-pro-t2v-480p')}",
                f"FAL {os.getenv('FAL_AUDIO_MODEL', 'fal-ai/mmaudio-v2')}",
                f"FAL {os.getenv('FAL_FFMPEG_MODEL', 'fal-ai/ffmpeg-api/compose')}"
            ]
        }
        
        print(f"🎉 Animation {animation_id} générée avec succès !")
        
    except Exception as e:
        task.status = "error"
        task.error = f"Erreur lors de la génération: {str(e)}"
        task.current_step = "❌ Erreur de génération"
        print(f"❌ Erreur génération {animation_id}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Animation Studio - PRODUCTION avec vraies APIs d'IA")
    print(f"🤖 OpenAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    print(f"🎥 Wavespeed: {'✅' if os.getenv('WAVESPEED_API_KEY') else '❌'}")
    print(f"🎵 FAL AI: {'✅' if os.getenv('FAL_API_KEY') else '❌'}")
    print("🎬 Prêt à générer des vraies animations sur le port 8010...")
    uvicorn.run(app, host="0.0.0.0", port=8010) 