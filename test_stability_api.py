"""
Script de test pour vérifier l'API Stability AI
"""
# -*- coding: utf-8 -*-
import sys
import os

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
import requests
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv("saas/.env")

# Récupérer la clé API
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

print("=" * 60)
print("TEST API STABILITY AI - CONTROLNET")
print("=" * 60)
print()

# 1. Vérifier la clé API
print(f"1. Clé API présente: {'Oui' if STABILITY_API_KEY else 'Non'}")
if STABILITY_API_KEY:
    print(f"   Clé: {STABILITY_API_KEY[:20]}...")
print()

# 2. Créer une image de test simple (contours noirs)
print("2. Création d'une image de test...")
test_image = Image.new('RGB', (512, 512), color='white')
# Dessiner un carré noir (contours)
from PIL import ImageDraw
draw = ImageDraw.Draw(test_image)
draw.rectangle([100, 100, 400, 400], outline='black', width=5)
print("   ✅ Image de test créée (512x512)")
print()

# 3. Convertir en bytes
print("3. Conversion en bytes...")
img_byte_arr = io.BytesIO()
test_image.save(img_byte_arr, format='PNG')
img_byte_arr.seek(0)
print("   ✅ Image convertie")
print()

# 4. Test endpoint /control/structure
print("4. Test endpoint /control/structure...")
url = "https://api.stability.ai/v2beta/stable-image/control/structure"
headers = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Accept": "image/*"
}
files = {
    "image": ("control.png", img_byte_arr, "image/png")
}
data = {
    "prompt": "black and white coloring book page, simple cartoon",
    "negative_prompt": "no colors, no shading",
    "control_strength": 0.7,
    "output_format": "png"
}

print(f"   URL: {url}")
print(f"   Prompt: {data['prompt']}")
print(f"   Control strength: {data['control_strength']}")
print()

print("5. Envoi de la requête...")
try:
    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data,
        timeout=30
    )
    
    print(f"   Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        print("✅ SUCCÈS!")
        print(f"   Taille de l'image: {len(response.content)} bytes")
        
        # Sauvegarder l'image
        output_path = "test_stability_output.png"
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"   Image sauvegardée: {output_path}")
    else:
        print("❌ ERREUR API")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print()
        print("   Réponse brute:")
        print("   " + "-" * 56)
        
        try:
            error_json = response.json()
            import json
            print(json.dumps(error_json, indent=2))
        except:
            print(response.text[:1000])
        
        print("   " + "-" * 56)
        
        # Messages d'aide selon le code d'erreur
        if response.status_code == 401:
            print()
            print("💡 La clé API est invalide ou expirée.")
            print("   → Vérifiez votre STABILITY_API_KEY dans Railway")
        elif response.status_code == 402:
            print()
            print("💡 Crédits insuffisants sur votre compte Stability AI.")
            print("   → Rechargez vos crédits sur https://platform.stability.ai")
        elif response.status_code == 404:
            print()
            print("💡 L'endpoint /control/structure n'existe pas.")
            print("   → Vérifiez la documentation officielle")
        elif response.status_code == 422:
            print()
            print("💡 Paramètres de requête invalides.")
            print("   → Vérifiez le format de l'image ou les paramètres")
        elif response.status_code == 500:
            print()
            print("💡 Erreur serveur Stability AI.")
            print("   → Réessayez dans quelques minutes")

except requests.exceptions.Timeout:
    print("❌ TIMEOUT - La requête a pris plus de 30 secondes")
except requests.exceptions.RequestException as e:
    print(f"❌ ERREUR REQUÊTE: {e}")
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("FIN DU TEST")
print("=" * 60)

