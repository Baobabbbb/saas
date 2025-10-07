#!/usr/bin/env python3
"""
Test script pour la génération de coloriages avec DALL-E 3 HD
Vérifie que le système fonctionne correctement avant le déploiement
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "saas"))

from services.coloring_generator_gpt4o import ColoringGeneratorGPT4o


async def test_theme_generation():
    """Test de génération par thème"""
    print("\n" + "="*60)
    print("TEST 1: Génération de coloriage par thème")
    print("="*60)
    
    try:
        generator = ColoringGeneratorGPT4o()
        print("\nOK: Generateur initialise avec succes")
        
        theme = "espace"
        print(f"\nGENERATE: Generation d'un coloriage sur le theme: {theme}")
        
        result = await generator.generate_coloring_from_theme(theme)
        
        if result.get("success"):
            print("\nOK: SUCCES - Coloriage genere!")
            print(f"   - Images: {len(result.get('images', []))}")
            print(f"   - Modele: {result['metadata']['model']}")
            print(f"   - URL: {result['images'][0]['image_url']}")
            return True
        else:
            print(f"\nERROR: ECHEC - {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_photo_conversion():
    """Test de conversion de photo en coloriage"""
    print("\n" + "="*60)
    print("TEST 2: Conversion de photo en coloriage")
    print("="*60)
    
    try:
        generator = ColoringGeneratorGPT4o()
        
        # Créer une image de test simple si elle n'existe pas
        test_photo_dir = Path("static/uploads/coloring")
        test_photo_dir.mkdir(parents=True, exist_ok=True)
        
        test_photo_path = test_photo_dir / "test_photo.png"
        
        if not test_photo_path.exists():
            print("\nWARNING: Aucune photo de test trouvee")
            print("   Pour tester la conversion photo, ajoutez une image a:")
            print(f"   {test_photo_path}")
            return None
        
        print(f"\nCONVERT: Conversion de la photo: {test_photo_path}")
        
        result = await generator.generate_coloring_from_photo(str(test_photo_path))
        
        if result.get("success"):
            print("\nOK: SUCCES - Photo convertie!")
            print(f"   - Description: {result.get('description', 'N/A')[:100]}...")
            print(f"   - Images: {len(result.get('images', []))}")
            print(f"   - Modele: {result['metadata']['model']}")
            print(f"   - URL: {result['images'][0]['image_url']}")
            return True
        else:
            print(f"\nERROR: ECHEC - {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("TEST DALLE-3 HD COLORING SYSTEM")
    print("="*60)
    
    # Verifier la cle API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nERROR: OPENAI_API_KEY non trouvee dans .env")
        return
    
    print(f"\nOK: OPENAI_API_KEY trouvee: {api_key[:20]}...")
    
    # Exécuter les tests
    results = []
    
    # Test 1: Génération par thème
    result1 = await test_theme_generation()
    results.append(("Génération par thème", result1))
    
    # Test 2: Conversion photo (optionnel)
    result2 = await test_photo_conversion()
    if result2 is not None:
        results.append(("Conversion photo", result2))
    
    # Résumé
    print("\n" + "="*60)
    print("RESUME DES TESTS")
    print("="*60)
    
    for test_name, test_result in results:
        status = "OK: PASSE" if test_result else "ERROR: ECHOUE"
        print(f"{status} - {test_name}")
    
    all_passed = all(r for _, r in results if r is not None)
    
    if all_passed:
        print("\nSUCCES: TOUS LES TESTS ONT REUSSI!")
        print("   Le systeme est pret pour le deploiement.")
    else:
        print("\nWARNING: CERTAINS TESTS ONT ECHOUE")
        print("   Verifiez les erreurs ci-dessus avant de deployer.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())

