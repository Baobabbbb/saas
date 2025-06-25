"""
Test de l'endpoint CrewAI depuis le serveur FastAPI
"""

import requests
import json
import time

def test_crewai_endpoint():
    """Test de l'endpoint /api/animations/test-crewai"""
    
    print("🧪 === TEST ENDPOINT CRÉAWAI ===")
    
    url = "http://127.0.0.1:8000/api/animations/test-crewai"
    
    payload = {
        "story": "Une petite fille découvre un château magique dans la forêt. Elle rencontre un dragon gentil qui garde des trésors colorés."
    }
    
    print(f"📡 URL: {url}")
    print(f"📝 Histoire: {payload['story']}")
    
    try:
        print("🚀 Envoi de la requête...")
        start_time = time.time()
        
        response = requests.post(url, json=payload, timeout=60)
        
        elapsed_time = time.time() - start_time
        
        print(f"⏱️  Temps de réponse: {elapsed_time:.1f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Réponse reçue avec succès !")
            
            if result.get('status') == 'test_completed':
                print("🎯 Test CrewAI terminé avec succès")
                
                if result.get('result', {}).get('status') == 'success':
                    print("🎬 Pipeline CrewAI opérationnel")
                    print(f"👥 Agents: {result['result'].get('agents_count', 0)}")
                    print(f"📋 Tâches: {result['result'].get('tasks_count', 0)}")
                    print(f"⚡ Temps exécution: {result['result'].get('execution_time', 0):.1f}s")
                else:
                    print("❌ Erreur dans le pipeline CrewAI")
                    print(f"Erreur: {result['result'].get('error', 'Inconnue')}")
            else:
                print("⚠️ Test non terminé")
                print(f"Résultat: {result}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Détail: {error_data.get('detail', 'Erreur inconnue')}")
            except:
                print(f"Réponse brute: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Le serveur met trop de temps à répondre")
    except requests.exceptions.ConnectionError:
        print("🔌 Erreur de connexion - Le serveur n'est peut-être pas démarré")
        print("💡 Démarrez le serveur avec: python main.py")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_story_animation_endpoint():
    """Test de l'endpoint /api/animations/generate-story"""
    
    print("\n🎬 === TEST ENDPOINT ANIMATION NARRATIVE ===")
    
    url = "http://127.0.0.1:8000/api/animations/generate-story"
    
    payload = {
        "story": "Un petit ourson découvre une rivière magique où les poissons brillent comme des étoiles. Il apprend à nager avec eux.",
        "style_preferences": {
            "style": "cartoon mignon et coloré",
            "mood": "merveilleux et doux",
            "target_age": "3-6 ans"
        }
    }
    
    print(f"📡 URL: {url}")
    print(f"📝 Histoire: {payload['story']}")
    print(f"🎨 Style: {payload['style_preferences']}")
    
    try:
        print("🚀 Envoi de la requête (génération complète)...")
        start_time = time.time()
        
        # Note: Cette requête peut prendre plus de temps car elle inclut la génération vidéo
        response = requests.post(url, json=payload, timeout=120)
        
        elapsed_time = time.time() - start_time
        
        print(f"⏱️  Temps de réponse: {elapsed_time:.1f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Animation générée avec succès !")
            
            print(f"🎥 Vidéo: {result.get('video_url', 'N/A')}")
            print(f"📊 Scènes: {result.get('scenes_count', 0)}")
            print(f"⏱️  Durée: {result.get('total_duration', 0)}s")
            print(f"🕒 Temps génération: {result.get('generation_time', 0):.1f}s")
            
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Détail: {error_data.get('detail', 'Erreur inconnue')}")
            except:
                print(f"Réponse brute: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La génération prend plus de 2 minutes")
    except requests.exceptions.ConnectionError:
        print("🔌 Erreur de connexion - Le serveur n'est peut-être pas démarré")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 TESTS ENDPOINTS CRÉAWAI")
    print("=" * 50)
    
    # Test 1: Test simple du pipeline
    test_crewai_endpoint()
    
    # Test 2: Génération complète (optionnel, prend plus de temps)
    print("\n" + "=" * 50)
    user_input = input("Voulez-vous tester la génération complète ? (y/N): ")
    if user_input.lower() in ['y', 'yes', 'oui']:
        test_story_animation_endpoint()
    else:
        print("⏭️  Test de génération complète ignoré")
    
    print("\n🎯 Tests terminés")
