"""
Service de composition amélioré utilisant CrewAI et le layout avancé
Remplace le système de composition basique par une version professionnelle
"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os
import json
from typing import Dict, List, Tuple, Optional
from services.advanced_bubble_layout import advanced_bubble_layout
from services.crewai_comic_service import crewai_comic_service

class CrewAIComicComposer:
    """
    Compositeur de BD utilisant les améliorations CrewAI
    """
    
    def __init__(self):
        self.advanced_layout = advanced_bubble_layout
        self.crewai_service = crewai_comic_service
        
    def estimate_character_position_advanced(self, description: str, character: str, 
                                           img_width: int, img_height: int,
                                           layout_metadata: Dict = None) -> Tuple[int, int]:
        """
        Estimation avancée de la position des personnages basée sur la description
        et les métadonnées CrewAI
        """
        desc_lower = description.lower()
        char_lower = character.lower()
        
        # Utilise les métadonnées CrewAI si disponibles
        if layout_metadata and layout_metadata.get('character_positions'):
            char_pos = layout_metadata['character_positions'].get(character)
            if char_pos:
                return (
                    int(img_width * char_pos.get('x_ratio', 0.5)),
                    int(img_height * char_pos.get('y_ratio', 0.7))
                )
        
        # Analyse textuelle avancée pour la position
        x_position = 0.5  # Centre par défaut
        y_position = 0.7  # Bas par défaut
        
        # Analyse horizontale
        if any(word in desc_lower for word in ['gauche', 'left', 'à gauche']):
            x_position = 0.25
        elif any(word in desc_lower for word in ['droite', 'right', 'à droite']):
            x_position = 0.75
        elif any(word in desc_lower for word in ['centre', 'center', 'milieu']):
            x_position = 0.5
        
        # Analyse verticale
        if any(word in desc_lower for word in ['haut', 'top', 'en haut', 'ciel']):
            y_position = 0.3
        elif any(word in desc_lower for word in ['bas', 'bottom', 'sol', 'terre']):
            y_position = 0.8
        elif any(word in desc_lower for word in ['milieu', 'middle', 'centre']):
            y_position = 0.5
        
        # Ajustements selon le contexte
        if any(word in desc_lower for word in ['vole', 'flying', 'air', 'nuage']):
            y_position = max(0.2, y_position - 0.2)
        elif any(word in desc_lower for word in ['assis', 'sitting', 'chaise']):
            y_position = min(0.8, y_position + 0.1)
        
        return (int(img_width * x_position), int(img_height * y_position))
    
    def determine_bubble_type(self, dialogue: Dict, scene_context: str) -> str:
        """
        Détermine le type de bulle selon le dialogue et le contexte
        """
        text = dialogue.get('text', '').lower()
        character = dialogue.get('character', '').lower()
        
        # Analyse du contenu pour déterminer le type
        if any(indicator in text for indicator in ['!', '!!', 'crie', 'hurle', 'ATTENTION']):
            return 'shout'
        elif any(indicator in text for indicator in ['...', 'chuchote', 'murmure', 'psst']):
            return 'whisper'
        elif any(indicator in text for indicator in ['pense', 'se dit', 'réfléchit']) or \
             text.startswith('(') and text.endswith(')'):
            return 'thought'
        else:
            return 'speech'
    
    async def compose_enhanced_scene(self, scene_data: Dict, scene_index: int, 
                                   total_scenes: int, output_path: str) -> str:
        """
        Compose une scène avec les améliorations CrewAI
        
        Args:
            scene_data: Données de la scène (possiblement améliorées par CrewAI)
            scene_index: Index de la scène
            total_scenes: Nombre total de scènes
            output_path: Chemin de sortie
            
        Returns:
            str: Chemin du fichier créé
        """
        try:
            # Récupération de l'image
            image_url = scene_data.get('image')
            if not image_url:
                raise ValueError(f"❌ Aucune image pour la scène {scene_index + 1}")
            
            # Chargement de l'image
            if image_url.startswith(("http://", "https://")):
                print(f"🌐 Téléchargement image scène {scene_index + 1}: {image_url}")
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content)).convert("RGBA")
            else:
                # Image locale
                local_path = image_url
                if image_url.startswith("/static/"):
                    local_path = os.path.normpath(image_url.lstrip("/"))
                print(f"📁 Chargement image locale scène {scene_index + 1}: {local_path}")
                img = Image.open(local_path).convert("RGBA")
            
            # Création de l'overlay pour les bulles
            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Police adaptative selon la taille de l'image
            font_size = max(16, min(24, img.width // 40))
            font = self.advanced_layout._get_font(font_size)
            
            # Données des dialogues
            dialogues = scene_data.get('dialogues', [])
            description = scene_data.get('description', '')
            
            # Métadonnées de layout CrewAI
            layout_metadata = scene_data.get('layout_metadata', {})
            
            print(f"🎭 Scène {scene_index + 1}: {len(dialogues)} dialogue(s)")
            
            # Suivi des bulles placées pour éviter les collisions
            placed_bubbles = []
            
            # Traitement de chaque dialogue
            for dialogue_index, dialogue in enumerate(dialogues):
                character = dialogue.get('character', f'Personnage {dialogue_index + 1}')
                text = f"{character}: {dialogue.get('text', '')}"
                
                # Détermination du type de bulle
                bubble_type = self.determine_bubble_type(dialogue, description)
                
                # Position du personnage
                char_pos = self.estimate_character_position_advanced(
                    description, character, img.width, img.height, layout_metadata
                )
                
                # Calcul de la taille optimale de la bulle
                bubble_width, bubble_height = self.advanced_layout.calculate_optimal_bubble_size(
                    text, font, max_width=int(img.width * 0.4)
                )
                
                # Position optimale de la bulle
                bubble_pos = self.advanced_layout._find_optimal_position(
                    img.width, img.height, bubble_width, bubble_height,
                    char_pos, placed_bubbles, dialogue_index
                )
                
                # Dessine la bulle avancée
                self.advanced_layout.draw_advanced_bubble(
                    draw, text, bubble_type, bubble_pos,
                    (bubble_width, bubble_height), char_pos, font
                )
                
                # Enregistre la bulle placée
                placed_bubbles.append({
                    'x': bubble_pos[0],
                    'y': bubble_pos[1],
                    'width': bubble_width,
                    'height': bubble_height,
                    'type': bubble_type,
                    'character': character
                })
                
                print(f"  💬 Bulle {dialogue_index + 1} ({bubble_type}): {character}")
            
            # Fusion des calques
            final_image = Image.alpha_composite(img, overlay).convert("RGB")
            
            # Sauvegarde avec métadonnées
            final_image.save(output_path, "PNG", optimize=True)
            
            print(f"✅ Scène {scene_index + 1} sauvegardée: {output_path}")
            
            # Retourne les informations de la scène composée
            return {
                'path': output_path,
                'bubbles_count': len(dialogues),
                'placed_bubbles': placed_bubbles,
                'scene_index': scene_index,
                'enhanced_by_crewai': scene_data.get('crewai_enhanced', False)
            }
            
        except Exception as e:
            print(f"❌ Erreur composition scène {scene_index + 1}: {e}")
            raise
    
    async def compose_enhanced_comic(self, enhanced_scenario: Dict) -> List[str]:
        """
        Compose une BD complète avec les améliorations CrewAI
        
        Args:
            enhanced_scenario: Scénario amélioré par CrewAI
            
        Returns:
            List[str]: Liste des chemins des images générées
        """
        try:
            scenes = enhanced_scenario.get('scenes', [])
            if not scenes:
                raise ValueError("❌ Aucune scène dans le scénario")
            
            print(f"🎬 Début composition BD améliorée: {len(scenes)} scène(s)")
            
            scene_files = []
            
            # Traite chaque scène
            for scene_index, scene in enumerate(scenes):
                output_filename = f"enhanced_scene_{scene_index + 1}.png"
                output_path = os.path.join("static", output_filename)
                
                # Assure que le dossier static existe
                os.makedirs("static", exist_ok=True)
                
                scene_result = await self.compose_enhanced_scene(
                    scene, scene_index, len(scenes), output_path
                )
                
                scene_files.append(scene_result['path'])
            
            print(f"🎉 BD améliorée terminée: {len(scene_files)} scène(s) générée(s)")
            
            return scene_files
            
        except Exception as e:
            print(f"❌ Erreur composition BD: {e}")
            raise
    
    def validate_scene_for_composition(self, scene: Dict) -> Dict:
        """
        Valide qu'une scène est prête pour la composition
        
        Returns:
            Dict avec is_valid et errors
        """
        errors = []
        
        if not scene.get('image'):
            errors.append("Image manquante")
            
        if not scene.get('description'):
            errors.append("Description manquante")
            
        dialogues = scene.get('dialogues', [])
        if not dialogues:
            errors.append("Aucun dialogue")
        
        for i, dialogue in enumerate(dialogues):
            if not dialogue.get('character'):
                errors.append(f"Personnage manquant pour le dialogue {i+1}")
            if not dialogue.get('text'):
                errors.append(f"Texte manquant pour le dialogue {i+1}")
            if len(dialogue.get('text', '')) > 150:
                errors.append(f"Dialogue {i+1} trop long (>{150} caractères)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'dialogues_count': len(dialogues),
            'has_layout_metadata': 'layout_metadata' in scene
        }

# Instance globale
crewai_comic_composer = CrewAIComicComposer()
