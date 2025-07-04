#!/usr/bin/env python3
"""
Diagnostic spécifique pour le problème d'audio 0 seconde
"""

import requests
import json
import time

def diagnose_audio_issue():
    """Diagnostic pour comprendre pourquoi l'audio fait 0 seconde"""
    
    print("🔍 === Diagnostic audio 0 seconde ===")
    
    # Test simple
    payload = {
        'rhyme_type': 'animal',
        'custom_request': 'chat mignon',
        'generate_music': True,
        'fast_mode': True
    }
    
    try:
        print("📝 Génération comptine...")
        response = requests.post('http://localhost:8000/generate_rhyme/', json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            
            print(f"✅ Task ID: {task_id}")
            
            if task_id:
                # Test immédiat du polling
                print("\\n🔄 Test polling...")
                
                # Poll 1 - état initial
                poll1 = requests.get(f'http://localhost:8000/check_task_status/{task_id}')
                if poll1.status_code == 200:
                    data1 = poll1.json()
                    print(f"Poll 1: {data1.get('status')} | {data1.get('task_status')}")
                    
                    # Attendre et repoll
                    time.sleep(10)
                    
                    # Poll 2 - après attente
                    poll2 = requests.get(f'http://localhost:8000/check_task_status/{task_id}')
                    if poll2.status_code == 200:
                        data2 = poll2.json()
                        print(f"Poll 2: {data2.get('status')} | {data2.get('task_status')}")
                        
                        # Vérifier si completed mais sans audio
                        if data2.get('status') == 'completed':
                            audio_url = data2.get('audio_url')
                            if not audio_url:
                                print("\\n❌ PROBLÈME IDENTIFIÉ:")
                                print("   - Status: completed")
                                print("   - Mais audio_url manquant!")
                                print(f"   - Données: {json.dumps(data2, indent=2)}")
                                
                                # Le problème est probablement dans l'extraction de l'URL
                                return "NO_AUDIO_URL"
                            else:
                                print(f"\\n🎵 Audio URL trouvée: {audio_url}")
                                
                                # Tester l'URL
                                try:
                                    head_response = requests.head(audio_url, timeout=5)
                                    print(f"   Status HTTP: {head_response.status_code}")
                                    
                                    if head_response.status_code == 200:
                                        content_length = head_response.headers.get('content-length', '0')
                                        print(f"   Taille fichier: {content_length} bytes")
                                        
                                        if content_length == '0':
                                            print("   ❌ PROBLÈME: Fichier audio vide (0 bytes)!")
                                            return "EMPTY_AUDIO_FILE"
                                        else:
                                            print("   ✅ Fichier audio semble correct")
                                            return "AUDIO_OK"
                                    else:
                                        print(f"   ❌ URL audio inaccessible: {head_response.status_code}")
                                        return "AUDIO_URL_ERROR"
                                        
                                except Exception as e:
                                    print(f"   ❌ Erreur test URL: {e}")
                                    return "AUDIO_TEST_ERROR"
                        else:
                            print(f"   Status: {data2.get('status')} (pas encore completed)")
                            return "STILL_PROCESSING"
                else:
                    print(f"❌ Erreur poll 2: {poll2.status_code}")
                    return "POLL_ERROR"
            else:
                print("❌ Pas de task_id")
                return "NO_TASK_ID"
        else:
            print(f"❌ Erreur génération: {response.status_code}")
            return "GENERATION_ERROR"
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return "EXCEPTION"

if __name__ == "__main__":
    result = diagnose_audio_issue()
    
    print(f"\\n🎯 Résultat diagnostic: {result}")
    
    if result == "NO_AUDIO_URL":
        print("\\n🔧 Solution suggérée:")
        print("   - Vérifier l'extraction de l'URL audio dans diffrhythm_service.py")
        print("   - Vérifier la structure de réponse GoAPI")
    elif result == "EMPTY_AUDIO_FILE":
        print("\\n🔧 Solution suggérée:")
        print("   - Le fichier audio est généré mais vide")
        print("   - Vérifier les paramètres envoyés à GoAPI")
        print("   - Possiblement un problème avec les paroles ou le style")
