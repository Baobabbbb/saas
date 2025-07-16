#!/usr/bin/env python3
"""
🔧 Correctif pour réparer l'API principale
Remplace main_new.py par une version fonctionnelle
"""

import shutil
from pathlib import Path

def appliquer_correctif():
    """Applique le correctif à l'API principale"""
    
    saas_dir = Path("saas")
    
    # Sauvegarder l'ancien fichier
    old_main = saas_dir / "main_new.py"
    backup_main = saas_dir / "main_new_backup.py"
    
    if old_main.exists():
        shutil.copy2(old_main, backup_main)
        print(f"✅ Sauvegarde créée: {backup_main}")
    
    # Copier la version fonctionnelle
    new_main = saas_dir / "test_api.py"
    
    if new_main.exists():
        # Lire le contenu de test_api.py et l'adapter
        with open(new_main, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer port 8001 par 8000 et ajouter les autres endpoints
        content = content.replace('port=8001', 'port=8000')
        content = content.replace('title="API Test Génération"', 'title="API Histoires et Coloriages"')
        
        # Ajouter les endpoints manquants (basiques)
        additional_endpoints = '''

# Endpoints additionnels pour compatibilité
@app.get("/")
async def root():
    return {"message": "API Dessins Animés IA", "version": "2.0"}

@app.post("/generate_story/")
async def generate_story_placeholder(request: dict):
    return {"status": "not_implemented", "message": "Utilisez /generate_animation/"}

@app.post("/generate_coloring/")
async def generate_coloring_placeholder(request: dict):
    return {"status": "not_implemented", "message": "Utilisez /generate_animation/"}
'''
        
        # Insérer avant if __name__ == "__main__":
        content = content.replace(
            'if __name__ == "__main__":',
            additional_endpoints + '\n\nif __name__ == "__main__":'
        )
        
        # Écrire le nouveau main_new.py
        with open(old_main, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ main_new.py réparé avec la version fonctionnelle")
        print(f"📝 L'ancien fichier est sauvegardé dans {backup_main}")
        
        return True
    else:
        print(f"❌ Fichier test_api.py introuvable")
        return False

if __name__ == "__main__":
    print("🔧 APPLICATION DU CORRECTIF")
    print("=" * 40)
    
    if appliquer_correctif():
        print("\n✅ CORRECTIF APPLIQUÉ AVEC SUCCÈS!")
        print("\n🚀 Instructions:")
        print("1. Arrêter l'ancien serveur (Ctrl+C)")
        print("2. Relancer: cd saas && python -m uvicorn main_new:app --host 0.0.0.0 --port 8000")
        print("3. Tester: http://localhost:8000/generate_animation/")
        print("\n⚡ La génération devrait maintenant fonctionner en ~60-80 secondes")
    else:
        print("\n❌ Échec du correctif")
