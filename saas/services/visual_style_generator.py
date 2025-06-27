"""
Service de génération de style visuel cohérent
Utilise GPT-4o-mini pour définir un style graphique uniforme
"""
import json
import asyncio
from typing import Dict, Any
import aiohttp

class VisualStyleGenerator:
    """Générateur de style visuel pour les animations"""
    
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate_visual_style(self, story: str, style_hint: str = "cartoon") -> Dict[str, Any]:
        """
        Générer un style visuel cohérent pour toute l'animation
        
        Args:
            story: Histoire source pour adapter le style
            style_hint: Indication de style (cartoon, anime, realistic, etc.)
            
        Returns:
            Dictionnaire avec style visuel détaillé
        """
        print(f"🎨 Génération du style visuel (hint: {style_hint})")
        
        # Analyser l'histoire pour extraire les éléments clés
        story_preview = story[:500] if len(story) > 500 else story
        
        # Prompt pour définir le style
        prompt = f"""
Tu es un directeur artistique expert en animation et design visuel.

MISSION: Créer un style visuel cohérent et esthétique pour cette histoire en animation.

HISTOIRE (extrait):
{story_preview}

STYLE DEMANDÉ: {style_hint}

Crée un guide de style complet qui sera utilisé pour générer TOUTES les vidéos de l'animation.

RÉPONSE ATTENDUE (JSON strict):
{{
  "name": "Nom du style (ex: 'Fantasy Cartoon')",
  "description": "Description complète du style en 2-3 phrases",
  "color_palette": {{
    "primary": ["#couleur1", "#couleur2", "#couleur3"],
    "secondary": ["#couleur4", "#couleur5"],
    "accent": "#couleur_accent"
  }},
  "visual_elements": {{
    "art_style": "Style artistique (ex: 2D cartoon, anime, watercolor)",
    "rendering": "Type de rendu (ex: cel-shaded, realistic, stylized)",
    "lighting": "Style d'éclairage (ex: soft warm, dramatic, magical)",
    "texture": "Qualité de texture (ex: smooth, detailed, painterly)"
  }},
  "character_style": {{
    "proportions": "Proportions des personnages (ex: chibi, realistic, exaggerated)",
    "features": "Style des traits (ex: rounded, angular, soft)",
    "expression": "Style d'expression (ex: expressive, subtle, dramatic)"
  }},
  "environment_style": {{
    "backgrounds": "Style des arrière-plans (ex: detailed landscapes, simple scenes)",
    "architecture": "Style architectural si applicable",
    "nature": "Style des éléments naturels"
  }},
  "animation_style": {{
    "movement": "Style de mouvement (ex: fluid, bouncy, realistic)",
    "camera": "Style de caméra (ex: dynamic, static, cinematic)",
    "transitions": "Style de transitions (ex: smooth cuts, creative wipes)"
  }},
  "technical_specs": {{
    "quality": "sd3-turbo",
    "resolution": "1024x576",
    "fps": 24,
    "duration_per_shot": "5-15 seconds"
  }},
  "consistency_keywords": [
    "mot-clé1 pour cohérence",
    "mot-clé2 pour cohérence",
    "mot-clé3 pour cohérence"
  ],
  "base_prompt_template": "Template de prompt de base qui sera utilisé pour toutes les générations vidéo"
}}

IMPORTANT: 
- Le style DOIT être cohérent pour toute l'animation
- Adapte le style à l'histoire (fantastique, réaliste, enfantine, etc.)
- Pense aux contraintes techniques de SD3-Turbo
- Le base_prompt_template sera préfixé à tous les prompts vidéo
"""

        try:
            # Appel à l'API OpenAI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en direction artistique et design visuel pour l'animation. Tu réponds UNIQUEMENT en JSON valide."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Parser le JSON
                        try:
                            style_data = json.loads(content)
                            print(f"✅ Style généré: {style_data.get('name', 'Unknown')}")
                            return style_data
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur parsing JSON: {e}")
                            return self._get_fallback_style(style_hint)
                    else:
                        print(f"❌ Erreur API OpenAI: {response.status}")
                        return self._get_fallback_style(style_hint)
                        
        except Exception as e:
            print(f"❌ Erreur génération style: {e}")
            return self._get_fallback_style(style_hint)
    
    def _get_fallback_style(self, style_hint: str) -> Dict[str, Any]:
        """Style de fallback si l'API échoue"""
        
        # Styles prédéfinis selon le hint
        fallback_styles = {
            "cartoon": {
                "name": "Classic Cartoon",
                "description": "Style cartoon coloré et expressif avec des traits arrondis et des couleurs vives.",
                "color_palette": {
                    "primary": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
                    "secondary": ["#FFA07A", "#98D8C8"],
                    "accent": "#F7DC6F"
                },
                "visual_elements": {
                    "art_style": "2D cartoon",
                    "rendering": "cel-shaded",
                    "lighting": "soft warm",
                    "texture": "smooth"
                },
                "character_style": {
                    "proportions": "slightly exaggerated",
                    "features": "rounded and friendly",
                    "expression": "very expressive"
                },
                "environment_style": {
                    "backgrounds": "colorful and detailed",
                    "architecture": "whimsical and rounded",
                    "nature": "lush and vibrant"
                },
                "animation_style": {
                    "movement": "bouncy and energetic",
                    "camera": "dynamic with smooth movements",
                    "transitions": "smooth cuts with occasional creative wipes"
                },
                "technical_specs": {
                    "quality": "sd3-turbo",
                    "resolution": "1024x576",
                    "fps": 24,
                    "duration_per_shot": "5-15 seconds"
                },
                "consistency_keywords": [
                    "cartoon style",
                    "colorful",
                    "smooth animation",
                    "family-friendly"
                ],
                "base_prompt_template": "High quality cartoon animation, colorful and expressive, smooth movements, family-friendly style"
            },
            "anime": {
                "name": "Anime Style",
                "description": "Style anime moderne avec des personnages expressifs et des environnements détaillés.",
                "color_palette": {
                    "primary": ["#E74C3C", "#3498DB", "#F39C12"],
                    "secondary": ["#9B59B6", "#1ABC9C"],
                    "accent": "#E67E22"
                },
                "visual_elements": {
                    "art_style": "anime",
                    "rendering": "cel-shaded with highlights",
                    "lighting": "dramatic with strong contrasts",
                    "texture": "detailed"
                },
                "character_style": {
                    "proportions": "anime proportions",
                    "features": "large eyes, detailed hair",
                    "expression": "dramatic and emotional"
                },
                "environment_style": {
                    "backgrounds": "highly detailed and atmospheric",
                    "architecture": "mix of modern and traditional",
                    "nature": "beautiful and serene"
                },
                "animation_style": {
                    "movement": "fluid with dramatic pauses",
                    "camera": "cinematic with varied angles",
                    "transitions": "dramatic cuts and effects"
                },
                "technical_specs": {
                    "quality": "sd3-turbo",
                    "resolution": "1024x576",
                    "fps": 24,
                    "duration_per_shot": "5-15 seconds"
                },
                "consistency_keywords": [
                    "anime style",
                    "cel-shaded",
                    "dramatic lighting",
                    "detailed backgrounds"
                ],
                "base_prompt_template": "High quality anime animation, cel-shaded style, dramatic lighting, detailed backgrounds"
            },
            "realistic": {
                "name": "Semi-Realistic",
                "description": "Style semi-réaliste avec des textures détaillées et un éclairage naturel.",
                "color_palette": {
                    "primary": ["#8B7355", "#6B8E23", "#4682B4"],
                    "secondary": ["#CD853F", "#708090"],
                    "accent": "#DAA520"
                },
                "visual_elements": {
                    "art_style": "semi-realistic",
                    "rendering": "realistic with soft edges",
                    "lighting": "natural and soft",
                    "texture": "detailed and tactile"
                },
                "character_style": {
                    "proportions": "realistic but slightly stylized",
                    "features": "natural and detailed",
                    "expression": "subtle and nuanced"
                },
                "environment_style": {
                    "backgrounds": "photorealistic environments",
                    "architecture": "realistic and grounded",
                    "nature": "natural and authentic"
                },
                "animation_style": {
                    "movement": "realistic and smooth",
                    "camera": "cinematic and steady",
                    "transitions": "smooth and natural"
                },
                "technical_specs": {
                    "quality": "sd3-turbo",
                    "resolution": "1024x576",
                    "fps": 24,
                    "duration_per_shot": "5-15 seconds"
                },
                "consistency_keywords": [
                    "semi-realistic",
                    "natural lighting",
                    "detailed textures",
                    "smooth animation"
                ],
                "base_prompt_template": "High quality semi-realistic animation, natural lighting, detailed textures, smooth movements"
            }
        }
        
        # Sélectionner le style approprié ou cartoon par défaut
        selected_style = fallback_styles.get(style_hint.lower(), fallback_styles["cartoon"])
        
        print(f"📦 Style de fallback utilisé: {selected_style['name']}")
        return selected_style
