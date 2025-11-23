"""
Service Suno AI - Génération de comptines musicales avec Suno API
Utilise l'API Suno officielle pour créer des comptines avec musique de haute qualité
Documentation: https://docs.sunoapi.org/suno-api/generate-music
"""

import aiohttp
import asyncio
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from config import SUNO_API_KEY, SUNO_BASE_URL

# Configuration optimisée pour les comptines enfant avec Suno
NURSERY_RHYME_STYLES = {
    "lullaby": {
        "style": "gentle French lullaby, soft children's melody, clear French female voice, articulated pronunciation, soothing, calming",
        "tempo": "slow",
        "mood": "calm",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "aggressive, loud, fast, rock, metal, scary"
    },
    "counting": {
        "style": "educational French children's song, clear French singing voice, pedagogical rhythm, articulated French pronunciation, playful, fun",
        "tempo": "medium",
        "mood": "educational",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "complex, adult, serious, slow"
    },
    "animal": {
        "style": "playful French children's song with animal sounds, happy French voice, clear articulation, fun, energetic, joyful",
        "tempo": "medium",
        "mood": "playful",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "sad, slow, serious, adult"
    },
    "seasonal": {
        "style": "festive French children's song, joyful French melody, clear French pronunciation, celebratory, cheerful",
        "tempo": "medium",
        "mood": "festive",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "sad, dark, slow, serious"
    },
    "educational": {
        "style": "educational French children's song, clear French voice, learning melody, articulated pronunciation, pedagogical, fun",
        "tempo": "medium",
        "mood": "educational",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "complex, fast, aggressive, adult"
    },
    "movement": {
        "style": "energetic French children's dance song, upbeat rhythm, clear French pronunciation, dynamic, fun, active",
        "tempo": "fast",
        "mood": "energetic",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "slow, calm, sad, quiet"
    },
    "custom": {
        "style": "French children's song, happy voice, simple melody, clear pronunciation, joyful, fun",
        "tempo": "medium",
        "mood": "joyful",
        "instrumental": False,
        "model": "V4_5",
        "vocal_gender": "f",
        "negative_tags": "adult, complex, serious, sad"
    }
}

