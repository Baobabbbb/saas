from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from unidecode import unidecode
import traceback
import os
import json
from fastapi import Form

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

from schemas.animation import AnimationRequest, AnimationResponse, AnimationStatusResponse, AnimationStatus
from datetime import datetime
from services.scenario import generate_scenario
from services.image_gen import generate_images
from services.composer import compose_pages
from services.tts import generate_speech
from services.stt import transcribe_audio
from services.veo3_fal import veo3_fal_service
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
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour afficher les erreurs
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:        return await call_next(request)
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
    """
    Génère une bande dessinée avec CrewAI activé par défaut
    pour des bulles et dialogues plus réalistes et professionnels
    """
    try:
        print("🚀 Génération BD avec CrewAI (défaut)")
        
        # Construction du prompt optimisé pour CrewAI
        prompt = f"""
Tu es un scénariste de bande dessinée pour enfants de 6 à 9 ans.

Crée une BD avec un héros nommé {hero_name}, sur le thème "{story_type}", 
dans un style {style}. Suis cette structure :

1. La BD doit comporter exactement **{num_images} scènes**, une par image.
2. Chaque scène contient :
   - Une description visuelle claire et précise pour l'image
   - **Entre 1 et 3 dialogues maximum**, adaptés aux bulles de BD
   - Des indications de placement des personnages (gauche, droite, centre, haut, bas)

3. Les dialogues doivent être :
   - Naturels et expressifs
   - Adaptés à des enfants
   - Courts et percutants (max 2-3 phrases par bulle)
   - Variés dans le ton (parole normale, cri, chuchotement, pensée)
   - Éviter les répétitions

Structure narrative : début → problème → aventure → résolution

Langue : français

{custom_request}
""".strip()

        print("📜 Prompt de génération optimisé :", prompt)

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
            raise        # --------- Génération du scénario avec CrewAI ---------
        try:            # Génération avec CrewAI activé par défaut
            scenario = await generate_scenario(prompt=prompt, style=style, use_crewai=True, num_images=num_images)
            
            print("🧠 Scénario généré :", json.dumps(scenario, indent=2, ensure_ascii=False))
            validate_scenario(scenario, expected_num_images=num_images)
            
            if scenario.get('crewai_enhanced'):
                print("✅ Scénario amélioré par CrewAI")
            else:
                print("📝 Scénario de base utilisé")
                
        except Exception as e:
            print("❌ ERREUR étape SCENARIO avec CrewAI :", e)
            # Fallback vers génération classique
            print("🔄 Fallback vers génération classique...")
            try:
                scenario = await generate_scenario(prompt=prompt, style=style, use_crewai=False, num_images=num_images)
                validate_scenario(scenario, expected_num_images=num_images)
                print("🟢 Fallback réussi")
            except Exception as fallback_error:
                print("❌ ERREUR Fallback :", fallback_error)
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
            raise        # --------- Affectation des images aux scènes ---------
        try:
            for i, scene in enumerate(scenario["scenes"]):
                print(f"➡️ Ajout image à la scène {i} : {images[i]}")
                scene["image"] = images[i]
        except Exception as e:
            print("❌ ERREUR étape AFFECTATION IMAGE SCENE :", e)
            raise

        # --------- Composition des pages avec le système classique ---------
        try:
            print("🛠️ Composition des pages finales...")
            result = await compose_pages(scenario)
            
            # Marquage de l'amélioration CrewAI (textuelle uniquement)
            result["enhanced_by_crewai"] = scenario.get("crewai_enhanced", False)
            if result["enhanced_by_crewai"]:
                print("✅ BD générée avec améliorations textuelles CrewAI")
            else:
                print("� BD générée avec système classique")
                
        except Exception as e:
            print(f"❌ ERREUR étape COMPOSITION : {e}")
            raise

        # Nettoyage final des chemins
        final_pages = result.get("final_pages", [])
        for i, page in enumerate(final_pages):
            if page.startswith("/static/static/"):
                final_pages[i] = page.replace("/static/static/", "/static/")

        print("✅ BD générée avec succès (CrewAI par défaut)")
        print(f"📖 Pages finales : {final_pages}")
        
        return {
            "title": result.get("title", scenario.get("title", "Ma BD")),
            "pages": final_pages,
            "enhanced_by_crewai": result.get("enhanced_by_crewai", False)
        }

    except Exception as e:
        print("❌ Erreur globale génération BD :")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

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
    """Génère une nouvelle animation avec Veo3 via fal-ai"""
    try:
        print(f"🎬 Génération d'animation demandée: {request.style} - {request.theme}")
        
        # Construction du prompt pour fal-ai
        style_map = {
            "cartoon": "style cartoon coloré",
            "fairy_tale": "style conte de fées magique",
            "anime": "style anime japonais",
            "realistic": "style réaliste cinématique",
            "paper_craft": "style papier découpé artisanal",
            "watercolor": "style aquarelle artistique"
        }
        
        theme_map = {
            "adventure": "aventure épique avec des héros",
            "magic": "monde magique avec des sortilèges",
            "animals": "animaux mignons et amicaux",
            "friendship": "amitié et entraide",
            "space": "exploration spatiale futuriste",
            "underwater": "monde sous-marin coloré",
            "forest": "forêt enchantée mystérieuse",
            "superhero": "super-héros sauvant le monde"
        }
        
        prompt_parts = [
            f"Animation courte {style_map.get(request.style, request.style)}",
            f"sur le thème: {theme_map.get(request.theme, request.theme)}",
            "Adapté aux enfants, couleurs vives, mouvements fluides",
            "Qualité professionnelle haute définition"
        ]
        
        if request.prompt:
            prompt_parts.append(f"Histoire: {request.prompt}")
        
        animation_prompt = ". ".join(prompt_parts)
        
        # Détermination de l'aspect ratio
        aspect_ratio = "9:16" if request.orientation == "portrait" else "16:9"
        
        # Génération avec le service fal-ai
        result = await veo3_fal_service.generate_video(
            prompt=animation_prompt,
            aspect_ratio=aspect_ratio,
            generate_audio=True
        )
        
        # Création de la réponse
        import uuid
        animation_id = str(uuid.uuid4())
        
        animation = AnimationResponse(
            id=animation_id,
            title=request.title or "Mon Dessin Animé",
            description=request.description or "Dessin animé créé avec Veo3",
            style=request.style,
            theme=request.theme,
            orientation=request.orientation,
            status=AnimationStatus.COMPLETED,
            video_url=result["video_url"],
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        print(f"✅ Animation créée avec l'ID: {animation.id}")
        print(f"🎥 URL vidéo: {animation.video_url}")
        
        return animation
        
    except Exception as e:
        print("❌ Erreur lors de la génération d'animation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}/status", response_model=AnimationStatusResponse)
async def get_animation_status(animation_id: str):
    """Récupère le statut d'une animation (pour compatibilité)"""
    try:
        # Avec fal-ai, les animations sont synchrones donc toujours completed
        return AnimationStatusResponse(
            status=AnimationStatus.COMPLETED,
            progress=100
        )
        
    except Exception as e:
        print("❌ Erreur lors de la récupération du statut:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations/{animation_id}", response_model=AnimationResponse)
async def get_animation(animation_id: str):
    """Récupère une animation complète (pour compatibilité)"""
    try:
        # Dans cette version simplifiée, on ne stocke pas les animations
        # On retourne une animation d'exemple ou une erreur 404
        raise HTTPException(status_code=404, detail="Animation non trouvée")
        
    except HTTPException:
        raise
    except Exception as e:
        print("❌ Erreur lors de la récupération de l'animation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/animations")
async def get_user_animations(page: int = 1, limit: int = 10):
    """Récupère les animations d'un utilisateur (version simplifiée)"""
    try:
        # Version simplifiée - retourne une liste vide
        # Dans un vrai projet, on aurait une base de données
        return {
            "animations": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0
        }
        
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
    if hasattr(veo3_fal_service, 'close'):
        await veo3_fal_service.close()

# === NOUVEAU ENDPOINT BD AMÉLIORÉE AVEC CREWAI ===

@app.post("/generate_comic_enhanced/")
async def generate_comic_enhanced(
    style: str = Form(...),
    hero_name: str = Form(...),
    story_type: str = Form(...),
    custom_request: str = Form(...),
    num_images: int = Form(...),
    avatar_type: str = Form(None),
    custom_prompt: str = Form(None),
    emoji: str = Form(None),
    use_crewai: bool = Form(True),
    custom_image: Optional[UploadFile] = File(None)
):
    """
    Génère une bande dessinée avec les améliorations CrewAI
    pour des bulles et dialogues plus réalistes
    """
    try:
        print(f"🚀 Génération BD améliorée - CrewAI: {'ON' if use_crewai else 'OFF'}")
        
        # Construction du prompt optimisé pour CrewAI
        prompt = f"""
Tu es un scénariste de bande dessinée pour enfants de 6 à 9 ans.

Crée une BD avec un héros nommé {hero_name}, sur le thème "{story_type}", 
dans un style {style}. Suis cette structure :

1. La BD doit comporter exactement **{num_images} scènes**, une par image.
2. Chaque scène contient :
   - Une description visuelle claire et précise pour l'image
   - **Entre 1 et 3 dialogues maximum**, adaptés aux bulles de BD
   - Des indications de placement des personnages (gauche, droite, centre, haut, bas)

3. Les dialogues doivent être :
   - Naturels et expressifs
   - Adaptés à des enfants
   - Courts et percutants (max 2-3 phrases par bulle)
   - Variés dans le ton (parole normale, cri, chuchotement, pensée)
   - Éviter les répétitions

Structure narrative : début → problème → aventure → résolution

Langue : français

{custom_request}
""".strip()

        print("📜 Prompt de génération amélioré :", prompt)

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

        # --------- Génération du scénario avec CrewAI ---------
        try:
            # Génération avec ou sans CrewAI selon le paramètre
            scenario = await generate_scenario(prompt, style, use_crewai=use_crewai, num_images=num_images)
            
            print("🧠 Scénario généré :", json.dumps(scenario, indent=2, ensure_ascii=False))
            validate_scenario(scenario, expected_num_images=num_images)
            
            if scenario.get('crewai_enhanced'):
                print("✅ Scénario amélioré par CrewAI")
            else:
                print("📝 Scénario de base utilisé")
                
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
        except Exception as e:
            print("❌ ERREUR étape GENERATE_IMAGES :", e)
            raise

        # --------- Affectation des images aux scènes ---------
        try:
            for i, scene in enumerate(scenario["scenes"]):
                scene["image"] = images[i]
                print(f"➡️ Image assignée à la scène {i+1} : {images[i]}")
        except Exception as e:
            print("❌ ERREUR étape AFFECTATION IMAGE SCENE :", e)
            raise        # --------- Composition avec le système classique ---------
        try:
            print("�️ Composition des pages finales...")
            result = await compose_pages(scenario)
            
            # Marquage de l'amélioration CrewAI
            result["enhanced_by_crewai"] = scenario.get("crewai_enhanced", False)
            if result["enhanced_by_crewai"]:
                print("✅ BD générée avec améliorations textuelles CrewAI")
            else:
                print("� BD générée avec système classique")
                
        except Exception as e:
            print(f"❌ ERREUR étape COMPOSITION : {e}")
            # Fallback sur le système classique
            print("🔄 Fallback vers composition classique...")
            result = await compose_pages(scenario)
            result["enhanced_by_crewai"] = False

        # Nettoyage final des chemins
        final_pages = result.get("final_pages", [])
        for i, page in enumerate(final_pages):
            if page.startswith("/static/static/"):
                final_pages[i] = page.replace("/static/static/", "/static/")

        print("✅ BD améliorée générée avec succès")
        print(f"📖 Pages finales : {final_pages}")
        
        return {
            "title": result.get("title", scenario.get("title", "Ma BD")),
            "pages": final_pages,
            "enhanced_by_crewai": result.get("enhanced_by_crewai", False),
            "total_scenes": len(scenario.get("scenes", [])),
            "improvements": result.get("improvements", [])
        }

    except Exception as e:
        print("❌ Erreur globale génération BD améliorée:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

# === ENDPOINT POUR ACTIVER/DÉSACTIVER CREWAI ===

@app.post("/toggle_crewai/")
async def toggle_crewai_enhancement(enabled: bool = Form(...)):
    """
    Active ou désactive l'amélioration CrewAI globalement
    """
    try:
        # Ici vous pourriez stocker cette préférence en base de données
        # Pour l'instant, on retourne juste le statut
        return {
            "crewai_enabled": enabled,
            "message": f"Amélioration CrewAI {'activée' if enabled else 'désactivée'}",
            "features": [
                "Dialogues plus naturels et réalistes",
                "Bulles de dialogue optimisées", 
                "Placement intelligent des bulles",
                "Révision narrative par des agents spécialisés"
            ] if enabled else ["Génération BD standard"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINT DE VALIDATION CREWAI ===

@app.post("/validate_crewai_scenario/")
async def validate_crewai_scenario(scenario: dict):
    """
    Valide un scénario avec le système CrewAI
    """
    try:
        from services.crewai_text_enhancer import crewai_comic_enhancer
        validation = crewai_comic_enhancer.validate_enhanced_scenario(scenario)
        return {
            "is_valid": validation["is_valid"],
            "errors": validation["errors"],
            "recommendations": [
                "Vérifiez que chaque dialogue fait moins de 120 caractères",
                "Assurez-vous que chaque scène a une description claire",
                "Évitez plus de 3 dialogues par scène"
            ] if not validation["is_valid"] else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
