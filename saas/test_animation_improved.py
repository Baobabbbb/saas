#!/usr/bin/env python3
"""
Test rapide de génération d'animation avec gestion d'erreur améliorée
"""

import requests
import json
import time

def test_animation_generation():
    """Test de génération d'animation via l'API"""
    
    print("🎬 Test de génération d'animation amélioré")
    print("=" * 50)
    
    api_url = "http://127.0.0.1:8000/api/animations/generate"
    
    # Données de test
    payload = {
        "style": "cartoon",
        "theme": "animals",
        "orientation": "landscape", 
        "prompt": "cute animals having fun in a magical forest"
    }
    
    print("📝 Paramètres:")
    for key, value in payload.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Lancement de la génération...")
    
    try:
        # Envoyer la requête
        start_time = time.time()
        response = requests.post(api_url, json=payload, timeout=1200)  # 20 minutes max
        elapsed_time = time.time() - start_time
        
        print(f"⏱️ Temps de réponse: {elapsed_time:.1f} secondes")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Génération terminée avec succès!")
            print(f"   ID: {data.get('id')}")
            print(f"   Titre: {data.get('title')}")
            print(f"   Description: {data.get('description')}")
            print(f"   Statut: {data.get('status')}")
            print(f"   URL Vidéo: {data.get('video_url')}")
            print(f"   URL Thumbnail: {data.get('thumbnail_url')}")
            
            # Analyser le mode utilisé
            description = data.get('description', '').lower()
            if 'simulation' in description:
                if 'timeout' in description:
                    print("\n⚠️ Mode simulation activé à cause d'un timeout")
                    print("   La génération Runway prenait trop de temps")
                elif 'crédits' in description:
                    print("\n⚠️ Mode simulation activé à cause des crédits")
                    print("   Crédits insuffisants sur le compte Runway")
                else:
                    print("\n⚠️ Mode simulation activé")
                print("   Une vidéo d'exemple est fournie immédiatement")
            else:
                print("\n🎉 Génération réelle via Runway Gen-4 réussie!")
                
        else:
            print(f"\n❌ Erreur HTTP: {response.status_code}")
            print(f"Détails: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n⏰ Timeout de la requête - Le serveur prend trop de temps")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

def test_credits_status():
    """Test de vérification des crédits"""
    
    print("\n🔍 Vérification des crédits Runway...")
    print("-" * 30)
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/runway/credits")
        if response.status_code == 200:
            data = response.json()
            print(f"   Statut: {data.get('status')}")
            print(f"   Crédits disponibles: {'✅' if data.get('credits_available') else '❌'}")
            if data.get('error_details'):
                print(f"   Détails: {data['error_details'].get('error', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    # Test des crédits d'abord
    test_credits_status()
    
    # Puis test de génération
    test_animation_generation()
    
    print("\n🎯 Résumé:")
    print("   - Le système détecte automatiquement les problèmes")
    print("   - En cas de timeout ou d'erreur, bascule en simulation")
    print("   - L'utilisateur obtient toujours une réponse rapidement")
    print("   - Les timeouts sont maintenant gérés sur 20 minutes max")
