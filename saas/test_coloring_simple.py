#!/usr/bin/env python3
"""
Test simple du service de génération de coloriages
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.coloring_generator import ColoringGenerator

async def test_coloring_generation():
    """Test de génération de coloriage"""
    
    print("🧪 Test génération coloriage...")
    
    try:
        generator = ColoringGenerator()
        
        # Test avec le thème espace
        result = await generator.generate_coloring_pages("espace")
        
        print(f"✅ Résultat: {result}")
        
        if result.get("success"):
            print(f"🎨 Images générées: {len(result.get('images', []))}")
            for img in result.get('images', []):
                print(f"   - {img.get('image_url')}")
        else:
            print(f"❌ Erreur: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coloring_generation())
