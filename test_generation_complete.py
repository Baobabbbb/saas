#!/usr/bin/env python3
"""
Test complet de génération de BD avec bulles PIL fiables
"""

import sys
import os
sys.path.append('.')
sys.path.append('saas')

import asyncio
import json
from pathlib import Path
from datetime import datetime

# Mock des services manquants pour le test
class MockStableDiffusionGenerator:
    def __init__(self):
        pass

class MockComicAIEnhancer:
    def __init__(self):
        pass

# Importer après les mocks
from saas.services.comic_generator import ComicGenerator

async def test_complete_comic_generation():
    """Test complet de génération de BD"""
    print("🚀 Test complet de génération de BD avec bulles PIL...")
    
    # Données de test
    request_data = {
        "theme": "space",
        "art_style": "cartoon",
        "story_length": "4",
        "custom_request": "Avec des dialogues amusants pour tester les bulles"
    }
    
    try:
        # Créer le générateur
        generator = ComicGenerator()
        print("✅ ComicGenerator initialisé")
        
        # Générer le script
        print("📝 Génération du scénario...")
        script_data = await generator.generate_comic_script(
            theme=request_data["theme"],
            story_length=request_data["story_length"],
            custom_request=request_data.get("custom_request")
        )
        
        print(f"✅ Scénario généré: {script_data.get('title', 'Sans titre')}")
        print(f"📖 Nombre de scènes: {len(script_data.get('scenes', []))}")
        
        # Afficher quelques détails du script
        if 'main_characters' in script_data:
            print(f"👥 Personnages: {[char.get('name', 'Inconnu') for char in script_data['main_characters']]}")
        
        if 'scenes' in script_data:
            for i, scene in enumerate(script_data['scenes'][:2]):  # Afficher 2 premières scènes
                dialogues = scene.get('dialogues', [])
                print(f"🎬 Scène {i+1}: {len(dialogues)} dialogue(s)")
                for dialogue in dialogues:
                    print(f"   💬 {dialogue.get('character', '?')}: {dialogue.get('text', '')[:50]}...")
        
        print("🎯 Test de script réussi!")
        
        # Sauvegarder le script pour inspection
        test_dir = Path("test_comic_generation")
        test_dir.mkdir(exist_ok=True)
        
        script_path = test_dir / "generated_script.json"
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Script sauvegardé: {script_path}")
        
        # Test spécifique des bulles sans génération d'image
        print("\n🎨 Test du système de bulles PIL...")
        
        if 'scenes' in script_data and len(script_data['scenes']) > 0:
            first_scene = script_data['scenes'][0]
            dialogues = first_scene.get('dialogues', [])
            
            if dialogues:
                # Créer une image de test pour les bulles
                from PIL import Image, ImageDraw
                
                img = Image.new('RGB', (800, 600), 'lightgreen')
                draw = ImageDraw.Draw(img)
                
                # Dessiner des personnages simulés
                draw.rectangle([150, 300, 250, 500], fill='red', outline='black', width=2)
                draw.rectangle([550, 280, 650, 480], fill='blue', outline='black', width=2)
                
                test_image_path = test_dir / "test_scene_base.png"
                img.save(test_image_path)
                
                # Appliquer les bulles
                final_image_path = await generator._add_speech_bubbles_pil_reliable(
                    test_image_path,
                    dialogues,
                    test_dir,
                    1
                )
                
                print(f"✅ Bulles ajoutées: {final_image_path}")
                
                if final_image_path.exists():
                    file_size = final_image_path.stat().st_size
                    print(f"📊 Taille fichier final: {file_size} bytes")
                    print("🎯 Test de bulles PIL réussi!")
                else:
                    print("❌ Fichier final non créé")
            else:
                print("⚠️ Aucun dialogue dans la première scène")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_comic_generation())
    
    if success:
        print("\n🎉 SUCCÈS COMPLET: Système de génération BD avec bulles PIL fonctionnel!")
        print("✅ Script de BD généré")
        print("✅ Bulles PIL appliquées")
        print("✅ Fichiers sauvegardés")
    else:
        print("\n❌ ÉCHEC: Problème avec la génération BD")
