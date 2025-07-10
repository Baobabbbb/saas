#!/usr/bin/env python3
"""
Test de cohérence narrative SEEDANCE
Vérifie que les histoires générées respectent la structure narrative et la cohérence thématique
"""

import asyncio
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent))

from services.seedance_service import SeedanceService
from config.seedance_stories import SEEDANCE_STORIES

async def test_narrative_coherence():
    """Teste la cohérence narrative pour différents thèmes"""
    print("🎭 Test de cohérence narrative SEEDANCE")
    print("=" * 60)
    
    # Initialiser le service
    service = SeedanceService()
    
    # Obtenir les histoires disponibles
    stories = SEEDANCE_STORIES
    
    # Sélectionner quelques thèmes pour test
    test_themes = ['space', 'nature', 'animals', 'ocean', 'friendship']
    
    for theme in test_themes:
        if theme not in stories:
            print(f"⚠️ Thème '{theme}' non trouvé dans les histoires")
            continue
            
        print(f"\n🎬 Test du thème: {theme.upper()}")
        print("-" * 40)
        
        # Prendre la première histoire du thème
        theme_stories = stories[theme].get('stories', [])
        if not theme_stories:
            print(f"❌ Aucune histoire trouvée pour le thème {theme}")
            continue
            
        # Obtenir le titre de la première histoire
        first_story = theme_stories[0]
        if isinstance(first_story, dict):
            story_title = first_story.get('title', first_story.get('story', 'Histoire inconnue'))
        else:
            story_title = str(first_story)
        print(f"📖 Histoire: {story_title}")
        
        try:
            # Tester la génération d'idées
            print("💡 Test génération d'idées...")
            idea_result = await service._generate_ideas(
                story=story_title,
                theme=theme,
                age_target="3-5 ans",
                style="cartoon"
            )
            
            if idea_result:
                print(f"   ✅ Idée: {idea_result.get('Idea', 'N/A')[:80]}...")
                print(f"   🌍 Environnement: {idea_result.get('Environment', 'N/A')}")
                print(f"   👥 Personnages: {idea_result.get('Characters', 'N/A')}")
                print(f"   📚 Valeur éducative: {idea_result.get('Educational_Value', 'N/A')}")
            else:
                print("   ❌ Échec génération d'idées")
                continue
            
            # Tester la génération de scènes
            print("📝 Test génération de scènes...")
            scenes = await service._generate_scene_prompts(idea_result, 30)
            
            if scenes and len(scenes) == 3:
                print(f"   ✅ {len(scenes)} scènes générées")
                
                # Vérifier la progression narrative
                scene_types = [scene.get('scene_type', '') for scene in scenes]
                expected_types = ['Introduction', 'Development', 'Resolution']
                
                if scene_types == expected_types:
                    print("   ✅ Structure narrative correcte: Introduction → Développement → Résolution")
                else:
                    print(f"   ⚠️ Structure narrative: {' → '.join(scene_types)}")
                
                # Analyser chaque scène
                for i, scene in enumerate(scenes):
                    scene_type = scene.get('scene_type', f'Scene{i+1}')
                    description = scene.get('description', '')
                    print(f"   📋 Scène {i+1} ({scene_type}): {description[:100]}...")
                    
                    # Vérifier que la description contient des éléments du thème
                    theme_check = await verify_theme_coherence(description, theme, idea_result)
                    if theme_check:
                        print(f"      ✅ Cohérence thématique vérifiée")
                    else:
                        print(f"      ⚠️ Possible incohérence thématique")
            else:
                print(f"   ❌ Échec génération scènes: {len(scenes) if scenes else 0} scènes")
            
            print(f"   ⏱️ Test terminé pour {theme}")
            
        except Exception as e:
            print(f"   ❌ Erreur test {theme}: {e}")
        
        # Pause entre les tests
        await asyncio.sleep(2)
    
    print(f"\n🏁 Test de cohérence narrative terminé")

async def verify_theme_coherence(description: str, theme: str, idea_result: Dict[str, Any]) -> bool:
    """Vérifie que la description est cohérente avec le thème"""
    description_lower = description.lower()
    
    # Mots-clés par thème
    theme_keywords = {
        'space': ['espace', 'vaisseau', 'spatial', 'planète', 'étoile', 'astronaute', 'cosmos', 'galaxie'],
        'nature': ['nature', 'arbre', 'forêt', 'plante', 'fleur', 'jardin', 'écosystème', 'environnement'],
        'animals': ['animal', 'animaux', 'chien', 'chat', 'oiseau', 'lion', 'tigre', 'ferme', 'zoo'],
        'ocean': ['océan', 'mer', 'poisson', 'requin', 'baleine', 'corail', 'plongée', 'sous-marin'],
        'friendship': ['ami', 'amitié', 'ensemble', 'partage', 'aide', 'copain', 'solidarité', 'équipe']
    }
    
    keywords = theme_keywords.get(theme, [])
    
    # Vérifier la présence de mots-clés du thème
    theme_match = any(keyword in description_lower for keyword in keywords)
    
    # Vérifier la cohérence avec les personnages et l'environnement
    characters = idea_result.get('Characters', '').lower()
    environment = idea_result.get('Environment', '').lower()
    
    character_match = any(char in description_lower for char in characters.split() if len(char) > 2)
    environment_match = any(env in description_lower for env in environment.split() if len(env) > 2)
    
    return theme_match or character_match or environment_match

async def test_single_generation():
    """Test complet d'une génération pour vérifier la cohérence"""
    print("\n🎯 Test de génération complète")
    print("=" * 40)
    
    service = SeedanceService()
    
    # Test avec un thème spécifique
    test_params = {
        'story': 'Les Amis de la Forêt',
        'theme': 'nature',
        'age_target': '3-5 ans',
        'duration': 30,
        'style': 'cartoon'
    }
    
    print(f"📖 Histoire: {test_params['story']}")
    print(f"🎭 Thème: {test_params['theme']}")
    print(f"👶 Age: {test_params['age_target']}")
    print(f"⏱️ Durée: {test_params['duration']}s")
    
    try:
        result = await service.generate_seedance_animation(**test_params)
        
        if result.get('status') == 'success':
            print("\n✅ Génération réussie!")
            print(f"🎬 ID Animation: {result.get('animation_id')}")
            print(f"📹 URL Vidéo: {result.get('video_url')}")
            print(f"⏱️ Durée actuelle: {result.get('actual_duration')}s")
            print(f"🎞️ Scènes: {result.get('scenes_count')}")
            print(f"🔄 Statut assemblage: {result.get('assembly_status')}")
            
            # Analyser les scènes
            scenes = result.get('scenes', [])
            print(f"\n📋 Analyse des scènes ({len(scenes)} scènes):")
            for scene in scenes:
                print(f"   🎬 Scène {scene.get('scene_number')}: {scene.get('description', '')[:80]}...")
            
            # Vérifier la vidéo générée
            video_path = result.get('video_path')
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                print(f"📁 Fichier vidéo: {video_path}")
                print(f"📊 Taille: {file_size / (1024*1024):.1f} MB")
            
        else:
            print(f"❌ Échec génération: {result.get('status')}")
            
    except Exception as e:
        print(f"❌ Erreur test complet: {e}")

if __name__ == "__main__":
    # Test de cohérence narrative
    asyncio.run(test_narrative_coherence())
    
    # Test de génération complète
    asyncio.run(test_single_generation())
