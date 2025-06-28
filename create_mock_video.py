#!/usr/bin/env python3
"""
Générateur de vidéo mock simple sans dépendances lourdes
"""

try:
    import cv2
    import numpy as np
except ImportError:
    print("OpenCV n'est pas installé. Installation avec: pip install opencv-python")
    # Créer des fonctions mock pour éviter les erreurs
    class MockCV2:
        @staticmethod
        def VideoWriter_fourcc(*args):
            return None
        
        @staticmethod
        def VideoWriter(output_path, fourcc, fps, size):
            return MockVideoWriter()
    
    class MockVideoWriter:
        def write(self, frame):
            pass
        
        def release(self):
            pass
    
    cv2 = MockCV2()
    
    class MockNumpy:
        @staticmethod
        def zeros(shape, dtype=None):
            return []
        
        @staticmethod
        def uint8():
            return 'uint8'
    
    np = MockNumpy()

import os
from pathlib import Path

def create_simple_video(text, duration, output_path, width=1280, height=720, fps=30):
    """Créer une vidéo simple avec du texte"""
    
    # Créer le writer vidéo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    total_frames = int(duration * fps)
    
    for frame_num in range(total_frames):
        # Créer une image avec fond coloré
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Couleur de fond qui change avec le temps
        progress = frame_num / total_frames
        hue = int(180 * progress)  # Cycle de couleurs
        
        # Convertir HSV vers BGR
        hsv_color = np.uint8([[[hue, 255, 200]]])
        bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
        img[:] = bgr_color
        
        # Ajouter du texte
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        color = (255, 255, 255)  # Blanc
        thickness = 3
        
        # Titre principal
        title = "🎬 Animation CrewAI"
        text_size = cv2.getTextSize(title, font, font_scale, thickness)[0]
        x = (width - text_size[0]) // 2
        y = height // 3
        cv2.putText(img, title, (x, y), font, font_scale, color, thickness)
        
        # Description
        desc = text[:40] + "..." if len(text) > 40 else text
        text_size = cv2.getTextSize(desc, font, 0.8, 2)[0]
        x = (width - text_size[0]) // 2
        y = height // 2
        cv2.putText(img, desc, (x, y), font, 0.8, color, 2)
        
        # Compteur de temps
        time_text = f"{frame_num/fps:.1f}s / {duration}s"
        cv2.putText(img, time_text, (50, height - 50), font, 0.7, color, 2)
        
        # Ajouter quelques formes animées
        center_x = width // 2
        center_y = height * 2 // 3
        radius = int(50 + 30 * np.sin(frame_num * 0.2))
        cv2.circle(img, (center_x, center_y), radius, (255, 255, 255), 3)
        
        out.write(img)
    
    out.release()
    print(f"✅ Vidéo mock créée: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    # Test de génération
    output_path = Path("saas/cache/crewai_animations/test_mock_video.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    create_simple_video(
        "Un petit chat découvre un jardin magique",
        10,  # 10 secondes
        output_path
    )
    
    print(f"🎥 Vidéo de test générée: {output_path}")
    print(f"📐 Taille: {output_path.stat().st_size} bytes")
