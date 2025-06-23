#!/usr/bin/env python3
"""
Test simple du générateur de coloriage
"""
import sys
import os

# Ajouter le répertoire au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.coloring_generator import ColoringGenerator
    
    print("✅ Import du ColoringGenerator réussi")
    
    generator = ColoringGenerator()
    print(f"📁 Répertoire de sortie: {generator.output_dir}")
    
    # Test du prompt
    prompt = generator._create_single_coloring_prompt('licorne')
    print(f"📝 Prompt généré: {prompt}")
    
    # Test de la clé API
    has_valid_key = generator.stability_key and 'sk-' in generator.stability_key
    print(f"🔑 API Stability: {'✅ Configurée' if has_valid_key else '❌ Mode fallback'}")
    
    if has_valid_key:
        print("🎨 Le système utilisera Stable Diffusion pour générer de vrais coloriages")
    else:
        print("🎨 Le système utilisera le mode fallback (dessins simples)")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
