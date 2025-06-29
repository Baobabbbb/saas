#!/usr/bin/env python3
"""
Créer des images de démonstration SVG pour les animations
"""

import os
from pathlib import Path

# Créer le répertoire des images de démonstration
demo_dir = Path("cache/animations/demo_images")
demo_dir.mkdir(parents=True, exist_ok=True)

# Templates d'images SVG pour différentes scènes
svg_templates = [
    # Scène 1 - Personnage principal
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sky1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#87CEEB;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#98FB98;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#sky1)"/>
  <circle cx="100" cy="180" r="30" fill="#8B4513"/>
  <circle cx="85" cy="170" r="3" fill="#000"/>
  <circle cx="115" cy="170" r="3" fill="#000"/>
  <ellipse cx="100" cy="185" rx="8" ry="4" fill="#FFB6C1"/>
  <rect x="80" y="130" width="40" height="20" rx="20" fill="#8B4513"/>
  <rect x="95" y="120" width="10" height="15" rx="5" fill="#8B4513"/>
  <text x="200" y="50" font-family="Arial" font-size="24" fill="#4169E1">Scène 1</text>
  <text x="200" y="80" font-family="Arial" font-size="16" fill="#000">Le petit héros apparaît</text>
</svg>""",
    
    # Scène 2 - Jardin magique
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="magic1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#FFD700;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#98FB98;stop-opacity:1" />
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#magic1)"/>
  <circle cx="150" cy="250" r="25" fill="#FF69B4"/>
  <rect x="145" y="275" width="10" height="25" fill="#228B22"/>
  <circle cx="250" cy="240" r="20" fill="#FF1493"/>
  <rect x="246" y="260" width="8" height="40" fill="#228B22"/>
  <circle cx="320" cy="230" r="30" fill="#9370DB"/>
  <rect x="315" y="260" width="10" height="40" fill="#228B22"/>
  <path d="M 50 100 Q 100 50 150 100 T 250 100" stroke="#FFD700" stroke-width="3" fill="none"/>
  <text x="50" y="30" font-family="Arial" font-size="20" fill="#4B0082">Scène 2 - Jardin Magique</text>
</svg>""",
    
    # Scène 3 - Aventure
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#87CEEB"/>
  <polygon points="50,250 150,150 250,200 350,120 400,180 400,300 0,300" fill="#32CD32"/>
  <circle cx="100" cy="80" r="40" fill="#FFD700"/>
  <polygon points="180,200 220,160 260,200 240,240 200,240" fill="#FF6347"/>
  <rect x="215" y="240" width="10" height="30" fill="#8B4513"/>
  <circle cx="150" cy="180" r="15" fill="#1E90FF"/>
  <circle cx="145" cy="175" r="2" fill="#000"/>
  <circle cx="155" cy="175" r="2" fill="#000"/>
  <text x="50" y="40" font-family="Arial" font-size="18" fill="#000">Scène 3 - L'Aventure</text>
</svg>""",
    
    # Scène 4 - Découverte
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="discover" cx="70%" cy="30%" r="50%">
      <stop offset="0%" style="stop-color:#FFFF00;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#87CEEB;stop-opacity:1" />
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#discover)"/>
  <rect x="150" y="150" width="100" height="80" rx="10" fill="#8B4513"/>
  <rect x="160" y="160" width="30" height="40" fill="#FFD700"/>
  <circle cx="175" cy="180" r="3" fill="#FF0000"/>
  <polygon points="200,100 250,140 150,140" fill="#DC143C"/>
  <circle cx="80" cy="120" r="20" fill="#FF69B4"/>
  <circle cx="320" cy="200" r="25" fill="#9370DB"/>
  <text x="100" y="280" font-family="Arial" font-size="16" fill="#000">Scène 4 - Découverte mystérieuse</text>
</svg>""",
    
    # Scène 5 - Amitié
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FFB6C1"/>
  <circle cx="150" cy="150" r="25" fill="#FF69B4"/>
  <circle cx="145" cy="140" r="3" fill="#000"/>
  <circle cx="155" cy="140" r="3" fill="#000"/>
  <path d="M 140 155 Q 150 165 160 155" stroke="#000" stroke-width="2" fill="none"/>
  <circle cx="250" cy="150" r="25" fill="#98FB98"/>
  <circle cx="245" cy="140" r="3" fill="#000"/>
  <circle cx="255" cy="140" r="3" fill="#000"/>
  <path d="M 240 155 Q 250 165 260 155" stroke="#000" stroke-width="2" fill="none"/>
  <path d="M 175 150 L 225 150" stroke="#FF1493" stroke-width="4"/>
  <path d="M 200 100 L 190 120 L 210 120 Z" fill="#FFD700"/>
  <text x="120" y="50" font-family="Arial" font-size="18" fill="#4B0082">Scène 5 - Nouvelle Amitié</text>
</svg>""",
    
    # Scène 6 - Défi
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="150" fill="#87CEEB"/>
  <rect width="400" height="150" y="150" fill="#32CD32"/>
  <polygon points="50,200 100,120 150,200" fill="#696969"/>
  <polygon points="200,180 280,100 360,180" fill="#2F4F4F"/>
  <circle cx="200" cy="220" r="15" fill="#FF4500"/>
  <rect x="190" y="235" width="20" height="15" fill="#8B4513"/>
  <rect x="185" y="250" width="10" height="20" fill="#8B4513"/>
  <rect x="205" y="250" width="10" height="20" fill="#8B4513"/>
  <path d="M 100 50 Q 150 30 200 50 T 300 50" stroke="#FFD700" stroke-width="5" fill="none"/>
  <text x="80" y="30" font-family="Arial" font-size="16" fill="#000">Scène 6 - Le Grand Défi</text>
</svg>""",
    
    # Scène 7 - Victoire
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="victory" cx="50%" cy="20%" r="80%">
      <stop offset="0%" style="stop-color:#FFD700;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#FFA500;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#FF69B4;stop-opacity:0.6" />
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#victory)"/>
  <circle cx="200" cy="150" r="35" fill="#FF1493"/>
  <circle cx="185" cy="135" r="4" fill="#000"/>
  <circle cx="215" cy="135" r="4" fill="#000"/>
  <path d="M 180 160 Q 200 180 220 160" stroke="#000" stroke-width="3" fill="none"/>
  <polygon points="200,50 210,80 240,80 220,100 230,130 200,110 170,130 180,100 160,80 190,80" fill="#FFD700"/>
  <circle cx="100" cy="80" r="8" fill="#FFFF00"/>
  <circle cx="300" cy="100" r="10" fill="#FFFF00"/>
  <circle cx="80" cy="200" r="6" fill="#FFFF00"/>
  <circle cx="320" cy="220" r="12" fill="#FFFF00"/>
  <text x="120" y="280" font-family="Arial" font-size="20" fill="#4B0082">Scène 7 - Victoire !</text>
</svg>""",
    
    # Scène 8 - Fin heureuse
    """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sunset" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#FFB6C1;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#FFA500;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#32CD32;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#sunset)"/>
  <circle cx="350" cy="60" r="40" fill="#FFD700"/>
  <circle cx="120" cy="180" r="20" fill="#FF69B4"/>
  <circle cx="200" cy="190" r="25" fill="#98FB98"/>
  <circle cx="280" cy="175" r="18" fill="#87CEEB"/>
  <path d="M 100 200 Q 200 160 300 200" stroke="#FF1493" stroke-width="3" fill="none"/>
  <polygon points="50,280 100,250 150,280 125,300 75,300" fill="#9370DB"/>
  <polygon points="250,290 300,260 350,290 325,300 275,300" fill="#FF6347"/>
  <text x="100" y="40" font-family="Arial" font-size="18" fill="#4B0082">Scène 8 - Fin Heureuse</text>
  <text x="150" y="250" font-family="Arial" font-size="14" fill="#000">Tous ensemble !</text>
</svg>"""
]

# Créer les fichiers SVG
for i, svg_content in enumerate(svg_templates, 1):
    filename = f"scene_{i}_demo.svg"
    filepath = demo_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✅ Image créée: {filename}")

print(f"\n🎨 {len(svg_templates)} images de démonstration créées dans {demo_dir}")
print("📁 Ces images seront directement visibles dans l'interface")
