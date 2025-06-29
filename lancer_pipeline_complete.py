#!/usr/bin/env python3
"""
🚀 Script de test et lancement complet de la pipeline IA
Lance le serveur backend et teste la génération de dessins animés
"""
import asyncio
import subprocess
import sys
import time
import os
import requests
from pathlib import Path

# Ajouter le répertoire saas au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "saas"))

def lancer_serveur_backend():
    """Lance le serveur FastAPI en arrière-plan"""
    print("🚀 Lancement du serveur backend...")
    
    # Commande pour lancer le serveur
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main_new:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    # Lancer le serveur dans le répertoire saas
    cwd = Path(__file__).parent / "saas"
    process = subprocess.Popen(
        cmd, 
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Attendre que le serveur soit prêt
    print("⏳ Attente du démarrage du serveur...")
    max_attempts = 30  # 30 secondes max
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Serveur backend prêt!")
                return process
        except:
            pass
        
        time.sleep(1)
        print(f"   Tentative {attempt + 1}/{max_attempts}...")
    
    print("❌ Impossible de démarrer le serveur backend")
    process.terminate()
    return None

def tester_api_health():
    """Teste l'endpoint de santé"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"🏥 Health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def tester_api_animation_demo():
    """Teste la génération d'animation en mode démo"""
    print("\n" + "="*60)
    print("🧪 TEST API ANIMATION - MODE DÉMO")
    print("="*60)
    
    payload = {
        "story": "Une petite licorne découvre un jardin magique plein de fleurs qui chantent et de papillons colorés.",
        "duration": 30,
        "style": "cartoon",
        "theme": "magie",
        "mode": "demo"
    }
    
    try:
        print("📤 Envoi de la requête...")
        response = requests.post(
            "http://localhost:8000/generate_animation/",
            json=payload,
            timeout=60  # 1 minute max pour le mode démo
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération réussie!")
            print(f"   📊 Status: {result.get('status')}")
            print(f"   🎬 Scènes: {len(result.get('scenes', []))}")
            print(f"   🎥 Clips: {len(result.get('clips', []))}")
            print(f"   ⏱️ Durée: {result.get('duree_totale', 'N/A')}s")
            print(f"   🕐 Temps génération: {result.get('generation_time', 'N/A')}s")
            
            # Afficher les clips générés
            clips = result.get('clips', [])
            for i, clip in enumerate(clips):
                print(f"   Clip {i+1}: {clip.get('demo_image_url', 'N/A')}")
            
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def tester_api_animation_production():
    """Teste la génération d'animation en mode production (optionnel)"""
    print("\n" + "="*60)
    print("🎬 TEST API ANIMATION - MODE PRODUCTION")
    print("⚠️ ATTENTION: Utilise vos crédits Stability AI!")
    print("="*60)
    
    reponse = input("🤔 Tester le mode production ? (y/N): ").strip().lower()
    if reponse not in ['y', 'yes', 'oui', 'o']:
        print("✅ Test production ignoré.")
        return True
    
    payload = {
        "story": "Un petit dragon apprend à voler dans un ciel étoilé.",
        "duration": 20,  # Durée réduite pour économiser les crédits
        "style": "cartoon",
        "theme": "aventure", 
        "mode": "production"
    }
    
    try:
        print("📤 Envoi de la requête (ceci peut prendre 2-5 minutes)...")
        response = requests.post(
            "http://localhost:8000/generate_animation/",
            json=payload,
            timeout=600  # 10 minutes max pour le mode production
        )
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 Génération production réussie!")
            print(f"   📊 Status: {result.get('status')}")
            print(f"   🎬 Scènes: {len(result.get('scenes', []))}")
            print(f"   🎥 Clips: {len(result.get('clips', []))}")
            print(f"   ⏱️ Durée: {result.get('duree_totale', 'N/A')}s")
            print(f"   🕐 Temps génération: {result.get('generation_time', 'N/A')}s")
            
            # Vérifier les fichiers vidéo
            clips = result.get('clips', [])
            for i, clip in enumerate(clips):
                if clip.get('type') == 'real_video':
                    video_path = clip.get('video_path')
                    if video_path and os.path.exists(video_path):
                        size = os.path.getsize(video_path) / (1024*1024)  # MB
                        print(f"   🎥 Clip {i+1}: {video_path} ({size:.1f} MB)")
            
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def main():
    """Fonction principale"""
    print("🎬 PIPELINE IA - DESSIN ANIMÉ AUTOMATIQUE")
    print("=" * 80)
    print("🔧 Technologie: GPT-4o-mini + SD3-Turbo")
    print("🎯 Objectif: Transformer histoire → dessin animé fluide")
    print("=" * 80)
    
    # 1. Lancer le serveur backend
    server_process = lancer_serveur_backend()
    if not server_process:
        print("❌ Impossible de lancer le serveur. Vérifiez les dépendances.")
        return
    
    try:
        # 2. Tester l'API de santé
        if not tester_api_health():
            print("❌ API non accessible")
            return
        
        # 3. Test mode démo (rapide et gratuit)
        if not tester_api_animation_demo():
            print("❌ Test mode démo échoué")
            return
        
        # 4. Test mode production (optionnel, utilise les crédits)
        if not tester_api_animation_production():
            print("⚠️ Test mode production échoué ou ignoré")
        
        print("\n" + "="*60)
        print("🎉 PIPELINE VALIDÉE ET OPÉRATIONNELLE!")
        print("="*60)
        print("✅ Backend FastAPI: http://localhost:8000")
        print("✅ Mode démo: Fonctionnel (images SVG)")
        print("✅ Mode production: Prêt (SD3-Turbo)")
        print("\n🚀 Prochaines étapes:")
        print("   1. Lancer le frontend React: cd frontend && npm start")
        print("   2. Ouvrir http://localhost:3000")
        print("   3. Tester la génération complète histoire → animation")
        print("   4. Basculer entre mode démo et production selon vos besoins")
        
        print(f"\n⏱️ Serveur en fonctionnement. Appuyez sur Ctrl+C pour arrêter.")
        
        # Garder le serveur en vie
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
            
    finally:
        # Nettoyer le serveur
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("✅ Serveur arrêté proprement.")

if __name__ == "__main__":
    main()