class SunoService:
    def __init__(self):
        self.api_key = SUNO_API_KEY
        self.base_url = SUNO_BASE_URL or "https://api.sunoapi.org/api/v1"
        
        # Initialisation silencieuse
        
    async def generate_musical_nursery_rhyme(
        self, 
        lyrics: Optional[str] = None,
        rhyme_type: str = "custom",
        custom_style: Optional[str] = None,
        title: Optional[str] = None,
        custom_mode: bool = True,
        prompt_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une comptine musicale avec Suno AI (Mode Custom ou Non-Custom)
        
        Args:
            lyrics: Les paroles exactes (mode custom uniquement)
            rhyme_type: Type de comptine (lullaby, counting, animal, etc.)
            custom_style: Style musical personnalisé optionnel
            title: Titre de la comptine
            custom_mode: True = paroles exactes (lyrics), False = Suno génère les paroles
            prompt_description: Description pour Suno en mode non-custom (max 500 chars)
            
        Returns:
            Dict contenant les informations de la tâche
        """
        try:
            if not self.api_key or self.api_key.startswith("your_suno") or self.api_key == "None" or str(self.api_key).lower() == "none":
                error_msg = "❌ Clé API Suno non configurée. Veuillez configurer SUNO_API_KEY dans les variables d'environnement Railway"
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "error": error_msg
                }

            # Récupérer le style prédéfini ou utiliser le style personnalisé
            style_config = NURSERY_RHYME_STYLES.get(rhyme_type, NURSERY_RHYME_STYLES["custom"])
            base_style = custom_style or style_config["style"]
            
            # Préparer le titre
            if not title:
                title = f"Comptine {rhyme_type.capitalize()}"
            
            title_truncated = title[:80] if len(title) > 80 else title
            
            # Préparer le payload selon le mode (Custom ou Non-Custom)
            # Documentation: https://docs.sunoapi.org/suno-api/generate-music
            
            if custom_mode:
                # MODE CUSTOM : Paroles exactes fournies par GPT-4o-mini
                # Utilisé quand personnalisation (prénom, détails spécifiques)
                if not lyrics:
                    return {
                        "status": "error",
                        "error": "Mode custom nécessite des paroles (lyrics)"
                    }
                
                lyrics_truncated = lyrics[:5000] if len(lyrics) > 5000 else lyrics
                
                # Si un prompt_description optimisé est fourni, l'utiliser pour enrichir le style
                if prompt_description:
                    # Combiner le style de base avec le prompt optimisé
                    enhanced_style = f"{prompt_description}. {base_style}"
                    style_truncated = enhanced_style[:1000] if len(enhanced_style) > 1000 else enhanced_style
                else:
                    style_truncated = base_style[:1000] if len(base_style) > 1000 else base_style
                
                payload = {
                    "prompt": lyrics_truncated,  # Paroles exactes
                    "style": style_truncated,
                    "title": title_truncated,
                    "customMode": True,
                    "instrumental": style_config["instrumental"],
                    "model": style_config["model"],
                    "vocalGender": style_config["vocal_gender"],
                    "negativeTags": style_config.get("negative_tags", ""),
                    "callBackUrl": f"{os.getenv('BASE_URL', 'https://herbbie.com')}/suno-callback"
                }
                
                print(f"🎵 Génération Suno (MODE CUSTOM) lancée:")
                print(f"   - Titre: {title_truncated}")
                print(f"   - Style: {style_config['mood']}")
                print(f"   - Modèle: {style_config['model']}")
                print(f"   - Paroles fournies: {len(lyrics_truncated)} caractères")
                if prompt_description:
                    print(f"   - Prompt optimisé: {prompt_description[:100]}...")
            else:
                # MODE NON-CUSTOM : Suno génère les paroles automatiquement
                # Utilisé pour demandes génériques (pas de personnalisation)
                if not prompt_description:
                    return {
                        "status": "error",
                        "error": "Mode non-custom nécessite une description (prompt_description)"
                    }
                
                # Max 500 caractères pour mode non-custom
                prompt_truncated = prompt_description[:500] if len(prompt_description) > 500 else prompt_description
                
                payload = {
                    "prompt": prompt_truncated,  # Description du thème
                    "customMode": False,
                    "instrumental": style_config["instrumental"],
                    "model": style_config["model"],
                    "callBackUrl": f"{os.getenv('BASE_URL', 'https://herbbie.com')}/suno-callback"
                }
                
                print(f"🎵 Génération Suno (MODE AUTO) lancée:")
                print(f"   - Description: {prompt_truncated}")
                print(f"   - Modèle: {style_config['model']}")
                print(f"   - Suno générera les paroles automatiquement")
            
            print(f"   - Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            # Faire la requête à l'API Suno
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            
                            if data.get("code") == 200:
                                task_id = data["data"]["taskId"]
                                
                                print(f"✅ Tâche Suno créée avec succès: {task_id}")
                                
                                return {
                                    "status": "success",
                                    "task_id": task_id,
                                    "message": "Génération musicale lancée avec Suno AI",
                                    "style_used": base_style,
                                    "model_used": style_config["model"],
                                    "service": "suno"
                                }
                            else:
                                error_msg = data.get("msg", "Erreur inconnue de l'API Suno")
                                print(f"❌ Erreur API Suno (code {data.get('code')}): {error_msg}")
                                return {
                                    "status": "error",
                                    "error": f"Erreur API Suno: {error_msg}",
                                    "code": data.get("code")
                                }
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur parsing JSON: {e}")
                            print(f"   Réponse brute: {response_text[:500]}")
                            return {
                                "status": "error",
                                "error": f"Erreur parsing réponse: {str(e)}"
                            }
                    else:
                        print(f"❌ Erreur HTTP {response.status}")
                        print(f"   Réponse: {response_text[:500]}")
                        return {
                            "status": "error",
                            "error": f"Erreur HTTP {response.status}: {response_text[:200]}"
                        }
            
        except asyncio.TimeoutError:
            print("❌ Timeout lors de la requête à l'API Suno")
            return {
                "status": "error",
                "error": "Timeout lors de la requête à l'API Suno (30s)"
            }
        except Exception as e:
            print(f"❌ Erreur génération musicale Suno: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    async def download_and_store_audio(self, audio_url: str, task_id: str) -> Optional[str]:
        """
        Télécharge automatiquement le fichier audio depuis Suno et le stocke côté serveur
        pour permettre un téléchargement instantané.

        Args:
            audio_url: URL du fichier audio chez Suno
            task_id: ID de la tâche pour nommer le fichier

        Returns:
            Chemin relatif du fichier stocké, ou None en cas d'erreur
        """
        try:
            print(f"🎵 [DOWNLOAD] Début téléchargement depuis: {audio_url[:100]}...")

            # Créer le dossier audio s'il n'existe pas
            audio_dir = os.path.join(os.getcwd(), "audio")
            os.makedirs(audio_dir, exist_ok=True)
            print(f"🎵 [DOWNLOAD] Dossier audio: {audio_dir}")

            # Générer un nom de fichier unique
            file_extension = ".mp3"
            unique_filename = f"comptine_{task_id}_{uuid.uuid4().hex[:8]}{file_extension}"
            local_path = os.path.join(audio_dir, unique_filename)
            print(f"🎵 [DOWNLOAD] Chemin local: {local_path}")

            # Télécharger le fichier
            print("🎵 [DOWNLOAD] Envoi requête HTTP...")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    audio_url,
                    timeout=aiohttp.ClientTimeout(total=60)  # Timeout plus long pour les gros fichiers
                ) as response:
                    print(f"🎵 [DOWNLOAD] Réponse HTTP: {response.status}")
                    print(f"🎵 [DOWNLOAD] Headers: {dict(response.headers)}")

                    if response.status == 200:
                        print("🎵 [DOWNLOAD] Téléchargement en cours...")
                        # Lire le contenu en chunks pour éviter la surcharge mémoire
                        with open(local_path, 'wb') as f:
                            chunk_count = 0
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                                chunk_count += 1
                                if chunk_count % 10 == 0:  # Log tous les 10 chunks
                                    print(f"🎵 [DOWNLOAD] Téléchargé {chunk_count * 8192} bytes...")

                        file_size = os.path.getsize(local_path)
                        print(f"✅ [DOWNLOAD] Audio téléchargé et stocké: {file_size} bytes")

                        # Vérifier que le fichier n'est pas vide
                        if file_size == 0:
                            print("❌ [DOWNLOAD] Fichier vide, suppression")
                            os.remove(local_path)
                            return None

                        # Retourner le chemin relatif pour l'accès via l'API
                        return f"audio/{unique_filename}"
                    else:
                        print(f"❌ [DOWNLOAD] Erreur HTTP: {response.status}")
                        response_text = await response.text()
                        print(f"❌ [DOWNLOAD] Réponse: {response_text[:200]}")
                        return None

        except Exception as e:
            print(f"❌ [DOWNLOAD] Erreur téléchargement: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def check_task_status(self, task_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Vérifie le statut d'une tâche Suno
        Documentation: https://docs.sunoapi.org/suno-api/generate-music
        
        Args:
            task_id: ID de la tâche
            
        Returns:
            Dict contenant le statut et les URLs si terminé
        """
        try:
            if not self.api_key or self.api_key.startswith("your_suno"):
                raise ValueError("❌ Clé API Suno non configurée")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Utiliser l'endpoint officiel /generate/record-info avec taskId en paramètre
            # Documentation: https://docs.sunoapi.org/suno-api/quickstart
            url = f"{self.base_url}/generate/record-info?taskId={task_id}"
            print(f"🔍 Vérification statut Suno: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            
                            if data.get("code") == 200:
                                task_data = data.get("data", {})
                                
                                # Vérifier le statut global de la tâche
                                # Documentation: status peut être "GENERATING", "SUCCESS", "FAILED", "PENDING"
                                task_status = task_data.get("status", "")
                                
                                print(f"📊 Statut tâche Suno: {task_status}")
                                print(f"📊 DEBUG - Structure complète:")
                                print(f"   task_data keys: {list(task_data.keys())}")
                                if task_data.get("response"):
                                    resp = task_data.get('response', {})
                                    print(f"   response keys: {list(resp.keys())}")
                                    suno_data = resp.get('sunoData', []) or resp.get('data', [])
                                    print(f"   sunoData length: {len(suno_data)}")
                                
                                if task_status == "SUCCESS" or task_status == "TEXT_SUCCESS":
                                    # Tâche terminée avec succès
                                    response_data = task_data.get("response", {})
                                    # IMPORTANT: L'API Suno retourne 'sunoData' et non 'data'
                                    clips = response_data.get("sunoData", []) or response_data.get("data", [])
                                    
                                    if not clips:
                                        return {
                                            "status": "failed",
                                            "error": "Aucun audio généré",
                                            "message": "❌ Aucune chanson retournée"
                                        }
                                    # Prendre seulement la première chanson disponible
                                    clip = clips[0] if clips else None

                                    if not clip:
                                        return {
                                            "status": "failed",
                                            "error": "Aucun audio généré",
                                            "message": "❌ Aucune chanson retournée"
                                        }

                                    audio_url_val = clip.get('audioUrl') or clip.get('streamAudioUrl')
                                    print(f"🎵 Clip principal:")
                                    print(f"   - id: {clip.get('id')}")
                                    print(f"   - title: {clip.get('title')}")
                                    print(f"   - audioUrl: {audio_url_val[:80] if audio_url_val else 'None'}...")
                                    print(f"   - duration: {clip.get('duration')}")

                                    if not audio_url_val:
                                        return {
                                            "status": "failed",
                                            "error": "URL audio manquante",
                                            "message": "❌ URL audio non disponible"
                                        }

                                    print(f"🎵 URL audio disponible: {audio_url_val[:100]}...")
                                    
                                    # 📤 Télécharger et uploader vers Supabase Storage si user_id fourni
                                    audio_path_supabase = None
                                    if user_id:
                                        try:
                                            # Télécharger l'audio depuis Suno
                                            temp_audio_path = await self.download_and_store_audio(audio_url_val, task_id)
                                            
                                            if temp_audio_path:
                                                # Uploader vers Supabase Storage
                                                from services.supabase_storage import get_storage_service
                                                storage_service = get_storage_service()
                                                
                                                if storage_service:
                                                    # Construire le chemin complet du fichier temporaire
                                                    import os
                                                    # temp_audio_path est déjà "audio/filename.mp3"
                                                    full_temp_path = os.path.join(os.getcwd(), temp_audio_path)
                                                    
                                                    if os.path.exists(full_temp_path):
                                                        upload_result = await storage_service.upload_file(
                                                            file_path=full_temp_path,
                                                            user_id=user_id,
                                                            content_type="rhyme",
                                                            custom_filename=f"comptine_{task_id}.mp3"
                                                        )
                                                        
                                                        if upload_result.get("success"):
                                                            audio_path_supabase = upload_result.get("signed_url")
                                                            print(f"✅ Audio uploadé vers Supabase Storage: {audio_path_supabase[:100]}...")
                                                            
                                                            # Supprimer le fichier temporaire local
                                                            try:
                                                                os.remove(full_temp_path)
                                                            except:
                                                                pass
                                                        else:
                                                            print(f"⚠️ Échec upload Supabase Storage: {upload_result.get('error')}")
                                                else:
                                                    print("⚠️ Service Supabase Storage non disponible")
                                            else:
                                                print("⚠️ Échec téléchargement audio depuis Suno")
                                        except Exception as upload_error:
                                            print(f"⚠️ Erreur upload audio vers Supabase Storage: {upload_error}")
                                            import traceback
                                            traceback.print_exc()
                                    
                                    return {
                                        "status": "completed",
                                        "task_id": task_id,
                                        "audio_path": audio_path_supabase,  # URL Supabase Storage si upload réussi
                                        "suno_url": audio_url_val,  # URL Suno originale (fallback)
                                        "title": clip.get("title", "Comptine"),
                                        "duration": clip.get("duration"),
                                        "message": "✅ Comptine générée avec succès"
                                    }
                                elif task_status == "FAILED":
                                    # Tâche échouée
                                    error_message = task_data.get("errorMessage", "Erreur inconnue")
                                    return {
                                        "status": "failed",
                                        "task_id": task_id,
                                        "error": error_message,
                                        "message": "❌ La génération a échoué"
                                    }
                                else:
                                    # Génération en cours (GENERATING, PENDING)
                                    return {
                                        "status": "processing",
                                        "task_id": task_id,
                                        "message": f"🔄 Génération Suno en cours... (statut: {task_status})"
                                    }
                            else:
                                error_msg = data.get("msg", "Erreur inconnue")
                                return {
                                    "status": "error",
                                    "error": f"Erreur API Suno: {error_msg}",
                                    "code": data.get("code")
                                }
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur parsing JSON status: {e}")
                            print(f"   Réponse brute: {response_text[:500]}")
                            return {
                                "status": "error",
                                "error": f"Erreur parsing réponse: {str(e)}"
                            }
                    else:
                        print(f"❌ Erreur HTTP {response.status} lors de la vérification")
                        return {
                            "status": "error",
                            "error": f"Erreur HTTP {response.status}: {response_text[:200]}"
                        }
                        
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "error": "Timeout lors de la vérification du statut"
            }
        except Exception as e:
            print(f"❌ Erreur vérification statut Suno: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

# Instance globale du service
suno_service = SunoService()
