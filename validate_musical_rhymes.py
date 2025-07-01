"""
Script de validation pour les comptines musicales
Vérifie que tous les composants sont correctement installés
"""

import os
import sys
from pathlib import Path

def check_backend_files():
    """Vérifie la présence des fichiers backend"""
    print("🔍 Vérification des fichiers backend...")
    
    backend_files = [
        "saas/.env",
        "saas/config.py", 
        "saas/models.py",
        "saas/main_new.py",
        "saas/services/diffrhythm_service.py",
        "saas/services/musical_nursery_rhyme_service.py"
    ]
    
    missing_files = []
    
    for file_path in backend_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_frontend_files():
    """Vérifie la présence des fichiers frontend"""
    print("\n🔍 Vérification des fichiers frontend...")
    
    frontend_files = [
        "frontend/src/components/MusicalRhymeSelector.jsx",
        "frontend/src/components/MusicalRhymeSelector.css",
        "frontend/src/components/ContentTypeSelector.jsx",
        "frontend/src/services/features.js",
        "frontend/src/App.jsx"
    ]
    
    missing_files = []
    
    for file_path in frontend_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_env_configuration():
    """Vérifie la configuration .env"""
    print("\n🔍 Vérification de la configuration .env...")
    
    env_path = Path("saas/.env")
    if not env_path.exists():
        print("  ❌ Fichier .env non trouvé")
        return False
    
    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    required_vars = [
        "GOAPI_API_KEY",
        "DIFFRHYTHM_MODEL", 
        "DIFFRHYTHM_TASK_TYPE"
    ]
    
    all_vars_present = True
    
    for var in required_vars:
        if var in env_content:
            print(f"  ✅ {var} présent")
        else:
            print(f"  ❌ {var} manquant")
            all_vars_present = False
    
    # Vérifier si la clé API est configurée
    if "GOAPI_API_KEY=votre_cle_goapi_ici" in env_content:
        print("  ⚠️  GOAPI_API_KEY pas encore configurée (valeur par défaut)")
    
    return all_vars_present

def check_imports_and_syntax():
    """Vérifie la syntaxe et imports des fichiers Python"""
    print("\n🔍 Vérification de la syntaxe Python...")
    
    python_files = [
        "saas/services/diffrhythm_service.py",
        "saas/services/musical_nursery_rhyme_service.py"
    ]
    
    all_valid = True
    
    for file_path in python_files:
        full_path = Path(file_path)
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérification basique de la syntaxe
                compile(content, file_path, 'exec')
                print(f"  ✅ {file_path} - syntaxe OK")
                
            except SyntaxError as e:
                print(f"  ❌ {file_path} - erreur de syntaxe: {e}")
                all_valid = False
            except Exception as e:
                print(f"  ⚠️  {file_path} - erreur: {e}")
    
    return all_valid

def check_api_endpoints():
    """Affiche les endpoints qui doivent être disponibles"""
    print("\n🔍 Endpoints API à tester:")
    
    endpoints = [
        "POST /generate_musical_rhyme/",
        "POST /check_rhyme_task_status/", 
        "GET /rhyme_styles/"
    ]
    
    for endpoint in endpoints:
        print(f"  📡 {endpoint}")
    
    print("\n  💡 Utilisez 'python test_musical_rhymes.py' pour tester les endpoints")

def main():
    """Fonction principale de validation"""
    print("🎼 Validation des Comptines Musicales DiffRhythm")
    print("=" * 60)
    
    # Changer vers le répertoire du script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Vérifications
    backend_ok = check_backend_files()
    frontend_ok = check_frontend_files()
    env_ok = check_env_configuration()
    syntax_ok = check_imports_and_syntax()
    
    check_api_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA VALIDATION:")
    print(f"  📁 Fichiers backend: {'✅' if backend_ok else '❌'}")
    print(f"  🎨 Fichiers frontend: {'✅' if frontend_ok else '❌'}")
    print(f"  ⚙️  Configuration .env: {'✅' if env_ok else '❌'}")
    print(f"  🐍 Syntaxe Python: {'✅' if syntax_ok else '❌'}")
    
    if all([backend_ok, frontend_ok, env_ok, syntax_ok]):
        print("\n🎉 Validation réussie! La fonctionnalité est prête à être testée.")
        print("\n📋 Prochaines étapes:")
        print("  1. Configurer GOAPI_API_KEY dans saas/.env")
        print("  2. Démarrer le backend: cd saas && python main_new.py")
        print("  3. Démarrer le frontend: cd frontend && npm start")
        print("  4. Tester les endpoints: python test_musical_rhymes.py")
    else:
        print("\n⚠️  Des problèmes ont été détectés. Veuillez les corriger.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
