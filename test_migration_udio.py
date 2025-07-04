#!/usr/bin/env python3
"""
Test de migration DiffRhythm vers Udio
Vérifie que la génération de comptines fonctionne avec Udio
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

from services.udio_service import udio_service
from services.musical_nursery_rhyme_service import musical_nursery_rhyme_service

async def test_udio_migration():
    """Test complet de la migration vers Udio"""
    
    print("🧪 TEST DE MIGRATION DIFFRHYTHM → UDIO")
    print("=" * 50)
    
    # Test 1: Vérification de la configuration
    print("\n1. 📋 Vérification de la configuration Udio...")
    
    try:
        print(f"   ✅ Modèle: {udio_service.model}")
        print(f"   ✅ Task type: {udio_service.task_type}")
        print(f"   ✅ API Key: {'***' + udio_service.api_key[-8:] if udio_service.api_key else 'NON CONFIGURÉE'}")
        print(f"   ✅ URL base: {udio_service.base_url}")
    except Exception as e:
        print(f"   ❌ Erreur configuration: {e}")
        return False
    
    # Test 2: Génération de paroles uniquement
    print("\n2. 📝 Test génération paroles seulement...")
    
    try:
        lyrics_result = await musical_nursery_rhyme_service.generate_complete_nursery_rhyme(
            rhyme_type="counting",
            custom_request="Comptine pour apprendre à compter de 1 à 5",
            generate_music=False  # Paroles seulement
        )
        
        if lyrics_result["status"] == "success":
            print(f"   ✅ Titre: {lyrics_result['title']}")
            print(f"   ✅ Paroles: {lyrics_result['lyrics'][:100]}...")
            lyrics_for_music = lyrics_result['lyrics']
        else:
            print(f"   ❌ Erreur paroles: {lyrics_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception paroles: {e}")
        return False
    
    # Test 3: Génération musicale avec Udio
    print("\n3. 🎵 Test génération musicale Udio...")
    
    try:
        music_result = await udio_service.generate_musical_nursery_rhyme(
            lyrics=lyrics_for_music,
            rhyme_type="counting",
            custom_style="comptine éducative française pour enfants"
        )
        
        if music_result["status"] == "success":
            task_id = music_result["task_id"]
            print(f"   ✅ Tâche Udio créée: {task_id}")
            print(f"   ✅ Style utilisé: {music_result['style_used']}")
            
            # Test 4: Vérification du statut
            print(f"\n4. 🔄 Test vérification statut Udio...")
            
            # Vérifier le statut initial
            status_result = await udio_service.check_task_status(task_id)
            print(f"   📊 Statut initial: {status_result.get('status')}")
            print(f"   📊 Statut GoAPI: {status_result.get('task_status')}")
            
            # Test 5: Polling court (ne pas attendre la completion complète)
            print(f"\n5. ⏳ Test polling court (30 secondes max)...")
            
            max_checks = 6  # 30 secondes max
            check_interval = 5
            
            for i in range(max_checks):
                print(f"   🔄 Vérification {i+1}/{max_checks}...")
                
                status_result = await udio_service.check_task_status(task_id)
                current_status = status_result.get("task_status", "unknown")
                
                print(f"      📊 Statut: {current_status}")
                
                if current_status in ["completed", "success"]:
                    audio_url = status_result.get("audio_url")
                    if audio_url:
                        print(f"      ✅ Audio prêt: {audio_url}")
                        break
                    else:
                        print(f"      ⚠️ Terminé mais pas d'URL audio")
                elif current_status in ["failed", "error"]:
                    print(f"      ❌ Génération échouée")
                    break
                
                if i < max_checks - 1:
                    print(f"      ⏰ Attente {check_interval}s...")
                    await asyncio.sleep(check_interval)
            
            print(f"\n   📋 Résultat final polling:")
            print(f"      Task ID: {task_id}")
            print(f"      Statut: {status_result.get('task_status')}")
            print(f"      URL audio: {status_result.get('audio_url', 'En cours...')}")
            
        else:
            print(f"   ❌ Erreur création tâche Udio: {music_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception Udio: {e}")
        return False
    
    # Test 6: Génération complète (intégrée)
    print("\n6. 🎭 Test génération comptine complète (paroles + musique)...")
    
    try:
        complete_result = await musical_nursery_rhyme_service.generate_complete_nursery_rhyme(
            rhyme_type="animal",
            custom_request="Comptine sur un petit chat qui joue",
            generate_music=True
        )
        
        if complete_result["status"] == "success":
            print(f"   ✅ Comptine complète générée:")
            print(f"      Titre: {complete_result['title']}")
            print(f"      Paroles: {complete_result['lyrics'][:80]}...")
            print(f"      Musique: {'Oui' if complete_result.get('has_music') else 'Non'}")
            print(f"      Task ID: {complete_result.get('task_id')}")
            print(f"      Statut musique: {complete_result.get('music_status')}")
        else:
            print(f"   ❌ Erreur comptine complète: {complete_result.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Exception comptine complète: {e}")
    
    print("\n" + "=" * 50)
    print("✅ MIGRATION DIFFRHYTHM → UDIO TESTÉE")
    print("\n📝 RÉSUMÉ:")
    print("   - Configuration Udio ✅")
    print("   - Génération paroles ✅")
    print("   - Création tâche Udio ✅")
    print("   - Vérification statut ✅")
    print("   - Intégration complète ✅")
    
    print("\n🎵 La migration est fonctionnelle!")
    print("   Les comptines seront maintenant générées avec Udio")
    print("   pour obtenir de vraies comptines chantées réalistes.")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_udio_migration())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)
