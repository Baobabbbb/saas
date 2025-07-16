#!/usr/bin/env python3
"""
🔍 Diagnostic de blocage pour la génération de bande dessinée
Identifie précisément où le processus se bloque
"""

import sys
import os
import requests
import json
import time
import asyncio
from pathlib import Path

# Ajouter saas au path
sys.path.insert(0, str(Path(__file__).parent / "saas"))

def test_configuration():
    """Teste la configuration des clés API"""
    print("🔧 Test de configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    config_issues = []
    
    # Vérifier OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key.startswith("sk-votre"):
        config_issues.append("❌ OPENAI_API_KEY non configurée")
    else:
        print("✅ OpenAI API Key configurée")
    
    # Vérifier Stability AI
    stability_key = os.getenv("STABILITY_API_KEY")
    if not stability_key or stability_key.startswith("sk-votre"):
        config_issues.append("❌ STABILITY_API_KEY non configurée")
    else:
        print("✅ Stability AI API Key configurée")
    
    if config_issues:
        print("\n".join(config_issues))
        return False
    
    return True

def test_openai_connexion():
    """Teste la connexion à OpenAI"""
    print("\n🤖 Test connexion OpenAI...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test simple: dis juste 'OK'"}],
            max_tokens=10,
            timeout=15
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI répond: '{result}'")
        return True
        
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return False

def test_stability_ai_connexion():
    """Teste la connexion à Stability AI"""
    print("\n🎨 Test connexion Stability AI...")
    
    try:
        stability_key = os.getenv("STABILITY_API_KEY")
        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "application/json"
        }
        
        # Test simple de l'API Stability AI
        response = requests.get(
            "https://api.stability.ai/v1/user/account",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stability AI OK - Crédits: {data.get('credits', 'N/A')}")
            return True
        else:
            print(f"❌ Stability AI erreur: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Stability AI: {e}")
        return False

def test_pipeline_etapes():
    """Teste chaque étape du pipeline séparément"""
    print("\n🧪 Test du pipeline par étapes...")
    
    try:
        # Importer le pipeline
        from services.pipeline_dessin_anime_v2 import DessinAnimePipeline
        
        # Créer l'instance
        pipeline = DessinAnimePipeline(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            stability_api_key=os.getenv("STABILITY_API_KEY")
        )
        
        # Test histoire simple
        histoire_test = "Un petit chat découvre un jardin magique."
        
        print("🎬 Test étape 1: Découpage en scènes...")
        
        # Test synchrone du découpage
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        scenes = loop.run_until_complete(
            pipeline.decouper_histoire_en_scenes(histoire_test, 30)
        )
        
        print(f"✅ Découpage OK - {len(scenes)} scènes générées")
        
        # Test génération d'une image en mode démo
        print("🎨 Test étape 2: Génération image démo...")
        
        scene_test = scenes[0] if scenes else {
            "description": "Un petit chat mignon dans un jardin",
            "id": 1
        }
        
        pipeline.mode = "demo"  # Mode démo pour éviter d'utiliser des crédits
        
        # Test avec un seul prompt correct
        prompts_test = [{
            "scene_id": 1,
            "prompt_text": scene_test.get("description", "Un petit chat mignon"),
            "duration": 5,
            "seed": 12345
        }]
        
        clips = loop.run_until_complete(
            pipeline.generer_clips_video(prompts_test)
        )
        
        print(f"✅ Génération clips OK - {len(clips)} clips générés")
        
        loop.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_complete():
    """Teste l'API complète avec un timeout court"""
    print("\n🌐 Test API complète avec timeout...")
    
    payload = {
        "story": "Test rapide: un petit oiseau vole.",
        "duration": 30,
        "style": "cartoon",
        "theme": "test",
        "mode": "demo"
    }
    
    try:
        print("📤 Envoi requête...")
        response = requests.post(
            "http://localhost:8000/generate_animation/",
            json=payload,
            timeout=60  # 1 minute max
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API répond correctement!")
            print(f"   Status: {result.get('status')}")
            print(f"   Scènes: {len(result.get('scenes', []))}")
            print(f"   Clips: {len(result.get('clips', []))}")
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT - L'API met plus de 60s à répondre")
        print("   → Ceci explique le blocage en chargement")
        return False
        
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC DE BLOCAGE - BANDE DESSINÉE")
    print("=" * 60)
    
    # Test 1: Configuration
    if not test_configuration():
        print("\n❌ PROBLÈME: Configuration incomplète")
        print("   → Configurer les clés API dans le fichier .env")
        return
    
    # Test 2: Connexions API
    openai_ok = test_openai_connexion()
    stability_ok = test_stability_ai_connexion()
    
    if not openai_ok:
        print("\n❌ PROBLÈME: OpenAI inaccessible")
        print("   → Vérifier la clé API OpenAI et la connexion internet")
        return
    
    if not stability_ok:
        print("\n⚠️ ATTENTION: Stability AI inaccessible")
        print("   → Mode démo uniquement disponible")
    
    # Test 3: Pipeline interne
    if not test_pipeline_etapes():
        print("\n❌ PROBLÈME: Pipeline interne défaillant")
        print("   → Erreur dans le code de génération")
        return
    
    # Test 4: API complète
    if not test_api_complete():
        print("\n❌ PROBLÈME: API bloque ou timeout")
        print("   → Processus trop long ou boucle infinie")
        return
    
    print("\n✅ DIAGNOSTIC COMPLET: Tout fonctionne normalement")
    print("   → Le blocage peut être dû à:")
    print("     • Requête trop complexe")
    print("     • Mode production trop lent")
    print("     • Problème réseau temporaire")

if __name__ == "__main__":
    main()
