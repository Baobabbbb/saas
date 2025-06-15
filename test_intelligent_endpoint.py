#!/usr/bin/env python3
"""
Script de test pour le nouveau endpoint intelligent de génération de BD
"""

import requests
import json

def test_intelligent_comic_endpoint():
    """Test du nouvel endpoint intelligent"""
    
    url = "http://127.0.0.1:8000/generate_comic_intelligent/"
    
    # Données de test
    payload = {
        "theme": "aventure spatiale",
        "style": "comic",
        "pages": 2,  # Commençons petit pour les tests
        "hero_name": "Astro",
        "custom_request": "Une aventure sur Mars avec un petit robot"
    }
    
    print("🚀 Test du système hybride CrewAI + Stability AI...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120  # 2 minutes pour la génération
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès !")
            print(f"Method: {result.get('method')}")
            print(f"Pages générées: {result.get('comic_data', {}).get('total_pages', 0)}")
            
            # Afficher quelques détails
            comic_data = result.get('comic_data', {})
            if comic_data.get('success'):
                print(f"ID BD: {comic_data.get('id')}")
                print(f"Real Stability AI: {comic_data.get('real_stability_ai')}")
                pages = comic_data.get('pages', [])
                for page in pages[:2]:  # Premiers pages seulement
                    print(f"  - Page {page.get('page_number')}: {page.get('bubbles_applied')} bulles")
            
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - la génération prend plus de 2 minutes")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    test_intelligent_comic_endpoint()
