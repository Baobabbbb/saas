#!/usr/bin/env python3
"""
Test de génération de comptine sans timeout
Vérifie que la génération peut maintenant durer aussi longtemps que nécessaire
"""

import requests
import time
import sys

def test_no_timeout_generation():
    """Test d'une génération sans timeout"""
    
    base_url = "http://localhost:8000"
    
    print("⏰ TEST GÉNÉRATION SANS TIMEOUT")
    print("=" * 40)
    
    # Génération d'une comptine
    print("\n1. 🎵 Lancement génération comptine...")
    
    payload = {
        "rhyme_type": "animal",
        "custom_request": "Une comptine sur un éléphant qui danse",
        "generate_music": True,
        "custom_style": "comptine joyeuse avec sons d'animaux"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/generate_rhyme/",
            json=payload,
            timeout=60  # Juste pour éviter blocage HTTP, pas pour la génération
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                task_id = result.get('task_id')
                print(f"   ✅ Paroles générées: {result.get('title')}")
                print(f"   🎵 Musique lancée: {task_id}")
                print(f"   📊 Statut initial: {result.get('music_status')}")
                
                if task_id:
                    # Polling sans limite de temps
                    print(f"\n2. 🔄 Polling sans limite de temps...")
                    
                    check_count = 0
                    last_status = None
                    
                    while True:
                        check_count += 1
                        elapsed = time.time() - start_time
                        
                        print(f"   🔄 Vérification {check_count} (⏱️ {elapsed:.0f}s)")
                        
                        try:
                            status_response = requests.get(
                                f"{base_url}/check_task_status/{task_id}",
                                timeout=10
                            )
                            
                            if status_response.status_code == 200:
                                status = status_response.json()
                                current_status = status.get('task_status')
                                
                                if current_status != last_status:
                                    print(f"      📊 Nouveau statut: {current_status}")
                                    last_status = current_status
                                
                                if current_status == "completed":
                                    audio_url = status.get('audio_url')
                                    if audio_url:
                                        print(f"\n✅ SUCCÈS ! Comptine générée en {elapsed:.0f} secondes")
                                        print(f"   🎵 Audio: {audio_url[:50]}...")
                                        
                                        # Test d'accès à l'audio
                                        try:
                                            head_response = requests.head(audio_url, timeout=10)
                                            if head_response.status_code == 200:
                                                print(f"   ✅ Audio accessible !")
                                            else:
                                                print(f"   ⚠️ Audio non accessible (status: {head_response.status_code})")
                                        except Exception as e:
                                            print(f"   ⚠️ Erreur test audio: {e}")
                                        
                                        return True
                                    else:
                                        print(f"\n⚠️ Terminé sans URL audio après {elapsed:.0f}s")
                                        return False
                                        
                                elif current_status in ["failed", "error"]:
                                    print(f"\n❌ Génération échouée après {elapsed:.0f}s")
                                    print(f"   Erreur: {status.get('error', 'Erreur inconnue')}")
                                    return False
                            else:
                                print(f"      ⚠️ Erreur HTTP: {status_response.status_code}")
                        
                        except Exception as e:
                            print(f"      ⚠️ Erreur requête: {e}")
                        
                        # Attendre avant la prochaine vérification
                        time.sleep(15)  # Vérifier toutes les 15 secondes
                        
                        # Affichage de progression périodique
                        if check_count % 4 == 0:  # Toutes les minutes
                            print(f"   📊 Toujours en cours... ({elapsed:.0f}s écoulées)")
                
                else:
                    print(f"   ❌ Pas de task_id reçu")
                    return False
            else:
                print(f"   ❌ Erreur génération: {result.get('error')}")
                return False
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎵 Ce test va attendre jusqu'à la fin de la génération Udio")
    print("   (Peut prendre plusieurs minutes)")
    print("   Appuyez sur Ctrl+C pour annuler")
    
    try:
        success = test_no_timeout_generation()
        
        if success:
            print(f"\n🎉 GÉNÉRATION RÉUSSIE SANS TIMEOUT !")
            print(f"   ✅ Les timeouts ont été correctement supprimés")
            print(f"   ✅ Udio peut maintenant générer sans limite de temps")
        else:
            print(f"\n⚠️ Génération non terminée ou échouée")
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
