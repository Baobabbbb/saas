"""
Routes pour la génération de comptines musicales avec Suno AI
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
from openai import AsyncOpenAI
from services.suno_service import suno_service

router = APIRouter()

# Configuration
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")


def detect_customization(custom_request: str) -> bool:
    """Détecte si personnalisation nécessaire"""
    import re
    
    if not custom_request:
        return False
    
    keywords = ['prénom', 'nom', 'appelle', 'appelé', 'appelée',
                'mon', 'ma', 'mes', 'notre', 'nos',
                'ans', 'année', 'anniversaire', 'ville', 'maison']
    
    for kw in keywords:
        if kw.lower() in custom_request.lower():
            return True
    
    if re.search(r'\b[A-Z][a-zéèêàâûôîïü]+\b', custom_request):
        return True
    
    if len(custom_request) > 30:
        return True
    
    return False


@router.post("/generate_rhyme/")
async def generate_rhyme_endpoint(request: Dict[str, Any]):
    """Génère une comptine musicale"""
    try:
        theme = request.get("theme", "animaux")
        custom_request = request.get("custom_request", "")
        
        needs_custom = detect_customization(custom_request)
        
        # Si l'utilisateur a entré une personnalisation, générer un prompt optimisé
        if needs_custom and custom_request:
            
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise HTTPException(400, "OpenAI key missing")
            
            client = AsyncOpenAI(api_key=openai_key)
            
            # Étape 1 : Générer un prompt optimisé pour Suno à partir de la demande utilisateur
            prompt_optimization_request = f"""Tu es un expert en création de prompts pour Suno AI qui génère de la musique.
L'utilisateur veut une comptine personnalisée. Voici sa demande : "{custom_request}"

Transforme cette demande en un prompt clair et détaillé pour Suno qui va générer une comptine pour enfants de 3-8 ans.
Le prompt doit :
- Être en français
- Décrire clairement le contenu de la comptine
- Inclure tous les éléments personnalisés (prénoms, thèmes, etc.)
- Être adapté aux enfants
- Être musical et joyeux

Réponds UNIQUEMENT avec le prompt optimisé, sans explications supplémentaires."""

            prompt_resp = await client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "Tu es un expert en création de prompts pour l'IA musicale Suno."},
                    {"role": "user", "content": prompt_optimization_request}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            optimized_prompt = prompt_resp.choices[0].message.content.strip() if prompt_resp.choices[0].message.content else custom_request
            
            # Étape 2 : Générer les paroles avec GPT-4o-mini
            lyrics_prompt = f"Écris une courte comptine joyeuse en français pour enfants de 3-8 ans.\nDemande: {custom_request}\nFormat: TITRE: [titre]\nCOMPTINE: [texte]"
            
            lyrics_resp = await client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "Tu es un spécialiste des comptines pour enfants."},
                    {"role": "user", "content": lyrics_prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            gpt_text = lyrics_resp.choices[0].message.content.strip() if lyrics_resp.choices[0].message.content else ""
            
            title_text = f"Comptine Personnalisée"
            lyrics_text = gpt_text
            
            if "TITRE:" in gpt_text and "COMPTINE:" in gpt_text:
                try:
                    for line in gpt_text.split('\n'):
                        if line.startswith("TITRE:"):
                            title_text = line.replace("TITRE:", "").strip()
                            break
                    idx = gpt_text.find("COMPTINE:")
                    if idx != -1:
                        lyrics_text = gpt_text[idx + 9:].strip()
                except:
                    pass
            
            # Étape 3 : Envoyer à Suno avec le prompt optimisé ET les paroles
            suno_res = await suno_service.generate_musical_nursery_rhyme(
                lyrics=lyrics_text,
                rhyme_type=theme,
                title=title_text,
                custom_mode=True,
                prompt_description=optimized_prompt
            )
            
        else:
            descriptions = {
                "animal": "Comptine joyeuse française sur les animaux avec leurs sons",
                "counting": "Comptine éducative française pour apprendre à compter en s'amusant",
                "colors": "Comptine joyeuse française pour découvrir toutes les couleurs",
                "alphabet": "Comptine éducative française pour apprendre l'alphabet en chantant",
                "family": "Comptine douce française sur la famille et l'amour",
                "nature": "Comptine apaisante française sur la nature, les arbres et les fleurs",
                "seasonal": "Comptine festive française pour célébrer les saisons",
                "movement": "Comptine énergique française pour bouger, sauter et danser",
                "emotions": "Comptine expressive française pour comprendre ses émotions",
                "lullaby": "Berceuse douce et apaisante française pour s'endormir paisiblement"
            }
            
            desc = descriptions.get(theme, f"Comptine joyeuse française pour enfants sur {theme}")
            title_text = f"Comptine {theme.capitalize()}"
            lyrics_text = ""  # Pas de paroles en mode auto, Suno génère tout
            
            suno_res = await suno_service.generate_musical_nursery_rhyme(
                rhyme_type=theme,
                title=title_text,
                custom_mode=False,
                prompt_description=desc
            )
        
        if suno_res.get("status") == "success":
            task_id = suno_res.get("task_id")
            
            return {
                "title": title_text,
                "content": lyrics_text,
                "type": "rhyme",
                "task_id": task_id,
                "music_task_id": task_id,
                "music_status": "processing",
                "service": "suno",
                "has_music": True,
                "custom_mode": needs_custom,
                "message": "Comptine générée, musique en cours..."
            }
        else:
            err = suno_res.get("error", "Unknown")
            raise HTTPException(500, f"Suno: {err}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")


@router.get("/proxy_audio")
async def proxy_audio(url: str, filename: str = "comptine.mp3"):
    """Proxy pour télécharger l'audio depuis Suno (évite les problèmes CORS)"""
    import httpx
    from fastapi.responses import StreamingResponse
    import io

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Créer un flux de données
            data = io.BytesIO(response.content)

            # Retourner le fichier avec les bons headers
            return StreamingResponse(
                data,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(len(response.content))
                }
            )
    except Exception as e:
        raise HTTPException(500, f"Erreur proxy audio: {str(e)}")


