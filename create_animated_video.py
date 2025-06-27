#!/usr/bin/env python3
"""
Générateur de vidéo simple utilisant PIL pour créer des images puis les assembler
"""
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
from pathlib import Path
import math

def create_frames_for_video(text, duration, output_dir, width=1280, height=720, fps=30):
    """Créer des frames d'image pour une vidéo"""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total_frames = int(duration * fps)
    
    # Couleurs pour l'animation
    colors = [
        (135, 206, 235),  # Sky blue
        (255, 182, 193),  # Light pink
        (144, 238, 144),  # Light green
        (255, 218, 185),  # Peach
        (221, 160, 221),  # Plum
    ]
    
    for frame_num in range(total_frames):
        # Créer une nouvelle image
        img = Image.new('RGB', (width, height), color=(50, 50, 50))
        draw = ImageDraw.Draw(img)
        
        # Progression de l'animation
        progress = frame_num / total_frames
        
        # Fond dégradé animé
        color_index = int(progress * len(colors)) % len(colors)
        bg_color = colors[color_index]
        
        # Créer un fond coloré
        for y in range(height):
            color_intensity = int(255 * (1 - y / height * 0.3))
            line_color = (
                min(255, bg_color[0] + color_intensity // 4),
                min(255, bg_color[1] + color_intensity // 4),
                min(255, bg_color[2] + color_intensity // 4)
            )
            draw.line([(0, y), (width, y)], fill=line_color)
        
        # Titre animé
        try:
            # Essayer une police système
            font_large = ImageFont.truetype("arial.ttf", 60)
            font_medium = ImageFont.truetype("arial.ttf", 40)
            font_small = ImageFont.truetype("arial.ttf", 30)
        except:
            # Fallback vers la police par défaut
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Titre principal
        title = "🎬 Animation IA"
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 4
        
        # Effet d'animation sur le titre
        title_offset = int(10 * math.sin(frame_num * 0.2))
        draw.text((title_x, title_y + title_offset), title, fill=(255, 255, 255), font=font_large)
        
        # Texte de description
        desc = text[:60] + "..." if len(text) > 60 else text
        desc_bbox = draw.textbbox((0, 0), desc, font=font_medium)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = (width - desc_width) // 2
        desc_y = height // 2
        draw.text((desc_x, desc_y), desc, fill=(255, 255, 255), font=font_medium)
        
        # Compteur de temps animé
        time_text = f"⏱️ {frame_num/fps:.1f}s / {duration}s"
        draw.text((50, height - 100), time_text, fill=(255, 255, 255), font=font_small)
        
        # Éléments animés
        # Cercles qui bougent
        for i in range(5):
            angle = frame_num * 0.1 + i * math.pi / 2.5
            center_x = width // 2 + int(100 * math.cos(angle))
            center_y = height * 3 // 4 + int(50 * math.sin(angle))
            radius = 20 + int(10 * math.sin(frame_num * 0.15 + i))
            
            circle_color = colors[i % len(colors)]
            draw.ellipse([
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius
            ], fill=circle_color)
        
        # Sauvegarder la frame
        frame_path = output_dir / f"frame_{frame_num:06d}.png"
        img.save(frame_path)
        
        if frame_num % 30 == 0:  # Log chaque seconde
            print(f"📸 Frame {frame_num}/{total_frames} créée")
    
    print(f"✅ {total_frames} frames créées dans {output_dir}")
    return total_frames

def frames_to_video_ffmpeg(frames_dir, output_video, fps=30):
    """Convertir les frames en vidéo avec FFmpeg"""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-framerate", str(fps),
        "-pattern_type", "glob",
        "-i", f"{frames_dir}/frame_*.png",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        str(output_video)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode == 0:
            return True
        else:
            print(f"❌ Erreur FFmpeg: {result.stderr.decode()}")
    except Exception as e:
        print(f"⚠️ FFmpeg non disponible: {e}")
    
    return False

def create_animated_video(text, duration, output_path):
    """Créer une vidéo animée complète"""
    
    # Répertoire temporaire pour les frames
    frames_dir = Path("temp_frames")
    frames_dir.mkdir(exist_ok=True)
    
    try:
        print(f"🎬 Création vidéo animée: {text[:30]}...")
        
        # Créer les frames
        total_frames = create_frames_for_video(text, duration, frames_dir)
        
        # Convertir en vidéo
        if frames_to_video_ffmpeg(frames_dir, output_path):
            print(f"✅ Vidéo créée: {output_path} ({Path(output_path).stat().st_size} bytes)")
            return True
        else:
            print("❌ Échec de la conversion vidéo")
            return False
    
    finally:
        # Nettoyer les frames temporaires
        try:
            import shutil
            shutil.rmtree(frames_dir)
        except:
            pass

if __name__ == "__main__":
    # Test
    output_path = Path("saas/cache/animations/animated_test_video.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    success = create_animated_video(
        "Un petit chat découvre un jardin magique où les fleurs chantent",
        10,
        output_path
    )
    
    if success:
        print(f"🎉 Vidéo test animée prête: {output_path}")
    else:
        print("❌ Échec de la création de vidéo animée")
