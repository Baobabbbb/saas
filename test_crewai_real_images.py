"""
Test de génération de BD avec images réelles
"""
import asyncio
import json
from pathlib import Path
import sys
import os

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from saas.services.crewai_comic_complete_v3 import crewai_comic_complete_v3, ComicSpecification

async def test_real_comic_generation():
    """Test de génération complète avec images réelles"""
    print("🧪 TEST GÉNÉRATION BD AVEC IMAGES RÉELLES")
    print("=" * 60)
    
    # Spécifications de test
    spec = ComicSpecification(
        style="pixel",
        hero_name="PixelBot",
        story_type="robot adventure",
        custom_request="Create an adventure where PixelBot discovers a secret digital world",
        num_images=3
    )
    
    print(f"📋 Spécifications:")
    print(f"   Style: {spec.style}")
    print(f"   Héros: {spec.hero_name}")
    print(f"   Type: {spec.story_type}")
    print(f"   Images: {spec.num_images}")
    
    try:
        print("\n🚀 Démarrage génération CrewAI V3...")
        result = await crewai_comic_complete_v3.generate_complete_comic(spec)
        
        print("\n✅ RÉSULTAT FINAL:")
        print("=" * 60)
        
        # Afficher les métadonnées
        metadata = result.get("comic_metadata", {})
        print(f"📖 Titre: {metadata.get('title', 'N/A')}")
        print(f"🎨 Style: {metadata.get('style', 'N/A')}")
        print(f"📅 Date: {metadata.get('creation_date', 'N/A')}")
        print(f"📄 Nombre de pages: {metadata.get('num_pages', 'N/A')}")
        
        # Afficher les pages générées
        pages = result.get("pages", [])
        print(f"\n📄 PAGES GÉNÉRÉES: {len(pages)}")
        
        for page in pages:
            print(f"\n📄 PAGE {page.get('page_number', 'N/A')}:")
            print(f"   Description: {page.get('description', 'N/A')[:100]}...")
            print(f"   Fichier image: {page.get('image_path', 'N/A')}")
            print(f"   URL image: {page.get('image_url', 'N/A')}")
            
            # Vérifier que le fichier existe
            image_path = page.get('image_path')
            if image_path and os.path.exists(image_path):
                file_size = os.path.getsize(image_path)
                print(f"   ✅ Fichier créé: {file_size} bytes")
            else:
                print(f"   ❌ Fichier manquant: {image_path}")
            
            # Dialogues
            dialogues = page.get("dialogues", [])
            print(f"   Dialogues: {len(dialogues)}")
            for i, dialogue in enumerate(dialogues):
                print(f"      💬 Dialogue {i+1}: {dialogue}")
        
        # Infos de traitement
        processing_info = result.get("processing_info", {})
        print(f"\n📊 INFOS DE TRAITEMENT:")
        print(f"   Images générées: {processing_info.get('images_generated', 0)}")
        print(f"   Bulles appliquées: {processing_info.get('bubbles_applied', 0)}")
        print(f"   Fichiers réels créés: {processing_info.get('real_files_created', False)}")
        
        # Résultat brut CrewAI (tronqué)
        crewai_result = processing_info.get("crewai_result", {})
        if crewai_result:
            print(f"\n🤖 RÉSULTAT BRUT CREWAI:")
            crewai_str = json.dumps(crewai_result, ensure_ascii=False, indent=2)[:1000]
            print(crewai_str + "..." if len(crewai_str) >= 1000 else crewai_str)
        
        print("\n" + "=" * 60)
        print("✅ TEST TERMINÉ AVEC SUCCÈS")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERREUR DURANT LE TEST: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_real_comic_generation())
