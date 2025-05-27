from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from unidecode import unidecode
import traceback
import os

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from models import ComicRequest
from services.scenario import generate_scenario
from services.image_gen import generate_images
from services.composer import compose_pages
from services.tts import generate_speech
from services.stt import transcribe_audio

# --- Chargement .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

def validate_scenario(scenario, expected_num_images: int):
    scenes = scenario.get("scenes", [])
    if not scenes:
        raise ValueError("❌ Le scénario ne contient aucune scène.")
    
    if len(scenes) != expected_num_images:
        raise ValueError(f"❌ Le scénario contient {len(scenes)} scènes au lieu de {expected_num_images}")

    for i, scene in enumerate(scenario["scenes"]):
        dialogues = scene.get("dialogues")
        if dialogues is None:
            raise ValueError(f"❌ La scène {i + 1} n'a pas de clé 'dialogues'")
        for j, dialog in enumerate(dialogues):
            if not isinstance(dialog, dict):
                raise ValueError(f"❌ Le dialogue {j + 1} de la scène {i + 1} est invalide")
            if "character" not in dialog or "text" not in dialog:
                raise ValueError(f"❌ Le dialogue {j + 1} est mal formé : {dialog}")

@app.post("/generate_comic/")
async def generate_comic(data: ComicRequest):
    try:
        prompt = f"""
Tu es un scénariste de bande dessinée pour enfants de 6 à 9 ans.

Crée une BD avec un héros nommé {data.hero_name}, sur le thème "{data.story_type}", 
dans un style {data.style}. Suis cette structure :

1. La BD doit comporter exactement **{data.num_images} scènes**, une par image.
2. Chaque scène contient :
   - Une description visuelle claire pour l'image
   - **Entre 1 et 4 dialogues maximum**, sous forme de petites bulles de BD.

3. Les dialogues doivent être :
   - Fluides et naturels
   - Adaptés à des enfants
   - Entre 1 et 4 phrases maximum par bulle
   - Possiblement avec une exclamation suivie d'une phrase (ex: "Wow ! C'est incroyable !")
   - Parfois un brin bavards mais jamais trop longs ni redondants avec l’image

Utilise une structure narrative : début (mise en place), problème, aventure, résolution.

Langue : français

{data.custom_request}
""".strip()

        print("📜 Prompt de génération :", prompt)

        # Génère le scénario avec une seed
        scenario = await generate_scenario(prompt)

        # Injecte le style dans le scénario (utilisé par image_gen)
        scenario["style"] = data.style
        print("🎨 Style injecté dans le scénario :", data.style)

        print("🧠 Scénario généré :", scenario)
        validate_scenario(scenario, expected_num_images=data.num_images)

        # Génère les images avec seed et style
        images = await generate_images(scenario)
        for i, scene in enumerate(scenario["scenes"]):
            scene["image"] = images[i]

        # Compose les pages avec bulles et retourne les pages finales
        result = await compose_pages(scenario)

        # Corrige les URLs redondantes au cas où (sécurité)
        final_pages = result["final_pages"]
        for i, page in enumerate(final_pages):
            if page.startswith("/static/static/"):
                final_pages[i] = page.replace("/static/static/", "/static/")

        print("✅ Pages finales :", final_pages)
        print("🎯 Données reçues :", data)

        return {
            "title": result["title"],
            "pages": final_pages
        }

    except Exception as e:
        import traceback
        print("❌ Erreur dans /generate_comic/ :", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


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
            final_title = content.split("**")[1].strip()

        # Nettoyer pour un nom de fichier
        safe_filename = unidecode(final_title.lower().replace(" ", "_"))

        audio_path = generate_speech(content, voice=request.voice, filename=safe_filename)

        return {
            "title": final_title,
            "content": content,
            "audio_path": audio_path
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
            "title": f"L’histoire de {request.story_type.capitalize()}",
            "content": content,
            "audio_path": audio_path
        }

    except Exception as e:
        print("❌ Erreur lors de la génération du conte audio :")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))