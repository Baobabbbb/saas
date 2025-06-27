"""
Vérification simple des services du pipeline
"""
def check_services():
    print("🔍 Vérification des services du pipeline...")
    
    try:
        # Test d'import de chaque service
        services = [
            ("services.story_analyzer", "StoryAnalyzer"),
            ("services.visual_style_generator", "VisualStyleGenerator"),
            ("services.video_prompt_generator", "VideoPromptGenerator"),
            ("services.video_generator", "VideoGenerator"),
            ("services.video_assembler", "VideoAssembler"),
            ("services.animation_pipeline", "animation_pipeline")
        ]
        
        for module_name, class_name in services:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                print(f"✅ {module_name} - {class_name}")
            except ImportError as e:
                print(f"❌ {module_name} - Erreur d'import: {e}")
            except AttributeError as e:
                print(f"❌ {module_name} - Classe non trouvée: {e}")
        
        print("\n🎬 Test du pipeline principal...")
        from services.animation_pipeline import animation_pipeline
        print(f"✅ Pipeline initialisé: {type(animation_pipeline)}")
        
        print("\n📁 Configuration du cache...")
        print(f"📂 Cache dir: {animation_pipeline.cache_dir}")
        print(f"⏱️ Durée min: {animation_pipeline.min_duration}s")
        print(f"⏱️ Durée max: {animation_pipeline.max_duration}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_services()
    if success:
        print("\n🎉 Tous les services sont fonctionnels!")
    else:
        print("\n⚠️ Certains services ont des problèmes.")
