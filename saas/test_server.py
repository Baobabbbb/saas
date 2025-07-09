#!/usr/bin/env python3
"""
Serveur minimal pour tester le ComicGenerator
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

# Import des services
from services.comic_generator import ComicGenerator

app = FastAPI(title="Test BD API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le générateur BD
comic_generator_instance = ComicGenerator()

# Servir les fichiers statiques
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Serveur BD Test OK", "status": "running"}

@app.post("/test_comic/")
async def test_comic():
    """Test simple de génération BD"""
    try:
        test_data = {
            "theme": "adventure",
            "story_length": "short",
            "art_style": "cartoon",
            "custom_request": "Test simple"
        }
        
        result = await comic_generator_instance.create_complete_comic(test_data)
        
        # Retourner le résultat complet pour l'interface
        return result
        
    except Exception as e:
        import traceback
        print(f"Erreur: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    print("🧪 Démarrage serveur test BD...")
    uvicorn.run(app, host="0.0.0.0", port=8010)
