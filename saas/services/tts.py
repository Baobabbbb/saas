import os
import requests
from datetime import datetime
from unidecode import unidecode

# Mapping des voix Runway pour différenciation homme/femme
VOICE_MAP = {
    "female": "Maya",    # Voix féminine douce
    "male": "Arjun",     # Voix masculine claire
}

def test_runway_api_key():
    """Test si la clé API Runway est valide"""
    try:
        runway_api_key = os.getenv("RUNWAY_API_KEY")
        if not runway_api_key:
            return False, "RUNWAY_API_KEY non configurée"

        # Test simple avec l'endpoint d'organisation (ne coûte rien)
        url = "https://api.runwayml.com/v1/organization"
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
        voice_preset = VOICE_MAP.get(voice, "Maya")  # Default to Maya (female)
        input_text = text[:1000]  # Limite Runway pour text_to_speech

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
        url = "https://api.runwayml.com/v1/text_to_speech"
        headers = {
            "Authorization": f"Bearer {runway_api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-09-13"  # Même version que pour les vidéos
        }

        payload = {
            "model": "eleven_multilingual_v2",
            "text": input_text,
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

        # Runway retourne directement l'audio en streaming
        print(f"✅ Audio généré avec succès via Runway (taille: {len(response.content)} bytes)")

        with open(path, "wb") as f:
            f.write(response.content)

        print(f"📁 Fichier sauvegardé: {path}")
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
