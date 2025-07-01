"""
Service de Comptines Musicales
Combine la génération de paroles (OpenAI) avec la génération musicale (DiffRhythm)
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, TEXT_MODEL
from services.diffrhythm_service import diffrhythm_service, NURSERY_RHYME_STYLES

class MusicalNurseryRhymeService:
    def __init__(self):
        self.openai_key = OPENAI_API_KEY
        self.text_model = TEXT_MODEL
        
    async def generate_complete_nursery_rhyme(
        self,
        rhyme_type: str,
        custom_request: Optional[str] = None,
        generate_music: bool = True,
        custom_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une comptine complète avec paroles et musique
        
        Args:
            rhyme_type: Type de comptine
            custom_request: Demande personnalisée
            generate_music: Si True, génère aussi la musique
            custom_style: Style musical personnalisé
            
        Returns:
            Dict contenant la comptine complète
        """
        try:
            print(f"🎵 Génération comptine complète: {rhyme_type}")
            
            # Étape 1: Générer les paroles
            lyrics_result = await self._generate_lyrics(rhyme_type, custom_request)
            
            if lyrics_result["status"] != "success":
                return lyrics_result
            
            title = lyrics_result["title"]
            lyrics = lyrics_result["lyrics"]
            
            result = {
                "status": "success",
                "title": title,
                "lyrics": lyrics,
                "rhyme_type": rhyme_type,
                "has_music": False,
                "generation_time": lyrics_result.get("generation_time", 0)
            }
            
            # Étape 2: Générer la musique (si demandé)
            if generate_music:
                print(f"🎼 Génération musique pour: {title}")
                
                music_result = await self._generate_music(
                    lyrics, rhyme_type, custom_style
                )
                
                if music_result["status"] == "success":
                    result.update({
                        "has_music": True,
                        "music_task_id": music_result.get("task_id"),
                        "music_status": "pending",
                        "style_used": music_result.get("style_used")
                    })
                    
                    # Attendre la génération musicale
                    completion_result = await diffrhythm_service.wait_for_completion(
                        music_result["task_id"]
                    )
                    
                    if completion_result["status"] == "completed":
                        result.update({
                            "music_status": "completed",
                            "audio_url": completion_result.get("audio_url"),
                            "music_output": completion_result.get("output")
                        })
                        print(f"✅ Comptine musicale complète générée!")
                    else:
                        result.update({
                            "music_status": "failed",
                            "music_error": completion_result.get("error")
                        })
                        print(f"⚠️ Musique échouée, mais paroles disponibles")
                else:
                    result.update({
                        "music_status": "failed",
                        "music_error": music_result.get("error")
                    })
                    print(f"⚠️ Impossible de générer la musique")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération comptine complète: {e}")
            return {
                "status": "error",
                "error": str(e),
                "rhyme_type": rhyme_type
            }
    
    async def _generate_lyrics(
        self, 
        rhyme_type: str, 
        custom_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère les paroles de la comptine avec OpenAI
        """
        try:
            if not self.openai_key or self.openai_key.startswith("sk-votre"):
                raise ValueError("❌ Clé API OpenAI non configurée")
            
            # Construire le prompt selon le type
            style_info = NURSERY_RHYME_STYLES.get(rhyme_type, NURSERY_RHYME_STYLES["custom"])
            
            prompt = self._build_lyrics_prompt(rhyme_type, custom_request, style_info)
            
            client = AsyncOpenAI(api_key=self.openai_key)
            
            start_time = datetime.now()
            response = await client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un spécialiste des comptines pour enfants. Tu écris des paroles simples, joyeuses et faciles à retenir, adaptées à la musique."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )
            generation_time = (datetime.now() - start_time).total_seconds()
            
            content = response.choices[0].message.content.strip()
            
            # Parser le contenu pour extraire titre et paroles
            title, lyrics = self._parse_lyrics_response(content)
            
            return {
                "status": "success",
                "title": title,
                "lyrics": lyrics,
                "generation_time": generation_time
            }
            
        except Exception as e:
            print(f"❌ Erreur génération paroles: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _generate_music(
        self, 
        lyrics: str, 
        rhyme_type: str, 
        custom_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère la musique avec DiffRhythm
        """
        try:
            # Formater les paroles avec timing
            formatted_lyrics = diffrhythm_service.format_lyrics_with_timing(lyrics, 30)
            
            # Générer la musique
            result = await diffrhythm_service.generate_musical_nursery_rhyme(
                formatted_lyrics, rhyme_type, custom_style
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération musique: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _build_lyrics_prompt(
        self, 
        rhyme_type: str, 
        custom_request: Optional[str], 
        style_info: Dict[str, str]
    ) -> str:
        """
        Construit le prompt pour la génération de paroles
        """
        base_prompts = {
            "lullaby": "Écris une berceuse douce et apaisante pour endormir un enfant",
            "counting": "Écris une comptine amusante pour apprendre à compter de 1 à 10",
            "animal": "Écris une comptine sur les animaux avec leurs cris et leurs caractéristiques",
            "seasonal": "Écris une comptine sur une saison ou une fête de l'année",
            "educational": "Écris une comptine éducative pour apprendre quelque chose d'important",
            "movement": "Écris une comptine avec des gestes et des mouvements pour bouger",
            "custom": "Écris une comptine joyeuse et rythmée pour enfants"
        }
        
        base_prompt = base_prompts.get(rhyme_type, base_prompts["custom"])
        
        prompt = f"{base_prompt}.\n"
        
        if custom_request:
            prompt += f"Demande spécifique : {custom_request}\n"
        
        prompt += f"""
La comptine doit être :
- En français, adaptée aux enfants de 3 à 8 ans
- Avec des rimes simples et un rythme {style_info['tempo']}
- D'ambiance {style_info['mood']}
- Facile à retenir et à chanter
- Avec des répétitions et un refrain si possible
- Environ 4-8 lignes pour être adaptée à la musique

IMPORTANT : 
1. Génère un titre court et attractif (maximum 4-5 mots)
2. Les paroles doivent être courtes et rythmées pour s'adapter à la musique
3. Utilise des mots simples que les enfants peuvent facilement chanter

Format de réponse :
TITRE: [titre de la comptine]
PAROLES: [paroles de la comptine]
"""
        
        return prompt
    
    def _parse_lyrics_response(self, content: str) -> tuple[str, str]:
        """
        Parse la réponse de l'IA pour extraire titre et paroles
        """
        lines = content.split('\n')
        title = ""
        lyrics = ""
        
        collecting_lyrics = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("TITRE:"):
                title = line.replace("TITRE:", "").strip()
            elif line.startswith("PAROLES:"):
                lyrics = line.replace("PAROLES:", "").strip()
                collecting_lyrics = True
            elif collecting_lyrics:
                lyrics += "\n" + line
            elif not title and not collecting_lyrics:
                # Si pas de format structuré, prendre la première ligne comme titre
                title = line
                collecting_lyrics = True
        
        # Nettoyer et valider
        title = title or "Comptine Joyeuse"
        lyrics = lyrics.strip() or content
        
        return title, lyrics

# Instance globale du service
musical_nursery_rhyme_service = MusicalNurseryRhymeService()
