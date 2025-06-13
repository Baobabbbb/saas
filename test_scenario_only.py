#!/usr/bin/env python3
"""
Test simple de la génération de scénario pour détecter le problème du nombre de scènes
"""

import asyncio
import sys
import os

# Ajouter le chemin du saas au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

from services.scenario import generate_scenario

async def test_scenario_generation():
    """Test simple de génération de scénario"""
    print("🧪 Test de génération de scénario")
    print("=" * 50)
    
    prompt = "Une histoire dans un Tokyo futuriste avec des robots et des néons"
    style = "manga"
    num_images = 3
    
    print(f"📝 Prompt: {prompt}")
    print(f"🎨 Style: {style}")
    print(f"📸 Nombre d'images demandées: {num_images}")
    print()
    
    # Test sans CrewAI
    print("🔧 Test SANS CrewAI...")
    try:
        scenario_basic = await generate_scenario(
            prompt=prompt, 
            style=style, 
            use_crewai=False, 
            num_images=num_images
        )
        
        print("✅ Scénario de base généré:")
        print(f"  Titre: {scenario_basic.get('title', 'N/A')}")
        print(f"  Nombre de scènes: {len(scenario_basic.get('scenes', []))}")
        print(f"  Seed: {scenario_basic.get('seed', 'N/A')}")
        print(f"  Style: {scenario_basic.get('style', 'N/A')}")
        
        for i, scene in enumerate(scenario_basic.get('scenes', [])):
            print(f"  Scène {i+1}: {scene.get('description', 'N/A')[:50]}...")
        print()
        
    except Exception as e:
        print(f"❌ Erreur génération de base: {e}")
        return
    
    # Test avec CrewAI
    print("🚀 Test AVEC CrewAI...")
    try:
        scenario_enhanced = await generate_scenario(
            prompt=prompt, 
            style=style, 
            use_crewai=True, 
            num_images=num_images
        )
        
        print("✅ Scénario amélioré généré:")
        print(f"  Titre: {scenario_enhanced.get('title', 'N/A')}")
        print(f"  Nombre de scènes: {len(scenario_enhanced.get('scenes', []))}")
        print(f"  Seed: {scenario_enhanced.get('seed', 'N/A')}")
        print(f"  Style: {scenario_enhanced.get('style', 'N/A')}")
        print(f"  CrewAI enhancé: {scenario_enhanced.get('crewai_enhanced', False)}")
        
        for i, scene in enumerate(scenario_enhanced.get('scenes', [])):
            print(f"  Scène {i+1}: {scene.get('description', 'N/A')[:50]}...")
        print()
        
    except Exception as e:
        print(f"❌ Erreur génération CrewAI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scenario_generation())
