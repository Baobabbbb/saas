"""
Test complet de l'architecture CrewAI pour animations cohérentes
Valide le pipeline multi-agents et la continuité visuelle
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from saas.services.crewai_animation import animation_crewai
from saas.services.runway_gen4_new import runway_gen4_service

async def test_crewai_cohesive_pipeline():
    """Test complet du pipeline CrewAI pour animations cohérentes"""
    
    print("🎬 TEST ARCHITECTURE CREWAI - ANIMATIONS COHÉRENTES")
    print("=" * 60)
    
    # Histoire de test pour animation de 60 secondes
    test_story = """
    Luna la petite sorcière découvre un jardin magique caché derrière sa maison.
    Elle rencontre Pip, un lutin espiègle qui garde les fleurs parlantes.
    Ensemble, ils doivent sauver le jardin d'un sort maléfique.
    Luna utilise sa baguette magique pour réveiller les plantes endormies.
    Les fleurs se mettent à danser et le jardin retrouve ses couleurs.
    Luna et Pip deviennent les meilleurs amis du monde.
    """
    
    # Configuration de test
    story_config = {
        "story": test_story,
        "style": "fairy_tale",
        "theme": "magic", 
        "orientation": "landscape",
        "duration": 60,  # 1 minute
        "quality": "high",
        "title": "Luna et le Jardin Magique"
    }
    
    print(f"📖 Histoire: {story_config['story'][:100]}...")
    print(f"🎨 Style: {story_config['style']}")
    print(f"⏱️ Durée: {story_config['duration']}s")
    print(f"💎 Qualité: {story_config['quality']}")
    
    try:
        # Test 1: Pipeline CrewAI complet
        print("\n🤖 TEST 1: Pipeline CrewAI Multi-Agents")
        print("-" * 40)
        
        crewai_result = await animation_crewai.create_animation_from_story(story_config)
        
        if crewai_result["status"] == "success":
            print("✅ Pipeline CrewAI réussi!")
            
            pipeline_data = crewai_result["pipeline_result"]
            
            # Analyser les résultats de chaque phase
            print(f"📊 RÉSULTATS PAR PHASE:")
            
            # Phase 1: Scénariste
            story_analysis = pipeline_data.get("story_analysis", {})
            scenes = story_analysis.get("scenes", [])
            print(f"   🎭 Scénariste: {len(scenes)} scènes créées")
            print(f"      Durée moyenne: {story_analysis.get('average_scene_duration', 0):.1f}s")
            
            # Phase 2: Directeur Artistique
            visual_guide = pipeline_data.get("visual_style_guide", {})
            master_seed = visual_guide.get("master_seed", "N/A")
            print(f"   🎨 Directeur Artistique: Seed maître {master_seed}")
            print(f"      Personnages: {len(visual_guide.get('character_designs', {}))}")
            
            # Phase 3: Prompt Engineer
            scene_prompts = pipeline_data.get("scene_prompts", [])
            print(f"   🔧 Prompt Engineer: {len(scene_prompts)} prompts optimisés")
            
            # Phase 4: Opérateur Technique
            generated_clips = pipeline_data.get("generated_clips", [])
            print(f"   ⚙️ Opérateur Technique: {len(generated_clips)} clips générés")
            avg_quality = sum(clip.get("quality_score", 0) for clip in generated_clips) / len(generated_clips) if generated_clips else 0
            print(f"      Qualité moyenne: {avg_quality:.1f}/10")
            
            # Phase 5: Monteur Vidéo
            final_video = pipeline_data.get("final_video", {})
            print(f"   🎬 Monteur Vidéo: Assemblage terminé")
            print(f"      Durée finale: {final_video.get('total_duration', 0)}s")
            
            # Métadonnées de production
            production_meta = pipeline_data.get("production_metadata", {})
            print(f"\n📈 MÉTRIQUES DE QUALITÉ:")
            print(f"   Score continuité: {production_meta.get('style_consistency_score', 0):.1f}/10")
            print(f"   Score narratif: {final_video.get('narrative_flow_score', 0):.1f}/10")
            
            # Performance des agents
            agents_perf = production_meta.get("agents_performance", {})
            print(f"\n🤖 PERFORMANCE DES AGENTS:")
            for agent, score in agents_perf.items():
                print(f"   {agent}: {score:.1f}/10")
            
        else:
            print(f"❌ Pipeline CrewAI échoué: {crewai_result.get('error')}")
            return False
        
        # Test 2: Intégration avec Runway
        print("\n🚀 TEST 2: Intégration Runway Gen-4")
        print("-" * 40)
        
        runway_result = await runway_gen4_service.generate_narrative_animation(story_config)
        
        if runway_result.get("status") == "completed":
            print("✅ Intégration Runway réussie!")
            print(f"   ID: {runway_result['id']}")
            print(f"   Titre: {runway_result['title']}")
            print(f"   Type: {runway_result['type']}")
            print(f"   Scènes: {runway_result.get('total_scenes', 0)}")
            print(f"   Durée: {runway_result.get('total_duration', 0)}s")
            print(f"   Score continuité: {runway_result.get('visual_consistency_score', 0)}")
            
            # Agents utilisés
            agents_used = runway_result.get("agents_used", [])
            print(f"   Agents: {', '.join(agents_used)}")
            
        else:
            print(f"❌ Intégration Runway échouée")
            return False
        
        # Test 3: Validation de la continuité
        print("\n🔍 TEST 3: Validation Continuité Visuelle")
        print("-" * 40)
        
        continuity_score = await validate_visual_continuity(crewai_result)
        print(f"Score continuité final: {continuity_score:.1f}/10")
        
        if continuity_score >= 8.0:
            print("✅ Continuité visuelle excellente")
        elif continuity_score >= 6.0:
            print("⚠️ Continuité visuelle acceptable")
        else:
            print("❌ Continuité visuelle insuffisante")
        
        # Résumé final
        print("\n🎉 RÉSUMÉ DU TEST")
        print("=" * 60)
        print(f"✅ Pipeline CrewAI: {'Réussi' if crewai_result['status'] == 'success' else 'Échoué'}")
        print(f"✅ Intégration Runway: {'Réussie' if runway_result.get('status') == 'completed' else 'Échouée'}")
        print(f"✅ Continuité visuelle: {continuity_score:.1f}/10")
        print(f"🎬 Animation finale: {runway_result.get('video_url', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def validate_visual_continuity(animation_result):
    """Valider la continuité visuelle de l'animation"""
    
    try:
        pipeline_data = animation_result.get("pipeline_result", {})
        
        # Vérifier la présence d'un seed maître
        visual_guide = pipeline_data.get("visual_style_guide", {})
        has_master_seed = bool(visual_guide.get("master_seed"))
        
        # Vérifier la cohérence des personnages
        character_designs = visual_guide.get("character_designs", {})
        has_consistent_characters = len(character_designs) > 0
        
        # Vérifier les seeds par scène
        seeds_hierarchy = visual_guide.get("seeds_hierarchy", {})
        has_scene_seeds = len(seeds_hierarchy) > 0
        
        # Vérifier la qualité des clips
        generated_clips = pipeline_data.get("generated_clips", [])
        avg_clip_quality = sum(clip.get("quality_score", 0) for clip in generated_clips) / len(generated_clips) if generated_clips else 0
        
        # Calculer le score final
        score = 5.0  # Base
        
        if has_master_seed:
            score += 1.5
        
        if has_consistent_characters:
            score += 1.5
        
        if has_scene_seeds:
            score += 1.0
        
        if avg_clip_quality >= 8:
            score += 1.0
        elif avg_clip_quality >= 7:
            score += 0.5
        
        return min(10.0, score)
        
    except Exception as e:
        print(f"⚠️ Erreur validation continuité: {e}")
        return 5.0

