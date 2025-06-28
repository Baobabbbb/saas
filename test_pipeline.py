#!/usr/bin/env python3
"""
Script de test pour la pipeline de génération de dessins animés
Teste l'intégration complète GPT-4o-mini + SD3-Turbo
"""
import asyncio
import json
import time
from pathlib import Path
import sys
import os

# Ajouter le répertoire saas au path et changer le répertoire de travail
saas_path = str(Path(__file__).parent / "saas")
sys.path.insert(0, saas_path)
os.chdir(saas_path)

from services.animation_pipeline import animation_pipeline
from dotenv import load_dotenv

load_dotenv("saas/.env")

async def test_pipeline():
    """Test complet de la pipeline d'animation"""
    
    print("🎬 === TEST PIPELINE ANIMATION ===")
    print("🔧 Configuration:")
    print(f"   📁 Cache: {animation_pipeline.cache_dir}")
    print(f"   🔑 OpenAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    print(f"   🔑 Stability: {'✅' if os.getenv('STABILITY_API_KEY') else '❌'}")
    
    # Histoire de test
    test_story = """
    Il était une fois, dans un petit village au bord d'une forêt enchantée, 
    une petite fille nommée Luna qui avait le pouvoir de parler aux animaux. 
    Un jour, son ami le renard Félix lui dit que la forêt est en danger car 
    un méchant sorcier a volé l'étoile magique qui protège tous les arbres. 
    Luna décide de partir en aventure avec Félix pour retrouver l'étoile. 
    Après un long voyage plein de défis, ils trouvent le sorcier et Luna 
    réussit à le convaincre de rendre l'étoile en lui montrant la beauté 
    de la nature. La forêt est sauvée et tout le monde vit heureux.
    """
    
    print(f"\n📖 Histoire de test:")
    print(f"   Longueur: {len(test_story)} caractères")
    print(f"   Mots: {len(test_story.split())} mots")
    
    # Paramètres de test
    target_duration = 45  # 45 secondes
    style_hint = "cartoon"
    
    print(f"\n⏱️ Paramètres:")
    print(f"   Durée: {target_duration}s")
    print(f"   Style: {style_hint}")
    
    try:
        start_time = time.time()
        
        # Lancer la génération
        print(f"\n🚀 Démarrage de la génération...")
        result = await animation_pipeline.generate_animation(
            story=test_story,
            target_duration=target_duration,
            style_hint=style_hint
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n📊 === RÉSULTATS ===")
        print(f"⏱️ Temps total: {total_time:.1f}s")
        print(f"📈 Status: {result.get('status')}")
        print(f"🆔 Animation ID: {result.get('animation_id')}")
        
        if result.get('status') == 'success':
            print(f"✅ Génération réussie!")
            print(f"🎬 URL vidéo: {result.get('videoUrl', 'N/A')}")
            print(f"⏱️ Durée réelle: {result.get('actual_duration', 0)}s")
            print(f"🎭 Nombre de scènes: {result.get('total_scenes', 0)}")
            print(f"🎨 Style: {result.get('visual_style', {}).get('name', 'N/A')}")
            
            # Détails techniques
            print(f"\n🔧 Détails techniques:")
            print(f"   Pipeline: {result.get('pipeline_type')}")
            print(f"   Qualité: {result.get('quality')}")
            print(f"   Temps génération: {result.get('generation_time')}s")
            
            # Scènes générées
            scenes = result.get('scenes', [])
            print(f"\n🎭 Scènes générées ({len(scenes)}):")
            for i, scene in enumerate(scenes, 1):
                duration = scene.get('duration', 0)
                description = scene.get('description', 'N/A')[:50]
                print(f"   {i}. [{duration}s] {description}...")
            
            return True
        else:
            print(f"❌ Échec de la génération:")
            print(f"   Erreur: {result.get('error', 'Inconnue')}")
            return False
            
    except Exception as e:
        print(f"💥 Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_services():
    """Test des services individuels"""
    
    print(f"\n🔧 === TEST SERVICES INDIVIDUELS ===")
    
    # Test 1: Story Analyzer
    try:
        from services.story_analyzer import StoryAnalyzer
        analyzer = StoryAnalyzer(os.getenv("OPENAI_API_KEY"))
        
        test_story = "Luna, une petite fille magique, sauve la forêt avec son ami renard."
        scenes = await analyzer.segment_story(test_story, 30, 5, 15)
        
        print(f"✅ Story Analyzer: {len(scenes)} scènes générées")
        
    except Exception as e:
        print(f"❌ Story Analyzer: {e}")
    
    # Test 2: Visual Style Generator
    try:
        from services.visual_style_generator import VisualStyleGenerator
        style_gen = VisualStyleGenerator(os.getenv("OPENAI_API_KEY"))
        
        style = await style_gen.generate_visual_style("Histoire de fée", "cartoon")
        
        print(f"✅ Visual Style Generator: {style.get('name', 'Style généré')}")
        
    except Exception as e:
        print(f"❌ Visual Style Generator: {e}")
    
    # Test 3: Video Prompt Generator
    try:
        from services.video_prompt_generator import VideoPromptGenerator
        prompt_gen = VideoPromptGenerator(os.getenv("OPENAI_API_KEY"))
        
        scenes = [{"description": "Luna dans la forêt", "duration": 10}]
        style = {"name": "Cartoon", "elements": ["couleurs vives", "formes douces"]}
        
        prompts = await prompt_gen.generate_prompts(scenes, style)
        
        print(f"✅ Video Prompt Generator: {len(prompts)} prompts générés")
        
    except Exception as e:
        print(f"❌ Video Prompt Generator: {e}")

if __name__ == "__main__":
    print("🎬 FRIDAY - Test Pipeline Animation")
    print("=" * 50)
    
    # Test des services individuels
    asyncio.run(test_individual_services())
    
    # Test de la pipeline complète
    success = asyncio.run(test_pipeline())
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 PIPELINE FONCTIONNELLE - Prête pour les tests utilisateur!")
        print("💡 Vous pouvez maintenant tester via:")
        print("   • Frontend React sur http://localhost:5173")
        print("   • API directe sur http://localhost:8000/api/animations/generate")
        print("   • Fichier main_new.py pour la nouvelle pipeline")
    else:
        print("⚠️ PROBLÈMES DÉTECTÉS - Vérifiez la configuration")
        print("🔧 Points à vérifier:")
        print("   • Clés API OpenAI et Stability AI")
        print("   • Installation des dépendances")
        print("   • Configuration .env")
