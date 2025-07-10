#!/usr/bin/env python3
"""
Test pour vérifier les durées des vidéos générées
"""

import os
from pathlib import Path

def check_video_files():
    """Vérifie les fichiers vidéo dans le cache SEEDANCE"""
    cache_dir = Path("cache/seedance")
    
    print("🎬 Vérification des fichiers vidéo SEEDANCE...")
    
    if not cache_dir.exists():
        print("❌ Répertoire cache/seedance n'existe pas")
        return
    
    video_files = list(cache_dir.glob("*.mp4"))
    
    if not video_files:
        print("❌ Aucun fichier vidéo trouvé")
        return
    
    print(f"✅ {len(video_files)} fichiers vidéo trouvés:")
    
    for video_file in video_files:
        file_size = video_file.stat().st_size
        print(f"   📹 {video_file.name}")
        print(f"      📊 Taille: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Essayer de lire la durée avec ffprobe si disponible
        try:
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', str(video_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                print(f"      ⏱️ Durée: {duration:.2f}s")
            else:
                print(f"      ⏱️ Durée: Impossible à lire")
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            print(f"      ⏱️ Durée: FFprobe non disponible")
        
        print()

if __name__ == "__main__":
    check_video_files()
