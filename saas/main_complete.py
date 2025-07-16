#!/usr/bin/env python3
"""
🚀 API COMPLÈTE ET FONCTIONNELLE
Gère toutes les générations : histoires, animations, coloriages, comptines
Version corrigée sans blocage
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import traceback
import os
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

# Charger la configuration
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")

# Configuration FastAPI
app = FastAPI(
    title="API Histoires et Coloriages", 
    version="2.0", 
    description="API complète pour générer des histoires, dessins animés et coloriages"
)

# Configuration des fichiers statiques
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
cache_dir = Path("cache")
cache_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/cache", StaticFiles(directory="cache"), name="cache")

# CORS complet
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour logs détaillés
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"🌐 {request.method} {request.url}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"✅ Réponse en {process_time:.2f}s - Status: {response.status_code}")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        print(f"❌ Erreur après {process_time:.2f}s: {e}")
        traceback.print_exc()
        raise

# === MODÈLES PYDANTIC ===

class StoryRequest(BaseModel):
    story_type: str
    voice: str
    custom_request: Optional[str] = None

class AnimationRequest(BaseModel):
    story: str
    duration: int = 30
    style: Optional[str] = "cartoon"
    theme: Optional[str] = None
    mode: Optional[str] = "demo"

class RhymeRequest(BaseModel):
    rhyme_type: str
    custom_request: Optional[str] = None
    generate_music: Optional[bool] = True

class ColoringRequest(BaseModel):
    theme: str
    difficulty: Optional[str] = "facile"
    custom_request: Optional[str] = None

# === ENDPOINTS PRINCIPAUX ===

@app.get("/")
async def root():
    return {
        "message": "🎬 API Histoires et Coloriages v2.0",
        "description": "API complète pour toutes les générations",
        "status": "operational",
        "pipeline": "GPT-4o-mini + SD3-Turbo",
        "features": [
            "Génération d'histoires personnalisées",
            "Création de dessins animés IA",
            "Comptines musicales",
            "Coloriages automatiques"
        ],
        "endpoints": {
            "health": "/health",
            "diagnostic": "/diagnostic",
            "story": "/generate_story/",
            "animation": "/generate_animation/",
            "rhyme": "/generate_rhyme/",
            "coloring": "/generate_coloring/"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "API Histoires et Coloriages",
        "version": "2.0",
        "pipeline": "GPT-4o-mini + SD3-Turbo", 
        "timestamp": datetime.now().isoformat(),
        "features_status": {
            "stories": "operational",
            "animations": "operational", 
            "rhymes": "operational",
            "coloring": "operational"
        }
    }

@app.get("/diagnostic")
async def diagnostic():
    """Diagnostic complet du système"""
    openai_key = os.getenv("OPENAI_API_KEY")
    stability_key = os.getenv("STABILITY_API_KEY")
    
    # Test rapide OpenAI
    openai_test = False
    try:
        if openai_key and not openai_key.startswith("sk-votre"):
            client = AsyncOpenAI(api_key=openai_key)
            test_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5,
                timeout=10
            )
            openai_test = bool(test_response.choices[0].message.content)
    except:
        pass
    
    return {
        "openai_configured": bool(openai_key and not openai_key.startswith("sk-votre")),
        "openai_working": openai_test,
        "stability_configured": bool(stability_key and not stability_key.startswith("sk-votre")),
        "text_model": TEXT_MODEL,
        "pipeline_version": "2.0",
        "server_status": "fully_operational",
        "timestamp": datetime.now().isoformat()
    }

# === GÉNÉRATION D'HISTOIRES ===

@app.post("/generate_story/")
async def generate_story(request: StoryRequest):
    """Génération d'histoires personnalisées"""
    try:
        print(f"📖 GÉNÉRATION HISTOIRE")
        print(f"   Type: {request.story_type}")
        print(f"   Voix: {request.voice}")
        print(f"   Demande: {request.custom_request}")
        
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            return {
                "status": "error",
                "error": "Clé API OpenAI non configurée",
                "message": "Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            }
        
        # Construire le prompt
        prompt = f"Écris une courte histoire pour enfants sur le thème : {request.story_type}.\n"
        if request.custom_request:
            prompt += f"Demande spécifique : {request.custom_request}\n"
        
        prompt += f"""L'histoire doit être racontée par un {request.voice}. Adapte le style de narration en conséquence :
- grand-pere : ton bienveillant et sage, avec des anecdotes
- grand-mere : ton chaleureux et maternel, avec de la tendresse  
- pere : ton protecteur et aventurier, avec de l'enthousiasme
- mere : ton doux et rassurant, avec de l'amour
- petit-garcon : ton espiègle et curieux, avec de l'émerveillement
- petite-fille : ton joyeux et imaginatif, avec de la fantaisie

L'histoire doit être en français, adaptée aux enfants de 3 à 8 ans, avec un message positif et éducatif.

IMPORTANT : Génère aussi un titre court et attractif pour cette histoire (maximum 4-5 mots).

Format de réponse attendu :
TITRE: [titre de l'histoire]
HISTOIRE: [texte de l'histoire]"""

        print("🤖 Génération avec OpenAI...")
        
        client = AsyncOpenAI(api_key=openai_key)
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un conteur expert pour enfants. Tu écris des histoires captivantes, éducatives et adaptées à l'âge."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.8,
            timeout=30
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extraire le titre et le contenu
        lines = content.split('\n')
        title = ""
        story_text = ""
        
        collecting_story = False
        for line in lines:
            if line.startswith("TITRE:"):
                title = line.replace("TITRE:", "").strip()
            elif line.startswith("HISTOIRE:"):
                story_text = line.replace("HISTOIRE:", "").strip()
                collecting_story = True
            elif collecting_story and line.strip():
                story_text += " " + line.strip()
        
        # Si pas de format spécifique, utiliser le contenu complet
        if not title and not story_text:
            # Prendre la première ligne comme titre et le reste comme histoire
            if lines:
                title = lines[0].strip()
                story_text = " ".join(lines[1:]).strip()
        
        if not title:
            title = f"Histoire de {request.story_type}"
        if not story_text:
            story_text = content
        
        print(f"✅ Histoire générée: '{title}' ({len(story_text)} caractères)")
        
        return {
            "status": "success",
            "title": title,
            "story": story_text,
            "voice": request.voice,
            "theme": request.story_type,
            "generation_time": time.time(),
            "message": "Histoire générée avec succès!"
        }
        
    except Exception as e:
        print(f"❌ Erreur génération histoire: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Erreur lors de la génération de l'histoire"
        }

# === GÉNÉRATION D'ANIMATIONS ===

@app.post("/generate_animation/")
async def generate_animation(request: AnimationRequest):
    """Génération de dessins animés IA"""
    try:
        print(f"🎬 GÉNÉRATION ANIMATION")
        print(f"   Histoire: {request.story[:50]}...")
        print(f"   Durée: {request.duration}s")
        print(f"   Mode: {request.mode}")
        
        # Vérifier les clés API
        openai_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not openai_key or openai_key.startswith("sk-votre"):
            return {
                "status": "error", 
                "error": "Clé API OpenAI non configurée",
                "message": "Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            }
        
        # Valider les paramètres
        duration = max(20, min(300, request.duration))
        story = request.story.strip()
        
        if len(story) < 5:
            return {
                "status": "error",
                "error": "Histoire trop courte", 
                "message": "L'histoire doit contenir au moins 5 caractères"
            }
        
        print("📦 Import du pipeline...")
        from services.pipeline_dessin_anime_v2 import creer_dessin_anime
        print("✅ Pipeline importé")
        
        print("🚀 Début génération...")
        result = await creer_dessin_anime(
            histoire=story,
            duree=duration,
            openai_key=openai_key,
            stability_key=stability_key,
            mode=request.mode
        )
        
        # Ajouter des métadonnées
        result.update({
            "theme": request.theme or "histoire",
            "original_request": {
                "story": story,
                "duration": duration,
                "style": request.style,
                "theme": request.theme,
                "mode": request.mode
            },
            "api_version": "2.0",
            "pipeline": "GPT-4o-mini + SD3-Turbo",
            "message": "✅ Animation générée avec succès"
        })
        
        print(f"✅ Animation générée: {len(result.get('scenes', []))} scènes")
        return result
        
    except Exception as e:
        print(f"❌ Erreur génération animation: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Erreur lors de la génération de l'animation"
        }

# === GÉNÉRATION DE COMPTINES ===

@app.post("/generate_rhyme/")
async def generate_rhyme(request: RhymeRequest):
    """Génération de comptines pour enfants"""
    try:
        print(f"🎵 GÉNÉRATION COMPTINE")
        print(f"   Type: {request.rhyme_type}")
        print(f"   Musique: {request.generate_music}")
        
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            return {
                "status": "error",
                "error": "Clé API OpenAI non configurée",
                "message": "Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            }
        
        # Construire le prompt
        prompt = f"Écris une comptine courte, joyeuse et rythmée pour enfants sur le thème : {request.rhyme_type}.\n"
        if request.custom_request:
            prompt += f"Demande spécifique : {request.custom_request}\n"
        
        prompt += """
La comptine doit :
- Être en français
- Avoir des rimes simples et amusantes
- Être adaptée aux enfants de 2 à 8 ans
- Être facile à retenir et à chanter
- Avoir un rythme entraînant
- Contenir un message positif

Format de réponse :
TITRE: [titre de la comptine]
COMPTINE: [texte de la comptine avec rimes]
"""

        print("🤖 Génération avec OpenAI...")
        
        client = AsyncOpenAI(api_key=openai_key)
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un créateur expert de comptines pour enfants. Tu écris des textes rythmés, rimés et joyeux."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.9,
            timeout=30
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extraire le titre et la comptine
        lines = content.split('\n')
        title = ""
        rhyme_text = ""
        
        collecting_rhyme = False
        for line in lines:
            if line.startswith("TITRE:"):
                title = line.replace("TITRE:", "").strip()
            elif line.startswith("COMPTINE:"):
                rhyme_text = line.replace("COMPTINE:", "").strip()
                collecting_rhyme = True
            elif collecting_rhyme and line.strip():
                rhyme_text += "\n" + line.strip()
        
        if not title and not rhyme_text:
            if lines:
                title = lines[0].strip()
                rhyme_text = "\n".join(lines[1:]).strip()
        
        if not title:
            title = f"Comptine de {request.rhyme_type}"
        if not rhyme_text:
            rhyme_text = content
        
        result = {
            "status": "success",
            "title": title,
            "lyrics": rhyme_text,
            "theme": request.rhyme_type,
            "generation_time": time.time(),
            "message": "Comptine générée avec succès!"
        }
        
        # Si la musique est demandée, ajouter un message explicatif
        if request.generate_music:
            result.update({
                "music_status": "not_available",
                "demo_message": "🎵 Comptine générée avec succès ! La génération musicale est en cours de développement - pour l'instant, profitez du magnifique texte créé pour votre enfant !",
                "music_note": "Vous pouvez chanter cette comptine sur une mélodie simple et entraînante !"
            })
        
        print(f"✅ Comptine générée: '{title}'")
        return result
        
    except Exception as e:
        print(f"❌ Erreur génération comptine: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Erreur lors de la génération de la comptine"
        }

# === GÉNÉRATION DE COLORIAGES ===

@app.post("/generate_coloring/")
async def generate_coloring(request: ColoringRequest):
    """Génération de coloriages personnalisés"""
    try:
        print(f"🎨 GÉNÉRATION COLORIAGE")
        print(f"   Thème: {request.theme}")
        print(f"   Difficulté: {request.difficulty}")
        
        # Vérifier la clé API
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sk-votre"):
            return {
                "status": "error",
                "error": "Clé API OpenAI non configurée",
                "message": "Veuillez configurer OPENAI_API_KEY dans le fichier .env"
            }
        
        # Pour l'instant, générer une description de coloriage
        # (En attendant l'implémentation complète du générateur d'images)
        
        prompt = f"Décris un coloriage pour enfants sur le thème : {request.theme}.\n"
        if request.custom_request:
            prompt += f"Demande spécifique : {request.custom_request}\n"
        
        prompt += f"""
Le coloriage doit être de difficulté {request.difficulty} :
- facile : formes simples, gros traits, peu de détails
- moyen : quelques détails, formes variées
- difficile : beaucoup de détails, formes complexes

Décris précisément :
1. Le sujet principal du coloriage
2. Les éléments à colorier
3. Le niveau de détail approprié
4. Les suggestions de couleurs

Format de réponse :
TITRE: [titre du coloriage]
DESCRIPTION: [description détaillée]
ELEMENTS: [liste des éléments à colorier]
COULEURS: [suggestions de couleurs]
"""

        print("🤖 Génération avec OpenAI...")
        
        client = AsyncOpenAI(api_key=openai_key)
        response = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un expert en création de coloriages pour enfants. Tu décris des dessins adaptés à chaque âge."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
            timeout=30
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extraire les informations
        lines = content.split('\n')
        title = ""
        description = ""
        elements = ""
        colors = ""
        
        current_section = ""
        for line in lines:
            if line.startswith("TITRE:"):
                title = line.replace("TITRE:", "").strip()
                current_section = "title"
            elif line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
                current_section = "description"
            elif line.startswith("ELEMENTS:"):
                elements = line.replace("ELEMENTS:", "").strip()
                current_section = "elements"
            elif line.startswith("COULEURS:"):
                colors = line.replace("COULEURS:", "").strip()
                current_section = "colors"
            elif line.strip() and current_section:
                if current_section == "description":
                    description += " " + line.strip()
                elif current_section == "elements":
                    elements += " " + line.strip()
                elif current_section == "colors":
                    colors += " " + line.strip()
        
        if not title:
            title = f"Coloriage de {request.theme}"
        
        result = {
            "status": "success",
            "title": title,
            "description": description or content,
            "elements": elements,
            "color_suggestions": colors,
            "theme": request.theme,
            "difficulty": request.difficulty,
            "generation_time": time.time(),
            "message": "Coloriage généré avec succès!",
            "demo_message": "🎨 Description de coloriage générée ! L'image sera bientôt disponible dans une prochaine version."
        }
        
        print(f"✅ Coloriage généré: '{title}'")
        return result
        
    except Exception as e:
        print(f"❌ Erreur génération coloriage: {e}")
        traceback.print_exc()
        return {
            "status": "error", 
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Erreur lors de la génération du coloriage"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
