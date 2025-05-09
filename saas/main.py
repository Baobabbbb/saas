from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware  # ✅ Import du middleware CORS

from models import ComicRequest
from services.scenario import generate_scenario
from services.image_gen import generate_images
from services.composer import compose_pages
from services.tts import generate_speech
from services.stt import transcribe_audio
import traceback

app = FastAPI()

# ✅ Middleware CORS pour autoriser les appels depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Middleware pour logguer les exceptions avec trace complète
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("🔥 Exception occurred during request:")
        traceback.print_exc()
        raise e

# ✅ Validation des dialogues dans le scénario
def validate_scenario(scenario):
    scenes = scenario.get("scenes", [])
    if not scenes:
        raise ValueError("❌ Le scénario ne contient aucune scène.")
    
    for i, scene in enumerate(scenes):
        dialogues = scene.get("dialogues")
        if dialogues is None:
            raise ValueError(f"❌ La scène {i + 1} ne contient pas de 'dialogues'")
        
        for j, dialog in enumerate(dialogues):
            if not isinstance(dialog, dict):
                raise ValueError(f"❌ Le dialogue {j + 1} de la scène {i + 1} n'est pas un dictionnaire")
            if "character" not in dialog or "text" not in dialog:
                raise ValueError(f"❌ Le dialogue {j + 1} de la scène {i + 1} est mal formé : {dialog}")

# ✅ Route de génération de BD
@app.post("/generate_comic/")
async def generate_comic(data: ComicRequest):
    try:
        # Construit le prompt à partir des champs reçus
        prompt = (
            f"Créer une bande dessinée pour enfant avec un style {data.style}, "
            f"un héros nommé {data.hero_name}, sur le thème '{data.story_type}'. "
            f"{data.custom_request}"
        )

        scenario = await generate_scenario(prompt)
        validate_scenario(scenario)

        images = await generate_images(scenario)
        for i, scene in enumerate(scenario["scenes"]):
            scene["image"] = images[i]

        final_pages = await compose_pages(scenario)

        print("✅ Images finales :", final_pages)

        return {
            "title": f"Aventure de {data.hero_name}",
            "pages": final_pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Route Text-to-Speech
@app.post("/tts")
async def tts_endpoint(data: dict):
    try:
        text = data["text"]
        path = generate_speech(text)
        return {"audio_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Route Speech-to-Text
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
