from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from unidecode import unidecode
import traceback
import os
from fastapi import Form

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from models import ComicRequest
from schemas.animation import AnimationRequest, AnimationResponse, AnimationStatusResponse
from services.scenario import generate_scenario
from services.image_gen import generate_images
from services.composer import compose_pages
from services.tts import generate_speech
from services.stt import transcribe_audio
from services.veo3_service_simple import veo3_service
from utils.translate import translate_text

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
async def generate_comic(
    style: str = Form(...),
    hero_name: str = Form(...),
    story_type: str = Form(...),
    custom_request: str = Form(...),
    num_images: int = Form(...),
    avatar_type: str = Form(None),
    custom_prompt: str = Form(None),
    emoji: str = Form(None),
    custom_image: Optional[UploadFile] = File(None)
):
    try:
        prompt = f"""
Tu es un scénariste de bande dessinée pour enfants de 6 à 9 ans.

Crée une BD avec un héros nommé {hero_name}, sur le thème "{story_type}", 
dans un style {style}. Suis cette structure :

1. La BD doit comporter exactement **{num_images} scènes**, une par image.
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

{custom_request}
""".strip()

        print("📜 Prompt de génération :", prompt)

        # -------- LOGIQUE CHOIX AVATAR --------
        image_path = None
        try:
            if avatar_type == "photo" and custom_image:
                # Cas photo uploadée
                image_bytes = await custom_image.read()
                os.makedirs("static/uploads", exist_ok=True)
                image_path = f"static/uploads/{custom_image.filename}"
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                print(f"📸 Image personnalisée enregistrée : {image_path}")

            elif avatar_type == "prompt" and custom_prompt:
                # Traduction du prompt en anglais
                prompt_en = await translate_text(custom_prompt)
                from services.image_gen import generate_hero_from_prompt
                image_path = await generate_hero_from_prompt(prompt_en)
                print(f"🤖 Héros généré par prompt (traduit) : {prompt_en} -> {image_path}")

            elif avatar_type == "emoji" and emoji:
                # Emoji = image par défaut (mapping conseillé)
                EMOJI_TO_FILENAME = {
                    "👦": "boy.png",
                    "👧": "girl.png",
                    "👶": "baby.png"
                }
                filename = EMOJI_TO_FILENAME.get(emoji, "default.png")
                image_path = f"static/emojis/{filename}"
                print(f"😀 Héros emoji : {emoji} → {image_path}")

            print("🟢 image_path utilisé :", image_path)
        except Exception as e:
            print("❌ ERREUR étape CHOIX AVATAR :", e)
            raise

        # --------- Génération du scénario ---------
        try:
            scenario = await generate_scenario(prompt)
            scenario["style"] = style
            print("🧠 Scénario généré :", scenario)
            validate_scenario(scenario, expected_num_images=num_images)
            print("🟢 Génération scénario OK")
        except Exception as e:
            print("❌ ERREUR étape SCENARIO :", e)
            raise

        # --------- Génération des images ---------
        try:
            if avatar_type == "prompt" and custom_prompt:
                images = await generate_images(scenario, hero_prompt_en=prompt_en, init_image_path=image_path)
            else:
                images = await generate_images(scenario, init_image_path=image_path)
            print("🟢 Images générées :", images)
            print("🟢 Nombre d'images générées :", len(images))
        except Exception as e:
            print("❌ ERREUR étape GENERATE_IMAGES :", e)
            raise

        # --------- Affectation des images aux scènes ---------
        try:
            for i, scene in enumerate(scenario["scenes"]):
                print(f"➡️ Ajout image à la scène {i} : {images[i]}")
                scene["image"] = images[i]
        except Exception as e:
            print("❌ ERREUR étape AFFECTATION IMAGE SCENE :", e)
            raise

        # --------- Composition des pages finales ---------
        try:
            print("🛠️ Lancement de compose_pages")
            result = await compose_pages(scenario)
        except Exception as e:
            print("❌ ERREUR étape COMPOSE_PAGES :", e)
            raise

        final_pages = result["final_pages"]
        for i, page in enumerate(final_pages):
            if page.startswith("/static/static/"):
                final_pages[i] = page.replace("/static/static/", "/static/")

        print("✅ Pages finales :", final_pages)
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

# === ENDPOINTS POUR LES ANIMATIONS ===

@app.post("/api/animations/generate", response_model=AnimationResponse)
async def generate_animation(request: AnimationRequest):
    """Génère une nouvelle animation avec Veo3"""
    try:
        print(f"🎬 Génération d'animation demandée: {request.style} - {request.theme}")
        
        animation = await veo3_service.generate_animation(request)
        
        print(f"✅ Animation créée avec l'ID: {animation.id}")
        return animation
        
    except Exception as e:
        print("❌ Erreur lors de la génération d'animation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}/status", response_model=AnimationStatusResponse)
async def get_animation_status(animation_id: str):
    """Récupère le statut d'une animation"""
    try:
        status = await veo3_service.get_animation_status(animation_id)
        return status
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("❌ Erreur lors de la récupération du statut:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}", response_model=AnimationResponse)
async def get_animation(animation_id: str):
    """Récupère une animation complète"""
    try:
        animation = await veo3_service.get_animation(animation_id)
        return animation
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("❌ Erreur lors de la récupération de l'animation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations")
async def get_user_animations(page: int = 1, limit: int = 10):
    """Récupère les animations d'un utilisateur (simulation)"""
    try:
        # Dans un vrai projet, on filtrerait par utilisateur
        # Pour la démo, on retourne toutes les animations stockées
        animations = []
        for anim_id, anim_data in veo3_service.animations_storage.items():
            animation = AnimationResponse(**anim_data["animation"])
            animations.append(animation)
        
        # Pagination simple
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_animations = animations[start_idx:end_idx]
        
        return {
            "animations": paginated_animations,
            "total": len(animations),
            "page": page,
            "limit": limit,
            "total_pages": (len(animations) + limit - 1) // limit
        }
        
    except Exception as e:
        print("❌ Erreur lors de la récupération des animations:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Cleanup à la fermeture
@app.on_event("shutdown")
async def shutdown_event():
    """Nettoie les ressources à la fermeture"""
    await veo3_service.close()
