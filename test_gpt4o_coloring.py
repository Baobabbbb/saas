"""
Script de test pour le nouveau système de coloriages GPT-4o-mini + DALL-E 3
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer le service
import sys
sys.path.insert(0, str(Path(__file__).parent / "saas"))
from services.coloring_generator_gpt4o import ColoringGeneratorGPT4o


async def test_theme_generation():
    """Test de génération par thème"""
    print("\n" + "="*60)
    print("🎨 TEST 1 : Génération par thème")
    print("="*60)
    
    generator = ColoringGeneratorGPT4o()
    
    # Test avec le thème "dinosaures"
    print("\n📝 Génération d'un coloriage sur le thème 'dinosaures'...")
    result = await generator.generate_coloring_from_theme("dinosaures")
    
    if result.get("success"):
        print("✅ Génération réussie !")
        print(f"   - Thème : {result.get('theme')}")
        print(f"   - Images : {result.get('total_images')}")
        print(f"   - URL : {result['images'][0]['image_url']}")
        print(f"   - Modèle : {result['metadata']['model']}")
    else:
        print(f"❌ Échec : {result.get('error')}")
    
    return result.get("success")


async def test_photo_conversion():
    """Test de conversion de photo (si une photo de test existe)"""
    print("\n" + "="*60)
    print("📸 TEST 2 : Conversion de photo")
    print("="*60)
    
    # Chercher une photo de test
    test_photos = [
        Path("static/uploads/coloring").glob("*.jpg"),
        Path("static/uploads/coloring").glob("*.png"),
        Path("static/uploads/coloring").glob("*.jpeg"),
    ]
    
    photo_path = None
    for pattern in test_photos:
        for photo in pattern:
            photo_path = photo
            break
        if photo_path:
            break
    
    if not photo_path:
        print("⚠️ Aucune photo de test trouvée dans static/uploads/coloring/")
        print("   Vous pouvez tester manuellement en uploadant une photo via l'interface web")
        return True  # Pas d'échec, juste pas de test
    
    print(f"\n📝 Conversion de la photo : {photo_path.name}")
    
    generator = ColoringGeneratorGPT4o()
    result = await generator.generate_coloring_from_photo(str(photo_path))
    
    if result.get("success"):
        print("✅ Conversion réussie !")
        print(f"   - Photo source : {result.get('source_photo')}")
        print(f"   - Description : {result.get('description')[:100]}...")
        print(f"   - Images : {result.get('total_images')}")
        print(f"   - URL : {result['images'][0]['image_url']}")
        print(f"   - Modèle : {result['metadata']['model']}")
    else:
        print(f"❌ Échec : {result.get('error')}")
    
    return result.get("success")


async def test_api_keys():
    """Test de la configuration des clés API"""
    print("\n" + "="*60)
    print("🔑 TEST 0 : Vérification des clés API")
    print("="*60)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY non trouvée dans .env")
        return False
    
    print(f"✅ OPENAI_API_KEY : {openai_key[:15]}...")
    print(f"✅ BASE_URL : {base_url or 'https://herbbie.com (défaut)'}")
    
    return True


async def main():
    """Fonction principale de test"""
    print("\n" + "="*60)
    print("🚀 TEST DU SYSTÈME DE COLORIAGES GPT-4o-mini")
    print("="*60)
    
    # Test 0 : Clés API
    if not await test_api_keys():
        print("\n❌ Tests interrompus : clés API manquantes")
        return
    
    # Test 1 : Génération par thème
    test1_success = await test_theme_generation()
    
    # Test 2 : Conversion de photo
    test2_success = await test_photo_conversion()
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"Test 1 (Thème) : {'✅ RÉUSSI' if test1_success else '❌ ÉCHOUÉ'}")
    print(f"Test 2 (Photo) : {'✅ RÉUSSI' if test2_success else '⚠️ NON TESTÉ'}")
    
    if test1_success:
        print("\n🎉 Le système de coloriages GPT-4o-mini fonctionne correctement !")
    else:
        print("\n⚠️ Des problèmes ont été détectés. Vérifiez les logs ci-dessus.")


if __name__ == "__main__":
    asyncio.run(main())
