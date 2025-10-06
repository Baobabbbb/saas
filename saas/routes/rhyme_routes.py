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
        
        if needs_custom:
            
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise HTTPException(400, "OpenAI key missing")
            
            prompt_text = f"Écris une courte comptine joyeuse en français pour enfants de 3-8 ans sur: {theme}"
            if custom_request:
                prompt_text += f". Demande: {custom_request}"
            prompt_text += "\nFormat: TITRE: [titre]\nCOMPTINE: [texte]"
            
            client = AsyncOpenAI(api_key=openai_key)
            resp = await client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "Tu es un spécialiste des comptines pour enfants."},
                    {"role": "user", "content": prompt_text}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            gpt_text = resp.choices[0].message.content.strip() if resp.choices[0].message.content else ""
            
            title_text = f"Comptine {theme}"
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
            
            suno_res = await suno_service.generate_musical_nursery_rhyme(
                lyrics=lyrics_text,
                rhyme_type=theme,
                title=title_text,
                custom_mode=True
            )
            
        else:
            descriptions = {
                "lullaby": "Berceuse douce française pour enfants",
                "counting": "Comptine éducative française pour compter",
                "animal": "Comptine joyeuse française sur les animaux",
                "seasonal": "Comptine festive française sur les saisons",
                "educational": "Comptine éducative française ludique",
                "movement": "Comptine énergique française pour danser"
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

