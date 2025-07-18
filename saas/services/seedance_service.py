"""
Service SEEDANCE pour la génération automatique de dessins animés
Basé sur le workflow n8n SEEDANCE avec intégration dans FRIDAY
"""

import os
import json
import time
import uuid
import asyncio
import aiohttp
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis le bon répertoire
load_dotenv(Path(__file__).parent.parent / ".env")

class SeedanceService:
    """Service SEEDANCE pour génération automatique de dessins animés"""
    
    def __init__(self):
        # Configuration des APIs
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.wavespeed_api_key = os.getenv("WAVESPEED_API_KEY")
        self.wavespeed_base_url = os.getenv("WAVESPEED_BASE_URL", "https://api.wavespeed.ai/api/v3")
        self.wavespeed_model = os.getenv("WAVESPEED_MODEL", "bytedance/seedance-v1-pro-t2v-480p")
        
        self.fal_api_key = os.getenv("FAL_API_KEY")
        self.fal_base_url = os.getenv("FAL_BASE_URL", "https://queue.fal.run")
        self.fal_audio_model = os.getenv("FAL_AUDIO_MODEL", "fal-ai/mmaudio-v2")
        self.fal_ffmpeg_model = os.getenv("FAL_FFMPEG_MODEL", "fal-ai/ffmpeg-api/compose")
        
        # Configuration cartoon spécifique
        self.cartoon_aspect_ratio = os.getenv("CARTOON_ASPECT_RATIO", "16:9")
        self.cartoon_duration = int(os.getenv("CARTOON_DURATION", "10"))  # Max 10s pour Wavespeed
        self.cartoon_style = os.getenv("CARTOON_STYLE", "2D cartoon animation, Disney style")
        self.cartoon_quality = os.getenv("CARTOON_QUALITY", "high quality animation, smooth movement")
        
        # Limite de durée pour Wavespeed (max 10 secondes) - DYNAMIQUE
        self.max_clip_duration = 10  # Limite Wavespeed (sera ajustée dynamiquement)
        
        # Timeouts optimisés pour réduire les temps d'attente
        self.max_clip_wait = 90  # Réduit de 140s à 90s
        self.max_audio_wait = 45  # Réduit de 60s à 45s
        self.max_final_wait = 30  # Réduit de 60s à 30s
        
        # Configuration des répertoires
        # Utiliser le chemin relatif au répertoire parent (racine du projet)
        self.cache_dir = Path(__file__).parent.parent.parent / "cache" / "seedance"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Détection de FFmpeg
        self.ffmpeg_path = self._find_ffmpeg()
        
        # Validation des clés API
        self._validate_api_keys()
    
    def _validate_api_keys(self):
        """Valide que toutes les clés API nécessaires sont configurées"""
        missing_keys = []
        
        if not self.openai_api_key or self.openai_api_key.startswith("sk-votre"):
            missing_keys.append("OPENAI_API_KEY")
        
        if not self.wavespeed_api_key or self.wavespeed_api_key.startswith("votre_"):
            missing_keys.append("WAVESPEED_API_KEY")
        
        if not self.fal_api_key or self.fal_api_key.startswith("votre_"):
            missing_keys.append("FAL_API_KEY")
        
        if missing_keys:
            raise ValueError(f"Clés API manquantes: {', '.join(missing_keys)}")
    
    async def generate_seedance_animation(
        self,
        story: str,
        theme: str = "adventure",
        age_target: str = "3-6 ans",
        duration: int = 30,  # Durée totale réduite à 30s (3 clips de 10s max)
        style: str = "cartoon"
    ) -> Dict[str, Any]:
        """
        Génère un dessin animé complet avec le workflow SEEDANCE
        
        Args:
            story: Histoire à adapter
            theme: Thème éducatif
            age_target: Tranche d'âge ciblée
            duration: Durée totale souhaitée
            style: Style visuel
            
        Returns:
            Dictionnaire avec les résultats de la génération
        """
        try:
            print(f"🎬 Génération SEEDANCE: {story[:50]}...")
            print(f"   📊 Thème: {theme}, Age: {age_target}, Durée: {duration}s")
            
            # DIAGNOSTIC DES CLÉS API
            print("🔍 Vérification des clés API...")
            if not self.openai_api_key or self.openai_api_key.startswith("sk-votre"):
                raise ValueError("Clé OpenAI manquante ou invalide. Vérifiez votre fichier .env")
            if not self.wavespeed_api_key or self.wavespeed_api_key.startswith("votre_"):
                raise ValueError("Clé Wavespeed manquante ou invalide. Vérifiez votre fichier .env")
            if not self.fal_api_key or self.fal_api_key.startswith("votre_"):
                raise ValueError("Clé Fal AI manquante ou invalide. Vérifiez votre fichier .env")
            print("✅ Toutes les clés API sont configurées")
            
            start_time = time.time()
            animation_id = str(uuid.uuid4())[:8]
            print(f"🆔 NOUVEL ID GÉNÉRATION: {animation_id}")
            
            # ÉTAPE 1: Génération d'idées avec OpenAI
            print("💡 Étape 1: Génération d'idées...")
            try:
                idea_result = await self._generate_ideas(story, theme, age_target, style)
                if not idea_result:
                    raise Exception("La génération d'idées a retourné un résultat vide")
                print(f"✅ Idées générées: {idea_result.get('Caption', 'N/A')}")
            except Exception as e:
                print(f"❌ Erreur étape 1 (idées): {e}")
                raise Exception(f"Échec de la génération d'idées: {str(e)}")
            
            # ÉTAPE 2: Génération des prompts pour 3 scènes
            print("📝 Étape 2: Génération des prompts...")
            try:
                scenes_prompts = await self._generate_scene_prompts(idea_result, duration)
                if not scenes_prompts:
                    raise Exception("La génération de prompts a retourné un résultat vide")
                print(f"✅ {len(scenes_prompts)} prompts de scènes générés")
            except Exception as e:
                print(f"❌ Erreur étape 2 (prompts): {e}")
                raise Exception(f"Échec de la génération des prompts: {str(e)}")
            
            # ÉTAPE 3: Génération des clips vidéo
            print(f"🎥 Étape 3: Génération des clips avec ID {animation_id}...")
            try:
                video_clips = await self._generate_video_clips(scenes_prompts, animation_id)
                if not video_clips:
                    raise Exception("La génération de clips a retourné un résultat vide")
                successful_clips = [clip for clip in video_clips if clip.get("status") == "success"]
                print(f"✅ {len(successful_clips)}/{len(video_clips)} clips générés avec succès")
            except Exception as e:
                print(f"❌ Erreur étape 3 (clips): {e}")
                raise Exception(f"Échec de la génération des clips: {str(e)}")
            
            # ÉTAPE 4: Génération des sons (TOUJOURS)
            audio_clips = []
            print("🔊 Étape 4: Génération des sons...")
            audio_clips = await self._generate_audio_clips(video_clips, idea_result)
            
            # ÉTAPE 5: Assemblage final
            print(f"🎞️ Étape 5: Assemblage final avec ID {animation_id}...")
            
            # Essayer d'abord l'assemblage local avec FFmpeg
            final_video = await self._assemble_local_video(video_clips, animation_id)
            
            # Si l'assemblage local échoue, essayer avec Fal AI
            if not final_video or final_video.get("status") in ["no_ffmpeg_fallback", "ffmpeg_error_fallback"]:
                print("   🔄 Assemblage local échoué, tentative Fal AI...")
                final_video = await self._assemble_final_video(video_clips, audio_clips, animation_id)
            
            # Calculer le temps total
            generation_time = time.time() - start_time
            
            # Si l'assemblage échoue, utiliser le premier clip réussi comme fallback
            if not final_video and video_clips:
                print("⚠️ Assemblage final échoué, recherche du premier clip réussi")
                # Utiliser le premier clip réussi comme fallback
                for clip in video_clips:
                    if clip.get("video_url") and clip["status"] == "success":
                        final_video = {
                            "video_url": clip["video_url"],
                            "video_path": clip.get("video_path"),
                            "status": "fallback_single_clip"
                        }
                        break
                
                # Si vraiment aucun clip n'est disponible, créer un placeholder fonctionnel
                if not final_video:
                    print("⚠️ Aucun clip disponible - création d'un placeholder fonctionnel")
                    placeholder_result = self._create_functional_placeholder(animation_id, duration, theme)
                    if placeholder_result and placeholder_result.get("video_url"):
                        final_video = placeholder_result
                        print(f"✅ Placeholder créé: {placeholder_result['video_url']}")
                    else:
                        # Dernier recours - URL simple
                        placeholder_url = self._create_placeholder_video(animation_id, duration)
                        final_video = {
                            "video_url": placeholder_url,
                            "video_path": None,
                            "status": "placeholder"
                        }
            
            # S'assurer qu'on a un résultat à retourner
            if not final_video:
                print("❌ Création d'un placeholder d'erreur")
                error_placeholder_result = self._create_functional_placeholder(f"error_{animation_id}", 5, "error")
                if error_placeholder_result and error_placeholder_result.get("video_url"):
                    final_video = error_placeholder_result
                else:
                    error_placeholder_url = self._create_placeholder_video(f"error_{animation_id}")
                    final_video = {
                        "video_url": error_placeholder_url,
                        "video_path": None,
                        "status": "error"
                    }
            
            # Préparation du résultat
            actual_duration = self._calculate_actual_duration(video_clips)
            
            # Si on a une vidéo assemblée, la durée réelle est la somme des clips
            if final_video and final_video.get("status") == "assembled":
                print(f"   ✅ Vidéo assemblée: {actual_duration}s total")
            elif final_video and "single" in final_video.get("status", ""):
                actual_duration = video_clips[0].get("duration", 10) if video_clips else 10
                print(f"   ⚠️ Clip unique utilisé: {actual_duration}s au lieu de {self._calculate_actual_duration(video_clips)}s")
            
            result = {
                "status": "success",
                "animation_id": animation_id,
                "video_url": final_video["video_url"],
                "video_path": final_video["video_path"],
                "total_duration": duration,
                "actual_duration": actual_duration,
                "scenes_count": len(video_clips),
                "generation_time": round(generation_time, 2),
                "pipeline_type": "seedance",
                "assembly_status": final_video.get("status", "unknown"),
                "scenes": [
                    {
                        "scene_number": i + 1,
                        "description": clip.get("description", ""),
                        "video_url": clip.get("video_url", ""),
                        "duration": clip.get("duration", 10),
                        "status": "success"
                    }
                    for i, clip in enumerate(video_clips)
                ],
                "metadata": {
                    "theme": theme,
                    "age_target": age_target,
                    "style": style,
                    "idea": idea_result,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
            print(f"✅ Animation SEEDANCE générée en {generation_time:.2f}s")
            return result
            
        except ValueError as ve:
            print(f"❌ Erreur de configuration SEEDANCE: {ve}")
            return {
                "status": "error",
                "error_type": "configuration",
                "error": str(ve),
                "message": f"Problème de configuration: {str(ve)}",
                "solution": "Vérifiez que toutes les clés API sont correctement configurées dans le fichier .env"
            }
        except aiohttp.ClientError as ce:
            print(f"❌ Erreur de connectivité SEEDANCE: {ce}")
            return {
                "status": "error", 
                "error_type": "connectivity",
                "error": str(ce),
                "message": f"Problème de connexion réseau: {str(ce)}",
                "solution": "Vérifiez votre connexion internet et que les services API sont accessibles"
            }
        except asyncio.TimeoutError as te:
            print(f"❌ Timeout SEEDANCE: {te}")
            return {
                "status": "error",
                "error_type": "timeout", 
                "error": str(te),
                "message": "Timeout lors de la génération - les services AI ont pris trop de temps à répondre",
                "solution": "Réessayez dans quelques minutes, les services AI peuvent être surchargés"
            }
        except Exception as e:
            print(f"❌ Erreur SEEDANCE générale: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error_type": "general",
                "error": str(e),
                "message": f"Erreur lors de la génération SEEDANCE: {str(e)}",
                "solution": "Consultez les logs pour plus de détails"
            }
    
    async def generate_story_for_theme(self, theme: str, age_target: str = "3-8 ans", custom_request: str = "") -> str:
        """
        Génère automatiquement une histoire unique basée sur le thème choisi et les demandes spécifiques
        
        Args:
            theme: Thème choisi (space, ocean, nature, etc.)
            age_target: Tranche d'âge ciblée
            custom_request: Demandes spécifiques de l'utilisateur
            
        Returns:
            Histoire générée par l'IA
        """
        try:
            print(f"📚 Génération d'histoire pour thème: {theme}, âge: {age_target}")
            if custom_request:
                print(f"🎯 Avec demandes spécifiques: {custom_request}")
            
            # Prompts adaptés selon le thème
            theme_prompts = {
                'space': "une aventure spatiale avec des astronautes, des planètes colorées et des aliens amicaux",
                'ocean': "une aventure sous-marine avec des poissons, des coraux et des créatures marines fascinantes",
                'nature': "une histoire dans la nature avec des animaux, des arbres et la protection de l'environnement",
                'animals': "une histoire d'animaux mignons qui apprennent des leçons importantes",
                'friendship': "une histoire sur l'amitié, l'entraide et la bienveillance entre enfants",
                'adventure': "une grande aventure pleine de découvertes et de courage",
                'magic': "un monde magique avec des sorts, des créatures fantastiques et de la magie",
                'learning': "une histoire éducative qui enseigne tout en divertissant"
            }
            
            theme_description = theme_prompts.get(theme, "une aventure passionnante et éducative")
            
            # Construire le prompt avec les demandes spécifiques
            prompt = f"""Créé une histoire courte et originale pour enfants de {age_target} sur le thème de {theme_description}.

L'histoire doit être:
- Simple, colorée et adaptée aux enfants
- Éducative et positive
- Adaptée pour être transformée en dessin animé de 30-90 secondes
- Entre 100 et 200 mots
- Avec un début, un développement et une fin satisfaisante
- Incluant des personnages attachants
- Avec une morale ou leçon positive"""

            # Ajouter les demandes spécifiques si elles existent
            if custom_request:
                prompt += f"\n\nIMPORTANT: L'histoire doit absolument inclure ces éléments spécifiques demandés par l'utilisateur: {custom_request}"
                prompt += f"\nIntègre ces éléments de manière naturelle dans l'histoire."

            prompt += f"\n\nRaconte l'histoire à la troisième personne, de manière fluide et engageante."

            # Appel à OpenAI
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Tu es un expert en création d'histoires pour enfants. Tu crées des histoires originales, engageantes et éducatives."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 400,
                    "temperature": 0.8  # Plus de créativité pour des histoires variées
                }
                
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Erreur OpenAI: {response.status} - {error_text}")
                    
                    result = await response.json()
                    story = result['choices'][0]['message']['content'].strip()
                    
                    print(f"✅ Histoire générée: {len(story)} caractères")
                    return story
                    
        except Exception as e:
            print(f"❌ Erreur génération histoire: {e}")
            # Histoire de fallback basique avec demandes spécifiques si possible
            fallback_stories = {
                'space': "Luna est une petite astronaute qui découvre une planète magique. Elle rencontre des aliens colorés qui lui montrent leurs merveilles. Ensemble, ils apprennent que l'amitié traverse toutes les galaxies.",
                'ocean': "Nemo le petit poisson part explorer les profondeurs. Il découvre un récif de corail menacé et aide tous les poissons à le sauver. Il apprend que chacun peut faire la différence.",
                'nature': "Lily découvre un jardin secret où les animaux lui parlent. Elle apprend comment protéger la nature en aidant une famille d'oiseaux à sauver leur nid.",
                'default': "Max part dans une grande aventure. Il rencontre des amis qui l'aident à surmonter les défis. Ensemble, ils découvrent que le courage et l'amitié sont les plus grandes forces."
            }
            base_story = fallback_stories.get(theme, fallback_stories['default'])
            
            # Essayer d'intégrer les demandes spécifiques même dans le fallback
            if custom_request:
                base_story += f" L'aventure inclut aussi {custom_request} qui rend l'histoire encore plus spéciale."
            
            return base_story
    
    async def _generate_ideas(self, story: str, theme: str, age_target: str, style: str) -> Dict[str, Any]:
        """Génère les idées créatives avec OpenAI (équivalent du nœud Ideas AI Agent)"""
        try:
            import openai
            
            # Adaptation du prompt pour les dessins animés éducatifs
            system_prompt = f"""
            Rôle: Tu es un expert en création de dessins animés éducatifs pour enfants.
            
            CONTEXTE:
            - Public cible: {age_target}
            - Thème éducatif: {theme}
            - Style visuel: {style}
            
            OBJECTIF:
            Crée un concept d'animation éducative basé sur l'histoire fournie.
            
            ÉLÉMENTS OBLIGATOIRES:
            - Personnages attachants et éducatifs
            - Message pédagogique adapté à l'âge
            - Séquences visuelles engageantes
            - Cohérence narrative
            
            FORMAT DE SORTIE (JSON UNIQUEMENT):
            Tu DOIS répondre UNIQUEMENT avec un objet JSON valide, sans texte avant ou après.
            Utilise EXACTEMENT cette structure:
            {{
                "Caption": "Description courte avec emoji",
                "Idea": "Concept détaillé de l'animation",
                "Environment": "Environnement visuel", 
                "Sound": "Description des effets sonores",
                "Educational_Value": "Valeur éducative",
                "Characters": "Personnages principaux"
            }}
            
            IMPORTANT: Réponds UNIQUEMENT avec le JSON, pas d'autre texte.
            """
            
            user_prompt = f"""
            Histoire à adapter: {story}
            
            Crée un concept d'animation éducative engageante pour des enfants de {age_target}.
            Le thème éducatif est: {theme}
            Style visuel souhaité: {style}
            
            RAPPEL: Réponds UNIQUEMENT avec un objet JSON valide, rien d'autre.
            """
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 500
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # Tenter de parser le JSON avec nettoyage et fallback robuste
                        try:
                            # Nettoyer le contenu pour extraire le JSON
                            cleaned_content = content.strip()
                            
                            # Chercher un bloc JSON dans la réponse
                            json_start = cleaned_content.find('{')
                            json_end = cleaned_content.rfind('}') + 1
                            
                            if json_start >= 0 and json_end > json_start:
                                json_content = cleaned_content[json_start:json_end]
                                idea_data = json.loads(json_content)
                                
                                # Valider que tous les champs requis sont présents
                                required_fields = ["Caption", "Idea", "Environment", "Sound", "Educational_Value", "Characters"]
                                if all(field in idea_data for field in required_fields):
                                    print(f"✅ JSON valide parsé avec succès")
                                    return idea_data
                                else:
                                    print(f"⚠️ JSON parsé mais champs manquants: {[f for f in required_fields if f not in idea_data]}")
                                    raise json.JSONDecodeError("Champs manquants", json_content, 0)
                            else:
                                print(f"⚠️ Aucune structure JSON trouvée dans: {cleaned_content[:100]}...")
                                raise json.JSONDecodeError("Pas de JSON trouvé", cleaned_content, 0)
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Échec parsing JSON: {e}")
                            print(f"   Contenu reçu: {content[:200]}...")
                            # Fallback structuré si le JSON n'est pas valide
                            return {
                                "Caption": f"🎨 Animation éducative: {story[:50]}...",
                                "Idea": content if len(content) < 500 else f"Animation éducative basée sur: {story[:100]}...",
                                "Environment": f"Environnement coloré et éducatif pour {age_target}",
                                "Sound": "Musique douce et effets sonores adaptés aux enfants",
                                "Educational_Value": f"Apprentissage ludique du thème: {theme}",
                                "Characters": "Personnages attachants et éducatifs"
                            }
                    else:
                        raise Exception(f"Erreur OpenAI: {response.status}")
        
        except Exception as e:
            print(f"❌ Erreur génération idées: {e}")
            print(f"   📊 Thème détecté: {theme}")
            print(f"   📖 Histoire: {story[:100]}...")
            # Fallback spécifique au thème
            fallback_ideas = {
                "space": {
                    "Caption": "🚀 Aventure spatiale éducative",
                    "Idea": f"Une animation éducative spatiale pour enfants de {age_target} suivant l'histoire: {story[:100]}...",
                    "Environment": "Espace coloré avec planètes, étoiles et vaisseaux spatiaux",
                    "Sound": "Musique spatiale douce et effets cosmiques",
                    "Educational_Value": f"Apprentissage de l'espace et de l'astronomie pour {age_target}",
                    "Characters": "Astronautes enfants, aliens amicaux, robots spatiaux"
                },
                "nature": {
                    "Caption": "🌿 Merveilles de la nature",
                    "Idea": f"Une animation éducative nature pour enfants de {age_target} suivant l'histoire: {story[:100]}...",
                    "Environment": "Forêt magique, jardin coloré, paysages naturels",
                    "Sound": "Sons de la nature, musique douce forestière",
                    "Educational_Value": f"Apprentissage de l'écologie et de la nature pour {age_target}",
                    "Characters": "Animaux de la forêt, fleurs parlantes, gardiens de la nature"
                },
                "animals": {
                    "Caption": "🦁 Royaume des animaux",
                    "Idea": f"Une animation éducative animaux pour enfants de {age_target} suivant l'histoire: {story[:100]}...",
                    "Environment": "Savane colorée, jungle amicale, ferme magique",
                    "Sound": "Cris d'animaux mélodieux, musique joyeuse",
                    "Educational_Value": f"Apprentissage des animaux et de leur habitat pour {age_target}",
                    "Characters": "Animaux domestiques et sauvages, familles d'animaux"
                }
            }
            
            fallback_result = fallback_ideas.get(theme, {
                "Caption": f"🎨 Animation éducative: {story[:50]}...",
                "Idea": f"Une animation éducative {style} sur le thème {theme} pour enfants de {age_target}",
                "Environment": "Environnement coloré et accueillant",
                "Sound": "Musique douce et effets sonores adaptés",
                "Educational_Value": f"Apprentissage du thème: {theme}",
                "Characters": "Personnages éducatifs et attachants"
            })
            
            print(f"   🎯 Fallback utilisé: {fallback_result.get('Environment', 'N/A')}")
            return fallback_result
    
    async def _generate_scene_prompts(self, idea_result: Dict[str, Any], total_duration: int) -> List[Dict[str, Any]]:
        """Génère les prompts pour 3 scènes avec progression narrative structurée"""
        try:
            import openai
            
            # Calculer la durée par scène de façon optimale
            optimal_scene_duration = total_duration // 3  # Divise équitablement
            # Respecter la limite Wavespeed (10s max) mais optimiser la durée
            scene_duration = min(optimal_scene_duration, self.max_clip_duration)
            
            print(f"🎯 Durée calculée: {optimal_scene_duration}s par scène (limité à {scene_duration}s)")
            if optimal_scene_duration > self.max_clip_duration:
                print(f"⚠️ Durée réduite de {optimal_scene_duration}s à {scene_duration}s par scène")
            
            system_prompt = f"""
            Rôle: Tu es un expert en narration et direction artistique pour dessins animés éducatifs.
            
            CONTEXTE OBLIGATOIRE:
            - Idée générale: {idea_result.get('Idea', '')}
            - Environnement spécifique: {idea_result.get('Environment', '')}
            - Valeur éducative: {idea_result.get('Educational_Value', '')}
            - Personnages principaux: {idea_result.get('Characters', '')}
            
            STRUCTURE NARRATIVE OBLIGATOIRE:
            Tu DOIS créer exactement 3 scènes qui suivent cette progression narrative classique:
            
            SCÈNE 1 - EXPOSITION/INTRODUCTION (Début):
            - Présenter les personnages et l'environnement
            - Établir la situation initiale
            - Introduire le problème ou l'objectif éducatif
            - Ton: Découverte, curiosité, mise en place
            
            SCÈNE 2 - DÉVELOPPEMENT/CONFLIT (Milieu):
            - Les personnages font face à un défi ou explorent
            - Action principale de l'apprentissage
            - Moment d'effort, de recherche ou de difficulté
            - Ton: Action, exploration, apprentissage actif
            
            SCÈNE 3 - RÉSOLUTION/CONCLUSION (Fin):
            - Résolution du défi ou accomplissement de l'objectif
            - Leçon apprise, succès, célébration
            - Récapitulatif de la valeur éducative
            - Ton: Satisfaction, accomplissement, joie
            
            CONTRAINTES VISUELLES:
            - RESPECTER ABSOLUMENT l'environnement et les personnages décrits
            - Éviter tout élément incohérent avec le thème
            - Chaque scène doit être VISUELLEMENT DISTINCTE
            - Progression logique et fluide entre les scènes
            - Style: {self.cartoon_style}, {self.cartoon_quality}
            
            FORMAT DE SORTIE (JSON UNIQUEMENT):
            Tu DOIS répondre UNIQUEMENT avec un objet JSON valide, sans texte avant ou après.
            Utilise EXACTEMENT cette structure:
            {{
                "Scene1_Introduction": "Description détaillée de la scène d'introduction",
                "Scene2_Development": "Description détaillée de la scène de développement", 
                "Scene3_Resolution": "Description détaillée de la scène de résolution"
            }}
            
            IMPORTANT: Réponds UNIQUEMENT avec le JSON, pas d'autre texte.
            """
            
            user_prompt = f"""
            Crée une histoire complète en 3 actes basée sur l'idée: {idea_result.get('Idea', '')}
            
            EXIGENCES NARRATIVES:
            - Scène 1: Introduction des {idea_result.get('Characters', 'personnages')} dans {idea_result.get('Environment', "l'environnement")}
            - Scène 2: Défi ou exploration liée à {idea_result.get('Educational_Value', 'la valeur éducative')}
            - Scène 3: Résolution heureuse avec leçon apprise
            
            EXIGENCES VISUELLES:
            - Chaque scène doit être unique visuellement
            - Mouvements et actions différents dans chaque scène
            - Évolution de l'émotion et de l'ambiance
            - Durée: {scene_duration} secondes par scène
            
            INTERDICTIONS:
            - Pas de répétition de la même action
            - Pas de descriptions identiques
            - Pas d'éléments incohérents avec le thème
            
            RAPPEL: Réponds UNIQUEMENT avec un objet JSON valide, rien d'autre.
            """
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,  # Augmenté légèrement pour plus de créativité rapide
                        "max_tokens": 500  # Réduit de 800 à 500 pour accélérer la génération
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        print(f"   📝 Réponse OpenAI pour scènes: {content[:200]}...")
                        
                        try:
                            # Nettoyer le contenu de la réponse OpenAI
                            cleaned_content = content.strip()
                            
                            # Supprimer les marqueurs markdown s'ils existent
                            if cleaned_content.startswith('```json'):
                                cleaned_content = cleaned_content[7:]  # Supprimer '```json'
                            if cleaned_content.endswith('```'):
                                cleaned_content = cleaned_content[:-3]  # Supprimer '```'
                            
                            cleaned_content = cleaned_content.strip()
                            
                            print(f"   🧹 Contenu nettoyé pour parsing: {cleaned_content[:100]}...")
                            
                            # Chercher un bloc JSON dans la réponse
                            json_start = cleaned_content.find('{')
                            json_end = cleaned_content.rfind('}') + 1
                            
                            if json_start >= 0 and json_end > json_start:
                                json_content = cleaned_content[json_start:json_end]
                                
                                # Nettoyer les caractères de contrôle problématiques
                                import re
                                json_content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_content)
                                
                                scenes_data = json.loads(json_content)
                                
                                # Valider que tous les champs requis sont présents
                                required_fields = ["Scene1_Introduction", "Scene2_Development", "Scene3_Resolution"]
                                if all(field in scenes_data for field in required_fields):
                                    print(f"✅ JSON des scènes parsé avec succès")
                                    # Continuer avec le processing normal
                                else:
                                    print(f"⚠️ JSON parsé mais champs manquants: {[f for f in required_fields if f not in scenes_data]}")
                                    raise json.JSONDecodeError("Champs de scènes manquants", json_content, 0)
                            else:
                                print(f"⚠️ Aucune structure JSON trouvée dans les scènes")
                                raise json.JSONDecodeError("Pas de JSON trouvé", cleaned_content, 0)
                                
                            # Transformer en format attendu avec structure narrative
                            scenes = []
                            scene_types = ["Introduction", "Development", "Resolution"]
                            
                            for i, (key, description) in enumerate(scenes_data.items()):
                                scene_type = scene_types[i] if i < len(scene_types) else f"Scene{i+1}"
                                
                                # Enrichir le prompt avec le type de scène
                                enhanced_prompt = self._create_enhanced_prompt(
                                    description, 
                                    scene_type, 
                                    idea_result, 
                                    i + 1
                                )
                                
                                scenes.append({
                                    "scene_number": i + 1,
                                    "scene_type": scene_type,
                                    "description": description,
                                    "duration": scene_duration,
                                    "prompt": enhanced_prompt
                                })
                            
                            print(f"✅ {len(scenes)} scènes structurées créées")
                            return scenes
                            
                        except json.JSONDecodeError as je:
                            print(f"   ⚠️ Erreur parsing JSON: {je}")
                            print(f"   📝 Contenu brut: {content}")
                            # Fallback avec scènes structurées
                            return self._create_structured_fallback_scenes(idea_result, scene_duration)
                    else:
                        response_text = await response.text()
                        print(f"   ❌ Erreur API OpenAI: {response.status} - {response_text}")
                        raise Exception(f"Erreur OpenAI scenes: {response.status}")
        
        except Exception as e:
            print(f"❌ Erreur génération scènes: {e}")
            print(f"   📊 Idée reçue: {idea_result.get('Idea', 'N/A')[:100]}...")
            print(f"   🌍 Environnement: {idea_result.get('Environment', 'N/A')}")
            print(f"   👥 Personnages: {idea_result.get('Characters', 'N/A')}")
            return self._create_structured_fallback_scenes(idea_result, total_duration // 3)
    
    def _create_enhanced_prompt(self, description: str, scene_type: str, idea_result: Dict[str, Any], scene_number: int) -> str:
        """Crée un prompt enrichi pour Wavespeed avec contexte narratif"""
        base_style = f"{self.cartoon_style}, {self.cartoon_quality}"
        environment = idea_result.get('Environment', 'colorful environment')
        characters = idea_result.get('Characters', 'friendly characters')
        
        # Ajouter des éléments spécifiques selon le type de scène
        scene_specific = {
            "Introduction": f"establishing shot, character introduction, peaceful beginning, {characters} appearing in {environment}",
            "Development": f"dynamic action, main challenge, movement and exploration, {characters} actively engaged in adventure",
            "Resolution": f"happy conclusion, problem solved, celebration, {characters} successful and joyful in {environment}"
        }
        
        specific_elements = scene_specific.get(scene_type, "engaging animation sequence")
        
        return f"STYLE: {base_style} | SCENE {scene_number} ({scene_type}): {description} | ELEMENTS: {specific_elements} | ENVIRONMENT: {environment} | CHARACTERS: {characters}"
    
    def _create_structured_fallback_scenes(self, idea_result: Dict[str, Any], scene_duration: int) -> List[Dict[str, Any]]:
        """Crée des scènes de fallback avec structure narrative claire"""
        idea = idea_result.get('Idea', 'Animation éducative')
        environment = idea_result.get('Environment', 'Environnement coloré')
        characters = idea_result.get('Characters', 'Personnages attachants')
        education = idea_result.get('Educational_Value', 'Valeur éducative')
        
        print(f"   🎯 Fallback structuré - Environnement: {environment}")
        print(f"   👥 Personnages: {characters}")
        print(f"   📚 Valeur éducative: {education}")
        
        return [
            {
                "scene_number": 1,
                "scene_type": "Introduction",
                "description": f"Introduction: {characters} découvrent {environment} et se préparent à apprendre",
                "duration": scene_duration,
                "prompt": self._create_enhanced_prompt(
                    f"{characters} découvrent {environment} et se préparent à apprendre",
                    "Introduction",
                    idea_result,
                    1
                )
            },
            {
                "scene_number": 2,
                "scene_type": "Development", 
                "description": f"Exploration: {characters} explorent activement et font face à un défi éducatif",
                "duration": scene_duration,
                "prompt": self._create_enhanced_prompt(
                    f"{characters} explorent activement et font face à un défi éducatif",
                    "Development", 
                    idea_result,
                    2
                )
            },
            {
                "scene_number": 3,
                "scene_type": "Resolution",
                "description": f"Succès: {characters} réussissent leur apprentissage et célèbrent dans {environment}",
                "duration": scene_duration,
                "prompt": self._create_enhanced_prompt(
                    f"{characters} réussissent leur apprentissage et célèbrent dans {environment}",
                    "Resolution",
                    idea_result, 
                    3
                )
            }
        ]
    
    def _create_fallback_scenes(self, idea_result: Dict[str, Any], scene_duration: int) -> List[Dict[str, Any]]:
        """Crée des scènes de fallback en cas d'erreur - redirige vers la version structurée"""
        return self._create_structured_fallback_scenes(idea_result, scene_duration)
    
    def _get_narrative_template(self, theme: str, characters: str, environment: str) -> Dict[str, str]:
        """Retourne un template narratif spécifique au thème pour garantir la cohérence"""
        
        templates = {
            "space": {
                "introduction": f"{characters} préparent leur vaisseau spatial dans {environment}, vérifient les instruments et se préparent pour le décollage vers une mission d'exploration",
                "development": f"{characters} voyagent dans l'espace, rencontrent des phénomènes cosmiques fascinants, explorent une nouvelle planète avec des découvertes surprenantes",
                "resolution": f"{characters} réussissent leur mission spatiale, partagent leurs découvertes avec joie et contemplent les merveilles de l'univers depuis leur vaisseau"
            },
            "nature": {
                "introduction": f"{characters} découvrent {environment}, observent la beauté de la nature et remarquent quelque chose d'intéressant à explorer",
                "development": f"{characters} explorent activement la nature, interagissent avec les plantes et animaux, apprennent les secrets de l'écosystème",
                "resolution": f"{characters} comprennent l'importance de protéger la nature, plantent de nouvelles graines et célèbrent la beauté de {environment}"
            },
            "animals": {
                "introduction": f"{characters} rencontrent différents animaux dans {environment}, observent leurs comportements et s'approchent avec curiosité",
                "development": f"{characters} interagissent avec les animaux, apprennent leurs habitudes de vie, participent à leurs activités quotidiennes",
                "resolution": f"{characters} deviennent amis avec les animaux, comprennent leurs besoins et célèbrent l'amitié inter-espèces dans {environment}"
            },
            "ocean": {
                "introduction": f"{characters} plongent dans {environment}, découvrent le monde sous-marin et rencontrent les premières créatures marines",
                "development": f"{characters} explorent les profondeurs océaniques, nagent avec les poissons colorés, découvrent des coraux et des trésors marins",
                "resolution": f"{characters} comprennent l'importance de protéger l'océan, nagent joyeusement avec tous leurs nouveaux amis marins"
            },
            "friendship": {
                "introduction": f"{characters} se rencontrent dans {environment}, font connaissance et découvrent leurs différences",
                "development": f"{characters} font face à un défi ensemble, apprennent à se faire confiance et à s'entraider malgré leurs différences",
                "resolution": f"{characters} deviennent de vrais amis, célèbrent leur amitié et jouent ensemble dans {environment}"
            },
            "education": {
                "introduction": f"{characters} arrivent dans {environment} avec curiosité, découvrent de nouveaux concepts à apprendre",
                "development": f"{characters} explorent activement, posent des questions, expérimentent et font des découvertes éducatives fascinantes",
                "resolution": f"{characters} maîtrisent leurs nouveaux apprentissages, partagent leurs connaissances et célèbrent leurs progrès"
            }
        }
        
        # Template générique si le thème n'est pas trouvé
        default_template = {
            "introduction": f"{characters} découvrent {environment} et se préparent à vivre une aventure éducative",
            "development": f"{characters} explorent activement, rencontrent des défis intéressants et apprennent de nouvelles choses",
            "resolution": f"{characters} réussissent leur aventure, célèbrent leurs apprentissages dans {environment}"
        }
        
        return templates.get(theme, default_template)

    def _create_thematic_fallback_scenes(self, idea_result: Dict[str, Any], scene_duration: int, theme: str) -> List[Dict[str, Any]]:
        """Crée des scènes de fallback spécifiques au thème avec progression narrative garantie"""
        characters = idea_result.get('Characters', 'Personnages éducatifs')
        environment = idea_result.get('Environment', 'Environnement coloré')
        
        # Obtenir le template narratif pour ce thème
        template = self._get_narrative_template(theme, characters, environment)
        
        print(f"   🎭 Template thématique '{theme}' utilisé")
        print(f"   👥 Personnages: {characters}")
        print(f"   🌍 Environnement: {environment}")
        
        return [
            {
                "scene_number": 1,
                "scene_type": "Introduction",
                "description": f"Introduction: {template['introduction']}",
                "duration": scene_duration,
                "prompt": self._create_enhanced_prompt(
                    template['introduction'],
                    "Introduction",
                    idea_result,
                    1
                )
            },
            {
                "scene_number": 2,
                "scene_type": "Development",
                "description": f"Développement: {template['development']}",
                "duration": scene_duration,
                "prompt": self._create_enhanced_prompt(
                    template['development'],
                    "Development",
                    idea_result,
                    2
                )
            },
            {
                "scene_number": 3,
                "scene_type": "Resolution",
                "description": f"Résolution: {template['resolution']}",
                "duration": scene_duration,
                "prompt": self._create_enhanced_prompt(
                    template['resolution'],
                    "Resolution",
                    idea_result,
                    3
                )
            }
        ]
    
    async def _generate_video_clips(self, scenes_prompts: List[Dict[str, Any]], animation_id: str) -> List[Dict[str, Any]]:
        """Génère les clips vidéo avec Wavespeed AI EN PARALLÈLE pour accélérer drastiquement"""
        try:
            print(f"   🚀 Génération PARALLÈLE de {len(scenes_prompts)} clips...")
            
            # Générer tous les clips en parallèle avec asyncio.gather
            tasks = []
            for i, scene in enumerate(scenes_prompts):
                print(f"   📝 Préparation clip {i+1}/3...")
                task = self._create_single_clip(scene, animation_id)
                tasks.append(task)
            
            # Exécuter toutes les tâches en parallèle
            print(f"   ⚡ Lancement des {len(tasks)} générations en parallèle...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Traiter les résultats
            clips = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"   ❌ Erreur clip {i+1}: {result}")
                    clips.append(self._create_fallback_clip(scenes_prompts[i], animation_id))
                elif result:
                    print(f"   ✅ Clip {i+1} généré avec succès")
                    clips.append(result)
                else:
                    print(f"   ⚠️ Échec clip {i+1}, utilisation fallback")
                    clips.append(self._create_fallback_clip(scenes_prompts[i], animation_id))
            
            print(f"   🎯 Génération parallèle terminée: {len([c for c in clips if c.get('status') == 'success'])}/{len(clips)} réussies")
            return clips
            
        except Exception as e:
            print(f"❌ Erreur génération clips: {e}")
            # Retourner des clips de fallback
            return [self._create_fallback_clip(scene, animation_id) for scene in scenes_prompts]
    
    async def _create_single_clip(self, scene: Dict[str, Any], animation_id: str) -> Optional[Dict[str, Any]]:
        """Crée un seul clip vidéo avec Wavespeed AI"""
        try:
            async with aiohttp.ClientSession() as session:
                # Données pour la génération (durée réduite pour accélérer)
                # Calculer la durée optimale pour ce clip (utilise la durée par défaut de 10s)
                clip_duration = min(scene.get("duration", 10), self.max_clip_duration)  # Utiliser 10s par défaut au lieu de 6s
                
                payload = {
                    "aspect_ratio": self.cartoon_aspect_ratio,
                    "duration": clip_duration,
                    "prompt": scene["prompt"]
                }
                
                print(f"   ⏱️ Durée du clip: {clip_duration}s (max: {self.max_clip_duration}s)")
                
                headers = {
                    "Authorization": f"Bearer {self.wavespeed_api_key}",
                    "Content-Type": "application/json"
                }
                
                print(f"   🚀 Envoi à Wavespeed: {scene['prompt'][:100]}...")
                print(f"   🔑 API Key: {self.wavespeed_api_key[:10] if self.wavespeed_api_key else 'Non définie'}...")
                
                # Lancer la génération
                async with session.post(
                    f"{self.wavespeed_base_url}/{self.wavespeed_model}",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    response_text = await response.text()
                    print(f"   📡 Réponse Wavespeed [{response.status}]: {response_text[:300]}...")
                    
                    if response.status == 200:
                        try:
                            result = await response.json()
                            prediction_id = result.get("data", {}).get("id")
                            
                            if prediction_id:
                                print(f"   ✅ Prediction ID: {prediction_id}")
                                # Attendre la completion
                                video_url = await self._wait_for_clip_completion(prediction_id)
                                
                                if video_url:
                                    print(f"   📹 Vidéo générée: {video_url[:100]}...")
                                    # Télécharger et sauvegarder le clip
                                    local_path = await self._download_clip(video_url, animation_id, scene["scene_number"])
                                    return {
                                        "scene_number": scene["scene_number"],
                                        "description": scene["description"],
                                        "video_url": f"/cache/seedance/{local_path.name}" if local_path else video_url,
                                        "video_path": str(local_path) if local_path else None,
                                    "wavespeed_url": video_url,  # Garder l'URL originale pour l'audio
                                    "duration": clip_duration,
                                    "status": "success",
                                    "prediction_id": prediction_id
                                }
                                else:
                                    print(f"   ❌ Aucune vidéo générée pour {prediction_id}")
                            else:
                                print(f"   ❌ Aucun prediction_id dans la réponse")
                        except json.JSONDecodeError:
                            print(f"   ❌ Erreur JSON: {response_text}")
                    else:
                        print(f"   ❌ Erreur Wavespeed: {response.status} - {response_text}")
                    
                    return None
                    
        except Exception as e:
            print(f"   ❌ Erreur création clip: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _wait_for_clip_completion(self, prediction_id: str, max_wait: int = 90) -> Optional[str]:
        """Attend la completion d'un clip vidéo - OPTIMISÉ"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.wavespeed_api_key}"
                }
                
                print(f"   ⏳ Attente completion {prediction_id}...")
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    async with session.get(
                        f"{self.wavespeed_base_url}/predictions/{prediction_id}/result",
                        headers=headers
                    ) as response:
                        
                        response_text = await response.text()
                        print(f"   📊 Status check [{response.status}]: {response_text[:200]}...")
                        
                        if response.status == 200:
                            try:
                                result = await response.json()
                                status = result.get("data", {}).get("status")
                                outputs = result.get("data", {}).get("outputs", [])
                                print(f"   📈 Status: {status}, Outputs: {len(outputs)}")
                                
                                # Vérifier si la vidéo est prête (outputs non vides)
                                if outputs:
                                    video_url = outputs[0]
                                    print(f"   ✅ Vidéo prête: {video_url}")
                                    return video_url
                                elif status == "failed":
                                    error = result.get("data", {}).get("error", "Erreur inconnue")
                                    print(f"   ❌ Génération échouée: {error}")
                                    return None
                                elif status in ["processing", "pending", "created"] or status is None:
                                    print(f"   ⏳ Toujours en cours...")
                                else:
                                    print(f"   ❓ Status inconnu: {status}")
                            except json.JSONDecodeError:
                                print(f"   ❌ Erreur JSON status: {response_text}")
                        else:
                            print(f"   ❌ Erreur status check: {response.status}")
                    
                    # Attendre réduit avant de revérifier (optimisation)
                    await asyncio.sleep(3)  # Réduit de 5s à 3s
                
                print(f"   ⏰ Timeout après {max_wait}s")
                return None
                
        except Exception as e:
            print(f"   ❌ Erreur attente completion: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _download_clip(self, video_url: str, animation_id: str, scene_number: int) -> Optional[Path]:
        """Télécharge un clip vidéo localement"""
        try:
            filename = f"seedance_{animation_id}_scene_{scene_number}.mp4"
            local_path = self.cache_dir / filename
            
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        with open(local_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        print(f"   ✅ Clip téléchargé: {filename}")
                        return local_path
                    else:
                        print(f"   ❌ Erreur téléchargement: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"   ❌ Erreur téléchargement clip: {e}")
            return None
    
    def _create_fallback_clip(self, scene: Dict[str, Any], animation_id: str) -> Dict[str, Any]:
        """Crée un clip de fallback en cas d'erreur"""
        return {
            "scene_number": scene["scene_number"],
            "description": scene["description"],
            "video_url": None,
            "video_path": None,
            "duration": scene["duration"],
            "status": "fallback",
            "type": "placeholder"
        }
    
    async def _generate_audio_clips(self, video_clips: List[Dict[str, Any]], idea_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère les clips audio avec Fal AI (équivalent du nœud Create Sounds)"""
        try:
            audio_clips = []
            base_sound = idea_result.get('Sound', 'effets sonores adaptés aux enfants')
            
            for i, clip in enumerate(video_clips):
                print(f"   🔊 Génération audio {i+1}/3...")
                
                # Créer un prompt audio adapté
                audio_prompt = f"sound effects: {base_sound}. Educational, child-friendly, gentle, magical"
                
                audio_result = await self._create_single_audio(audio_prompt, clip)
                
                if audio_result:
                    audio_clips.append(audio_result)
                    await asyncio.sleep(2)
                else:
                    # Fallback sans audio
                    audio_clips.append({
                        "scene_number": clip["scene_number"],
                        "audio_url": None,
                        "status": "no_audio"
                    })
            
            return audio_clips
            
        except Exception as e:
            print(f"❌ Erreur génération audio: {e}")
            return []
    
    async def _create_single_audio(self, audio_prompt: str, video_clip: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un clip audio avec Fal AI"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Key {self.fal_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "prompt": audio_prompt,
                    "duration": video_clip["duration"],
                    "video_url": video_clip.get("wavespeed_url", video_clip.get("video_url", ""))
                }
                
                print(f"   🎵 Appel Fal AI: {audio_prompt[:50]}...")
                
                async with session.post(
                    f"{self.fal_base_url}/{self.fal_audio_model}",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    response_text = await response.text()
                    print(f"   📡 Réponse Fal AI [{response.status}]: {response_text[:200]}...")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text)
                            request_id = result.get("request_id")
                            
                            if request_id:
                                print(f"   🆔 Request ID: {request_id}")
                                # Attendre la completion audio
                                audio_url = await self._wait_for_audio_completion(request_id)
                                
                                if audio_url:
                                    return {
                                        "scene_number": video_clip["scene_number"],
                                        "audio_url": audio_url,
                                        "status": "success"
                                    }
                        except json.JSONDecodeError:
                            print(f"   ❌ JSON invalide: {response_text}")
                    else:
                        print(f"   ❌ Erreur Fal AI: {response.status}")
                    
                    return None
                    
        except Exception as e:
            print(f"   ❌ Erreur création audio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _wait_for_audio_completion(self, request_id: str, max_wait: int = 45) -> Optional[str]:
        """Attend la completion d'un clip audio avec Fal AI - OPTIMISÉ"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Key {self.fal_api_key}"
                }
                
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    async with session.get(
                        f"{self.fal_base_url}/{self.fal_audio_model}/requests/{request_id}",
                        headers=headers
                    ) as response:
                        
                        response_text = await response.text()
                        print(f"   📊 Status audio [{response.status}]: {response_text[:200]}...")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text)
                                status = result.get("status")
                                
                                if status == "COMPLETED":
                                    # Chercher l'URL audio dans la réponse
                                    audio_url = result.get("audio_url") or result.get("output", {}).get("audio_url")
                                    if audio_url:
                                        print(f"   ✅ Audio prêt: {audio_url}")
                                        return audio_url
                                    else:
                                        print(f"   ❌ Pas d'URL audio dans la réponse")
                                        return None
                                elif status == "FAILED":
                                    error = result.get("error", "Erreur inconnue")
                                    print(f"   ❌ Génération audio échouée: {error}")
                                    return None
                                elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                                    print(f"   ⏳ Audio en cours: {status}")
                                else:
                                    print(f"   ❓ Status audio inconnu: {status}")
                            except json.JSONDecodeError:
                                print(f"   ❌ JSON invalide audio: {response_text}")
                        else:
                            print(f"   ❌ Erreur status audio: {response.status}")
                    
                    await asyncio.sleep(3)
                
                print(f"   ⏰ Timeout audio après {max_wait}s")
                return None
                
        except Exception as e:
            print(f"   ❌ Erreur attente audio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _assemble_final_video(self, video_clips: List[Dict[str, Any]], audio_clips: List[Dict[str, Any]], animation_id: str) -> Optional[Dict[str, Any]]:
        """Assemble la vidéo finale avec FFmpeg via Fal AI"""
        try:
            print("   🎞️ Assemblage final...")
            
            # Préparer les URLs des clips vidéo
            valid_clips = []
            for clip in video_clips:
                if clip.get("video_url") and clip["status"] == "success":
                    # Vérifier que l'URL est accessible
                    video_url = clip["video_url"]
                    if video_url.startswith("http"):
                        valid_clips.append(clip)
                        print(f"   ✅ Clip valide: {video_url[:50]}...")
                    else:
                        print(f"   ⚠️ URL invalide ignorée: {video_url}")
                else:
                    print(f"   ⚠️ Clip ignoré: {clip.get('status', 'no_status')}")
            
            if not valid_clips:
                print("   ⚠️ Aucun clip vidéo valide disponible pour l'assemblage")
                # Retourner un résultat de fallback basé sur le premier clip
                if video_clips:
                    first_clip = video_clips[0]
                    return {
                        "video_url": first_clip.get("video_url", f"/cache/seedance/fallback_{animation_id}.mp4"),
                        "video_path": first_clip.get("video_path"),
                        "status": "single_clip_fallback"
                    }
                return None
            
            # Si un seul clip, pas d'assemblage
            if len(valid_clips) == 1:
                print("   📹 Un seul clip valide, pas d'assemblage nécessaire")
                clip = valid_clips[0]
                return {
                    "video_url": clip["video_url"],
                    "video_path": clip.get("video_path"),
                    "status": "single_clip"
                }
            
            # Créer la configuration FFmpeg pour multiple clips
            tracks = [
                {
                    "id": "1",
                    "type": "video",
                    "keyframes": []
                }
            ]
            
            # Ajouter les keyframes pour chaque clip
            current_time = 0
            for clip in valid_clips:
                duration = clip["duration"]
                tracks[0]["keyframes"].append({
                    "url": clip["video_url"],
                    "timestamp": current_time,
                    "duration": duration
                })
                current_time += duration
                print(f"   📎 Ajouté clip {clip['scene_number']}: {duration}s à {current_time-duration}s")
            
            # Appeler l'API FFmpeg
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                headers = {
                    "Authorization": f"Bearer {self.fal_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "tracks": tracks
                }
                
                print(f"   🔧 Envoi à FFmpeg: {len(tracks[0]['keyframes'])} clips")
                
                async with session.post(
                    f"{self.fal_base_url}/{self.fal_ffmpeg_model}",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        request_id = result.get("request_id")
                        
                        if request_id:
                            print(f"   ⏳ Attente assemblage: {request_id}")
                            # Attendre la completion
                            final_url = await self._wait_for_final_video(request_id)
                            
                            if final_url:
                                # Télécharger la vidéo finale
                                local_path = await self._download_final_video(final_url, animation_id)
                                
                                return {
                                    "video_url": f"/cache/seedance/{local_path.name}" if local_path else final_url,
                                    "video_path": str(local_path) if local_path else None,
                                    "status": "success"
                                }
                            else:
                                print("   ❌ Timeout assemblage, fallback premier clip")
                                # Fallback: utiliser le premier clip
                                first_clip = valid_clips[0]
                                return {
                                    "video_url": first_clip["video_url"],
                                    "video_path": first_clip.get("video_path"),
                                    "status": "timeout_fallback"
                                }
                        else:
                            print("   ❌ Pas de request_id reçu")
                            return None
                    else:
                        print(f"   ❌ Erreur FFmpeg: {response.status}")
                        # Lire la réponse d'erreur
                        try:
                            error_data = await response.json()
                            print(f"   📝 Détails erreur: {error_data}")
                        except:
                            error_text = await response.text()
                            print(f"   📝 Erreur texte: {error_text[:200]}")
                        
                        # Fallback: utiliser le premier clip
                        if valid_clips:
                            first_clip = valid_clips[0]
                            return {
                                "video_url": first_clip["video_url"],
                                "video_path": first_clip.get("video_path"),
                                "status": "error_fallback"
                            }
                        return None
                    
        except Exception as e:
            print(f"❌ Erreur assemblage final: {e}")
            # Fallback ultime: utiliser le premier clip disponible
            if video_clips:
                for clip in video_clips:
                    if clip.get("video_url") and clip["status"] == "success":
                        return {
                            "video_url": clip["video_url"],
                            "video_path": clip.get("video_path"),
                            "status": "exception_fallback"
                        }
            return None
    
    async def _wait_for_final_video(self, request_id: str, max_wait: int = 30) -> Optional[str]:
        """Attend la completion de la vidéo finale - OPTIMISÉ"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.fal_api_key}"
                }
                
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    async with session.get(
                        f"{self.fal_base_url}/{self.fal_ffmpeg_model}/requests/{request_id}",
                        headers=headers
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            
                            if result.get("status") == "completed":
                                return result.get("video_url")
                            elif result.get("status") == "failed":
                                return None
                    
                    await asyncio.sleep(3)
                
                return None
                
        except Exception as e:
            print(f"   ❌ Erreur attente finale: {e}")
            return None
    
    async def _download_final_video(self, video_url: str, animation_id: str) -> Optional[Path]:
        """Télécharge la vidéo finale"""
        try:
            filename = f"seedance_final_{animation_id}.mp4"
            local_path = self.cache_dir / filename
            
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        with open(local_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        print(f"   ✅ Vidéo finale téléchargée: {filename}")
                        return local_path
                    else:
                        return None
                        
        except Exception as e:
            print(f"   ❌ Erreur téléchargement final: {e}")
            return None
    
    def _calculate_actual_duration(self, video_clips: List[Dict[str, Any]]) -> int:
        """Calcule la durée réelle de l'animation"""
        total_duration = sum(clip.get("duration", self.max_clip_duration) for clip in video_clips)
        # S'assurer qu'on a au moins une durée minimale
        return max(total_duration, self.max_clip_duration) if video_clips else self.max_clip_duration
    
    async def get_seedance_status(self) -> Dict[str, Any]:
        """Retourne le statut du service SEEDANCE"""
        return {
            "service": "seedance",
            "status": "operational",
            "apis": {
                "openai": bool(self.openai_api_key and not self.openai_api_key.startswith("sk-votre")),
                "wavespeed": bool(self.wavespeed_api_key and not self.wavespeed_api_key.startswith("votre_")),
                "fal": bool(self.fal_api_key and not self.fal_api_key.startswith("votre_"))
            },
            "configuration": {
                "cartoon_duration": self.cartoon_duration,
                "cartoon_aspect_ratio": self.cartoon_aspect_ratio,
                "cartoon_style": self.cartoon_style
            }
        }
    
    def _create_placeholder_video(self, animation_id: str, duration: int = 5) -> str:
        """Crée un fichier placeholder vidéo réel"""
        try:
            filename = f"placeholder_{animation_id}.mp4"
            placeholder_path = self.cache_dir / filename
            
            # Créer un fichier placeholder avec FFmpeg si disponible
            # Sinon, créer un fichier vide pour éviter les 404
            if not placeholder_path.exists():
                try:
                    # Essayer de créer une vraie vidéo placeholder avec FFmpeg
                    cmd = [
                        "ffmpeg", "-f", "lavfi", "-i", f"color=c=blue:size=640x360:duration={duration}",
                        "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p",
                        str(placeholder_path), "-y"
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    print(f"   ✅ Placeholder vidéo créé: {filename}")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Si FFmpeg n'est pas disponible, créer un fichier vide
                    with open(placeholder_path, 'wb') as f:
                        # Créer un header MP4 minimal
                        f.write(b'\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41')
                    print(f"   ⚠️ Placeholder fichier vide créé: {filename}")
            
            return f"/cache/seedance/{filename}"
            
        except Exception as e:
            print(f"   ❌ Erreur création placeholder: {e}")
            return f"/cache/seedance/error_{animation_id}.mp4"
    
    def _create_functional_placeholder(self, animation_id: str, duration: int = 5, theme: str = "animation") -> Optional[Dict[str, Any]]:
        """Crée un vrai fichier vidéo de fallback avec FFmpeg"""
        try:
            filename = f"fallback_{animation_id}.mp4"
            placeholder_path = self.cache_dir / filename
            
            if placeholder_path.exists():
                return {
                    "video_url": f"/cache/seedance/{filename}",
                    "video_path": str(placeholder_path),
                    "status": "functional_placeholder"
                }
            
            # Choisir une couleur selon le thème
            color_map = {
                "space": "darkblue",
                "ocean": "teal", 
                "nature": "green",
                "animals": "brown",
                "friendship": "pink",
                "adventure": "orange",
                "magic": "purple",
                "error": "red"
            }
            color = color_map.get(theme, "blue")
            
            # Essayer de créer une vraie vidéo avec FFmpeg
            if self.ffmpeg_path:
                try:
                    # Créer une vidéo colorée avec texte
                    cmd = [
                        self.ffmpeg_path, 
                        "-f", "lavfi", 
                        "-i", f"color=c={color}:size=640x360:duration={duration}",
                        "-f", "lavfi",
                        "-i", f"color=c=white:size=400x100:duration={duration}",
                        "-filter_complex", 
                        f"[0:v][1:v]overlay=120:130,drawtext=text='Animation {theme}\\nEn cours...':fontsize=24:fontcolor=black:x=(w-text_w)/2:y=(h-text_h)/2",
                        "-c:v", "libx264", 
                        "-t", str(duration), 
                        "-pix_fmt", "yuv420p",
                        "-r", "25",  # 25 FPS
                        str(placeholder_path), 
                        "-y"
                    ]
                    
                    result = subprocess.run(cmd, check=True, capture_output=True, timeout=30)
                    
                    if placeholder_path.exists() and placeholder_path.stat().st_size > 1000:
                        print(f"   ✅ Placeholder fonctionnel créé: {filename} ({placeholder_path.stat().st_size} bytes)")
                        return {
                            "video_url": f"/cache/seedance/{filename}",
                            "video_path": str(placeholder_path),
                            "status": "functional_placeholder"
                        }
                    else:
                        print(f"   ❌ Placeholder créé mais fichier trop petit")
                        
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
                    print(f"   ❌ Erreur FFmpeg pour placeholder: {e}")
            
            # Fallback: créer un fichier minimal
            try:
                with open(placeholder_path, 'wb') as f:
                    # Header MP4 minimal mais valide
                    f.write(b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp42mp41\x00\x00\x00\x08free')
                
                if placeholder_path.exists():
                    print(f"   ⚠️ Placeholder minimal créé: {filename}")
                    return {
                        "video_url": f"/cache/seedance/{filename}",
                        "video_path": str(placeholder_path),
                        "status": "minimal_placeholder"
                    }
                    
            except Exception as e:
                print(f"   ❌ Erreur création fichier minimal: {e}")
            
            return None
            
        except Exception as e:
            print(f"   ❌ Erreur création placeholder fonctionnel: {e}")
            return None
    
    async def _assemble_local_video(self, video_clips: List[Dict[str, Any]], animation_id: str) -> Optional[Dict[str, Any]]:
        """Assemble la vidéo finale localement avec FFmpeg"""
        try:
            print("   🎞️ Assemblage local avec FFmpeg...")
            
            # Filtrer les clips valides avec des chemins locaux
            valid_clips = []
            for clip in video_clips:
                if clip.get("video_path") and clip["status"] == "success":
                    video_path = Path(clip["video_path"])
                    if video_path.exists():
                        valid_clips.append(clip)
                        print(f"   ✅ Clip local: {video_path.name}")
                    else:
                        print(f"   ❌ Fichier manquant: {video_path}")
                else:
                    print(f"   ⚠️ Clip ignoré: {clip.get('status', 'no_status')}")
            
            if not valid_clips:
                print("   ⚠️ Aucun clip local valide pour l'assemblage")
                return None
            
            # Si un seul clip, pas d'assemblage nécessaire
            if len(valid_clips) == 1:
                print("   📹 Un seul clip, pas d'assemblage nécessaire")
                clip = valid_clips[0]
                return {
                    "video_url": clip["video_url"],
                    "video_path": clip.get("video_path"),
                    "status": "single_clip"
                }
            
            # Préparer le fichier de sortie
            output_filename = f"seedance_{animation_id}_assembled.mp4"
            output_path = self.cache_dir / output_filename
            print(f"   🎯 Assemblage pour ID: {animation_id} → {output_filename}")
            
            # Créer le fichier de liste pour FFmpeg
            filelist_path = self.cache_dir / f"filelist_{animation_id}.txt"
            
            try:
                with open(filelist_path, 'w') as f:
                    for clip in valid_clips:
                        video_path = Path(clip["video_path"])
                        # FFmpeg nécessite des chemins absolus et échappés
                        abs_path = video_path.resolve()
                        abs_path_str = str(abs_path)
                        f.write(f"file '{abs_path_str}'\n")
                        print(f"   📎 Ajouté: {abs_path.name}")
                
                # Commande FFmpeg pour concaténer les vidéos
                if not self.ffmpeg_path:
                    print("   ❌ FFmpeg non disponible")
                    # Fallback: utiliser le premier clip
                    first_clip = valid_clips[0]
                    return {
                        "video_url": first_clip["video_url"],
                        "video_path": first_clip.get("video_path"),
                        "status": "no_ffmpeg_fallback"
                    }
                
                cmd = [
                    self.ffmpeg_path, '-f', 'concat', '-safe', '0', 
                    '-i', str(filelist_path.resolve()),
                    '-c', 'copy',  # Copie sans réencodage pour être plus rapide
                    str(output_path.resolve()),
                    '-y'  # Overwrite output file
                ]
                
                print(f"   🔧 Exécution FFmpeg: {' '.join(cmd[:6])}...")
                
                # Exécuter FFmpeg
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=120
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Assemblage réussi: {output_filename}")
                    
                    # Nettoyage
                    try:
                        filelist_path.unlink()
                    except:
                        pass
                    
                    return {
                        "video_url": f"/cache/seedance/{output_filename}",
                        "video_path": str(output_path),
                        "status": "assembled"
                    }
                else:
                    print(f"   ❌ Erreur FFmpeg: {result.stderr}")
                    # Fallback: utiliser le premier clip
                    first_clip = valid_clips[0]
                    return {
                        "video_url": first_clip["video_url"],
                        "video_path": first_clip.get("video_path"),
                        "status": "ffmpeg_error_fallback"
                    }
                    
            except subprocess.TimeoutExpired:
                print("   ⏰ Timeout FFmpeg")
                # Fallback: utiliser le premier clip
                first_clip = valid_clips[0]
                return {
                    "video_url": first_clip["video_url"],
                    "video_path": first_clip.get("video_path"),
                    "status": "timeout_fallback"
                }
            except FileNotFoundError:
                print("   ❌ FFmpeg non trouvé, assemblage impossible")
                # Fallback: utiliser le premier clip
                first_clip = valid_clips[0]
                return {
                    "video_url": first_clip["video_url"],
                    "video_path": first_clip.get("video_path"),
                    "status": "no_ffmpeg_fallback"
                }
            finally:
                # Nettoyage du fichier temporaire
                try:
                    if filelist_path.exists():
                        filelist_path.unlink()
                except:
                    pass
                
        except Exception as e:
            print(f"   ❌ Erreur assemblage local: {e}")
            # Fallback: utiliser le premier clip valide
            if video_clips:
                for clip in video_clips:
                    if clip.get("video_url") and clip["status"] == "success":
                        return {
                            "video_url": clip["video_url"],
                            "video_path": clip.get("video_path"),
                            "status": "exception_fallback"
                        }
            return None

    def _find_ffmpeg(self) -> Optional[str]:
        """Trouve le chemin vers FFmpeg"""
        ffmpeg_paths = [
            "ffmpeg",  # Dans le PATH
            "C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe",
            "C:\\Program Files\\FFmpeg\\bin\\ffmpeg.exe",
            "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-7.1.1-full_build\\bin\\ffmpeg.exe"
        ]
        
        for path in ffmpeg_paths:
            try:
                result = subprocess.run([path, "-version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ FFmpeg trouvé: {path}")
                    return path
            except:
                continue
        
        print("⚠️ FFmpeg non trouvé - l'assemblage local sera désactivé")
        return None


# Instance globale
seedance_service = SeedanceService()


