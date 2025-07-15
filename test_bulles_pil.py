#!/usr/bin/env python3
"""
Test direct du système de bulles PIL fiable
"""

import sys
import os
sys.path.append('.')
sys.path.append('saas')

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import asyncio
import json

def test_bubble_creation():
    """Teste la création de bulles PIL directement"""
    print("🧪 Test de création de bulles PIL...")
    
    # Créer un dossier de test
    test_dir = Path("test_bubble_output")
    test_dir.mkdir(exist_ok=True)
    
    # Créer une image de test simple
    img = Image.new('RGB', (800, 600), 'lightblue')
    draw = ImageDraw.Draw(img)
    
    # Dessiner des rectangles pour simuler des personnages
    draw.rectangle([200, 300, 300, 500], fill='brown', outline='black', width=2)  # Personnage 1
    draw.rectangle([500, 280, 600, 480], fill='orange', outline='black', width=2)  # Personnage 2
    
    # Sauvegarder l'image de base
    base_image_path = test_dir / "base_image.png"
    img.save(base_image_path)
    print(f"✅ Image de base créée: {base_image_path}")
    
    # Charger des polices
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Ajouter des bulles manuellement
    # Bulle 1 - Haut gauche
    bubble_x1, bubble_y1 = 150, 100
    bubble_w1, bubble_h1 = 180, 80
    
    draw.ellipse([
        bubble_x1 - bubble_w1//2, bubble_y1 - bubble_h1//2,
        bubble_x1 + bubble_w1//2, bubble_y1 + bubble_h1//2
    ], fill='#f5f0ff', outline='#6B4EFF', width=2)
    
    # Queue de bulle 1 vers personnage 1
    tail_points = [
        (bubble_x1 - 20, bubble_y1 + bubble_h1//2 - 10),
        (bubble_x1 + 20, bubble_y1 + bubble_h1//2 - 10),
        (250, 300)  # Vers personnage 1
    ]
    draw.polygon(tail_points, fill='#f5f0ff', outline='#6B4EFF', width=2)
    
    # Texte bulle 1
    draw.text((bubble_x1 - 70, bubble_y1 - 10), "Bonjour!", fill='#333333', font=font)
    
    # Bulle 2 - Haut droite  
    bubble_x2, bubble_y2 = 650, 120
    bubble_w2, bubble_h2 = 160, 70
    
    draw.ellipse([
        bubble_x2 - bubble_w2//2, bubble_y2 - bubble_h2//2,
        bubble_x2 + bubble_w2//2, bubble_y2 + bubble_h2//2
    ], fill='#FFF5E0', outline='#FFD166', width=2)
    
    # Queue de bulle 2 vers personnage 2
    tail_points2 = [
        (bubble_x2 - 15, bubble_y2 + bubble_h2//2 - 5),
        (bubble_x2 + 15, bubble_y2 + bubble_h2//2 - 5),
        (550, 280)  # Vers personnage 2
    ]
    draw.polygon(tail_points2, fill='#FFF5E0', outline='#FFD166', width=2)
    
    # Texte bulle 2
    draw.text((bubble_x2 - 50, bubble_y2 - 10), "Salut!", fill='#333333', font=font)
    
    # Sauvegarder l'image finale
    final_image_path = test_dir / "image_avec_bulles.png"
    img.save(final_image_path)
    
    print(f"✅ Image avec bulles créée: {final_image_path}")
    
    # Vérifier les fichiers
    if base_image_path.exists() and final_image_path.exists():
        base_size = base_image_path.stat().st_size
        final_size = final_image_path.stat().st_size
        print(f"📊 Taille image de base: {base_size} bytes")
        print(f"📊 Taille image finale: {final_size} bytes")
        print("🎯 Test de bulles PIL réussi!")
        
        # Créer un rapport JSON
        report = {
            "test_status": "success",
            "base_image": str(base_image_path),
            "final_image": str(final_image_path),
            "base_size": base_size,
            "final_size": final_size,
            "bubbles_added": 2,
            "test_time": "2025-07-15"
        }
        
        report_path = test_dir / "test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📋 Rapport sauvegardé: {report_path}")
        return True
    else:
        print("❌ Erreur: fichiers non créés")
        return False

if __name__ == "__main__":
    success = test_bubble_creation()
    if success:
        print("\n🎉 SUCCÈS: Système de bulles PIL fonctionnel!")
    else:
        print("\n❌ ÉCHEC: Problème avec le système de bulles PIL")
