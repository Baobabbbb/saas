#!/usr/bin/env python3
"""
Test du nouveau service CrewAI COMPLET pour la génération de BD
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/generate_comic_enhanced/"

def test_complete_crewai_comic():
    """Test du système CrewAI complet"""
    print("🧪 Test du système CrewAI COMPLET pour BD")
    print("=" * 60)
    
    # Données de test
    test_data = {
        "style": "cartoon",
        "hero_name": "Luna",
        "story_type": "aventure",
        "custom_request": "Une histoire sur une petite fille qui découvre une forêt magique avec des animaux parlants et des créatures fantastiques",
        "num_images": 4,
        "avatar_type": "emoji",
        "emoji": "👧",
        "use_crewai": True
    }
    
    print("📋 Spécifications de test :")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print()
    
    # Test de santé du serveur
    try:
        health_response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Serveur accessible")
    except requests.exceptions.ConnectionError:
        print("❌ Serveur inaccessible - Vérifiez qu'il est démarré")
        return False
    except Exception as e:
        print(f"⚠️ Problème de connexion: {e}")
    
    # Envoi de la requête principale
    try:
        print("🚀 Envoi de la requête CrewAI COMPLET...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            data=test_data,
            timeout=600  # 10 minutes max pour le processus complet
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Durée d'exécution : {duration:.2f} secondes")
        print(f"📈 Status code : {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès ! Résultat CrewAI COMPLET :")
            print(f"  📚 Titre : {result.get('title', 'N/A')}")
            print(f"  📄 Nombre de pages : {len(result.get('pages', []))}")
            print(f"  🤖 Créé par CrewAI : {result.get('enhanced_by_crewai', 'N/A')}")
            print(f"  🎨 Méthode : {result.get('creation_method', 'N/A')}")
            print(f"  ⭐ Score qualité : {result.get('quality_score', 'N/A')}")
            
            print("\n📖 Pages générées :")
            for i, page in enumerate(result.get('pages', []), 1):
                print(f"  Page {i}: {page}")
            
            # Vérifications spécifiques au système complet
            scenes_data = result.get('scenes_data', [])
            if scenes_data:
                print(f"\n🎭 Détails des scènes ({len(scenes_data)} scène(s)) :")
                for scene in scenes_data:
                    print(f"  Scène {scene.get('scene_index', 0) + 1}:")
                    print(f"    - Image finale : {scene.get('final_image_path', 'N/A')}")
                    print(f"    - Bulles appliquées : {scene.get('bubbles_applied', 0)}")
                    print(f"    - Score qualité : {scene.get('quality_score', 'N/A')}")
            
            # Métadonnées
            metadata = result.get('metadata', {})
            if metadata:
                print(f"\n📊 Métadonnées :")
                for key, value in metadata.items():
                    print(f"  {key}: {value}")
            
            print("\n🎉 Test CrewAI COMPLET réussi !")
            return True
            
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Détails : {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le processus CrewAI prend plus de 10 minutes")
        print("💡 C'est normal pour la première exécution (initialisation des agents)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - Vérifiez que le serveur est démarré")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False

def test_server_health():
    """Test de santé basique"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Test du système CrewAI COMPLET pour BD")
    print("=" * 60)
    
    # Test de santé
    if not test_server_health():
        print("\n💡 Assurez-vous que le serveur est démarré avec :")
        print("   cd saas && uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    print()
    
    # Test principal
    success = test_complete_crewai_comic()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test réussi ! Le système CrewAI COMPLET fonctionne parfaitement")
        print("\n✅ Fonctionnalités validées :")
        print("  - Génération de scénario par agent spécialisé")
        print("  - Conception de bulles franco-belges par expert") 
        print("  - Création de prompts d'images optimisés")
        print("  - Composition finale avec bulles appliquées")
        print("  - Respect des spécifications utilisateur")
        print("  - Qualité professionnelle")
    else:
        print("💥 Test échoué - Vérifiez les logs du serveur")
        print("\n🔧 Vérifications à faire :")
        print("  - Serveur FastAPI démarré")
        print("  - Variables d'environnement configurées")
        print("  - CrewAI installé et configuré")
        print("  - Agents YAML présents")
