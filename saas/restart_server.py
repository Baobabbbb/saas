#!/usr/bin/env python3
"""
Script pour redémarrer le serveur FastAPI avec le code corrigé
"""

import uvicorn
import os
import sys

# Changer vers le répertoire du script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🔄 Redémarrage du serveur FastAPI avec les corrections...")
print("📁 Répertoire de travail:", os.getcwd())

try:
    # Tester l'import du module principal
    print("🧪 Test d'import du module main...")
    import main
    print("✅ Module main importé avec succès")
    
    # Tester l'import des dépendances SEEDANCE
    print("🧪 Test d'import SEEDANCE...")
    from config.seedance_stories import SEEDANCE_STORIES, get_story_by_theme_and_title
    print(f"✅ SEEDANCE importé: {len(SEEDANCE_STORIES)} thèmes disponibles")
    
    # Démarrer le serveur
    print("🚀 Démarrage du serveur sur http://localhost:8000...")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
