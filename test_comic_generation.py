#!/usr/bin/env python3
"""
Test complet de génération de BD avec CrewAI
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_comic_generation():
    """Test de génération de BD avec CrewAI"""
    print("=== Test de génération de BD avec CrewAI ===\n")
    
    # D'abord, activer CrewAI
    print("1. Activation de CrewAI...")
    response = requests.post(f"{BASE_URL}/toggle_crewai/", data={"enabled": "true"})
    if response.status_code == 200:
        print("✅ CrewAI activé")
    else:
        print("❌ Échec d'activation de CrewAI")
        return False
      # Préparer les données de test pour la BD
    comic_data = {
        "style": "cartoon",
        "hero_name": "Robo",
        "story_type": "adventure",
        "custom_request": "L'aventure d'un petit robot qui découvre le monde",
        "num_images": 4,
        "use_crewai": True    }
    
    print("2. Lancement de la génération de BD avec CrewAI...")
    print(f"   Héros: {comic_data['hero_name']}")
    print(f"   Type d'histoire: {comic_data['story_type']}")
    print(f"   Style: {comic_data['style']}")
    print(f"   Nombre d'images: {comic_data['num_images']}")
    print(f"   Requête personnalisée: {comic_data['custom_request']}")
    print()
    
    try:
        # Envoyer la requête de génération
        response = requests.post(
            f"{BASE_URL}/generate_comic_enhanced/",
            data=comic_data,
            timeout=60  # 60 secondes pour la génération
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération réussie!")
            print(f"Scenario amélioré reçu: {len(result.get('enhanced_scenario', ''))} caractères")
            print(f"Comic data: {type(result.get('comic_data', {}))}")
            
            # Afficher un extrait du scénario amélioré si disponible
            enhanced_scenario = result.get('enhanced_scenario', '')
            if enhanced_scenario:
                print("\n--- Extrait du scénario amélioré ---")
                # Limiter l'affichage pour la lisibilité
                if len(enhanced_scenario) > 500:
                    print(enhanced_scenario[:500] + "...")
                else:
                    print(enhanced_scenario)
            
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La génération prend plus de 60 secondes")
        print("Ceci est normal pour la première exécution car CrewAI doit initialiser les agents")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_standard_comic_generation():
    """Test de génération de BD standard (sans CrewAI) pour comparaison"""
    print("\n=== Test de génération de BD standard (sans CrewAI) ===\n")
    
    # Désactiver CrewAI
    print("1. Désactivation de CrewAI...")
    response = requests.post(f"{BASE_URL}/toggle_crewai/", data={"enabled": "false"})
    if response.status_code == 200:
        print("✅ CrewAI désactivé")
    else:
        print("❌ Échec de désactivation de CrewAI")
        return False
      # Préparer les données de test (format standard)
    comic_data = {
        "style": "cartoon",
        "hero_name": "Robo",
        "story_type": "adventure", 
        "custom_request": "L'aventure d'un petit robot qui découvre le monde",
        "num_images": 4
    }
    
    print("2. Lancement de la génération de BD standard...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate_comic/",
            data=comic_data,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération standard réussie!")
            print(f"Comic data: {type(result.get('comic_data', {}))}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("🚀 Test complet de la génération de BD avec et sans CrewAI\n")
    
    tests = [
        ("Génération BD avec CrewAI", test_comic_generation),
        ("Génération BD standard", test_standard_comic_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        result = test_func()
        results.append((test_name, result))
        print(f"\nRésultat {test_name}: {'✅ RÉUSSI' if result else '❌ ÉCHOUÉ'}")
    
    print(f"\n{'='*60}")
    print("=== RÉSUMÉ FINAL ===")
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTests réussis: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés ! L'intégration CrewAI fonctionne correctement.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) ont échoué.")
        return 1

if __name__ == "__main__":
    exit(main())
