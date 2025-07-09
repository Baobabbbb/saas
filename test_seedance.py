#!/usr/bin/env python3
"""
Script de test pour l'API SEEDANCE
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8006"
SEEDANCE_ENDPOINT = f"{API_BASE_URL}/api/seedance/generate"
STATUS_ENDPOINT = f"{API_BASE_URL}/api/seedance/status"

def test_seedance_status():
    """Test du statut du service SEEDANCE"""
    print("🔍 Test du statut SEEDANCE...")
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Service SEEDANCE opérationnel")
            print(f"📊 Statut: {status_data}")
            return True
        else:
            print(f"❌ Erreur statut: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def test_seedance_generate():
    """Test de génération SEEDANCE"""
    print("\n🚀 Test de génération SEEDANCE...")
    
    # Payload de test
    payload = {
        "story": "Un petit hérisson curieux découvre que les déchets dans la forêt font du mal à ses amis les animaux. Il décide d'organiser une grande journée de nettoyage avec tous les habitants de la forêt pour apprendre l'importance de protéger la nature.",
        "theme": "ecology",
        "age_target": "4-6", 
        "duration": 60
    }
    
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("⏳ Envoi de la requête...")
        response = requests.post(
            SEEDANCE_ENDPOINT,
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        print(f"📡 Code de réponse: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération SEEDANCE réussie !")
            print(f"🎬 Résultat: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Erreur génération: {response.status_code}")
            print(f"📝 Détails: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La génération prend plus de temps que prévu")
        return False
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def main():
    print("🎭 Test de l'intégration SEEDANCE dans FRIDAY")
    print("=" * 50)
    
    # Test du statut
    if not test_seedance_status():
        print("❌ Impossible de continuer - service non disponible")
        return
    
    # Test de génération
    print("\n" + "=" * 50)
    test_result = test_seedance_generate()
    
    print("\n" + "=" * 50)
    if test_result:
        print("🎉 Tests SEEDANCE réussis ! L'intégration fonctionne.")
    else:
        print("⚠️ Problème détecté dans l'intégration SEEDANCE.")
    
    print("\n💡 Vous pouvez maintenant tester l'interface sur http://localhost:5174/")
    print("   1. Sélectionnez 'Animation SEEDANCE'")
    print("   2. Remplissez le formulaire")
    print("   3. Cliquez sur 'Générer'")

if __name__ == "__main__":
    main()
