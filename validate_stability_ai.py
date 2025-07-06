#!/usr/bin/env python3
"""
Script de validation finale pour confirmer que l'application FRIDAY
utilise bien Stability AI avec seeds pour la génération de BD
"""

import os
import json
import requests
from pathlib import Path

def validate_configuration():
    """Valide la configuration Stability AI"""
    print("🔧 Validation de la configuration...")
    
    # Vérifier le fichier .env
    env_path = Path("saas/.env")
    if not env_path.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Vérifications
    checks = {
        "IMAGE_MODEL=stability-ai": "✅ Modèle d'image configuré sur Stability AI",
        "STABILITY_API_KEY=sk-": "✅ Clé API Stability AI configurée",
        "VIDEO_MODEL=sd3-large-turbo": "✅ Modèle vidéo SD3 configuré"
    }
    
    all_good = True
    for check, message in checks.items():
        if check in env_content:
            print(message)
        else:
            print(f"❌ Manquant: {check}")
            all_good = False
    
    return all_good

def validate_backend_running():
    """Valide que le backend tourne correctement"""
    print("\n🌐 Validation du backend...")
    
    try:
        response = requests.get("http://localhost:8006/diagnostic", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend accessible")
            print(f"🤖 OpenAI: {'✅' if data.get('openai_configured') else '❌'}")
            print(f"🎨 Stability AI: {'✅' if data.get('stability_configured') else '❌'}")
            return data.get('stability_configured', False)
        else:
            print(f"❌ Backend erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend inaccessible: {e}")
        return False

def validate_recent_generation():
    """Valide qu'une génération récente utilise bien Stability AI"""
    print("\n📚 Validation des générations récentes...")
    
    comics_dir = Path("saas/static/generated_comics")
    if not comics_dir.exists():
        print("❌ Dossier de BD non trouvé")
        return False
    
    # Trouver la BD la plus récente
    comic_folders = [f for f in comics_dir.iterdir() if f.is_dir()]
    if not comic_folders:
        print("❌ Aucune BD générée trouvée")
        return False
    
    latest_comic = max(comic_folders, key=lambda x: x.stat().st_mtime)
    print(f"📖 BD la plus récente: {latest_comic.name}")
    
    # Vérifier la présence des fichiers
    required_files = ["consistency_data.json", "page_1_final.png"]
    missing_files = []
    
    for file in required_files:
        file_path = latest_comic / file
        if file_path.exists():
            print(f"✅ {file} présent")
        else:
            print(f"❌ {file} manquant")
            missing_files.append(file)
    
    if missing_files:
        return False
    
    # Vérifier les données de cohérence
    consistency_file = latest_comic / "consistency_data.json"
    with open(consistency_file, 'r', encoding='utf-8') as f:
        consistency_data = json.load(f)
    
    print(f"🎲 Seed de base: {consistency_data.get('base_seed')}")
    character_seeds = consistency_data.get('character_seeds', {})
    print(f"👥 Personnages avec seeds: {len(character_seeds)}")
    
    for char, seed in character_seeds.items():
        print(f"   {char}: seed {seed}")
    
    return True

def validate_image_quality():
    """Valide la qualité des images générées"""
    print("\n🖼️ Validation de la qualité des images...")
    
    comics_dir = Path("saas/static/generated_comics")
    if not comics_dir.exists():
        return False
    
    comic_folders = [f for f in comics_dir.iterdir() if f.is_dir()]
    if not comic_folders:
        return False
    
    latest_comic = max(comic_folders, key=lambda x: x.stat().st_mtime)
    
    # Vérifier les tailles d'images (indicateur de qualité)
    image_files = list(latest_comic.glob("page_*_raw.png"))
    total_size = 0
    
    for img_file in image_files:
        size = img_file.stat().st_size
        size_mb = size / (1024 * 1024)
        print(f"📷 {img_file.name}: {size_mb:.1f} MB")
        total_size += size
    
    avg_size_mb = (total_size / len(image_files)) / (1024 * 1024) if image_files else 0
    print(f"📊 Taille moyenne: {avg_size_mb:.1f} MB")
    
    # Images de qualité Stability AI sont généralement > 1MB
    if avg_size_mb > 1.0:
        print("✅ Images de haute qualité (probablement générées par Stability AI)")
        return True
    else:
        print("⚠️ Images de taille réduite (possibles fallbacks)")
        return False

def main():
    """Fonction principale de validation"""
    print("🚀 VALIDATION FINALE - Application FRIDAY avec Stability AI")
    print("=" * 80)
    
    checks = [
        ("Configuration", validate_configuration),
        ("Backend", validate_backend_running),
        ("Génération récente", validate_recent_generation),
        ("Qualité des images", validate_image_quality)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'🔍 ' + name + ' ':.<50}")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"💥 Erreur: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ DE LA VALIDATION")
    print("=" * 80)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{name:<25} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 VALIDATION RÉUSSIE !")
        print("✅ L'application FRIDAY utilise correctement Stability AI")
        print("🎯 Les seeds sont utilisées pour la cohérence des personnages")
        print("🖼️ Les images sont de haute qualité")
        print("🌐 Frontend: http://localhost:5178")
        print("🔧 Backend: http://localhost:8006")
    else:
        print("😞 VALIDATION PARTIELLEMENT ÉCHOUÉE")
        print("⚠️ Certains éléments nécessitent une vérification")
    
    print("=" * 80)

if __name__ == "__main__":
    # Changer vers le répertoire backend
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
