"""
Service de génération de prompts vidéo détaillés
Utilise GPT-4o-mini pour créer des prompts optimisés pour SD3-Turbo
"""
import json
import asyncio
from typing import List, Dict, Any
import aiohttp

class VideoPromptGenerator:
    """Générateur de prompts vidéo pour SD3-Turbo"""
    
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate_prompts(self, scenes: List[Dict], visual_style: Dict) -> List[Dict[str, Any]]:
        """
        Générer des prompts vidéo détaillés pour chaque scène
        
        Args:
            scenes: Liste des scènes analysées
            visual_style: Style visuel défini
            
        Returns:
            Liste de prompts optimisés pour SD3-Turbo
        """
        print(f"🎯 Génération de {len(scenes)} prompts vidéo")
        
        prompts = []
        base_template = visual_style.get('base_prompt_template', 'High quality animation')
        consistency_keywords = visual_style.get('consistency_keywords', [])
        
        # Générer les prompts de manière séquentielle pour maintenir la cohérence
        for i, scene in enumerate(scenes):
            print(f"  📝 Prompt pour scène {i+1}/{len(scenes)}")
            
            prompt_data = await self._generate_scene_prompt(
                scene, 
                visual_style, 
                base_template, 
                i, 
                len(scenes)
            )
            
            if prompt_data:
                prompts.append(prompt_data)
            else:
                # Fallback si la génération échoue
                fallback_prompt = self._create_fallback_prompt(scene, visual_style, i)
                prompts.append(fallback_prompt)
        
        print(f"✅ {len(prompts)} prompts générés")
        return prompts
    
    async def _generate_scene_prompt(self, scene: Dict, visual_style: Dict, base_template: str, scene_index: int, total_scenes: int) -> Dict[str, Any]:
        """Générer un prompt pour une scène spécifique"""
        
        # Préparer le contexte pour GPT
        style_context = {
            "art_style": visual_style.get('visual_elements', {}).get('art_style', 'cartoon'),
            "lighting": visual_style.get('visual_elements', {}).get('lighting', 'soft'),
            "character_style": visual_style.get('character_style', {}),
            "environment_style": visual_style.get('environment_style', {}),
            "colors": visual_style.get('color_palette', {})
        }
        
        prompt = f"""
Tu es un expert en génération d'images et vidéos par IA, spécialisé dans SD3-Turbo.

MISSION: Créer un prompt vidéo parfait pour cette scène d'animation.

SCÈNE À TRAITER:
- Numéro: {scene_index + 1}/{total_scenes}
- Description: {scene.get('description', '')}
- Action: {scene.get('action', '')}
- Personnages: {scene.get('characters', [])}
- Durée: {scene.get('duration', 5)} secondes
- Émotion: {scene.get('emotion', 'neutral')}

STYLE VISUEL IMPOSÉ:
{json.dumps(style_context, indent=2)}

TEMPLATE DE BASE: {base_template}

CONTRAINTES SD3-Turbo:
- Résolution: 1024x576
- Durée: 5-15 secondes max
- Éviter les mouvements trop complexes
- Privilégier les plans fixes avec de petits mouvements
- Décrire précisément les personnages et environnements

RÉPONSE ATTENDUE (JSON strict):
{{
  "scene_id": {scene_index + 1},
  "main_prompt": "Prompt principal optimisé pour SD3-Turbo (150-200 mots max)",
  "negative_prompt": "Éléments à éviter (50-100 mots)",
  "technical_params": {{
    "width": 1024,
    "height": 576,
    "duration": {scene.get('duration', 5)},
    "motion_intensity": "low|medium|high",
    "camera_movement": "static|pan|zoom|none"
  }},
  "style_consistency": {{
    "character_description": "Description précise des personnages pour cohérence",
    "environment_description": "Description de l'environnement",
    "color_scheme": "Palette de couleurs à utiliser"
  }},
  "movement_description": "Description des mouvements attendus (subtils pour SD3-Turbo)",
  "composition": {{
    "shot_type": "close-up|medium|wide|establishing",
    "focus_point": "Point focal principal",
    "background_elements": "Éléments d'arrière-plan"
  }},
  "quality_keywords": [
    "mot-clé qualité 1",
    "mot-clé qualité 2",
    "mot-clé qualité 3"
  ]
}}

IMPORTANT:
- Le prompt DOIT être cohérent avec les scènes précédentes
- Utilise le style visuel défini
- Optimise pour SD3-Turbo (pas trop complexe)
- Assure-toi que les personnages sont reconnaissables d'une scène à l'autre
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en génération d'images par IA et en prompts pour SD3-Turbo. Tu réponds UNIQUEMENT en JSON valide."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.8
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        try:
                            prompt_data = json.loads(content)
                            
                            # Ajouter des informations de contexte
                            prompt_data['scene_source'] = scene
                            prompt_data['visual_style_name'] = visual_style.get('name', 'Unknown')
                            prompt_data['base_template'] = base_template
                            
                            return prompt_data
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur parsing JSON prompt {scene_index + 1}: {e}")
                            return None
                    else:
                        print(f"❌ Erreur API OpenAI pour prompt {scene_index + 1}: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Erreur génération prompt {scene_index + 1}: {e}")
            return None
    
    def _create_fallback_prompt(self, scene: Dict, visual_style: Dict, scene_index: int) -> Dict[str, Any]:
        """Créer un prompt de fallback si l'API échoue"""
        
        # Extraire les informations de base
        description = scene.get('description', 'Animation scene')
        characters = scene.get('characters', [])
        duration = scene.get('duration', 5)
        
        # Style de base
        art_style = visual_style.get('visual_elements', {}).get('art_style', 'cartoon')
        base_template = visual_style.get('base_prompt_template', 'High quality animation')
        
        # Créer un prompt simple mais efficace
        character_text = f"featuring {', '.join(characters)}" if characters else ""
        
        main_prompt = f"{base_template}, {art_style} style, {description} {character_text}, smooth animation, high quality, detailed, colorful"
        
        fallback = {
            "scene_id": scene_index + 1,
            "main_prompt": main_prompt,
            "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy, text, watermark",
            "technical_params": {
                "width": 1024,
                "height": 576,
                "duration": duration,
                "motion_intensity": "medium",
                "camera_movement": "static"
            },
            "style_consistency": {
                "character_description": f"Consistent {art_style} style characters",
                "environment_description": f"{art_style} style environment",
                "color_scheme": "Vibrant and consistent colors"
            },
            "movement_description": "Smooth, gentle movements suitable for SD3-Turbo",
            "composition": {
                "shot_type": "medium",
                "focus_point": "Main characters and action",
                "background_elements": "Simple but detailed background"
            },
            "quality_keywords": [
                "high quality",
                "smooth animation",
                "detailed",
                art_style
            ],
            "scene_source": scene,
            "visual_style_name": visual_style.get('name', 'Fallback Style'),
            "base_template": base_template,
            "is_fallback": True
        }
        
        print(f"📦 Prompt de fallback créé pour scène {scene_index + 1}")
        return fallback
    
    def optimize_prompt_for_sd3_turbo(self, prompt: str) -> str:
        """
        Optimiser un prompt pour SD3-Turbo
        """
        # Mots-clés qui fonctionnent bien avec SD3-Turbo
        quality_keywords = [
            "high quality",
            "detailed",
            "sharp focus",
            "professional",
            "cinematic"
        ]
        
        # Ajouter les mots-clés de qualité si pas présents
        optimized = prompt
        for keyword in quality_keywords:
            if keyword not in optimized.lower():
                optimized = f"{optimized}, {keyword}"
        
        # Limiter la longueur (SD3-Turbo préfère des prompts concis)
        if len(optimized) > 300:
            optimized = optimized[:297] + "..."
        
        return optimized
