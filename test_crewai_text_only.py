#!/usr/bin/env python3
"""
Test pour valider que CrewAI améliore UNIQUEMENT le texte 
sans interférer avec le flux technique (images Stable Diffusion, seeds, etc.)
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/generate_comic/"

def test_crewai_text_only_enhancement():
    """Test que CrewAI améliore seulement le texte, pas le flux technique"""
    print("🧪 Test CrewAI - Amélioration textuelle uniquement")
    print("=" * 60)
    
    # Données de test avec paramètres spécifiques
    test_data = {
        "style": "manga",  # Style spécifique pour vérifier la cohérence
        "hero_name": "Akira",
        "story_type": "science-fiction",
        "custom_request": "Une histoire dans un Tokyo futuriste avec des robots et des néons",
        "num_images": 3,
        "avatar_type": "emoji",
        "emoji": "👦"
    }
    
    print("📊 Données de test :")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print()
    
    # Test avec CrewAI (endpoint principal)
    print("🚀 Test avec CrewAI activé...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            data=test_data,
            timeout=300
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Durée d'exécution : {duration:.2f} secondes")
        print(f"📈 Status code : {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Génération réussie !")
            print(f"📚 Titre : {result.get('title', 'N/A')}")
            print(f"📄 Nombre de pages : {len(result.get('pages', []))}")
            print(f"🤖 Amélioré par CrewAI : {result.get('enhanced_by_crewai', 'N/A')}")
            
            print("\n📖 Pages générées :")
            for i, page in enumerate(result.get('pages', []), 1):
                print(f"  Page {i}: {page}")
            
            # Vérifications techniques importantes
            print("\n🔍 Vérifications techniques :")
            
            # 1. Nombre de pages correct
            expected_pages = test_data["num_images"]
            actual_pages = len(result.get('pages', []))
            if actual_pages == expected_pages:
                print(f"✅ Nombre de pages : {actual_pages}/{expected_pages}")
            else:
                print(f"❌ Nombre de pages : {actual_pages}/{expected_pages}")
            
            # 2. Format des fichiers (doit être le système classique, pas CrewAI)
            pages = result.get('pages', [])
            uses_classic_format = any('page_' in page for page in pages)
            uses_crewai_format = any('enhanced_scene_' in page for page in pages)
            
            if uses_classic_format and not uses_crewai_format:
                print("✅ Format de fichiers : Système classique (correct)")
            elif uses_crewai_format:
                print("❌ Format de fichiers : CrewAI (incorrect - doit utiliser le système classique)")
            else:
                print("⚠️  Format de fichiers : Format inattendu")
            
            # 3. CrewAI utilisé pour le texte uniquement
            if result.get('enhanced_by_crewai'):
                print("✅ CrewAI utilisé pour l'amélioration textuelle")
            else:
                print("⚠️  CrewAI non utilisé (possible fallback)")
            
            # 4. Structure du titre (doit être améliorée par CrewAI)
            title = result.get('title', '')
            if title and len(title) > 10:  # Titre enrichi
                print(f"✅ Titre enrichi : '{title}'")
            else:
                print(f"⚠️  Titre basique : '{title}'")
            
            return {
                "success": True,
                "crewai_used": result.get('enhanced_by_crewai', False),
                "correct_page_count": actual_pages == expected_pages,
                "uses_classic_system": uses_classic_format and not uses_crewai_format,
                "title": title,
                "duration": duration
            }
            
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Détails : {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return {"success": False, "error": str(e)}

def test_server_health():
    """Test de santé du serveur"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Test du nouveau système CrewAI (amélioration textuelle uniquement)")
    print("=" * 70)
    
    # Vérification serveur
    if not test_server_health():
        print("❌ Serveur non accessible")
        print("💡 Lancez: cd saas && uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    print("✅ Serveur accessible\n")
    
    # Test principal
    result = test_crewai_text_only_enhancement()
    
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DU TEST")
    print("=" * 70)
    
    if result.get("success"):
        print("🎉 Test global : RÉUSSI")
        
        # Analyse détaillée
        if result.get("crewai_used"):
            print("✅ CrewAI : Utilisé pour l'amélioration textuelle")
        else:
            print("⚠️  CrewAI : Non utilisé (fallback possible)")
        
        if result.get("correct_page_count"):
            print("✅ Pages : Nombre correct")
        else:
            print("❌ Pages : Nombre incorrect")
        
        if result.get("uses_classic_system"):
            print("✅ Système : Flux technique classique conservé")
        else:
            print("❌ Système : Flux technique modifié par CrewAI")
        
        print(f"📚 Titre généré : '{result.get('title', 'N/A')}'")
        print(f"⏱️  Durée : {result.get('duration', 0):.1f}s")
        
        # Conclusion
        if (result.get("uses_classic_system") and 
            result.get("correct_page_count")):
            print("\n🎯 CONCLUSION : L'architecture est CORRECTE")
            print("   CrewAI améliore le texte sans interférer avec le système technique")
        else:
            print("\n⚠️  CONCLUSION : Problèmes détectés")
            print("   CrewAI interfère encore avec le flux technique")
            
    else:
        print("💥 Test global : ÉCHOUÉ")
        print(f"   Erreur : {result.get('error', 'Inconnue')}")
        
    print()
