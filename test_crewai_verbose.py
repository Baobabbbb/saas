"""
Test détaillé du CrewAI V2 pour voir exactement ce qui est généré
"""

import asyncio
import json
import sys
import os

# Ajouter le chemin pour importer les modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

from services.crewai_comic_complete_v2 import CrewAIComicCompleteV2, ComicSpecification

async def test_crewai_verbose():
    """Test détaillé de CrewAI avec logs complets"""
    
    print("🧪 TEST DÉTAILLÉ CREWAI V2")
    print("=" * 50)
    
    # Créer le service
    service = CrewAIComicCompleteV2()
    
    # Spécifications de test
    spec = ComicSpecification(
        style="pixel",
        hero_name="TestHero",
        story_type="space adventure",
        custom_request="Create an epic space adventure",
        num_images=2,
        user_parameters={}
    )
    
    print(f"📋 Spécifications:")
    print(f"   Style: {spec.style}")
    print(f"   Héros: {spec.hero_name}")
    print(f"   Type: {spec.story_type}")
    print(f"   Images: {spec.num_images}")
    print()
    
    try:
        # Lancer la génération
        print("🚀 Démarrage génération CrewAI...")
        result = await service.generate_complete_comic(spec)
        
        print()
        print("✅ RÉSULTAT FINAL:")
        print("=" * 50)
        
        # Afficher les métadonnées
        metadata = result.get('comic_metadata', {})
        print(f"📖 Titre: {metadata.get('title')}")
        print(f"🎨 Style: {metadata.get('style')}")
        print(f"📅 Date: {metadata.get('creation_date')}")
        print(f"📄 Nombre de pages: {metadata.get('num_pages')}")
        print()
        
        # Afficher les pages
        pages = result.get('pages', [])
        print(f"📄 PAGES GÉNÉRÉES: {len(pages)}")
        for i, page in enumerate(pages):
            print(f"\n📄 PAGE {i+1}:")
            print(f"   Description: {page.get('scene_description')}")
            print(f"   Image URL: {page.get('image_url')}")
            print(f"   Dialogues: {len(page.get('dialogues', []))}")
            print(f"   Bulles: {len(page.get('bubble_specifications', []))}")
            
            # Afficher les dialogues
            dialogues = page.get('dialogues', [])
            for j, dialogue in enumerate(dialogues):
                print(f"      💬 Dialogue {j+1}: {dialogue}")
        
        # Afficher les infos de traitement
        processing_info = result.get('processing_info', {})
        print(f"\n📊 INFOS DE TRAITEMENT:")
        print(f"   Images générées: {processing_info.get('images_generated')}")
        print(f"   Bulles appliquées: {processing_info.get('bubbles_applied')}")
        
        # Afficher le résultat brut de CrewAI
        crewai_result = processing_info.get('crewai_result', {})
        print(f"\n🤖 RÉSULTAT BRUT CREWAI:")
        print(json.dumps(crewai_result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_crewai_verbose())
    
    if result:
        print("\n" + "=" * 50)
        print("✅ TEST TERMINÉ AVEC SUCCÈS")
    else:
        print("\n" + "=" * 50)
        print("❌ TEST ÉCHOUÉ")
