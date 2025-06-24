#!/usr/bin/env python3
"""
Test de comparaison de vitesse - Mode normal vs Mode rapide
"""

import requests
import time
import asyncio
import json

def test_speed_comparison():
    """Comparer les vitesses entre mode normal et mode rapide"""
    
    print("⚡ Test de Comparaison de Vitesse")
    print("=" * 50)
    
    # Paramètres de test
    test_params = {
        "style": "cartoon",
        "theme": "animals",
        "orientation": "landscape",
        "prompt": "cute animals playing"
    }
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Mode normal
    print("\n🐌 Test Mode NORMAL...")
    print("-" * 30)
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{base_url}/api/animations/generate",
            json=test_params,
            timeout=600
        )
        normal_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mode Normal réussi en {normal_time:.1f}s")
            print(f"   ID: {data.get('id')}")
            print(f"   Titre: {data.get('title')}")
            print(f"   Description: {data.get('description')}")
            
            # Analyser le mode utilisé
            if 'cache' in data.get('description', '').lower():
                print("   📦 Résultat depuis le cache")
            elif 'simulation' in data.get('description', '').lower():
                print("   🔄 Mode simulation")
            else:
                print("   🎬 Génération réelle Runway")
        else:
            print(f"❌ Erreur mode normal: {response.status_code}")
            normal_time = None
            
    except Exception as e:
        print(f"❌ Erreur mode normal: {e}")
        normal_time = None
    
    # Petite pause
    time.sleep(2)
    
    # Test 2: Mode rapide
    print("\n⚡ Test Mode RAPIDE...")
    print("-" * 30)
    
    # Modifier légèrement les paramètres pour éviter le cache
    test_params_fast = test_params.copy()
    test_params_fast["prompt"] = "cute animals playing happily"
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{base_url}/api/animations/generate-fast",
            json=test_params_fast,
            timeout=600
        )
        fast_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mode Rapide réussi en {fast_time:.1f}s")
            print(f"   ID: {data.get('id')}")
            print(f"   Titre: {data.get('title')}")
            print(f"   Description: {data.get('description')}")
            
            # Analyser le mode utilisé
            if 'cache' in data.get('description', '').lower():
                print("   📦 Résultat depuis le cache")
            elif 'simulation' in data.get('description', '').lower():
                print("   🔄 Mode simulation")
            elif 'optimisée' in data.get('description', '').lower():
                print("   ⚡ Mode optimisé Runway")
            else:
                print("   🎬 Génération Runway")
        else:
            print(f"❌ Erreur mode rapide: {response.status_code}")
            fast_time = None
            
    except Exception as e:
        print(f"❌ Erreur mode rapide: {e}")
        fast_time = None
    
    # Comparaison
    print(f"\n📊 Résultats de Comparaison")
    print("=" * 40)
    
    if normal_time and fast_time:
        improvement = ((normal_time - fast_time) / normal_time) * 100
        print(f"   Mode Normal: {normal_time:.1f}s")
        print(f"   Mode Rapide: {fast_time:.1f}s")
        print(f"   Amélioration: {improvement:.1f}% plus rapide")
        
        if improvement > 0:
            print("   🎉 Le mode rapide est plus efficace!")
        else:
            print("   📝 Les deux modes ont des performances similaires")
    else:
        print("   ⚠️ Impossible de comparer - certains tests ont échoué")

def test_cache_effectiveness():
    """Tester l'efficacité du cache"""
    
    print(f"\n💾 Test d'Efficacité du Cache")
    print("-" * 30)
    
    test_params = {
        "style": "fairy_tale",
        "theme": "magic",
        "orientation": "portrait",
        "prompt": "magical fairy in enchanted forest"
    }
    
    # Premier appel (sans cache)
    print("🔄 Premier appel (sans cache)...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/animations/generate-fast",
            json=test_params,
            timeout=600
        )
        first_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Premier appel: {first_time:.1f}s")
        else:
            print(f"❌ Erreur premier appel: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Erreur premier appel: {e}")
        return
    
    # Deuxième appel (avec cache)
    print("📦 Deuxième appel (avec cache)...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/animations/generate-fast",
            json=test_params,
            timeout=60
        )
        second_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Deuxième appel: {second_time:.1f}s")
            
            if 'cache' in data.get('description', '').lower():
                cache_improvement = ((first_time - second_time) / first_time) * 100
                print(f"📦 Résultat depuis le cache!")
                print(f"⚡ Amélioration cache: {cache_improvement:.1f}% plus rapide")
            else:
                print("⚠️ Cache non utilisé (paramètres différents?)")
        else:
            print(f"❌ Erreur deuxième appel: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur deuxième appel: {e}")

def main():
    """Fonction principale de test"""
    
    print("🚀 Tests d'Optimisation de Vitesse")
    print("=" * 60)
    
    # Vérifier que le serveur est actif
    try:
        response = requests.get("http://127.0.0.1:8000/api/runway/credits", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Statut Runway: {data.get('status')}")
            print(f"💳 Crédits: {'✅' if data.get('credits_available') else '❌'}")
        else:
            print("⚠️ Impossible de vérifier le statut Runway")
    except:
        print("❌ Serveur backend non accessible")
        return
    
    # Tests de vitesse
    test_speed_comparison()
    
    # Tests de cache  
    test_cache_effectiveness()
    
    print(f"\n🎯 Résumé des Optimisations")
    print("=" * 40)
    print("✅ Mode rapide: Résolution réduite, durée plus courte")
    print("✅ Cache intelligent: Évite la régénération")
    print("✅ Timeouts optimisés: Moins d'attente")
    print("✅ Mode asynchrone: Disponible pour le polling")
    print("✅ Prompts optimisés: Plus courts et efficaces")

if __name__ == "__main__":
    main()
