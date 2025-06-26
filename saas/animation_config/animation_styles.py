"""
Documentation des styles d'animation supportés par FRIDAY
"""

# Styles optimisés pour Stable Diffusion
FRIDAY_ANIMATION_STYLES = {
    'cartoon': {
        'name': '2D Cartoon',
        'description': 'Style cartoon 2D coloré et expressif',
        'sd_prompt': 'cartoon style, 2D animation, colorful, cel-shaded, Disney-style, hand-drawn animation',
        'recommended_model': 'dreamshaper_8.safetensors',
        'works_well_with': ['adventure', 'friendship', 'animals', 'magic'],
        'icon': '🎨'
    },
    'anime': {
        'name': 'Anime',
        'description': 'Style anime japonais détaillé',
        'sd_prompt': 'anime style, manga style, Japanese animation, detailed eyes, vibrant colors, Studio Ghibli inspired',
        'recommended_model': 'animePastelDream_softBakedVae.safetensors',
        'works_well_with': ['magic', 'adventure', 'friendship', 'nature'],
        'icon': '✨'
    },
    '3d': {
        'name': '3D Animation',
        'description': 'Rendu 3D moderne et fluide',
        'sd_prompt': '3D rendered, computer animation, smooth lighting, modern CGI, high quality render',
        'recommended_model': 'realisticVisionV51_v51VAE.safetensors',
        'works_well_with': ['space', 'adventure', 'animals', 'nature'],
        'icon': '🎮'
    },
    'pixar': {
        'name': 'Style Pixar',
        'description': 'Animation 3D style studios Pixar',
        'sd_prompt': 'Pixar style, 3D animation, warm lighting, character-focused, family-friendly, studio quality',
        'recommended_model': 'epicrealism_naturalSinRC1VAE.safetensors',
        'works_well_with': ['friendship', 'adventure', 'animals', 'magic'],
        'icon': '🏰'
    }
}

def get_style_info():
    """Retourne les informations sur les styles supportés"""
    return {
        'supported_styles': list(FRIDAY_ANIMATION_STYLES.keys()),
        'total_styles': len(FRIDAY_ANIMATION_STYLES),
        'optimized_for': 'Stable Diffusion',
        'styles_details': FRIDAY_ANIMATION_STYLES
    }

def validate_friday_style(style: str) -> bool:
    """Vérifie si un style est supporté par FRIDAY"""
    return style in FRIDAY_ANIMATION_STYLES

print("📚 Styles FRIDAY chargés:")
for style_key, style_info in FRIDAY_ANIMATION_STYLES.items():
    print(f"  • {style_info['name']} ({style_key}) - {style_info['description']}")

print(f"\n✅ Total: {len(FRIDAY_ANIMATION_STYLES)} styles optimisés pour Stable Diffusion")
