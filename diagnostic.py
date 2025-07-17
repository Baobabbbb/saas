#!/usr/bin/env python3
"""
Diagnostic SEEDANCE - Outil de dépannage rapide
"""

import os
import sys
import aiohttp
import asyncio
from pathlib import Path

def check_files():
    """Vérifier les fichiers essentiels"""
    print("📁 Vérification des fichiers...")
    
    base_dir = Path(__file__).parent
    
    # Fichiers critiques
    critical_files = [
        "saas/.env",
        "saas/main.py", 
        "saas/services/seedance_service.py",
        "frontend/package.json"
    ]
    
    for file_path in critical_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MANQUANT!")
            return False
    
    return True

def check_env_vars():
    """Vérifier les variables d'environnement"""
    print("\n🔑 Vérification des clés API...")
    
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / "saas" / ".env")
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "WAVESPEED_API_KEY": os.getenv("WAVESPEED_API_KEY"),
        "FAL_API_KEY": os.getenv("FAL_API_KEY")
    }
    
    all_ok = True
    for key_name, key_value in api_keys.items():
        if key_value and not key_value.startswith("votre_") and not key_value.startswith("sk-votre"):
            print(f"   ✅ {key_name}: Configurée ({key_value[:15]}...)")
        else:
            print(f"   ❌ {key_name}: Manquante ou invalide")
            all_ok = False
    
    return all_ok

def check_dependencies():
    """Vérifier les dépendances Python"""
    print("\n📦 Vérification des dépendances Python...")
    
    required_modules = [
        "fastapi", "uvicorn", "aiohttp", "openai", 
        "dotenv", "pydantic", "pathlib"
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - MANQUANT!")
            missing.append(module)
    
    if missing:
        print(f"\n💡 Pour installer les dépendances manquantes:")
        print(f"   cd saas/saas && pip install {' '.join(missing)}")
        return False
    
    return True

async def check_backend():
    """Tester la connectivité du backend"""
    print("\n🌐 Test de connectivité backend...")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get("http://localhost:8004/diagnostic") as response:
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ Backend accessible")
                    print(f"   📊 OpenAI: {'✅' if data.get('openai_configured') else '❌'}")
                    print(f"   📊 Stability: {'✅' if data.get('stability_configured') else '❌'}")
                    print(f"   📊 FAL: {'✅' if data.get('fal_configured') else '❌'}")
                    return True
                else:
                    print(f"   ❌ Backend répond avec code {response.status}")
                    return False
    except aiohttp.ClientConnectorError:
        print("   ❌ Backend non accessible - pas démarré?")
        return False
    except Exception as e:
        print(f"   ❌ Erreur backend: {e}")
        return False

def check_ports():
    """Vérifier les ports"""
    print("\n🔌 Vérification des ports...")
    
    import socket
    
    ports = [8004, 5173]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Port {port}: En cours d'utilisation")
        else:
            print(f"   ⚠️ Port {port}: Libre")

def print_solutions():
    """Afficher les solutions courantes"""
    print("\n🛠️ Solutions aux problèmes courants:")
    print()
    print("1. 🔑 Clés API manquantes:")
    print("   - Éditer saas/.env")
    print("   - Remplir OPENAI_API_KEY, WAVESPEED_API_KEY, FAL_API_KEY")
    print()
    print("2. 📦 Dépendances manquantes:")
    print("   - cd saas && pip install -r requirements.txt")
    print("   - cd frontend && npm install")
    print()
    print("3. 🌐 Backend non accessible:")
    print("   - cd saas")
    print("   - python -m uvicorn main:app --host 0.0.0.0 --port 8004")
    print()
    print("4. 🎨 Frontend non accessible:")
    print("   - cd frontend")
    print("   - npm run dev")
    print()
    print("5. 🚀 Lancement complet:")
    print("   - chmod +x QUICK_START_SECURE.sh && ./QUICK_START_SECURE.sh")
    print("   - Ou: powershell -ExecutionPolicy Bypass -File QUICK_START_SECURE.ps1")

async def main():
    """Diagnostic principal"""
    print("🔍 DIAGNOSTIC SEEDANCE")
    print("=" * 50)
    
    checks = [
        ("Fichiers", check_files()),
        ("Variables", check_env_vars()),
        ("Dépendances", check_dependencies())
    ]
    
    # Tests synchrones
    all_ok = True
    for name, result in checks:
        if not result:
            all_ok = False
    
    # Tests asynchrones
    check_ports()
    backend_ok = await check_backend()
    
    if not backend_ok:
        all_ok = False
    
    print("\n" + "=" * 50)
    
    if all_ok:
        print("🎉 DIAGNOSTIC: TOUT EST OK!")
        print("   Le système devrait fonctionner correctement.")
    else:
        print("⚠️ DIAGNOSTIC: PROBLÈMES DÉTECTÉS")
        print("   Consultez les solutions ci-dessous:")
        print_solutions()
    
    print("\n📚 Documentation complète: TROUBLESHOOTING.md")

if __name__ == "__main__":
    asyncio.run(main())
