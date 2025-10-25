import os
import requests
from datetime import datetime
from unidecode import unidecode

# Mapping des voix Runway pour différenciation homme/femme
# Versions optimisées : Eleanor (féminin) + James (masculin chaleureux)
VOICE_MAP = {
    "female": "Eleanor", # Voix féminine élégante et raffinée, moins aiguë
    "male": "James",     # Voix masculine chaleureuse et paternelle
}

def wait_for_runway_task(task_id, headers, max_attempts=30):
    """Attend qu'une tâche Runway soit terminée et retourne l'URL du résultat"""
    print(f"⏳ Attente de la tâche Runway: {task_id}")

    for attempt in range(max_attempts):
        try:
            task_url = f"https://api.dev.runwayml.com/v1/tasks/{task_id}"
            task_response = requests.get(task_url, headers=headers, timeout=10)
            task_response.raise_for_status()

            task_data = task_response.json()
            status = task_data.get("status")
            print(f"📊 Statut tâche {attempt+1}/{max_attempts}: {status}")

            if status == "SUCCEEDED":
                # Tâche terminée avec succès
                output = task_data.get("output", {})
                print(f"🔍 Output de la tâche: {output}")

                # Gérer les différents formats d'output
                if isinstance(output, list) and len(output) > 0:
                    first_item = output[0]
                    print(f"📋 Premier élément de la liste: {first_item}")

                    # Si c'est une string qui ressemble à une URL, c'est l'audio_url
                    if isinstance(first_item, str) and (first_item.startswith('http') or 'cloudfront' in first_item):
                        print(f"✅ URL audio trouvée directement: {first_item}")
                        return first_item
                    # Si c'est un dict, chercher audio_url
                    elif isinstance(first_item, dict):
                        audio_url = first_item.get("audio_url")
                        if audio_url:
                            return audio_url
                        else:
                            print(f"❌ Pas d'audio_url dans dict: {first_item}")
                            raise ValueError(f"No audio_url in task output dict: {first_item}")

                elif isinstance(output, dict):
                    audio_url = output.get("audio_url")
                    if audio_url:
                        return audio_url
                    else:
                        print(f"❌ Pas d'audio_url dans output dict: {output}")
                        raise ValueError(f"No audio_url in task output dict: {output}")

                elif isinstance(output, str) and (output.startswith('http') or 'cloudfront' in output):
                    # L'output est directement l'URL
                    print(f"✅ Output est directement l'URL audio: {output}")
                    return output

                else:
                    print(f"❌ Format d'output non reconnu: {type(output)} - {output}")
                    raise ValueError(f"Unrecognized output format: {output}")

            elif status == "FAILED":
                failure_reason = task_data.get("failure_reason", "Unknown failure")
                raise ValueError(f"Task failed: {failure_reason}")

            elif status in ["PENDING", "RUNNING"]:
                # Attendre avant la prochaine vérification
                import time
                time.sleep(3)  # Attendre 3 secondes
                continue

            else:
                raise ValueError(f"Unknown task status: {status}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur vérification tâche (tentative {attempt+1}): {e}")
            if attempt < max_attempts - 1:
                import time
                time.sleep(3)
                continue
            else:
                raise

    raise TimeoutError(f"Task {task_id} did not complete within {max_attempts * 3} seconds")

