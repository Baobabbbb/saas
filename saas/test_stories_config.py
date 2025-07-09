#!/usr/bin/env python3
"""Test script for SEEDANCE stories API"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.seedance_stories import SEEDANCE_STORIES, get_story_by_theme_and_title

# Test the stories configuration
print("=== Test Configuration SEEDANCE ===")
print(f"Nombre de thèmes: {len(SEEDANCE_STORIES)}")

for theme_key, theme_data in SEEDANCE_STORIES.items():
    print(f"\n🎯 Thème: {theme_key}")
    print(f"   Titre: {theme_data['title']}")
    print(f"   Icône: {theme_data['icon']}")
    print(f"   Histoires: {len(theme_data['stories'])}")
    
    for story in theme_data['stories']:
        print(f"      - {story['title']} ({story['age_target']})")

# Test retrieval function
print("\n=== Test Récupération d'Histoire ===")
test_story = get_story_by_theme_and_title("space", "Le Petit Astronaute")
if test_story:
    print(f"✅ Histoire trouvée: {test_story['title']}")
    print(f"   Description: {test_story['description']}")
    print(f"   Âge cible: {test_story['age_target']}")
    print(f"   Contenu: {test_story['story'][:100]}...")
else:
    print("❌ Histoire non trouvée")

# Test with invalid parameters
invalid_story = get_story_by_theme_and_title("invalid_theme", "Invalid Story")
if invalid_story:
    print("❌ Erreur: Histoire trouvée avec paramètres invalides")
else:
    print("✅ Gestion correcte des paramètres invalides")

print("\n=== Test terminé ===")
