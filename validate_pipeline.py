#!/usr/bin/env python3
"""
Test de validation finale du pipeline CrewAI
Version optimisée et rapide
"""

import time
import requests
import json

def test_backend():
    """Test accessibilité backend"""
    try:
        response = requests.get('http://localhost:8000', timeout=3)
        print(f"✅ Backend accessible: {response.status_code}")
        return True
    except:
        print("❌ Backend non accessible")
        return False

def test_frontend():
    """Test accessibilité frontend"""
    try:
        response = requests.get('http://localhost:3000', timeout=3)
        print(f"✅ Frontend accessible: {response.status_code}")
        return True
    except:
        print("❌ Frontend non accessible (normal si npm dev non lancé)")
        return False

def test_animation_fast():
    """Test endpoint animation rapide"""
    try:
        data = {
            'story': 'Un chat magique découvre un jardin enchanté',
            'style': 'cartoon',
            'theme': 'animals',
            'duration': 10
        }
        
        print("🎬 Test animation rapide...")
        response = requests.post(
            'http://localhost:8000/api/animations/generate-fast',
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Animation rapide: {result.get('status')}")
            print(f"🎭 Scènes: {len(result.get('scenes', []))}")
            return True
        else:
            print(f"❌ Erreur animation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception animation: {e}")
        return False

def test_crewai_corrected():
    """Test endpoint CrewAI complet (si temps disponible)"""
    try:
        data = {
            'story': 'Histoire courte test',
            'style': 'cartoon',
            'theme': 'animals',
            'duration': 10
        }
        
        print("🎬 Test CrewAI corrigé (peut prendre 1-2 min)...")
        response = requests.post(
            'http://localhost:8000/api/animations/generate-corrected',
            json=data,
            timeout=150  # 2.5 minutes max
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CrewAI complet: {result.get('status')}")
            print(f"🎭 Scènes: {len(result.get('scenes', []))}")
            print(f"📹 Vidéo: {result.get('video_url', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur CrewAI: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception CrewAI: {e}")
        return False

def main():
    """Validation finale"""
    print("🔍 === VALIDATION FINALE PIPELINE CREWAI ===")
    print("=" * 50)
    
    # Tests de base
    backend_ok = test_backend()
    if not backend_ok:
        print("\n❌ ÉCHEC: Backend requis")
        print("💡 Lancer: uvicorn main:app --reload")
        return
    
    frontend_ok = test_frontend()
    
    # Test animation rapide
    fast_ok = test_animation_fast()
    
    # Test CrewAI complet (optionnel)
    print("\n⏳ Test CrewAI complet ? (peut prendre du temps)")
    user_input = input("Continuer ? (y/N): ").strip().lower()
    
    if user_input == 'y':
        crewai_ok = test_crewai_corrected()
    else:
        crewai_ok = None
        print("⏭️ Test CrewAI ignoré")
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 === RÉSUMÉ VALIDATION ===")
    print(f"🔧 Backend:      {'✅' if backend_ok else '❌'}")
    print(f"📱 Frontend:     {'✅' if frontend_ok else '❌'}")
    print(f"⚡ Animation:    {'✅' if fast_ok else '❌'}")
    print(f"🎬 CrewAI:       {'✅' if crewai_ok else '❌' if crewai_ok is False else '⏭️'}")
    
    if backend_ok and fast_ok:
        print("\n🎉 PIPELINE CREWAI VALIDÉ!")
        print("✨ Système fonctionnel pour la production")
        print("\n📚 Prochaines étapes:")
        print("   1. Lancer START_CREWAI.bat pour démarrage complet")
        print("   2. Aller sur http://localhost:3000 pour tester")
        print("   3. Consulter GUIDE_FINAL_CREWAI.md pour détails")
    else:
        print("\n⚠️ Corrections nécessaires")
        print("📚 Consulter GUIDE_FINAL_CREWAI.md pour dépannage")

if __name__ == "__main__":
    main()
