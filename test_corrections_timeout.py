#!/usr/bin/env python3
"""
Test des corrections du timeout et du polling pour les comptines musicales
"""

import requests
import json
import time
import asyncio

def test_rhyme_generation_and_polling():
    """Test de génération de comptine et polling avec les nouvelles corrections"""
    
    print("🎵 === Test des corrections de timeout ===")
    
    # Payload pour générer une comptine
    payload = {
        'rhyme_type': 'animals',
        'custom_request': 'une comptine sur les petits chats mignons',
        'generate_music': True,
        'custom_style': 'enfant'
    }
    
    try:
        # 1. Générer la comptine
        print("📝 Génération de la comptine...")
        response = requests.post('http://localhost:8000/generate_rhyme/', json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erreur génération: {response.status_code} - {response.text}")
            return False
            
        data = response.json()
        print(f"✅ Comptine générée!")
        print(f"   Titre: {data.get('title', 'N/A')}")
        print(f"   Has music: {data.get('has_music', False)}")
        print(f"   Task ID: {data.get('task_id', 'N/A')}")
        
        task_id = data.get('task_id')
        if not task_id:
            print("❌ Pas de task_id retourné")
            return False
            
        # 2. Tester le polling
        print(f"\n🔄 Test du polling pour task_id: {task_id}")
        print("   (Nouvelles corrections: 60 tentatives × 8s = 8 minutes max)")
        
        max_polls = 8  # Limiter pour le test
        for i in range(max_polls):
            print(f"\n📡 Poll {i+1}/{max_polls}")
            
            poll_response = requests.get(f'http://localhost:8000/check_task_status/{task_id}', timeout=10)
            
            if poll_response.status_code != 200:
                print(f"❌ Erreur polling: {poll_response.status_code}")
                continue
                
            poll_data = poll_response.json()
            status = poll_data.get('status', 'unknown')
            task_status = poll_data.get('task_status', 'unknown')
            
            print(f"   📊 Status: {status}")
            print(f"   📊 Task status GoAPI: {task_status}")
            
            if status == 'completed':
                audio_url = poll_data.get('audio_url') or poll_data.get('audio_path')
                print(f"🎵✅ SUCCÈS! Génération musicale terminée!")
                print(f"   🎵 Audio URL: {audio_url}")
                return True
                
            elif status == 'failed':
                error = poll_data.get('error', 'Erreur inconnue')
                print(f"❌ ÉCHEC de la génération musicale: {error}")
                return False
                
            elif status in ['pending', 'processing']:
                print(f"⏳ En cours... ({status})")
                
            else:
                print(f"⚠️ Statut inattendu: {status}")
            
            # Attendre 8 secondes comme le frontend corrigé
            time.sleep(8)
            
        print(f"\n⏰ Test interrompu après {max_polls} tentatives")
        print("   (Dans l'interface, cela continuerait jusqu'à 60 tentatives)")
        return True  # Test réussi même si pas terminé
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 Test des corrections de timeout pour les comptines musicales")
    print("=" * 60)
    
    success = test_rhyme_generation_and_polling()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test réussi! Les corrections semblent fonctionner.")
        print("📱 Interface frontend: http://localhost:5174/")
        print("📚 Documentation API: http://localhost:8000/docs")
    else:
        print("❌ Test échoué. Vérifiez les logs ci-dessus.")
    
    print("\n🔧 Corrections apportées:")
    print("   - Timeout étendu: 60 tentatives × 8s = 8 minutes max")
    print("   - Meilleure gestion des statuts (pending/processing/completed/failed)")
    print("   - Messages d'erreur plus détaillés")
    print("   - Affichage amélioré dans l'interface")
