#!/usr/bin/env python3
"""
Test final pour gpt-image-1 avec organisation verifiee
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / "saas"))

from services.coloring_generator_gpt4o import ColoringGeneratorGPT4o


async def test_gpt_image_1():
    print("\n" + "="*60)
    print("TEST FINAL: gpt-image-1 (Organisation verifiee)")
    print("="*60)
    
    try:
        generator = ColoringGeneratorGPT4o()
        print("\nOK: Generateur initialise")
        
        theme = "espace"
        print(f"\nGENERATE: Coloriage theme '{theme}' avec gpt-image-1...")
        
        result = await generator.generate_coloring_from_theme(theme)
        
        if result.get("success"):
            print("\n" + "="*60)
            print("SUCCES: gpt-image-1 fonctionne parfaitement!")
            print("="*60)
            print(f"   - Images: {len(result.get('images', []))}")
            print(f"   - Modele: {result['metadata']['model']}")
            print(f"   - URL: {result['images'][0]['image_url']}")
            print("\nLe systeme est pret pour le deploiement!")
            return True
        else:
            print(f"\nERROR: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_gpt_image_1())

