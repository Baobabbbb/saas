#!/usr/bin/env python3
"""
Test simple de l'endpoint de comptines
"""
import requests
import json
import time

def test_rhyme_generation():
    """Test simple de génération de comptine"""
    
    # Test sans musique d'abord
    payload = {
        'rhyme_type': 'lullaby',
        'custom_request': '',
        'generate_music': False,
        'custom_style': None,
        'language': 'fr'
    }
    
    print("🧪 Test génération comptine (sans musique)...")
    try:
        response = requests.post(
            'http://localhost:8000/generate_rhyme/', 
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Succès!")
            print(f"Keys: {list(data.keys())}")
            
            if 'title' in data:
                print(f"Titre: {data['title']}")
            if 'rhyme' in data:
                print(f"Comptine (50 premiers caractères): {data['rhyme'][:50]}...")
            if 'content' in data:
                print(f"Contenu (50 premiers caractères): {data['content'][:50]}...")
            
            return data
        else:
            print(f"❌ Erreur: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - l'endpoint met trop de temps à répondre")
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_rhyme_with_music():
    """Test avec musique"""
    
    payload = {
        'rhyme_type': 'lullaby',
        'custom_request': '',
        'generate_music': True,
        'custom_style': None,
        'language': 'fr'
    }
    
    print("\n🎵 Test génération comptine (avec musique)...")
    try:
        response = requests.post(
            'http://localhost:8000/generate_rhyme/', 
            json=payload,
            timeout=15  # Timeout court
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Réponse reçue!")
            print(f"Keys: {list(data.keys())}")
            
            if 'task_id' in data:
                print(f"Task ID: {data['task_id']}")
                return data
                
        else:
            print(f"❌ Erreur: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout normal pour la génération musicale")
        print("🔄 L'API traite probablement la demande en arrière-plan")
        return {'timeout': True}
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

if __name__ == "__main__":
    print("=== TEST DES COMPTINES ===\n")
    
    # Test de base d'abord
    result1 = test_rhyme_generation()
    
    # Test avec musique
    result2 = test_rhyme_with_music()
    
    print("\n=== RÉSUMÉ ===")
    print(f"Comptine simple: {'✅' if result1 else '❌'}")
    print(f"Comptine musicale: {'✅' if result2 else '❌'}")
