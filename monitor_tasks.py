#!/usr/bin/env python3
"""
Surveillance automatique des tâches GoAPI pour identifier le problème audio 0 seconde
"""

import requests
import time
import json

def monitor_task(task_id, max_minutes=10):
    """Surveiller une tâche GoAPI et capturer le moment où elle se termine"""
    
    print(f"🔄 Surveillance de la tâche: {task_id}")
    print(f"⏰ Durée max: {max_minutes} minutes")
    
    max_polls = max_minutes * 6  # 6 polls par minute (toutes les 10s)
    
    for i in range(max_polls):
        try:
            response = requests.get(f'http://localhost:8000/check_task_status/{task_id}', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                task_status = data.get('task_status')
                
                print(f"Poll {i+1:2d}: {status:10} | {task_status:10} | {time.strftime('%H:%M:%S')}")
                
                # Si le statut change
                if status != 'processing':
                    print(f"\\n🎯 CHANGEMENT DÉTECTÉ!")
                    print(f"Status: {status}")
                    print(f"Task status: {task_status}")
                    
                    # Sauvegarder la réponse complète
                    with open(f'task_result_{task_id[:8]}.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"💾 Réponse sauvée dans task_result_{task_id[:8]}.json")
                    
                    # Analyser spécifiquement l'output
                    task_data = data.get('task_data', {})
                    output = task_data.get('output')
                    
                    print(f"\\n🔍 ANALYSE DE L'OUTPUT:")
                    print(f"Type output: {type(output)}")
                    print(f"Output: {output}")
                    
                    if output:
                        if isinstance(output, dict):
                            print(f"Clés dans output: {list(output.keys())}")
                            for key, value in output.items():
                                print(f"  {key}: {value}")
                        elif isinstance(output, list):
                            print(f"Liste avec {len(output)} éléments")
                            for idx, item in enumerate(output):
                                print(f"  [{idx}]: {item}")
                    
                    # Vérifier l'URL audio extraite
                    audio_url = data.get('audio_url')
                    if audio_url:
                        print(f"\\n🎵 URL AUDIO EXTRAITE: {audio_url}")
                        
                        # Tester l'URL
                        try:
                            head_resp = requests.head(audio_url, timeout=5)
                            print(f"Status HTTP: {head_resp.status_code}")
                            print(f"Headers: {dict(head_resp.headers)}")
                            
                            size = head_resp.headers.get('content-length', '0')
                            if size == '0':
                                print("❌ PROBLÈME CONFIRMÉ: Fichier audio vide!")
                            else:
                                print(f"✅ Taille fichier: {size} bytes")
                        except Exception as e:
                            print(f"❌ Erreur test URL: {e}")
                    else:
                        print("❌ PROBLÈME: Aucune URL audio extraite!")
                    
                    return data
                    
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
        time.sleep(10)  # Attendre 10 secondes
        
    print(f"\\n⏰ Timeout après {max_minutes} minutes")
    return None

if __name__ == "__main__":
    # Surveiller les tâches actuelles
    tasks = [
        "c865a3ba-5132-4407-bfcd-87cbe068b8a6",  # Tâche récente (souris)
        "bdf2f3ae-692d-4a76-9711-2104b687cacf"   # Tâche ancienne (chat)
    ]
    
    print("🚀 === Surveillance des tâches GoAPI ===")
    
    for task_id in tasks:
        print(f"\\n{'='*50}")
        result = monitor_task(task_id, max_minutes=5)
        
        if result:
            print(f"✅ Tâche {task_id[:8]} terminée")
            break
        else:
            print(f"⏰ Tâche {task_id[:8]} toujours en cours")
    
    print("\\n🏁 Surveillance terminée")
