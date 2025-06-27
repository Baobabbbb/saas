"""
Service d'animation simplifié pour tests de durée
"""
import json
import time
from typing import Dict, Any, List

class SimpleDurationService:
    """Service simplifié pour tester les durées"""
    
    def __init__(self):
        pass
    
    def correct_scene_durations(self, scenes: List[Dict], target_duration: int) -> List[Dict]:
        """Corriger les durées des scènes pour respecter la durée totale exacte"""
        
        if not scenes:
            return scenes
            
        print(f"🔧 Correction durées: {len(scenes)} scènes pour {target_duration}s total")
        
        # Calculer la durée actuelle
        current_total = sum(scene.get('duration', 0) for scene in scenes)
        print(f"📊 Durée actuelle: {current_total}s, cible: {target_duration}s")
        
        if current_total == target_duration:
            print("✅ Durées déjà correctes")
            return scenes
            
        # Stratégie de correction intelligente
        num_scenes = len(scenes)
        
        if target_duration <= 12:
            # Pour de courtes durées, répartition égale avec ajustements
            base_duration = target_duration // num_scenes
            remainder = target_duration % num_scenes
            
            for i, scene in enumerate(scenes):
                scene['duration'] = base_duration + (1 if i < remainder else 0)
                
        else:
            # Pour des durées plus longues, répartition proportionnelle intelligente
            if num_scenes == 3:
                # Répartition 30%, 40%, 30% pour 3 scènes
                scenes[0]['duration'] = round(target_duration * 0.3)
                scenes[1]['duration'] = round(target_duration * 0.4) 
                scenes[2]['duration'] = target_duration - scenes[0]['duration'] - scenes[1]['duration']
            elif num_scenes == 4:
                # Répartition 25%, 30%, 30%, 15% pour 4 scènes
                scenes[0]['duration'] = round(target_duration * 0.25)
                scenes[1]['duration'] = round(target_duration * 0.30)
                scenes[2]['duration'] = round(target_duration * 0.30)
                scenes[3]['duration'] = target_duration - sum(s['duration'] for s in scenes[:3])
            else:
                # Répartition égale avec ajustements
                base_duration = target_duration // num_scenes
                remainder = target_duration % num_scenes
                
                for i, scene in enumerate(scenes):
                    scene['duration'] = base_duration + (1 if i < remainder else 0)
        
        # Vérification finale
        final_total = sum(scene['duration'] for scene in scenes)
        print(f"✅ Durées corrigées: {final_total}s (cible: {target_duration}s)")
        
        # Afficher le détail
        durations = [f"Scène {i+1}: {scene['duration']}s" for i, scene in enumerate(scenes)]
        print(f"📋 Répartition: {', '.join(durations)}")
        
        return scenes

    async def generate_simple_animation(self, story: str, style_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Générer une animation simple sans CrewAI, juste pour tester les durées"""
        
        target_duration = int(style_preferences.get('duration', 25))
        style = style_preferences.get('style', 'cartoon')
        theme = style_preferences.get('theme', 'animals')
        
        print(f"🎬 === GÉNÉRATION SIMPLE POUR TEST DURÉE ===")
        print(f"📖 Histoire: {story}")
        print(f"🎨 Style: {style}")
        print(f"⏱️ Durée: {target_duration}s")
        
        # Créer des scènes par défaut
        if target_duration <= 15:
            num_scenes = 3
        else:
            num_scenes = 4
            
        # Scènes de base avec durées incorrectes (pour tester la correction)
        base_scenes = []
        for i in range(num_scenes):
            base_scenes.append({
                "scene_number": i + 1,
                "duration": 8,  # Durée intentionnellement incorrecte
                "description": f"Scène {i + 1}: {story[:30]}...",
                "action": f"Action {i + 1}",
                "setting": f"Décor {i + 1}",
                "status": "generated",
                "prompt": f"Scene {i + 1} prompt",
                "image_url": f"/cache/crewai_animations/scene_{i + 1}_test.jpg",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            })
        
        print(f"📋 Scènes avant correction: {[s['duration'] for s in base_scenes]} = {sum(s['duration'] for s in base_scenes)}s")
        
        # Appliquer la correction des durées
        corrected_scenes = self.correct_scene_durations(base_scenes, target_duration)
        
        # Calculer la durée totale finale
        final_total = sum(scene['duration'] for scene in corrected_scenes)
        
        # Résultat
        result = {
            "status": "success",
            "type": "simple_duration_test",
            "videoUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",  # Frontend attend videoUrl
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",  # Compatibilité
            "scenes_count": len(corrected_scenes),
            "total_duration": final_total,
            "duration_requested": target_duration,
            "duration_respected": final_total == target_duration,
            "scenes": corrected_scenes,  # Pour compatibilité avec les tests
            "scenes_details": corrected_scenes,  # Pour compatibilité avec les tests
            "generation_time": 1.0,
            "pipeline_type": "simple_duration_test",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "story_input": story,
            "style_preferences": style_preferences,
            "note": "✅ Test simple de respect des durées"
        }
        
        print(f"🎉 Test durée terminé!")
        print(f"   🎬 {len(corrected_scenes)} scènes")
        print(f"   ⏱️ {final_total}s total (demandé: {target_duration}s)")
        print(f"   🎯 Respect durée: {'✅' if final_total == target_duration else '❌'}")
        
        return result