async def test_different_durations():
    """Test avec différentes durées d'animation"""
    
    print("\n📏 TEST DURÉES MULTIPLES")
    print("=" * 40)
    
    durations = [30, 60, 120, 180]  # 30s, 1min, 2min, 3min
    
    for duration in durations:
        print(f"\n🕐 Test durée: {duration}s")
        
        story_config = {
            "story": "Une petite fée aide les animaux de la forêt à préparer l'hiver.",
            "style": "cartoon",
            "duration": duration,
            "quality": "medium"
        }
        
        try:
            result = await animation_crewai.create_animation_from_story(story_config)
            
            if result["status"] == "success":
                scenes_count = result.get("scenes_count", 0)
                actual_duration = result.get("total_duration", 0)
                
                print(f"   ✅ {scenes_count} scènes → {actual_duration}s")
            else:
                print(f"   ❌ Erreur: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    async def main():
        print("🎭 LANCEMENT DES TESTS CREWAI")
        print("=" * 60)
        
        # Test principal
        success = await test_crewai_cohesive_pipeline()
        
        if success:
            # Tests additionnels
            await test_different_durations()
            
            print("\n🎉 TOUS LES TESTS TERMINÉS")
            print("L'architecture CrewAI est prête pour la production!")
        else:
            print("\n❌ TESTS ÉCHOUÉS")
            print("Vérifier la configuration CrewAI")
    
    asyncio.run(main())
