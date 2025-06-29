# Images de test pour les animations
# Ces fichiers seront utilisés comme aperçu pendant le développement

import os
import json
from pathlib import Path

# Créer le répertoire cache s'il n'existe pas
cache_dir = Path("cache/animations")
cache_dir.mkdir(parents=True, exist_ok=True)

# Créer des métadonnées de test avec des images par défaut
test_scenes = [
    {
        "scene_number": 1,
        "description": "Un petit lapin curieux dans un jardin coloré",
        "duration": 10,
        "image_placeholder": "🐰🌸"
    },
    {
        "scene_number": 2, 
        "description": "Le lapin découvre des fleurs magiques qui brillent",
        "duration": 10,
        "image_placeholder": "✨🌺"
    },
    {
        "scene_number": 3,
        "description": "Des papillons colorés dansent autour du lapin",
        "duration": 10,
        "image_placeholder": "🦋🌈"
    }
]

for i, scene in enumerate(test_scenes, 1):
    # Créer un fichier JSON pour la scène de test
    scene_file = cache_dir / f"scene_{i}_test.json"
    with open(scene_file, 'w', encoding='utf-8') as f:
        json.dump(scene, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Scène de test {i} créée: {scene_file}")

print("\n🎬 Images de test créées pour démonstration")
print("   Ces fichiers serviront d'aperçu en attendant la génération DALL-E")
