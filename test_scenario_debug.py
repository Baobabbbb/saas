#!/usr/bin/env python3
"""
Test direct du service de scénario pour déboguer CrewAI
"""

import asyncio
import sys
import os

# Ajouter le répertoire saas au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

async def test_scenario_service():
    """Test direct du service scenario"""
    
    try:
        from services.scenario import generate_scenario
        
        prompt = """
        Tu es un scénariste de bande dessinée pour enfants de 6 à 9 ans.

        Crée une BD avec un héros nommé Akira, sur le thème "science-fiction", 
        dans un style manga. Suis cette structure :

        1. La BD doit comporter exactement **3 scènes**, une par image.
        2. Chaque scène contient :
           - Une description visuelle claire et précise pour l'image
           - **Entre 1 et 3 dialogues maximum**, adaptés aux bulles de BD
           - Des indications de placement des personnages (gauche, droite, centre, haut, bas)

        3. Les dialogues doivent être :
           - Naturels et expressifs
           - Adaptés à des enfants
           - Courts et percutants (max 2-3 phrases par bulle)
           - Variés dans le ton (parole normale, cri, chuchotement, pensée)
           - Éviter les répétitions

        Structure narrative : début → problème → aventure → résolution

        Langue : français

        Une histoire dans un Tokyo futuriste avec des robots et des néons
        """
        
        print("🧪 Test du service de scénario avec CrewAI")
        print("=" * 60)
        
        # Test avec CrewAI activé
        print("🚀 Test avec CrewAI activé...")
        
        scenario = await generate_scenario(
            prompt=prompt, 
            style="manga", 
            use_crewai=True
        )
        
        print("✅ Scénario généré")
        print(f"📚 Titre: {scenario.get('title', 'N/A')}")
        print(f"🔢 Nombre de scènes: {len(scenario.get('scenes', []))}")
        print(f"🤖 CrewAI utilisé: {scenario.get('crewai_enhanced', False)}")
        print(f"🎯 Seed: {scenario.get('seed', 'N/A')}")
        print(f"🎨 Style: {scenario.get('style', 'N/A')}")
        
        if scenario.get('review_notes'):
            print(f"📝 Notes d'amélioration: {len(scenario['review_notes'])}")
            for note in scenario['review_notes']:
                print(f"   - {note}")
        
        print("\n📖 Scènes générées:")
        for i, scene in enumerate(scenario.get('scenes', []), 1):
            print(f"\n  Scène {i}:")
            print(f"    Description: {scene.get('description', 'N/A')[:100]}...")
            print(f"    Dialogues: {len(scene.get('dialogues', []))}")
            for j, dialogue in enumerate(scene.get('dialogues', []), 1):
                print(f"      {j}. {dialogue.get('character', 'N/A')}: {dialogue.get('text', 'N/A')}")
        
        return scenario
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_scenario_service())
