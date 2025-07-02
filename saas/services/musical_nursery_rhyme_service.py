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
        custom_style: Optional[str] = None,
        fast_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Génère une comptine complète avec paroles et musique
        
        Args:
            rhyme_type: Type de comptine
            custom_request: Demande personnalisée
            generate_music: Si True, génère aussi la musique
            custom_style: Style musical personnalisé
            fast_mode: Si True, optimise pour la vitesse
            
        Returns:
            Dict contenant la comptine complète
        """
        try:
            print(f"🎵 Génération comptine complète: {rhyme_type} (mode {'rapide' if fast_mode else 'complet'})")
            
            # Étape 1: Générer les paroles (avec optimisation pour le mode rapide)
            lyrics_result = await self._generate_lyrics(rhyme_type, custom_request, fast_mode)
            
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
                print(f"🎼 Génération musique pour: {title} (mode {'rapide' if fast_mode else 'complet'})")
                
                music_result = await self._generate_music(
                    lyrics, rhyme_type, custom_style, fast_mode
                )
                
                if music_result["status"] == "success":
                    result.update({
                        "has_music": True,
                        "task_id": music_result.get("task_id"),  # Exposer le task_id
                        "music_status": "pending",
                        "style_used": music_result.get("style_used")
                    })
                    print(f"🎵 Génération musicale lancée (task_id: {music_result.get('task_id')})")
                    
                    # NE PAS attendre - retourner immédiatement pour éviter les timeouts
                    # Le frontend utilisera le task_id pour faire du polling
                    
                else:
                    result.update({
                        "music_status": "failed",
                        "music_error": music_result.get("error")
                    })
                    print(f"⚠️ Impossible de générer la musique: {music_result.get('error')}")
            
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
        custom_request: Optional[str] = None,
        fast_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Génère les paroles de la comptine avec OpenAI
        """
        try:
            if not self.openai_key or self.openai_key.startswith("sk-votre"):
                raise ValueError("❌ Clé API OpenAI non configurée")
            
            # Construire le prompt selon le type et le mode
            style_info = NURSERY_RHYME_STYLES.get(rhyme_type, NURSERY_RHYME_STYLES["custom"])
            
            prompt = self._build_lyrics_prompt(rhyme_type, custom_request, style_info, fast_mode)
            
            client = AsyncOpenAI(api_key=self.openai_key)
            
            start_time = datetime.now()
            response = await client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un spécialiste des comptines pour enfants. Tu écris des paroles simples, joyeuses et faciles à retenir, adaptées à la musique." + (
                            " PRIORITÉ: Comptines très courtes et simples pour génération rapide." if fast_mode else ""
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200 if fast_mode else 400,  # Réduire les tokens en mode rapide
                temperature=0.7 if fast_mode else 0.8  # Moins de créativité = plus rapide
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
        custom_style: Optional[str] = None,
        fast_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Génère la musique avec DiffRhythm
        """
        try:
            # Formater les paroles avec timing (plus court en mode rapide)
            duration = 20 if fast_mode else 30
            formatted_lyrics = diffrhythm_service.format_lyrics_with_timing(lyrics, duration)
            
            # Générer la musique avec le mode rapide
            result = await diffrhythm_service.generate_musical_nursery_rhyme(
                formatted_lyrics, rhyme_type, custom_style, fast_mode
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
        style_info: Dict[str, str],
        fast_mode: bool = True
    ) -> str:
        """
        Construit le prompt pour la génération de paroles
        """
        if fast_mode:
            # Prompts optimisés pour la vitesse
            base_prompts = {
                "lullaby": "Écris une berceuse très courte (4 lignes max) pour endormir",
                "counting": "Écris une comptine courte (4 lignes max) pour compter jusqu'à 5",
                "animal": "Écris une comptine courte (4 lignes max) sur 2-3 animaux",
                "seasonal": "Écris une comptine courte (4 lignes max) sur une saison",
                "educational": "Écris une comptine courte (4 lignes max) éducative simple",
                "movement": "Écris une comptine courte (4 lignes max) pour bouger",
                "custom": "Écris une comptine très courte (4 lignes max)"
            }
        else:
            # Prompts complets
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
- TRÈS COURTE : maximum 4-6 lignes total
- Avec des mots simples et répétitifs
- Format couplet simple (pas de refrain complexe)

OPTIMISÉ POUR GÉNÉRATION RAPIDE :
1. Titre : 2-3 mots maximum
2. Paroles : 4-6 lignes courtes maximum  
3. Mots très simples, faciles à chanter
4. Rimes évidentes (ex: chat/là, rouge/bouge)

Format de réponse :
TITRE: [titre court]
PAROLES: [4-6 lignes courtes avec rimes]
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
