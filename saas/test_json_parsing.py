#!/usr/bin/env python3
"""
Test rapide de parsing JSON amélioré pour SEEDANCE
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent))

from services.seedance_service import SeedanceService

async def test_json_parsing():
    """Test rapide du parsing JSON amélioré"""
    print("🧪 Test du parsing JSON amélioré")
    print("=" * 40)
    
    service = SeedanceService()
    
    # Test avec un thème spécifique
    test_params = {
        'story': 'Le Petit Astronaute',
        'theme': 'space',
        'age_target': '3-5 ans',
        'style': 'cartoon'
    }
    
    print(f"🚀 Test: {test_params['story']} (thème: {test_params['theme']})")
    
    try:
        # Tester la génération d'idées
        print("💡 Génération d'idées...")
        idea_result = await service._generate_ideas(**test_params)
        
        if idea_result:
            print("✅ Idées générées avec succès")
            
            # Tester la génération de scènes avec parsing amélioré
            print("📝 Génération de scènes avec parsing amélioré...")
            scenes = await service._generate_scene_prompts(idea_result, 30)
            
            if scenes and len(scenes) == 3:
                print(f"✅ {len(scenes)} scènes générées avec parsing amélioré!")
                
                for i, scene in enumerate(scenes):
                    scene_type = scene.get('scene_type', f'Scene{i+1}')
                    description = scene.get('description', '')
                    print(f"   🎬 Scène {i+1} ({scene_type}): {description[:100]}...")
                
                return True
            else:
                print(f"❌ Échec génération scènes: {len(scenes) if scenes else 0}")
                return False
        else:
            print("❌ Échec génération d'idées")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_json_parsing())
    if result:
        print("\n🎉 Test de parsing JSON réussi!")
    else:
        print("\n❌ Test de parsing JSON échoué!")
