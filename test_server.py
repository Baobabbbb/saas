#!/usr/bin/env python3
"""
Script de test pour vérifier que le serveur FastAPI fonctionne correctement.
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test d'un endpoint basique pour vérifier que le serveur fonctionne"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"Docs endpoint: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur lors du test health: {e}")
    return False

def test_crewai_toggle():
    """Test d'activation/désactivation de CrewAI"""
    try:
        # Test toggle (activation)
        response = requests.post(f"{BASE_URL}/toggle_crewai/", 
                               data={"enabled": "true"}, timeout=10)
        print(f"CrewAI toggle (enable): {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            
            # Test toggle (désactivation)
            response = requests.post(f"{BASE_URL}/toggle_crewai/", 
                                   data={"enabled": "false"}, timeout=10)
            print(f"CrewAI toggle (disable): {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
                return True
    except Exception as e:
        print(f"Erreur lors du test CrewAI toggle: {e}")
    return False

def test_crewai_validation():
    """Test de validation d'un scénario CrewAI"""
    try:
        test_scenario = {
            "title": "Le Trésor du Jardin",
            "panels": [
                {"action": "Un petit garçon creuse dans son jardin"},
                {"action": "Il découvre un coffre brillant"},
                {"action": "Il ouvre le coffre et trouve des pièces d'or"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/validate_crewai_scenario/", 
                               json=test_scenario, timeout=15)
        print(f"CrewAI validation: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Erreur lors du test CrewAI validation: {e}")
    return False

def test_docs():
    """Test de l'endpoint de documentation"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"Docs: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur lors du test docs: {e}")
    return False

def main():
    print("=== Test du serveur FastAPI avec CrewAI ===\n")
    
    tests = [
        ("Health Check", test_health),
        ("Documentation", test_docs),
        ("CrewAI Toggle", test_crewai_toggle),
        ("CrewAI Validation", test_crewai_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
        print(f"Résultat: {'✅ PASSÉ' if result else '❌ ÉCHOUÉ'}\n")
    
    print("=== Résumé des tests ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
    
    print(f"\nTests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le serveur fonctionne correctement.")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez que le serveur est bien démarré.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