def test_runway_api_key():
    """Test si la clé API Runway est valide"""
    try:
        runway_api_key = os.getenv("RUNWAY_API_KEY")
        if not runway_api_key:
            return False, "RUNWAY_API_KEY non configurée"

        # Test simple avec l'endpoint d'organisation (ne coûte rien)
        url = "https://api.dev.runwayml.com/v1/organization"
        headers = {
            "Authorization": f"Bearer {runway_api_key}",
            "X-Runway-Version": "2024-09-13"  # Version utilisée dans les vidéos
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return True, "Clé API valide"
        elif response.status_code == 401:
            return False, "Clé API invalide ou expirée"
        else:
            return False, f"Erreur API: {response.status_code} - {response.text}"

    except Exception as e:
        return False, f"Erreur de connexion: {str(e)}"

def generate_speech(text, voice=None, filename=None):
    """Génération audio avec Runway TTS - version simplifiée"""
    print(f"🎵 TTS: Génération audio Runway - voice={voice}, filename={filename}")

    try:
        # Configuration de l'API Runway
        runway_api_key = os.getenv("RUNWAY_API_KEY")
        if not runway_api_key:
            print("❌ RUNWAY_API_KEY non configurée")
            raise ValueError("RUNWAY_API_KEY environment variable is not set")

        # Note: La clé fonctionne pour les vidéos, on suppose qu'elle fonctionne aussi pour TTS
        print("✅ Clé API Runway présumée valide (fonctionne pour les vidéos)")

        # Utilisation du mapping des voix
        voice_preset = VOICE_MAP.get(voice, "Eleanor")  # Default to Eleanor (female)
        input_text = text[:1000]  # Limite Runway pour text_to_speech

        print(f"🎤 Configuration voix - voice param: '{voice}', voice_preset: '{voice_preset}'")

        # Nettoyer le nom de fichier
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.mp3"
        else:
            filename = unidecode(filename).lower().replace(" ", "_").replace("'", "").replace("’", "").replace(",", "")
            if not filename.endswith(".mp3"):
                filename += ".mp3"

        path = f"static/{filename}"

        # Préparation de la requête Runway API selon la documentation
        url = "https://api.dev.runwayml.com/v1/text_to_speech"
        headers = {
            "Authorization": f"Bearer {runway_api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-09-13"  # Même version que pour les vidéos
        }

        payload = {
            "model": "eleven_multilingual_v2",
            "promptText": input_text,
            "voice": {
                "type": "runway-preset",
                "presetId": voice_preset
            }
        }

        print(f"🔑 Utilisation clé API: {runway_api_key[:15]}...")
        print(f"🎤 Voix sélectionnée: {voice_preset}")
        print(f"📝 Texte à traiter: {input_text[:50]}...")

        # Faire la requête
        print(f"🌐 Envoi requête à: {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"❌ Réponse: {response.text}")
            print(f"❌ Headers envoyés: {headers}")
            print(f"❌ Payload: {payload}")
            response.raise_for_status()

        # Vérifier le type de réponse
        content_length = len(response.content)
        content_type = response.headers.get('content-type', '').lower()
        print(f"✅ Réponse reçue (taille: {content_length} bytes, type: {content_type})")

        # Si c'est du JSON, c'est probablement une réponse avec task_id ou une erreur
        if 'application/json' in content_type or content_length < 1000:
            try:
                response_data = response.json()
                print(f"📄 Réponse JSON: {response_data}")

                # Vérifier si c'est une tâche asynchrone
                task_id = response_data.get("id")
                if task_id:
                    print(f"🎯 Tâche asynchrone détectée: {task_id}")
                    # Attendre que la tâche soit terminée
                    audio_url = wait_for_runway_task(task_id, headers)
                    print(f"🎵 URL audio obtenue: {audio_url}")

                    # Télécharger l'audio depuis l'URL
                    audio_response = requests.get(audio_url, timeout=30)
                    audio_response.raise_for_status()

                    with open(path, "wb") as f:
                        f.write(audio_response.content)

                    print(f"📁 Audio téléchargé et sauvegardé: {path} ({len(audio_response.content)} bytes)")
                    return path
                else:
                    # C'est peut-être une erreur
                    if "error" in response_data:
                        print(f"❌ Erreur JSON retournée par Runway: {response_data}")
                        raise ValueError(f"Runway API returned error: {response_data}")
                    else:
                        print(f"⚠️ Réponse JSON inattendue: {response_data}")

            except ValueError as json_error:
                print(f"⚠️ Impossible de parser JSON: {json_error}")
                # Si ce n'est pas du JSON valide, traiter comme fichier audio

        # Traiter comme fichier audio direct
        print(f"🎵 Sauvegarde du fichier audio direct: {path}")

        with open(path, "wb") as f:
            f.write(response.content)

        print(f"📁 Fichier sauvegardé: {path} ({content_length} bytes)")
        return path

    except requests.exceptions.Timeout:
        print("❌ Timeout - Runway API trop lent")
        raise ValueError("Timeout lors de la génération audio Runway")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau Runway: {e}")
        raise ValueError(f"Erreur réseau Runway: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        raise
