#!/usr/bin/env python3
"""
Test simple pour diagnostiquer le problème de génération BD
"""
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test des imports"""
    print("🔍 Test des imports...")
    
    try:
        from services.comic_generator import ComicGenerator
        print("✅ ComicGenerator importé")
        
        generator = ComicGenerator()
        print("✅ ComicGenerator initialisé")
        
        # Test des attributs
        if hasattr(generator, 'sd_generator'):
            print("✅ sd_generator disponible")
        else:
            print("❌ sd_generator manquant")
            
        if hasattr(generator, 'ai_enhancer'):
            print("✅ ai_enhancer disponible")
        else:
            print("❌ ai_enhancer manquant")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_comic_generation():
    """Test rapide de génération"""
    print("\n🎨 Test de génération BD...")
    
    try:
        from services.comic_generator import ComicGenerator
        
        generator = ComicGenerator()
        
        # Données de test minimalistes
        test_data = {
            "theme": "adventure",
            "story_length": "short",
            "art_style": "cartoon",
            "custom_request": "Test simple"
        }
        
        print("📤 Lancement de la génération...")
        result = await generator.create_complete_comic(test_data)
        
        print(f"📊 Résultat: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            print("✅ Génération réussie!")
            print(f"Pages: {result.get('total_pages', 0)}")
        else:
            print("❌ Génération échouée:")
            print(f"Erreur: {result.get('error', 'Inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Diagnostic BD FRIDAY")
    print("=" * 30)
    
    if test_imports():
        import asyncio
        asyncio.run(test_comic_generation())
    else:
        print("\n❌ Impossible de continuer - problème d'import")
