#!/usr/bin/env python3
"""
🎬 Pipeline de Génération de Dessin Animé IA
Implémentation complète selon les spécifications fonctionnelles
"""

import json
import os
import asyncio
import aiohttp
import subprocess
import requests  # Ajout pour Stability AI
import base64  # Pour décoder les vidéos base64
from typing import List, Dict, Any
from pathlib import Path
import time
import openai
from openai import AsyncOpenAI
from PIL import Image  # Pour redimensionner les images

class DessinAnimePipeline:
    """Pipeline modulaire pour génération de dessins animés IA"""
    
    def __init__(self, openai_api_key: str, stability_api_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.stability_api_key = stability_api_key
        self.mode = "demo"  # Mode par défaut
        
        # Configuration
        self.cache_dir = Path("cache/animations")
        self.clips_dir = self.cache_dir / "clips"
        self.final_dir = self.cache_dir / "final"
        
        # Créer les répertoires
        for dir_path in [self.cache_dir, self.clips_dir, self.final_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def decouper_histoire_en_scenes(self, histoire: str, duree_totale: int) -> List[Dict[str, Any]]:
        """
        Étape 1: Découper l'histoire en 8-12 scènes visuelles
        """
        print(f"🎬 Étape 1: Découpage de l'histoire en scènes (durée cible: {duree_totale}s)")
        
        # Calculer le nombre de scènes optimal
        nb_scenes = max(8, min(12, duree_totale // 20))  # 20s par scène en moyenne
        duree_par_scene = duree_totale // nb_scenes
        
        prompt = f"""Tu es un expert en narration visuelle pour dessins animés enfants.

HISTOIRE À DÉCOUPER:
{histoire}

CONTRAINTES:
- Découper en {nb_scenes} scènes visuelles distinctes
- Durée cible par scène: {duree_par_scene} secondes
- Chaque scène doit être visuellement marquante et adaptée aux enfants
- Privilégier les actions et mouvements visibles
- Éviter les dialogues longs, se concentrer sur l'action visuelle

STRUCTURE DE RÉPONSE JSON EXACTE:
{{
    "total_scenes": {nb_scenes},
    "duree_totale_cible": {duree_totale},
    "scenes": [
        {{
            "id": 1,
            "description": "Description visuelle précise de la scène",
            "duree_estimee": {duree_par_scene},
            "action_principale": "Action ou mouvement principal",
            "personnages": ["personnage1", "personnage2"],
            "decor": "Description du décor/environnement"
        }}
    ]
}}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            scenes_data = json.loads(content)
            print(f"✅ {scenes_data['total_scenes']} scènes générées")
            
            return scenes_data['scenes']
            
        except Exception as e:
            print(f"❌ Erreur découpage: {e}")
            # Fallback simple
            return [
                {
                    "id": i+1,
                    "description": f"Scène {i+1} de l'histoire",
                    "duree_estimee": duree_par_scene,
                    "action_principale": "Action narrative",
                    "personnages": ["personnage principal"],
                    "decor": "Environnement de l'histoire"
                }
                for i in range(nb_scenes)
            ]
    
    async def definir_style_et_seeds(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Étape 2: Définir style visuel homogène et seeds pour cohérence
        """
        print("🎨 Étape 2: Définition du style visuel et seeds")
        
        # Extraire personnages et lieux récurrents
        tous_personnages = set()
        tous_lieux = set()
        
        for scene in scenes:
            tous_personnages.update(scene.get('personnages', []))
            tous_lieux.add(scene.get('decor', ''))
        
        prompt = f"""Tu es un directeur artistique pour dessins animés enfants.

SCÈNES À STYLISER:
{json.dumps(scenes, indent=2, ensure_ascii=False)}

OBJECTIF:
Créer un style visuel cohérent et des seeds pour garantir la consistance entre les clips.

STRUCTURE DE RÉPONSE JSON EXACTE:
{{
    "style_global": "description complète du style visuel (couleurs, ambiance, technique d'animation)",
    "palette_couleurs": ["#couleur1", "#couleur2", "#couleur3"],
    "ambiance": "magique/aventureuse/douce/etc",
    "seeds": {{
        "style_principal": 12345,
        "environnement_principal": 23456
    }},
    "qualite_tags": ["high quality", "detailed", "colorful", "child-friendly"],
    "style_prompt_base": "prompt de base à injecter dans chaque génération"
}}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            style_data = json.loads(content)
            print(f"✅ Style défini: {style_data['ambiance']}")
            
            return style_data
            
        except Exception as e:
            print(f"❌ Erreur style: {e}")
            # Fallback
            return {
                "style_global": "Dessin animé coloré et lumineux adapté aux enfants",
                "palette_couleurs": ["#FFB6C1", "#87CEEB", "#98FB98"],
                "ambiance": "magique",
                "seeds": {"style_principal": 12345, "environnement_principal": 23456},
                "qualite_tags": ["high quality", "detailed", "colorful", "child-friendly"],
                "style_prompt_base": "beautiful animated style, child-friendly, colorful"
            }
    
    async def generer_prompts_videos(self, scenes: List[Dict[str, Any]], style: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Étape 3: Générer prompts text-to-video optimisés pour SD3-Turbo
        """
        print("📝 Étape 3: Génération des prompts vidéo")
        
        prompts = []
        
        for scene in scenes:
            prompt = f"""You are an expert in text-to-video prompts for Stability AI.

SCENE TO CONVERT:
{json.dumps(scene, indent=2, ensure_ascii=False)}

IMPOSED STYLE:
{json.dumps(style, indent=2, ensure_ascii=False)}

OBJECTIVE:
Create an optimized prompt for SD3-Turbo that generates a {scene['duree_estimee']}s video clip.

EXACT JSON RESPONSE STRUCTURE:
{{
    "scene_id": {scene['id']},
    "prompt_text": "complete prompt optimized for text-to-video IN ENGLISH ONLY",
    "prompt_text_english": "same prompt in English for Stability AI",
    "duration": {scene['duree_estimee']},
    "seed": {style['seeds']['style_principal']},
    "camera_movement": "camera movement description",
    "visual_elements": ["element1", "element2"],
    "style_tags": {json.dumps(style['qualite_tags'])}
}}

PROMPT RULES:
- WRITE EVERYTHING IN ENGLISH (Stability AI requirement)
- Maximum 500 characters
- Describe action, movement, atmosphere
- Include camera movement (zoom, pan, tracking)
- Visual style naturally integrated
- Optimized for text-to-video, not static image
- Child-friendly cartoon style
- Use words like: cartoon, animated, colorful, cute, friendly"""

            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=800
                )
                
                content = response.choices[0].message.content.strip()
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                prompt_data = json.loads(content)
                prompts.append(prompt_data)
                
            except Exception as e:
                print(f"❌ Erreur prompt scène {scene['id']}: {e}")
                # Fallback
                prompts.append({
                    "scene_id": scene['id'],
                    "prompt_text": f"{style['style_prompt_base']}, {scene['description']}, {scene['action_principale']}",
                    "duration": scene['duree_estimee'],
                    "seed": style['seeds']['style_principal'],
                    "camera_movement": "smooth camera movement",
                    "visual_elements": scene.get('personnages', []),
                    "style_tags": style['qualite_tags']
                })
        
        print(f"✅ {len(prompts)} prompts générés")
        return prompts
    
    async def generer_clips_video(self, prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Étape 4: Générer les clips vidéo via Stability AI
        """
        if self.mode == "production":
            print("🎥 Étape 4: Génération des clips vidéo avec Stability AI (MODE PRODUCTION)")
        else:
            print("🎥 Étape 4: Génération des clips vidéo (MODE DÉMO)")
        
        clips = []
        
        for prompt_data in prompts:
            print(f"   Génération clip scène {prompt_data['scene_id']}...")
            
            if self.mode == "production":
                try:
                    # Mode production : vraie génération Stability AI
                    print(f"      🎬 Tentative génération Stability AI...")
                    clip_result = await self._generer_clip_stability_ai(prompt_data)
                    
                    if clip_result:
                        clips.append(clip_result)
                        print(f"      ✅ Clip Stability AI généré avec succès")
                    else:
                        print(f"      ⚠️ Clip Stability AI vide - fallback vers démo")
                        clip_result = await self._generer_clip_demo(prompt_data)
                        clips.append(clip_result)
                    
                    # Pause entre les générations pour éviter la rate limit
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"      ❌ ERREUR Stability AI pour scène {prompt_data['scene_id']}: {e}")
                    print(f"      📋 Type d'erreur: {type(e).__name__}")
                    import traceback
                    print(f"      📝 Détails: {traceback.format_exc()}")
                    print("      🔄 Fallback vers génération de démo...")
                    
                    # Fallback vers démo en cas d'erreur
                    clip_result = await self._generer_clip_demo(prompt_data)
                    clips.append(clip_result)
            else:
                # Mode démo : génération rapide avec images
                clip_result = await self._generer_clip_demo(prompt_data)
                clips.append(clip_result)
        
        print(f"✅ {len(clips)} clips générés")
        return clips

    async def _generer_clip_stability_ai(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génération de clip vidéo réelle via Stability AI
        """
        scene_id = prompt_data['scene_id']
        
        # Pour SD3-Turbo, nous devons d'abord générer une image, puis la convertir en vidéo
        # Étape 1: Générer une image de base avec SD3
        image_result = await self._generer_image_sd3(prompt_data)
        
        if not image_result:
            raise Exception("Échec génération image de base")
        
        # Étape 2: Convertir l'image en vidéo avec Stable Video Diffusion
        video_result = await self._image_to_video_stability(image_result, prompt_data)
        
        if not video_result:
            raise Exception("Échec conversion image vers vidéo")
        
        return {
            "scene_number": scene_id,
            "scene_id": scene_id,
            "video_path": video_result['video_path'],
            "video_url": video_result['video_url'],
            "image_url": image_result['image_url'],  # Image de base
            "thumbnail_url": image_result['image_url'],
            "status": "success",
            "statut": "generated",
            "duration": prompt_data['duration'],
            "prompt": prompt_data['prompt_text'],
            "generation_method": "stability_ai",
            "type": "real_video",
            "metadata": {
                "scene_id": scene_id,
                "image_generation": image_result,
                "video_generation": video_result,
                "timestamp": time.time()
            }
        }

    async def _generer_image_sd3(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Générer une image de base avec SD3
        """
        print(f"      🖼️ Génération image SD3 pour scène {prompt_data['scene_id']}")
        
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Accept": "image/*",
        }
        
        # Optimiser le prompt pour SD3 (utiliser la version anglaise)
        prompt_text = prompt_data.get('prompt_text_english', prompt_data.get('prompt_text', ''))
        optimized_prompt = f"{prompt_text}, single frame, high quality animation style, colorful, child-friendly"
        
        # SOLUTION: Utiliser requests pour Stability AI (fonctionne!)
        headers_req = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Accept": "image/*",
        }
        
        files = {
            "prompt": (None, optimized_prompt),
            "mode": (None, "text-to-image"),
            "model": (None, "sd3-medium"),
            "seed": (None, str(prompt_data.get('seed', 12345))),
            "output_format": (None, "png"),
            "width": (None, "1024"),
            "height": (None, "576")  # Format 16:9 compatible avec Stable Video
        }
        
        try:
            response = requests.post(url, headers=headers_req, files=files, timeout=60)
            
            print(f"        📊 Status SD3: {response.status_code}")
            
            if response.status_code == 200:
                # Sauvegarder l'image temporaire
                image_data = response.content
                temp_image_path = self.clips_dir / f"scene_{prompt_data['scene_id']}_temp.png"
                
                with open(temp_image_path, 'wb') as f:
                    f.write(image_data)
                
                # Redimensionner pour Stable Video (1024x576)
                with Image.open(temp_image_path) as img:
                    # Redimensionner en gardant le ratio et en centrant
                    resized_img = img.resize((1024, 576), Image.Resampling.LANCZOS)
                    
                    # Sauvegarder l'image redimensionnée
                    image_filename = f"scene_{prompt_data['scene_id']}_base.png"
                    image_path = self.clips_dir / image_filename
                    resized_img.save(image_path, "PNG")
                
                # Supprimer l'image temporaire
                temp_image_path.unlink(missing_ok=True)
                
                print(f"        ✅ Image générée et redimensionnée: {image_filename} (1024x576)")
                
                return {
                    "image_path": str(image_path),
                    "image_url": f"/cache/animations/clips/{image_filename}",
                    "generation_id": f"sd3_{prompt_data['scene_id']}_{int(time.time())}"
                }
            else:
                error_text = response.text
                print(f"        ❌ Erreur SD3: {response.status_code} - {error_text}")
                return None
                
        except Exception as e:
            print(f"        💥 Exception requests: {e}")
            return None

    async def _image_to_video_stability(self, image_result: Dict[str, Any], prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertir l'image en vidéo avec Stable Video Diffusion
        """
        print(f"      🎬 Conversion image→vidéo pour scène {prompt_data['scene_id']}")
        
        url = "https://api.stability.ai/v2beta/image-to-video"
        
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
        }
        
        # Préparer l'image pour upload
        image_path = image_result['image_path']
        
        # SOLUTION: Utiliser requests pour la conversion image→vidéo aussi
        try:
            with open(image_path, 'rb') as image_file:
                files = {
                    'image': ('input.png', image_file, 'image/png'),
                    'seed': (None, str(prompt_data.get('seed', 12345))),
                    'cfg_scale': (None, '2.5'),
                    'motion_bucket_id': (None, '127'),
                }
                
                response = requests.post(url, headers=headers, files=files, timeout=60)
                
                print(f"        📊 Status conversion: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    response_text = response.text
                    
                    print(f"        📊 Content-Type: {content_type}")
                    print(f"        📊 Response length: {len(response_text)}")
                    print(f"        📊 Response starts with: {response_text[:50]}...")
                    
                    # Vérifier si c'est du JSON
                    try:
                        result = response.json()
                        generation_id = result.get('id')
                        
                        if generation_id:
                            print(f"        🎬 Génération ID: {generation_id}")
                            # Attendre et récupérer le résultat
                            video_result = await self._wait_for_video_result(generation_id)
                            return video_result
                        else:
                            print(f"        ❌ Pas d'ID de génération reçu")
                            return None
                    except:
                        # Ce n'est pas du JSON valide
                        pass
                    
                    # Vérifier si c'est une réponse vidéo en base64 ou binaire
                    if 'video/' in content_type or len(response.content) > 10000:
                        # Réponse directe avec vidéo binaire
                        print(f"        ✅ Vidéo binaire reçue directement ({len(response.content)} bytes)")
                        
                        scene_id = prompt_data['scene_id']
                        video_filename = f"scene_{scene_id}_{int(time.time())}.mp4"
                        video_path = self.clips_dir / video_filename
                        
                        with open(video_path, 'wb') as f:
                            f.write(response.content)
                        
                        print(f"        💾 Vidéo sauvegardée: {video_filename}")
                        
                        return {
                            "video_path": str(video_path),
                            "video_url": f"/cache/animations/clips/{video_filename}",
                            "generation_id": f"direct_{scene_id}"
                        }
                    elif len(response_text) > 1000 and (response_text.startswith('UklGR') or response_text.startswith('//')):
                        # Réponse directe avec vidéo en base64
                        print(f"        ✅ Vidéo base64 reçue directement ({len(response_text)} caractères)")
                        
                        try:
                            # Décoder le base64
                            video_data = base64.b64decode(response_text)
                            
                            scene_id = prompt_data['scene_id']
                            video_filename = f"scene_{scene_id}_{int(time.time())}.mp4"
                            video_path = self.clips_dir / video_filename
                            
                            with open(video_path, 'wb') as f:
                                f.write(video_data)
                            
                            print(f"        💾 Vidéo décodée et sauvegardée: {video_filename}")
                            
                            return {
                                "video_path": str(video_path),
                                "video_url": f"/cache/animations/clips/{video_filename}",
                                "generation_id": f"direct_{scene_id}"
                            }
                        except Exception as e:
                            print(f"        ❌ Erreur décodage base64: {e}")
                            return None
                    else:
                        print(f"        ❓ Type de contenu inattendu: {content_type}")
                        print(f"        ❓ Longueur: {len(response_text)}")
                        return None
                else:
                    error_text = response.text
                    print(f"        ❌ Erreur image-to-video: {response.status_code} - {error_text}")
                    return None
                    
        except Exception as e:
            print(f"        💥 Exception conversion: {e}")
            return None

    async def _wait_for_video_result(self, generation_id: str) -> Dict[str, Any]:
        """
        Attendre et récupérer le résultat de génération vidéo
        """
        print(f"      ⏳ Attente génération vidéo {generation_id}")
        
        url = f"https://api.stability.ai/v2beta/image-to-video/result/{generation_id}"
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Accept": "application/json"
        }
        
        max_attempts = 30  # Maximum 5 minutes d'attente
        attempt = 0
        
        async with aiohttp.ClientSession() as session:
            while attempt < max_attempts:
                await asyncio.sleep(10)  # Attendre 10 secondes entre chaque vérification
                attempt += 1
                
                async with session.get(url, headers=headers) as response:
                    print(f"      📊 Status check: {response.status}")
                    
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        print(f"      📊 Content-Type: {content_type}")
                        
                        if 'application/json' in content_type:
                            result = await response.json()
                            print(f"      📊 JSON keys: {list(result.keys())}")
                            
                            # Vérifier si c'est une URL de téléchargement
                            video_url = result.get('video')
                            if video_url:
                                print(f"      🔗 Données vidéo trouvées: {video_url[:50]}...")
                                
                                # Vérifier si c'est une URL ou du base64
                                if video_url.startswith('http'):
                                    # C'est une URL, télécharger
                                    video_filename = f"scene_{generation_id}.mp4"
                                    video_path = self.clips_dir / video_filename
                                    
                                    async with session.get(video_url) as video_response:
                                        if video_response.status == 200:
                                            video_data = await video_response.read()
                                            with open(video_path, 'wb') as f:
                                                f.write(video_data)
                                            
                                            print(f"      ✅ Vidéo téléchargée: {video_filename}")
                                            
                                            return {
                                                "video_path": str(video_path),
                                                "video_url": f"/cache/animations/clips/{video_filename}",
                                                "generation_id": generation_id
                                            }
                                else:
                                    # C'est du base64, décoder directement
                                    try:
                                        video_data = base64.b64decode(video_url)
                                        
                                        video_filename = f"scene_{generation_id}.mp4"
                                        video_path = self.clips_dir / video_filename
                                        
                                        with open(video_path, 'wb') as f:
                                            f.write(video_data)
                                        
                                        print(f"      ✅ Vidéo base64 décodée: {video_filename}")
                                        
                                        return {
                                            "video_path": str(video_path),
                                            "video_url": f"/cache/animations/clips/{video_filename}",
                                            "generation_id": generation_id
                                        }
                                    except Exception as e:
                                        print(f"      ❌ Erreur décodage base64: {e}")
                                        return None
                            
                            # Vérifier si la vidéo est directement en base64 dans la réponse
                            elif 'video' in result or any(k for k in result.keys() if 'video' in k.lower()):
                                print(f"      📹 Vidéo trouvée dans JSON")
                                # Chercher le champ contenant la vidéo
                                video_content = None
                                for key, value in result.items():
                                    if isinstance(value, str) and len(value) > 1000:
                                        video_content = value
                                        break
                                
                                if video_content:
                                    try:
                                        # Essayer de décoder le base64
                                        video_data = base64.b64decode(video_content)
                                        
                                        video_filename = f"scene_{generation_id}.mp4"
                                        video_path = self.clips_dir / video_filename
                                        
                                        with open(video_path, 'wb') as f:
                                            f.write(video_data)
                                        
                                        print(f"      ✅ Vidéo base64 décodée: {video_filename}")
                                        
                                        return {
                                            "video_path": str(video_path),
                                            "video_url": f"/cache/animations/clips/{video_filename}",
                                            "generation_id": generation_id
                                        }
                                    except Exception as e:
                                        print(f"      ❌ Erreur décodage: {e}")
                            
                            # Vérifier le statut
                            status = result.get('status', '')
                            if status == 'in-progress':
                                print(f"      ⏳ Génération en cours... (tentative {attempt}/{max_attempts})")
                                continue
                            elif status == 'complete':
                                print(f"      ❓ Génération complète mais pas de vidéo trouvée")
                                print(f"      📋 Réponse: {result}")
                                return None
                            else:
                                print(f"      ❓ Statut inconnu: {status}")
                                print(f"      📋 Réponse: {result}")
                        else:
                            # Réponse non-JSON, peut-être vidéo directe
                            video_data = await response.read()
                            if len(video_data) > 1000:
                                video_filename = f"scene_{generation_id}.mp4"
                                video_path = self.clips_dir / video_filename
                                
                                with open(video_path, 'wb') as f:
                                    f.write(video_data)
                                
                                print(f"      ✅ Vidéo directe téléchargée: {video_filename}")
                                
                                return {
                                    "video_path": str(video_path),
                                    "video_url": f"/cache/animations/clips/{video_filename}",
                                    "generation_id": generation_id
                                }
                    
                    elif response.status == 202:
                        # Toujours en cours de génération
                        print(f"      ⏳ Génération en cours... (tentative {attempt}/{max_attempts})")
                        continue
                    
                    else:
                        error_text = await response.text()
                        print(f"      ❌ Erreur vérification: {response.status} - {error_text}")
                        return None
        
        print(f"      ⏰ Timeout: génération trop longue")
        return None
    
    async def _generer_clip_demo(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génération de clip de démonstration (remplace SD3-Turbo temporairement)
        """
        scene_id = prompt_data['scene_id']
        
        # Créer un fichier JSON avec les métadonnées du clip
        clip_metadata = {
            "scene_id": scene_id,
            "prompt": prompt_data['prompt_text'],
            "duration": prompt_data['duration'],
            "seed": prompt_data.get('seed', 12345),
            "status": "demo_generated",
            "timestamp": time.time()
        }
        
        # Sauvegarder les métadonnées
        metadata_path = self.clips_dir / f"scene_{scene_id}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(clip_metadata, f, ensure_ascii=False, indent=2)
        
        # Utiliser l'image SVG de démo existante
        demo_image_path = f"/cache/animations/demo_images/scene_{scene_id}_demo.svg"
        
        return {
            "scene_number": scene_id,
            "scene_id": scene_id,
            "video_path": str(metadata_path),
            "video_url": demo_image_path,  # Pour la compatibilité 
            "image_url": demo_image_path,  # URL de l'image pour affichage immédiat
            "demo_image_url": demo_image_path,
            "status": "success",
            "statut": "demo_ok",
            "duration": prompt_data['duration'],
            "prompt": prompt_data['prompt_text'],
            "metadata": clip_metadata,
            "type": "local_image"
        }
    
    async def assembler_video_finale(self, clips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Étape 5: Assembler les clips en vidéo finale MP4
        """
        print("🎬 Étape 5: Assemblage vidéo finale MP4")
        
        # Séparer les vrais clips vidéo des démos
        vrais_clips = [c for c in clips if c.get('type') == 'real_video']
        clips_demo = [c for c in clips if c.get('type') != 'real_video']
        
        if vrais_clips:
            # Assembler les vraies vidéos avec FFmpeg
            video_result = await self._assembler_videos_ffmpeg(clips)
        else:
            # Mode démo : créer une playlist
            video_result = await self._creer_playlist_demo(clips)
        
        duree_totale = sum(clip.get('duration', 20) for clip in clips)
        
        result = {
            "video_finale_path": video_result['path'],
            "video_url": video_result['url'],
            "duree_totale": duree_totale,
            "clips_count": len(clips),
            "format": video_result['format'],
            "has_real_videos": len(vrais_clips) > 0,
            "demo_clips": len(clips_demo)
        }
        
        print(f"✅ Vidéo finale assemblée: {duree_totale}s ({result['format']})")
        return result

    async def _assembler_videos_ffmpeg(self, clips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assembler les clips vidéo en MP4 final avec FFmpeg
        """
        print("      🔧 Assemblage FFmpeg...")
        
        import subprocess
        
        # Créer une liste des fichiers vidéo
        video_files = []
        concat_file = self.final_dir / f"concat_{int(time.time())}.txt"
        
        with open(concat_file, 'w', encoding='utf-8') as f:
            for clip in clips:
                if clip.get('type') == 'real_video' and 'video_path' in clip:
                    video_path = clip['video_path']
                    if os.path.exists(video_path):
                        f.write(f"file '{os.path.abspath(video_path)}'\n")
                        video_files.append(video_path)
        
        if not video_files:
            raise Exception("Aucun fichier vidéo valide à assembler")
        
        # Nom du fichier final
        final_video_path = self.final_dir / f"dessin_anime_{int(time.time())}.mp4"
        
        # Commande FFmpeg pour concatener avec transitions douces
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # -y pour overwrite
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c:v', 'libx264',  # Codec vidéo
            '-preset', 'medium',  # Qualité/vitesse
            '-crf', '23',  # Qualité (lower = better)
            '-c:a', 'aac',  # Codec audio si présent
            '-movflags', '+faststart',  # Optimisation web
            str(final_video_path)
        ]
        
        try:
            # Exécuter FFmpeg
            result = subprocess.run(ffmpeg_cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minutes max
            
            if result.returncode == 0:
                print(f"      ✅ Vidéo assemblée: {final_video_path.name}")
                
                # Nettoyer le fichier concat temporaire
                concat_file.unlink(missing_ok=True)
                
                return {
                    "path": str(final_video_path),
                    "url": f"/cache/animations/final/{final_video_path.name}",
                    "format": "mp4"
                }
            else:
                print(f"      ❌ Erreur FFmpeg: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("      ⏰ Timeout FFmpeg")
            raise Exception("Assemblage vidéo trop long")
        except FileNotFoundError:
            print("      ❌ FFmpeg non trouvé")
            # Fallback vers playlist
            return await self._creer_playlist_demo(clips)

    async def _creer_playlist_demo(self, clips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Créer une playlist de démonstration
        """
        print("      📋 Création playlist démo...")
        
        playlist_data = {
            "clips": clips,
            "format": "demo_playlist",
            "timestamp": time.time(),
            "note": "Mode démonstration - utilisez des vraies vidéos pour un MP4 final"
        }
        
        playlist_path = self.final_dir / f"playlist_{int(time.time())}.m3u8"
        with open(playlist_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, ensure_ascii=False, indent=2)
        
        return {
            "path": str(playlist_path),
            "url": f"/cache/animations/final/{playlist_path.name}",
            "format": "playlist"
        }
        
        return {
            "video_finale_path": str(playlist_path),
            "video_url": f"/cache/animations/final/{playlist_path.name}",
            "duree_totale": duree_totale,
            "clips_count": len(clips),
            "format": "demo_playlist"
        }
    
    async def generer_dessin_anime_complet(self, histoire: str, duree_totale: int = 60) -> Dict[str, Any]:
        """
        Pipeline complet: histoire → dessin animé
        """
        print(f"\n🚀 DÉBUT GÉNÉRATION DESSIN ANIMÉ")
        print(f"📖 Histoire: {histoire[:100]}...")
        print(f"⏱️ Durée cible: {duree_totale}s")
        
        start_time = time.time()
        
        try:
            # Étape 1: Découpage en scènes
            scenes = await self.decouper_histoire_en_scenes(histoire, duree_totale)
            
            # Étape 2: Style et seeds
            style = await self.definir_style_et_seeds(scenes)
            
            # Étape 3: Prompts vidéo
            prompts = await self.generer_prompts_videos(scenes, style)
            
            # Étape 4: Génération clips
            clips = await self.generer_clips_video(prompts)
            
            # Étape 5: Assemblage final
            video_finale = await self.assembler_video_finale(clips)
            
            generation_time = time.time() - start_time
            
            # Préparer le résultat dans le format attendu par le frontend
            result = {
                "status": "success",
                "message": "✅ Animation générée avec succès",
                "timeline": {
                    "total_duration": duree_totale,
                    "scenes_count": len(scenes),
                    "clips_count": len(clips)
                },
                "clips": clips,  # Les clips contiennent déjà les image_url
                "video_finale": video_finale,
                "generation_time": generation_time,
                "pipeline_version": "v2.0_specs",
                
                # Métadonnées additionnelles pour compatibilité
                "scenes": scenes,
                "style": style,
                "histoire": histoire,
                "duree_totale": duree_totale
            }
            
            print(f"\n🎉 GÉNÉRATION TERMINÉE en {generation_time:.1f}s")
            return result
            
        except Exception as e:
            print(f"\n💥 ERREUR PIPELINE: {e}")
            raise


# Fonction utilitaire pour l'intégration
async def creer_dessin_anime(histoire: str, duree: int, openai_key: str, stability_key: str, mode: str = "demo") -> Dict[str, Any]:
    """
    Fonction d'entrée principale pour l'API
    
    Args:
        histoire: Texte de l'histoire
        duree: Durée cible en secondes
        openai_key: Clé API OpenAI
        stability_key: Clé API Stability AI
        mode: "demo" pour mode test avec images, "production" pour vraies vidéos
    """
    pipeline = DessinAnimePipeline(openai_key, stability_key)
    pipeline.mode = mode  # Définir le mode
    return await pipeline.generer_dessin_anime_complet(histoire, duree)


if __name__ == "__main__":
    # Test du pipeline
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_pipeline():
        openai_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not openai_key or not stability_key:
            print("❌ Clés API manquantes")
            return
        
        histoire = "Une petite licorne découvre un jardin magique plein de fleurs qui chantent et de papillons colorés qui dansent au rythme de la musique du vent."
        
        result = await creer_dessin_anime(histoire, 90, openai_key, stability_key)
        
        print("\n📊 RÉSULTAT:")
        print(f"✅ Status: {result['status']}")
        print(f"🎬 Scènes: {len(result['scenes'])}")
        print(f"🎥 Clips: {len(result['clips'])}")
        print(f"⏱️ Durée: {result['duree_totale']}s")
        print(f"🕐 Temps: {result['generation_time']:.1f}s")
    
    asyncio.run(test_pipeline())
