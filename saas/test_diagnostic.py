#!/usr/bin/env python3
"""
Script de test pour identifier les problèmes de génération
"""
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test des imports de base"""
    try:
        print("🔍 Test des imports...")
        
        # Test des imports principaux
        from fastapi import FastAPI
        print("✅ FastAPI - OK")
        
        from services.coloring_generator import ColoringGenerator
        print("✅ ColoringGenerator - OK")
        
        from services.tts import generate_speech
        print("✅ TTS - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_coloring_generator():
    """Test du générateur de coloriage"""
    try:
        print("\n🎨 Test du générateur de coloriage...")
        
        from services.coloring_generator import ColoringGenerator
        generator = ColoringGenerator()
        
        print(f"📁 Répertoire de sortie: {generator.output_dir}")
        print(f"🔑 Clé Stability: {'✅ Configurée' if generator.stability_key else '❌ Manquante'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générateur coloriage: {e}")
        return False

def test_endpoint_structure():
    """Test de la structure des endpoints"""
    try:
        print("\n🌐 Test de la structure des endpoints...")
        
        # Simuler les requests
        class MockRequest:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Test des modèles de requête
        rhyme_request = MockRequest(rhyme_type="animaux", custom_request=None)
        print(f"✅ RhymeRequest simulé: {rhyme_request.rhyme_type}")
        
        audio_request = MockRequest(story_type="aventure", voice=None, custom_request=None)
        print(f"✅ AudioStoryRequest simulé: {audio_request.story_type}")
        
        coloring_request = MockRequest(theme="licorne")
        print(f"✅ ColoringRequest simulé: {coloring_request.theme}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur structure endpoints: {e}")
        return False

if __name__ == "__main__":
    print("🧪 DIAGNOSTIC DES PROBLÈMES DE GÉNÉRATION")
    print("=" * 50)
    
    all_good = True
    
    # Tests des imports
    if not test_basic_imports():
        all_good = False
    
    # Test du générateur de coloriage
    if not test_coloring_generator():
        all_good = False
    
    # Test de la structure des endpoints
    if not test_endpoint_structure():
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ TOUS LES TESTS PASSENT - Le problème peut venir des clés API ou du réseau")
    else:
        print("❌ DES PROBLÈMES ONT ÉTÉ DÉTECTÉS - Voir les erreurs ci-dessus")
    
    print("\n💡 SOLUTIONS RECOMMANDÉES:")
    print("1. Vérifier les clés API dans le fichier .env")
    print("2. S'assurer que le serveur backend est accessible sur le port 8000")
    print("3. Vérifier la connectivité réseau pour les API externes")
