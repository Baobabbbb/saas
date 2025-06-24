#!/usr/bin/env python3
"""
Script de démonstration pour tester l'intégration complète 
de la génération d'animations avec Runway Gen-4
"""

import requests
import json
import time

# Configuration
API_BASE = "http://127.0.0.1:8000"

def check_runway_status():
    """Vérifier l'état des crédits Runway"""
    print("🔍 Vérification de l'état de Runway...")
    
    try:
        response = requests.get(f"{API_BASE}/api/runway/credits")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data['service']}")
            print(f"   Statut: {data['status']}")
            print(f"   Crédits disponibles: {'✅ Oui' if data['credits_available'] else '❌ Non'}")
            
            if data['status'] == 'no_credits':
                print(f"   Raison: {data.get('reason', 'N/A')}")
            elif data['status'] == 'active':
                print("   🚀 Prêt pour la génération réelle !")
            
            return data['credits_available']
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def generate_animation(style="cartoon", theme="animals", orientation="landscape", prompt=""):
    """Générer une animation"""
    print(f"\n🎬 Génération d'animation...")
    print(f"   Style: {style}")
    print(f"   Thème: {theme}")
    print(f"   Orientation: {orientation}")
    print(f"   Prompt: {prompt}")
    
    payload = {
        "style": style,
        "theme": theme,
        "orientation": orientation,
        "prompt": prompt
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/animations/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Animation générée avec succès !")
            print(f"   ID: {data['id']}")
            print(f"   Titre: {data['title']}")
            print(f"   Description: {data['description']}")
            print(f"   Statut: {data['status']}")
            print(f"   URL Vidéo: {data['video_url']}")
            
            # Détecter si c'est une simulation
            if "simulation" in data['description'].lower():
                print("\n⚠️ Mode simulation activé (crédits insuffisants)")
                print("   - La vidéo de démonstration est fournie")
                print("   - Ajoutez des crédits pour la génération réelle")
            else:
                print("\n🎉 Génération réelle via Runway Gen-4 !")
            
            return data
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"   Détails: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def main():
    """Fonction principale de démonstration"""
    print("🎭 Démonstration - Génération d'Animations avec Runway Gen-4")
    print("=" * 60)
    
    # 1. Vérifier l'état de Runway
    has_credits = check_runway_status()
    
    # 2. Générer quelques animations de test
    test_cases = [
        {
            "style": "cartoon",
            "theme": "animals", 
            "orientation": "landscape",
            "prompt": "cute forest animals having a picnic"
        },
        {
            "style": "fairy_tale",
            "theme": "magic",
            "orientation": "portrait", 
            "prompt": "magical fairy casting sparkles"
        },
        {
            "style": "anime",
            "theme": "space",
            "orientation": "portrait",
            "prompt": "space explorer discovering new planet"
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/3")
        print("-" * 30)
        result = generate_animation(**test_case)
        if result:
            results.append(result)
        time.sleep(1)  # Petite pause entre les générations
    
    # 3. Résumé
    print(f"\n📊 Résumé de la démonstration")
    print("=" * 40)
    print(f"   Animations générées: {len(results)}")
    print(f"   Mode utilisé: {'Vraie API' if has_credits else 'Simulation'}")
    
    if not has_credits:
        print("\n💡 Pour activer la génération réelle:")
        print("   1. Ajoutez des crédits à votre compte Runway")
        print("   2. Relancez le système - il détectera automatiquement les crédits")
        print("   3. Les générations utiliseront alors la vraie API Runway Gen-4 !")
    else:
        print("\n🚀 Génération réelle active - Profitez des animations Runway Gen-4 !")
    
    print("\n✨ Démonstration terminée !")

if __name__ == "__main__":
    main()
