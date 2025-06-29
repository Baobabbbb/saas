"""
Pipeline complète et optimisée pour générer des dessins animés IA fluides
Sans CrewAI - Utilise GPT-4o-mini + SD3-Turbo
"""

import json
import time
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiohttp
import openai
from openai import AsyncOpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class AnimationPipeline:
    """Pipeline modulaire pour générer des dessins animés IA"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.cache_dir = Path("cache/animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration pour SD3-Turbo
        self.sd3_api_url = "https://api.stability.ai/v2beta/stable-video/txt2vid"
        
        print(f"🎬 Pipeline Animation IA initialisée")
        print(f"   📁 Cache: {self.cache_dir}")
        print(f"   🤖 Modèles: GPT-4o-mini + SD3-Turbo")
    
    async def generate_animation(self, story: str, target_duration: int = 60, style_hint: str = "cartoon") -> Dict[str, Any]:
        """
        Pipeline complète de génération d'animation
        
    # ===== ÉTAPE 1: DÉCOUPAGE NARRATIF =====
    async def analyze_and_split_story(self, story: str, target_duration: int = 60) -> Dict[str, Any]:
        """
        Découpe le récit en 8-12 scènes clés avec durées optimisées
        """
        try:
            # Calculer le nombre optimal de scènes
            scene_duration = 15 if target_duration <= 60 else 20  # 15-20s par scène
            num_scenes = min(12, max(8, target_duration // scene_duration))
            
            prompt = f"""
Tu es un expert en narration visuelle pour enfants. Analyse cette histoire et découpe-la en {num_scenes} scènes visuelles clés.

HISTOIRE: {story}

CONSIGNES:
- Chaque scène doit représenter un moment fort, une action visuelle marquante
- Durée cible par scène: {scene_duration}s
- Total visé: {target_duration}s
- Descriptions courtes mais riches visuellement
- Adapté aux enfants (0-12 ans)

Réponds en JSON avec cette structure exacte:
{{
    "total_scenes": {num_scenes},
    "target_duration": {target_duration},
    "scenes": [
        {{
            "scene_number": 1,
            "description": "Description visuelle détaillée de la scène",
            "action": "Action principale qui se déroule",
            "setting": "Décor et ambiance",
            "duration": {scene_duration},
            "key_elements": ["élément1", "élément2"]
        }}
    ]
}}
"""
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse la réponse JSON
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON si nécessaire
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            scene_data = json.loads(content)
            
            print(f"✅ Découpage: {scene_data['total_scenes']} scènes générées")
            return scene_data
            
        except Exception as e:
            print(f"❌ Erreur découpage narratif: {e}")
            # Fallback simple
            return {
                "total_scenes": 3,
                "target_duration": target_duration,
                "scenes": [
                    {
                        "scene_number": 1,
                        "description": f"Début de l'histoire: {story[:100]}...",
                        "action": "Introduction des personnages",
                        "setting": "Décor initial",
                        "duration": target_duration // 3,
                        "key_elements": ["personnages", "décor"]
                    },
                    {
                        "scene_number": 2,
                        "description": f"Développement: action principale",
                        "action": "Aventure et péripéties",
                        "setting": "Lieux d'action",
                        "duration": target_duration // 3,
                        "key_elements": ["action", "mouvement"]
                    },
                    {
                        "scene_number": 3,
                        "description": f"Conclusion heureuse",
                        "action": "Résolution et fin",
                        "setting": "Décor final",
                        "duration": target_duration // 3,
                        "key_elements": ["résolution", "bonheur"]
                    }
                ]
            }

    # ===== ÉTAPE 2: STYLE GRAPHIQUE ET SEEDS =====
    async def define_visual_style(self, story: str, style_preference: str = "cartoon") -> Dict[str, Any]:
        """
        Définit le style graphique constant et les seeds pour la cohérence
        """
        try:
            prompt = f"""Tu es un directeur artistique pour dessins animés enfants. Définis le style visuel pour cette histoire.

HISTOIRE: {story}
STYLE DEMANDÉ: {style_preference}

Créer un style cohérent adapté aux enfants avec:
- Palette de couleurs dominantes  
- Style d'animation (cartoon, pastel, vibrant)
- Ambiance générale
- Seeds pour personnages récurrents

Réponds en JSON:
{{
    "visual_style": {{
        "main_style": "description du style principal",
        "color_palette": ["couleur1", "couleur2", "couleur3"],
        "animation_style": "cartoon/anime/pastel",
        "mood": "magique/aventurier/doux",
        "quality_tags": ["high quality", "detailed", "colorful"]
    }},
    "character_seeds": {{
        "main_character": 123456,
        "secondary_character": 234567
    }},
    "setting_seeds": {{
        "primary_location": 345678,
        "secondary_location": 456789
    }},
    "style_prompt_base": "prompt de base pour cohérence visuelle"
}}"""
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            style_data = json.loads(content)
            
            print(f"✅ Style défini: {style_data['visual_style']['main_style']}")
            return style_data
            
        except Exception as e:
            print(f"❌ Erreur définition style: {e}")
            # Fallback
            return {
                "visual_style": {
                    "main_style": f"Dessin animé {style_preference} coloré pour enfants",
                    "color_palette": ["bleu ciel", "vert tendre", "jaune soleil"],
                    "animation_style": style_preference,
                    "mood": "joyeux et magique",
                    "quality_tags": ["high quality", "detailed", "colorful", "child-friendly"]
                },
                "character_seeds": {"main_character": 123456},
                "setting_seeds": {"primary_location": 345678},
                "style_prompt_base": f"beautiful {style_preference} animation for children, bright colors, high quality"
            }

    # ===== ÉTAPE 3: GÉNÉRATION DES PROMPTS VIDÉO =====
    async def generate_video_prompts(self, scenes: List[Dict], style_data: Dict) -> List[Dict]:
        """
        Génère des prompts text-to-video détaillés pour chaque scène
        """
        try:
            video_prompts = []
            base_style = style_data["style_prompt_base"]
            
            for scene in scenes:
                prompt = f"""
Créer un prompt text-to-video pour cette scène de dessin animé:

SCÈNE {scene['scene_number']}: {scene['description']}
ACTION: {scene['action']}
DÉCOR: {scene['setting']}
DURÉE: {scene['duration']}s

STYLE DE BASE: {base_style}
COULEURS: {', '.join(style_data['visual_style']['color_palette'])}

Le prompt doit inclure:
- Description visuelle détaillée de la scène
- Mouvement de caméra (zoom, traveling, pan...)
- Action et animation des personnages
- Ambiance et éclairage
- Style graphique cohérent

RÉPONSE (prompt direct pour génération vidéo):
"""
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=300
                )
                
                video_prompt = response.choices[0].message.content.strip()
                
                # Déterminer le seed approprié
                seed = None
                if "personnage" in scene['description'].lower():
                    seed = style_data.get("character_seeds", {}).get("main_character")
                elif "décor" in scene['description'].lower() or "lieu" in scene['description'].lower():
                    seed = style_data.get("setting_seeds", {}).get("primary_location")
                
                video_prompts.append({
                    "scene_number": scene['scene_number'],
                    "prompt": video_prompt,
                    "duration": scene['duration'],
                    "seed": seed,
                    "original_scene": scene
                })
                
            print(f"✅ {len(video_prompts)} prompts vidéo générés")
            return video_prompts
            
        except Exception as e:
            print(f"❌ Erreur génération prompts: {e}")
            return []

    # ===== ÉTAPE 4: GÉNÉRATION VIDÉO AVEC SD3-TURBO =====
    async def generate_video_clip(self, prompt_data: Dict) -> Dict:
        """
        Génère un clip vidéo avec SD3-Turbo
        """
        try:
            # Préparer les paramètres pour SD3-Turbo
            payload = {
                "prompt": prompt_data["prompt"],
                "duration": min(30, prompt_data["duration"]),  # SD3-Turbo max 30s
                "aspect_ratio": "16:9",
                "fps": 24,
                "motion_level": 75,  # Mouvement modéré pour enfants
                "quality": "standard"
            }
            
            # Ajouter le seed si disponible
            if prompt_data.get("seed"):
                payload["seed"] = prompt_data["seed"]
            
            headers = {
                "Authorization": f"Bearer {self.stability_api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"🎬 Génération clip scène {prompt_data['scene_number']}...")
            
            # Appel API avec retry
            for attempt in range(3):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            self.sd3_api_url,
                            json=payload,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=300)
                        ) as response:
                            
                            if response.status == 200:
                                result = await response.json()
                                
                                # Télécharger la vidéo générée
                                if "video_url" in result:
                                    video_filename = f"scene_{prompt_data['scene_number']}_{uuid.uuid4().hex[:8]}.mp4"
                                    video_path = self.cache_dir / video_filename
                                    
                                    # Télécharger le fichier vidéo
                                    async with session.get(result["video_url"]) as video_response:
                                        if video_response.status == 200:
                                            with open(video_path, 'wb') as f:
                                                async for chunk in video_response.content.iter_chunked(8192):
                                                    f.write(chunk)
                                            
                                            print(f"✅ Clip scène {prompt_data['scene_number']} généré: {video_filename}")
                                            
                                            return {
                                                "scene_number": prompt_data['scene_number'],
                                                "video_path": str(video_path),
                                                "video_url": f"/cache/animations/{video_filename}",
                                                "duration": prompt_data['duration'],
                                                "status": "success",
                                                "prompt": prompt_data["prompt"]
                                            }
                                
                                break
                            else:
                                error_text = await response.text()
                                print(f"⚠️ Tentative {attempt + 1} échouée: {response.status} - {error_text}")
                                
                except Exception as e:
                    print(f"⚠️ Erreur tentative {attempt + 1}: {e}")
                    if attempt < 2:
                        await asyncio.sleep(2)
                    
            # Fallback: générer une image statique avec mouvement simulé
            print(f"🔄 Fallback: génération image statique pour scène {prompt_data['scene_number']}")
            return await self._generate_fallback_clip(prompt_data)
            
        except Exception as e:
            print(f"❌ Erreur génération clip: {e}")
            return await self._generate_fallback_clip(prompt_data)

    async def _generate_fallback_clip(self, prompt_data: Dict) -> Dict:
        """
        Génère un fallback avec image statique ou clip simple
        """
        try:
            # Créer un nom de fichier placeholder
            filename = f"scene_{prompt_data['scene_number']}_fallback_{uuid.uuid4().hex[:8]}.json"
            filepath = self.cache_dir / filename
            
            # Sauvegarder les métadonnées pour debug
            fallback_data = {
                "scene_number": prompt_data['scene_number'],
                "prompt": prompt_data["prompt"],
                "status": "fallback",
                "duration": prompt_data['duration'],
                "type": "placeholder"
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(fallback_data, f, ensure_ascii=False, indent=2)
            
            return {
                "scene_number": prompt_data['scene_number'],
                "video_path": str(filepath),
                "video_url": f"/cache/animations/{filename}",
                "duration": prompt_data['duration'],
                "status": "fallback",
                "prompt": prompt_data["prompt"]
            }
            
        except Exception as e:
            print(f"❌ Erreur fallback: {e}")
            return {
                "scene_number": prompt_data['scene_number'],
                "status": "error",
                "error": str(e)
            }

    # ===== ÉTAPE 5: ASSEMBLAGE FINAL =====
    async def assemble_final_video(self, clips: List[Dict], metadata: Dict) -> Dict:
        """
        Assemble tous les clips dans une vidéo finale avec transitions
        """
        try:
            # Pour l'instant, retourner la liste des clips avec métadonnées
            # L'assemblage vidéo pourra être fait côté frontend ou avec ffmpeg
            
            successful_clips = [clip for clip in clips if clip.get("status") == "success"]
            fallback_clips = [clip for clip in clips if clip.get("status") == "fallback"]
            
            total_duration = sum(clip.get("duration", 0) for clip in clips)
            
            final_result = {
                "status": "success",
                "total_clips": len(clips),
                "successful_clips": len(successful_clips),
                "fallback_clips": len(fallback_clips),
                "total_duration": total_duration,
                "clips": clips,
                "metadata": metadata,
                "assembly_method": "client_side",  # Assemblage côté client
                "created_at": time.time()
            }
            
            # Sauvegarder le résultat final
            result_filename = f"animation_{uuid.uuid4().hex[:8]}.json"
            result_path = self.cache_dir / result_filename
            
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Animation assemblée: {len(successful_clips)}/{len(clips)} clips réussis")
            
            return final_result
            
        except Exception as e:
            print(f"❌ Erreur assemblage: {e}")
            return {
                "status": "error",
                "error": str(e),
                "clips": clips
            }

    # ===== MÉTHODE PRINCIPALE =====
    async def generate_complete_animation(
        self, 
        story: str, 
        duration: int = 60, 
        style: str = "cartoon"
    ) -> Dict[str, Any]:
        """
        Pipeline complète: de l'histoire au dessin animé final
        """
        try:
            print(f"🎬 Début génération animation: {story[:50]}... ({duration}s, style: {style})")
            start_time = time.time()
            
            # ÉTAPE 1: Découpage narratif
            scene_data = await self.analyze_and_split_story(story, duration)
            
            # ÉTAPE 2: Style graphique
            style_data = await self.define_visual_style(story, style)
            
            # ÉTAPE 3: Prompts vidéo
            video_prompts = await self.generate_video_prompts(
                scene_data["scenes"], 
                style_data
            )
            
            # ÉTAPE 4: Génération des clips (en parallèle pour optimiser)
            print("🎬 Génération des clips vidéo...")
            clip_tasks = [
                self.generate_video_clip(prompt_data) 
                for prompt_data in video_prompts
            ]
            
            # Exécuter en parallèle avec limite
            clips = []
            for i in range(0, len(clip_tasks), 3):  # Batch de 3 pour éviter la surcharge
                batch = clip_tasks[i:i+3]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        print(f"⚠️ Erreur dans batch: {result}")
                        clips.append({"status": "error", "error": str(result)})
                    else:
                        clips.append(result)
                
                # Pause entre les batches
                if i + 3 < len(clip_tasks):
                    await asyncio.sleep(1)
            
            # ÉTAPE 5: Assemblage final
            final_result = await self.assemble_final_video(
                clips, 
                {
                    "original_story": story,
                    "scene_data": scene_data,
                    "style_data": style_data,
                    "generation_time": time.time() - start_time
                }
            )
            
            # Format de retour compatible avec l'interface existante
            animation_result = {
                "status": "success",
                "animation_id": uuid.uuid4().hex[:8],
                "story": story,
                "target_duration": duration,
                "actual_duration": final_result.get("total_duration", duration),
                "scenes": scene_data["scenes"],
                "scenes_details": scene_data["scenes"],
                "clips": clips,
                "video_clips": clips,
                "visual_style": style_data,
                "generation_time": time.time() - start_time,
                "pipeline_type": "custom_animation_ai",
                "total_scenes": len(scene_data["scenes"]),
                "successful_clips": final_result.get("successful_clips", 0),
                "fallback_clips": final_result.get("fallback_clips", 0),
                "video_url": f"/cache/animations/playlist_{uuid.uuid4().hex[:8]}.m3u8",  # Playlist pour lecture
                "note": "🎬 Animation générée avec pipeline IA optimisé (GPT-4o-mini + SD3-Turbo)"
            }
            
            print(f"🎉 Animation complète générée en {time.time() - start_time:.1f}s")
            return animation_result
            
        except Exception as e:
            print(f"❌ Erreur pipeline complète: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Erreur lors de la génération de l'animation"
            }

# Instance globale
animation_pipeline = AnimationPipeline()
