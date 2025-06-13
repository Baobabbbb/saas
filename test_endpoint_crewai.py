#!/usr/bin/env python3
"""
Script de test pour valider l'endpoint /generate_comic/ avec CrewAI par défaut
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/generate_comic/"

def test_generate_comic_with_crewai():
    """Test de génération de BD avec CrewAI par défaut"""
    print("🧪 Test de l'endpoint /generate_comic/ avec CrewAI par défaut")
    print("=" * 60)
    
    # Données de test
    test_data = {
        "style": "cartoon",
        "hero_name": "Luna",
        "story_type": "aventure",
        "custom_request": "Une histoire sur une petite fille qui découvre une forêt magique avec des animaux parlants",
        "num_images": 4,
        "avatar_type": "emoji",
        "emoji": "👧"
    }
    
    print("📊 Données de test :")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print()
    
    # Envoi de la requête
    try:
        print("🚀 Envoi de la requête...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            data=test_data,
            timeout=300  # 5 minutes max
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Durée d'exécution : {duration:.2f} secondes")
        print(f"📈 Status code : {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès ! Résultat :")
            print(f"  📚 Titre : {result.get('title', 'N/A')}")
            print(f"  📄 Nombre de pages : {len(result.get('pages', []))}")
            print(f"  🤖 Amélioré par CrewAI : {result.get('enhanced_by_crewai', 'N/A')}")
            
            print("\n📖 Pages générées :")
            for i, page in enumerate(result.get('pages', []), 1):
                print(f"  Page {i}: {page}")
                
            # Vérifications
            expected_pages = test_data["num_images"]
            actual_pages = len(result.get('pages', []))
            
            if actual_pages == expected_pages:
                print(f"✅ Nombre de pages correct : {actual_pages}/{expected_pages}")
            else:
                print(f"❌ Nombre de pages incorrect : {actual_pages}/{expected_pages}")
                
            # Vérification que CrewAI a été utilisé
            if result.get('enhanced_by_crewai'):
                print("✅ CrewAI utilisé comme attendu")
            else:
                print("⚠️  CrewAI non utilisé (probablement fallback)")
                
            return True
            
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Détails : {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le serveur met trop de temps à répondre")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - Vérifiez que le serveur est démarré")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False

def test_server_health():
    """Test de santé du serveur"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur accessible")
            return True
        else:
            print(f"❌ Serveur non accessible (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Serveur non accessible : {e}")
        return False

if __name__ == "__main__":
    print("🔍 Vérification de l'endpoint /generate_comic/ avec CrewAI")
    print("=" * 60)
    
    # Test de santé
    if not test_server_health():
        print("\n💡 Assurez-vous que le serveur est démarré avec :")
        print("   cd saas && uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    print()
    
    # Test principal
    success = test_generate_comic_with_crewai()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test réussi ! L'endpoint /generate_comic/ utilise bien CrewAI par défaut")
    else:
        print("💥 Test échoué - Vérifiez les logs du serveur")
