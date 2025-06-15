"""
Test détaillé du CrewAI V3 avec génération réelle d'images
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Ajouter le chemin pour importer les modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

from services.crewai_comic_complete_v3 import CrewAIComicCompleteV3, ComicSpecification

async def test_crewai_v3_verbose():
    """Test détaillé de CrewAI V3 avec génération réelle d'images"""
    
    print("🧪 TEST DÉTAILLÉ CREWAI V3 (VRAIES IMAGES)")
    print("=" * 60)
    
    # Créer le service
    service = CrewAIComicCompleteV3()
      # Spécifications de test
    spec = ComicSpecification(
        style="pixel",
        hero_name="TestHero",
        story_type="space adventure",
        custom_request="Create an epic space adventure",
        num_images=3
    )
    
    print(f"📋 Spécifications:")
    print(f"   Style: {spec.style}")
    print(f"   Héros: {spec.hero_name}")
    print(f"   Type: {spec.story_type}")
    print(f"   Images: {spec.num_images}")
    print()
    
    try:
        # Lancer la génération
        print("🚀 Démarrage génération CrewAI V3...")
        result = await service.generate_complete_comic(spec)
        
        print()
        print("✅ RÉSULTAT FINAL:")
        print("=" * 60)
        
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
        static_dir = Path("saas/static/generated_comics")
        
        for i, page in enumerate(pages):
            print(f"\n📄 PAGE {i+1}:")
            print(f"   Description: {page.get('scene_description')}")
            print(f"   Image URL: {page.get('image_url')}")
            print(f"   Dialogues: {len(page.get('dialogues', []))}")
            print(f"   Bulles: {len(page.get('bubble_specifications', []))}")
              # Vérifier si le fichier image existe vraiment
            image_url = page.get('image_url', '')
            if image_url.startswith('/static/generated_comics/'):
                # Extraire le chemin relatif depuis l'URL
                rel_path = image_url[len('/static/generated_comics/'):]
                file_path = static_dir / rel_path
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    print(f"   ✅ Fichier image créé: {file_path} ({file_size} bytes)")
                else:
                    print(f"   ❌ Fichier image manquant: {file_path}")
                    print(f"       URL: {image_url}")
                    print(f"       Chemin calculé: {file_path}")
            else:
                print(f"   ⚠️  URL d'image inattendue: {image_url}")
            
            # Afficher les dialogues
            dialogues = page.get('dialogues', [])
            for j, dialogue in enumerate(dialogues):
                print(f"      💬 Dialogue {j+1}: {dialogue}")
            
            # Afficher les spécifications de bulles
            bubbles = page.get('bubble_specifications', [])
            for j, bubble in enumerate(bubbles):
                print(f"      🗨️ Bulle {j+1}: {bubble}")
        
        # Afficher les infos de traitement
        processing_info = result.get('processing_info', {})
        print(f"\n📊 INFOS DE TRAITEMENT:")
        print(f"   Images générées: {processing_info.get('images_generated')}")
        print(f"   Bulles appliquées: {processing_info.get('bubbles_applied')}")
        print(f"   Fichiers créés: {processing_info.get('files_created', [])}")
          # Vérifier le répertoire static
        print(f"\n📁 VÉRIFICATION RÉPERTOIRE STATIC:")
        if static_dir.exists():
            # Lister tous les dossiers de comic
            comic_dirs = [d for d in static_dir.iterdir() if d.is_dir()]
            print(f"   Répertoire: {static_dir}")
            print(f"   Dossiers de comics trouvés: {len(comic_dirs)}")
            
            total_files = 0
            for comic_dir in comic_dirs:
                files = list(comic_dir.glob("*.png"))
                total_files += len(files)
                print(f"     Dossier: {comic_dir.name}")
                for file in files:
                    size = file.stat().st_size
                    print(f"       - {file.name} ({size} bytes)")
            
            print(f"   Total fichiers PNG: {total_files}")
        else:
            print(f"   ❌ Répertoire static manquant: {static_dir}")
        
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

async def test_image_generator_only():
    """Test isolé du générateur d'images"""
    
    print("\n" + "=" * 60)
    print("🧪 TEST ISOLÉ DU GÉNÉRATEUR D'IMAGES")
    print("=" * 60)
    
    try:
        from services.crewai_image_generator import ComicImageGenerator
        from services.crewai_comic_complete_v3 import ComicSpecification
        
        generator = ComicImageGenerator()
        
        # Créer des spécifications de test
        spec = ComicSpecification(
            style="pixel",
            hero_name="TestHero",
            story_type="space adventure",
            custom_request="Test image generation",
            num_images=1,
            user_parameters={}
        )
        
        # Données de test simulant un résultat CrewAI
        mock_comic_data = {
            "result": """{"titre":"Test Comic","chapitres":[{"description":"A brave astronaut exploring an alien planet with purple skies"}]}"""
        }
        
        print("🖼️ Test de génération complète d'images...")
        
        # Test de génération d'images complète
        pages = await generator.generate_comic_images(mock_comic_data, spec)
        
        print(f"✅ {len(pages)} pages générées avec succès!")
        
        # Vérifier les fichiers générés
        for i, page in enumerate(pages):
            print(f"\n📄 PAGE {i+1}:")
            print(f"   URL: {page.get('image_url')}")
            print(f"   Chemin: {page.get('image_path')}")
            print(f"   Dialogues: {len(page.get('dialogues', []))}")
            
            # Vérifier que le fichier existe
            image_path = Path(page.get('image_path', ''))
            if image_path.exists():
                size = image_path.stat().st_size
                print(f"   ✅ Fichier créé: {image_path} ({size} bytes)")
            else:
                print(f"   ❌ Fichier manquant: {image_path}")
        
        return len(pages) > 0
        
    except Exception as e:
        print(f"❌ ERREUR dans le test du générateur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DES TESTS CREWAI V3")
    print("=" * 60)
    
    # Test du générateur d'images seul
    generator_ok = asyncio.run(test_image_generator_only())
    
    # Test complet CrewAI V3
    result = asyncio.run(test_crewai_v3_verbose())
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   Générateur d'images: {'✅ OK' if generator_ok else '❌ ÉCHEC'}")
    print(f"   CrewAI V3 complet: {'✅ OK' if result else '❌ ÉCHEC'}")
    
    if result and generator_ok:
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("   La génération réelle d'images fonctionne correctement.")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Vérifiez les erreurs ci-dessus.")
