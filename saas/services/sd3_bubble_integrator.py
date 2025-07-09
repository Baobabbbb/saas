"""
🎯 SYSTÈME AUTONOME D'INTÉGRATION DE BULLES RÉALISTES 
Analyse les images de BD et y intègre automatiquement des bulles professionnelles
via Stable Diffusion 3 Image-to-Image pour un rendu indiscernable d'une vraie BD
"""

import os
import json
import base64
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class SD3BubbleIntegrator:
    """
    🚀 SYSTÈME AUTONOME COMPLET DE BULLES INTÉGRÉES
    
    FONCTIONNALITÉS :
    ✅ Analyse automatique des scènes et dialogues
    ✅ Détection intelligente des positions de personnages  
    ✅ Génération de prompts ultra-précis pour SD3
    ✅ Intégration séquentielle de multiples bulles
    ✅ Équilibrage visuel et cohérence stylistique
    ✅ Fallback robuste en cas d'échec SD3
    ✅ Assembly final en BD professionnelle
    """
    
    def __init__(self):
        print("🎨 Initialisation SD3BubbleIntegrator - Système autonome de bulles intégrées")
        
        # Configuration API Stable Diffusion 3
        self.stability_key = os.getenv("STABILITY_API_KEY")
        self.sd3_img2img_endpoint = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        self.sd3_edit_endpoint = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
        
        # Nouveau: Configuration avancée pour qualité professionnelle
        self.bubble_models = {
            "high_quality": "sd3-large",
            "fast": "sd3-medium", 
            "turbo": "sd3-large-turbo"
        }
        self.current_model = "sd3-large-turbo"  # Optimal pour bulles
        
        # Configuration qualité et limites
        self.bubble_quality = "high" 
        self.max_bubbles_per_image = 4
        self.image_resolution = 1024
        
        # Patterns de détection de positions
        self.position_patterns = {
            'left': ['gauche', 'left', 'à gauche', 'on the left', 'leftmost'],
            'right': ['droite', 'right', 'à droite', 'on the right', 'rightmost'], 
            'center': ['centre', 'center', 'milieu', 'middle', 'au centre'],
            'foreground': ['devant', 'foreground', 'premier plan', 'front'],
            'background': ['derrière', 'background', 'arrière-plan', 'back', 'fond']
        }
        
        # Templates de prompts optimisés
        self.bubble_prompt_templates = {
            'single': "Add a professional comic book speech bubble in the {position} area of the image, containing the text '{text}'. The bubble should have a clean white background, bold black outline, and a curved tail pointing toward the {character_position}. Style: hand-drawn comic book bubble, naturally integrated, {style_context}.",
            
            'multiple': "Add {count} comic book speech bubbles: {bubble_descriptions}. Each bubble should have a white background, black outline, and curved tail pointing to the speaker. Maintain visual balance and ensure bubbles don't overlap or cover important details. Style: professional comic book artwork.",
            
            'narrative': "Add a rectangular narrative text box in the {position} of the image containing '{text}'. Style: comic book caption box with clean edges, subtle background, and clear readable text that complements the {style_context}."
        }
        
    
    async def process_comic_pages(self, comic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 POINT D'ENTRÉE PRINCIPAL - Traite une BD complète
        Analyse chaque page et intègre automatiquement les bulles réalistes
        """
        print("🚀 === DÉMARRAGE TRAITEMENT BD AVEC BULLES INTÉGRÉES ===")
        
        pages = comic_data.get("pages", [])
        if not pages:
            print("⚠️ Aucune page à traiter")
            return comic_data
            
        processed_pages = []
        
        for i, page_data in enumerate(pages):
            try:
                print(f"\n📄 TRAITEMENT PAGE {i+1}/{len(pages)}")
                print(f"   Description: {page_data.get('description', 'N/A')[:80]}...")
                print(f"   Dialogues: {len(page_data.get('dialogues', []))} éléments")
                
                # Traiter la page avec intégration de bulles
                enhanced_page = await self._process_single_page(page_data)
                processed_pages.append(enhanced_page)
                
                print(f"✅ Page {i+1} traitée avec succès")
                
            except Exception as e:
                print(f"❌ Erreur page {i+1}: {e}")
                # Fallback : garder la page originale
                page_fallback = page_data.copy()
                page_fallback["bubble_integration"] = "failed_fallback"
                page_fallback["error"] = str(e)
                processed_pages.append(page_fallback)
        
        # Mettre à jour les métadonnées de la BD
        result = comic_data.copy()
        result["pages"] = processed_pages
        result["bubble_system"] = "sd3_integrated"
        result["processing_time"] = datetime.now().isoformat()
        result["total_pages_processed"] = len(processed_pages)
        
        print(f"\n🎉 BD COMPLÈTE TRAITÉE: {len(processed_pages)} pages avec bulles intégrées")
        return result
    
    async def _process_single_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 TRAITEMENT COMPLET D'UNE PAGE INDIVIDUELLE
        1. Analyse de la scène et des dialogues
        2. Planification des positions de bulles  
        3. Intégration séquentielle via SD3
        """
        # Extraire les données essentielles
        image_path = page_data.get("image_path", "")
        description = page_data.get("description", "")
        dialogues = page_data.get("dialogues", [])
        page_number = page_data.get("page_number", 1)
        
        print(f"   🔍 Analyse: {len(dialogues)} dialogues détectés")
        
        if not image_path or not dialogues:
            print("   ⚠️ Page sans image ou sans dialogues - passage sans modification")
            return page_data
        
        # Vérifier que l'image existe
        if not Path(image_path).exists():
            print(f"   ❌ Image non trouvée: {image_path}")
            return page_data
        
        try:
            # ÉTAPE 1: Analyser la composition de la scène
            print("   📊 Analyse de la composition...")
            scene_analysis = await self._analyze_scene_composition(description, dialogues)
            
            # ÉTAPE 2: Intégrer les bulles séquentiellement avec SD3
            print("   🎨 Intégration des bulles via SD3...")
            final_image_path = await self._integrate_bubbles_with_sd3(
                image_path, scene_analysis, page_number
            )
            
            # ÉTAPE 3: Préparer les données finales
            enhanced_page = page_data.copy()
            enhanced_page["image_path"] = str(final_image_path)
            enhanced_page["bubble_integration"] = "sd3_success"
            enhanced_page["scene_analysis"] = scene_analysis
            enhanced_page["processing_timestamp"] = datetime.now().isoformat()
            
            # Mettre à jour l'URL si nécessaire
            if "image_url" in enhanced_page:
                enhanced_page["image_url"] = f"/static/generated_comics/{final_image_path.parent.name}/{final_image_path.name}"
            
            print(f"   ✅ Bulles intégrées avec succès dans: {final_image_path.name}")
            return enhanced_page
            
        except Exception as e:
            print(f"   ❌ Erreur intégration bulles: {e}")
            # Fallback vers l'image originale
            fallback_page = page_data.copy()
            fallback_page["bubble_integration"] = "sd3_failed_fallback"
            fallback_page["error"] = str(e)
            return fallback_page
    
    
    async def _analyze_scene_composition(self, description: str, dialogues: List[Dict]) -> Dict[str, Any]:
        """
        🧠 ANALYSE INTELLIGENTE DE LA SCÈNE
        Croise la description avec les dialogues pour inférer automatiquement :
        - Qui parle et où il se trouve
        - Où placer chaque bulle optimalement
        - Le style et l'équilibre visuel
        """
        print(f"      🔍 Analyse description: {description[:60]}...")
        
        # Extraire les positions des personnages
        character_positions = self._extract_character_positions(description)
        print(f"      📍 Positions détectées: {character_positions}")
        
        # Associer chaque dialogue à une position
        bubble_plan = []
        for i, dialogue in enumerate(dialogues):
            speaker = dialogue.get("character", "").lower()
            text = dialogue.get("text", "")
            
            if not text.strip():
                continue
                
            # Déterminer la position du personnage
            position_info = self._determine_speaker_position(speaker, character_positions, description)
            
            # Créer le plan de bulle
            bubble_spec = {
                "bubble_id": f"bubble_{i+1}",
                "speaker": speaker,
                "text": text,
                "position": position_info["position"],
                "area": position_info["area"], 
                "priority": i + 1,  # Ordre d'intégration
                "style_context": self._infer_style_context(description)
            }
            
            bubble_plan.append(bubble_spec)
            print(f"      💬 Bulle {i+1}: {speaker} ({position_info['position']}) - '{text[:30]}...'")
        
        return {
            "total_bubbles": len(bubble_plan),
            "bubble_plan": bubble_plan,
            "character_positions": character_positions,
            "scene_description": description,
            "visual_balance": self._calculate_visual_balance(bubble_plan)
        }
    
    def _extract_character_positions(self, description: str) -> Dict[str, str]:
        """
        📍 EXTRACTION AUTOMATIQUE DES POSITIONS
        Parse la description pour identifier où se trouve chaque personnage
        """
        positions = {}
        description_lower = description.lower()
        
        # Patterns de détection sophistiqués
        patterns = [
            # Français
            (r'(\w+)\s+(?:se trouve|est|se tient)\s+(?:à\s+)?(?:la\s+)?(gauche|droite|centre|devant|derrière)', 
             lambda m: (m.group(1), m.group(2))),
            # Anglais  
            (r'(\w+)\s+(?:is|stands|sits)\s+(?:on\s+the\s+)?(left|right|center|front|back)', 
             lambda m: (m.group(1), m.group(2))),
            # Positions relatives
            (r'(?:à\s+)?(gauche|droite),\s*(\w+)', 
             lambda m: (m.group(2), m.group(1))),
            (r'(?:on\s+the\s+)?(left|right),\s*(\w+)', 
             lambda m: (m.group(2), m.group(1)))
        ]
        
        for pattern, extractor in patterns:
            matches = re.finditer(pattern, description_lower)
            for match in matches:
                try:
                    character, position = extractor(match)
                    # Normaliser les positions
                    normalized_pos = self._normalize_position(position)
                    if normalized_pos:
                        positions[character.strip()] = normalized_pos
                except:
                    continue
        
        # Si aucune position explicite, inférer depuis le contexte
        if not positions:
            positions = self._infer_positions_from_context(description_lower)
        
        return positions
    
    def _normalize_position(self, position: str) -> str:
        """Normalise les positions en catégories standard"""
        position_lower = position.lower().strip()
        
        position_map = {
            'gauche': 'left', 'left': 'left', 'leftmost': 'left',
            'droite': 'right', 'right': 'right', 'rightmost': 'right', 
            'centre': 'center', 'center': 'center', 'milieu': 'center', 'middle': 'center',
            'devant': 'foreground', 'front': 'foreground', 'foreground': 'foreground',
            'derrière': 'background', 'back': 'background', 'background': 'background', 'fond': 'background'
        }
        
        return position_map.get(position_lower, 'center')
    
    def _determine_speaker_position(self, speaker: str, positions: Dict[str, str], description: str) -> Dict[str, str]:
        """
        🎯 DÉTERMINATION INTELLIGENTE DE POSITION
        Associe chaque personnage qui parle à sa position dans l'image
        """
        # Recherche directe par nom
        for char_name, position in positions.items():
            if speaker.lower() in char_name.lower() or char_name.lower() in speaker.lower():
                return {
                    "position": position,
                    "area": self._position_to_area(position),
                    "confidence": "high"
                }
        
        # Fallback : inférer depuis la description
        if "premier" in speaker.lower() or "first" in speaker.lower():
            return {"position": "left", "area": "upper_left", "confidence": "medium"}
        elif "second" in speaker.lower() or "autre" in speaker.lower():
            return {"position": "right", "area": "upper_right", "confidence": "medium"}
        
        # Valeur par défaut
        return {"position": "center", "area": "upper_center", "confidence": "low"}
    
    def _position_to_area(self, position: str) -> str:
        """Convertit une position en zone d'image pour placement de bulle"""
        area_map = {
            'left': 'upper_left',
            'right': 'upper_right', 
            'center': 'upper_center',
            'foreground': 'lower_center',
            'background': 'upper_center'
        }
        return area_map.get(position, 'upper_center')
    
    def _infer_style_context(self, description: str) -> str:
        """Infère le contexte stylistique pour les prompts"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['cartoon', 'colorful', 'bright']):
            return "vibrant cartoon comic book style"
        elif any(word in description_lower for word in ['realistic', 'detailed', 'photo']):
            return "realistic comic book illustration style"
        elif any(word in description_lower for word in ['manga', 'anime', 'japanese']):
            return "manga and anime comic style"
        else:
            return "professional comic book art style"
    
    def _calculate_visual_balance(self, bubble_plan: List[Dict]) -> Dict[str, Any]:
        """Calcule l'équilibre visuel pour optimiser le placement"""
        if not bubble_plan:
            return {"balance": "empty", "zones_used": []}
        
        zones_used = [bubble["area"] for bubble in bubble_plan]
        zone_counts = {}
        for zone in zones_used:
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
        
        # Déterminer l'équilibre
        max_count = max(zone_counts.values()) if zone_counts else 0
        balance = "good" if max_count <= 2 else "crowded"
        
        return {
            "balance": balance,
            "zones_used": zones_used,
            "zone_distribution": zone_counts,
            "recommendation": "spread_bubbles" if balance == "crowded" else "optimal"
        }
        
        # Associer chaque dialogue à une position
        dialogue_plan = []
        
        for i, dialogue in enumerate(dialogues):
            character_name = dialogue.get("character", "")
            text = dialogue.get("text", "")
            dialogue_type = dialogue.get("type", "speech")
            
            # Trouver la position du personnage
            position_info = self._find_character_position(character_name, character_positions, description)
            
            # Déterminer la position optimale de la bulle
            bubble_position = self._calculate_bubble_position(position_info, i, len(dialogues))
            
            dialogue_plan.append({
                "text": text,
                "character": character_name,
                "type": dialogue_type,
                "character_position": position_info,
                "bubble_position": bubble_position,
                "priority": self._calculate_priority(dialogue_type, i)
            })
        
        return {
            "character_positions": character_positions,
            "dialogue_plan": dialogue_plan,
            "scene_description": description
        }
    
    def _extract_character_positions(self, description: str) -> Dict[str, str]:
        """
        Extrait les positions des personnages depuis la description textuelle
        """
        positions = {}
        
        # Patterns de position courants
        position_patterns = [
            (r"(\w+)\s+(?:se trouve|est|se tient)\s+(?:à|au|sur|dans)\s+(.*?)(?:,|\.|$)", "detailed"),
            (r"(\w+)\s+(?:à|au|sur)\s+(gauche|droite|centre|fond|premier plan)", "simple"),
            (r"(?:à|au)\s+(gauche|droite|centre|fond),?\s+(\w+)", "position_first"),
            (r"(\w+)\s+(?:brandissant|tenant|portant|regardant)", "action_based")
        ]
        
        description_lower = description.lower()
        
        for pattern, pattern_type in position_patterns:
            matches = re.finditer(pattern, description_lower)
            for match in matches:
                if pattern_type == "detailed":
                    character, position = match.groups()
                    positions[character.capitalize()] = position
                elif pattern_type == "simple":
                    character, position = match.groups()
                    positions[character.capitalize()] = position
                elif pattern_type == "position_first":
                    position, character = match.groups()
                    positions[character.capitalize()] = position
        
        # Fallback: positions par défaut si pas détectées
        if not positions:
            # Extraire les noms probables et assigner des positions par défaut
            probable_names = re.findall(r'\b[A-Z][a-z]+\b', description)
            default_positions = ["gauche", "droite", "centre", "arrière-plan"]
            
            for i, name in enumerate(set(probable_names)):
                if i < len(default_positions):
                    positions[name] = default_positions[i]
        
        return positions
    
    def _find_character_position(self, character_name: str, positions: Dict[str, str], description: str) -> Dict[str, Any]:
        """
        Trouve la position d'un personnage spécifique
        """
        # Recherche directe dans les positions extraites
        for name, position in positions.items():
            if character_name.lower() in name.lower() or name.lower() in character_name.lower():
                return {
                    "name": character_name,
                    "textual_position": position,
                    "coordinates": self._convert_position_to_coordinates(position),
                    "confidence": "high"
                }
        
        # Fallback: analyse contextuelle
        if "gauche" in description.lower() and character_name.lower() in description.lower():
            return {
                "name": character_name,
                "textual_position": "gauche",
                "coordinates": {"x": 0.25, "y": 0.5},
                "confidence": "medium"
            }
        
        # Position par défaut
        return {
            "name": character_name,
            "textual_position": "centre",
            "coordinates": {"x": 0.5, "y": 0.6},
            "confidence": "low"
        }
    
    def _convert_position_to_coordinates(self, position: str) -> Dict[str, float]:
        """
        Convertit une position textuelle en coordonnées relatives
        """
        position_map = {
            "gauche": {"x": 0.25, "y": 0.6},
            "droite": {"x": 0.75, "y": 0.6},
            "centre": {"x": 0.5, "y": 0.6},
            "fond": {"x": 0.5, "y": 0.7},
            "arrière-plan": {"x": 0.5, "y": 0.8},
            "premier plan": {"x": 0.5, "y": 0.4},
            "haut": {"x": 0.5, "y": 0.3},
            "bas": {"x": 0.5, "y": 0.8}
        }
        
        # Recherche de correspondance
        for key, coords in position_map.items():
            if key in position.lower():
                return coords
        
        # Position par défaut
        return {"x": 0.5, "y": 0.6}
    
    def _calculate_bubble_position(self, character_pos: Dict, dialogue_index: int, total_dialogues: int) -> Dict[str, Any]:
        """
        Calcule la position optimale de la bulle par rapport au personnage
        """
        char_coords = character_pos.get("coordinates", {"x": 0.5, "y": 0.6})
        
        # Position de base: au-dessus du personnage
        bubble_x = char_coords["x"]
        bubble_y = char_coords["y"] - 0.2
        
        # Ajustements pour éviter les chevauchements
        if total_dialogues > 1:
            if dialogue_index == 0:
                bubble_x -= 0.1  # Légèrement à gauche
            elif dialogue_index == 1:
                bubble_x += 0.1  # Légèrement à droite
            elif dialogue_index == 2:
                bubble_y -= 0.1  # Plus haut
        
        # S'assurer que la bulle reste dans l'image
        bubble_x = max(0.15, min(0.85, bubble_x))
        bubble_y = max(0.05, min(0.8, bubble_y))
        
        return {
            "x": bubble_x,
            "y": bubble_y,
            "relative_to_character": "above",
            "adjustment": f"dialogue_{dialogue_index}"
        }
    
    def _calculate_priority(self, dialogue_type: str, index: int) -> int:
        """
        Calcule la priorité d'intégration de la bulle
        """
        type_priority = {
            "speech": 10,
            "shout": 15,
            "thought": 8,
            "whisper": 5
        }
        
        base_priority = type_priority.get(dialogue_type, 10)
        # Premier dialogue a priorité plus élevée
        position_bonus = max(0, 5 - index)
        
        return base_priority + position_bonus
    
    async def _integrate_bubbles_with_sd3(self, image_path: str, scene_analysis: Dict[str, Any], page_number: int) -> Path:
        """
        🚀 INTÉGRATION SÉQUENTIELLE DES BULLES AVEC SD3
        Traite chaque bulle individuellement pour un résultat professionnel
        """
        bubble_plan = scene_analysis["bubble_plan"]
        if not bubble_plan:
            print("      ⚠️ Aucune bulle à intégrer")
            return Path(image_path)
        
        current_image_path = Path(image_path)
        
        print(f"      🎨 Intégration de {len(bubble_plan)} bulle(s) séquentiellement...")
        
        for i, bubble_spec in enumerate(bubble_plan):
            try:
                print(f"         💬 Bulle {i+1}/{len(bubble_plan)}: {bubble_spec['speaker']}")
                
                # Générer le prompt SD3 ultra-précis
                sd3_prompt = self._generate_sd3_prompt(bubble_spec, scene_analysis, i == 0)
                print(f"         🎯 Prompt: {sd3_prompt[:80]}...")
                
                # Appeler SD3 Image-to-Image
                result_image_path = await self._call_sd3_image_to_image(
                    current_image_path, sd3_prompt, page_number, i+1
                )
                
                if result_image_path and result_image_path.exists():
                    current_image_path = result_image_path
                    print(f"         ✅ Bulle {i+1} intégrée avec succès")
                else:
                    print(f"         ❌ Échec intégration bulle {i+1}, fallback PIL")
                    current_image_path = await self._fallback_pil_bubble(
                        current_image_path, bubble_spec, page_number, i+1
                    )
                
                # Pause courte entre les bulles pour éviter rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"         ❌ Erreur bulle {i+1}: {e}")
                # Continuer avec l'image actuelle en cas d'erreur
                continue
        
        print(f"      ✅ Intégration terminée: {current_image_path.name}")
        return current_image_path
    
    def _generate_sd3_prompt(self, bubble_spec: Dict[str, Any], scene_analysis: Dict[str, Any], is_first: bool) -> str:
        """
        🎯 GÉNÉRATION DE PROMPTS ULTRA-PRÉCIS POUR SD3
        Crée des prompts détaillés qui produisent des bulles parfaitement intégrées
        """
        text = bubble_spec["text"]
        position = bubble_spec["position"]
        area = bubble_spec["area"]
        speaker = bubble_spec["speaker"]
        style_context = bubble_spec["style_context"]
        
        # Templates spécialisés selon le nombre de bulles
        if scene_analysis["total_bubbles"] == 1:
            # Une seule bulle - prompt simple et direct
            prompt = f"""Add a professional comic book speech bubble in the {self._area_to_description(area)} area of the image. The bubble contains the text: "{text}". 
            
The speech bubble should have:
- Clean white background with bold black outline
- Curved tail pointing toward the {position} character's mouth
- Natural integration that doesn't cover important image details
- {style_context} consistent with the image
- Professional comic book quality lettering

Ensure the bubble looks hand-drawn and naturally part of the original artwork."""
            
        else:
            # Multiples bulles - préciser la position et l'équilibre
            bubble_number = bubble_spec["priority"]
            total_bubbles = scene_analysis["total_bubbles"]
            
            prompt = f"""Add speech bubble #{bubble_number} of {total_bubbles} total bubbles. Place this bubble in the {self._area_to_description(area)} containing the text: "{text}".

This bubble should:
- Have white background and black outline like a professional comic
- Point toward the {position} character with a curved tail
- Maintain visual balance with other bubbles in the scene
- Not overlap or interfere with other speech bubbles
- Match the {style_context} of the image
- Look naturally integrated, as if drawn by the original artist

Priority: ensure this bubble complements the overall composition."""
        
        return prompt.strip()
    
    def _area_to_description(self, area: str) -> str:
        """Convertit les zones en descriptions naturelles pour les prompts"""
        area_descriptions = {
            'upper_left': 'upper left',
            'upper_right': 'upper right', 
            'upper_center': 'upper center',
            'lower_left': 'lower left',
            'lower_right': 'lower right',
            'lower_center': 'lower center',
            'center': 'center'
        }
        return area_descriptions.get(area, 'center')
    
    async def _call_sd3_image_to_image(self, image_path: Path, prompt: str, page_number: int, bubble_number: int) -> Optional[Path]:
        """
        🔧 APPEL API STABLE DIFFUSION 3 IMAGE-TO-IMAGE CORRIGÉ
        Utilise la véritable API SD3 image-to-image pour intégrer les bulles
        """
        if not self.stability_key:
            print("         ⚠️ Clé Stability AI manquante - fallback PIL")
            return None
        
        try:
            # Préparer l'image en format compatible
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Paramètres headers corrects pour multipart/form-data
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Accept": "image/*"
            }
            
            # Préparer les données multipart pour SD3 image-to-image
            form_data = aiohttp.FormData()
            form_data.add_field('image', image_data, filename='input.png', content_type='image/png')
            form_data.add_field('prompt', prompt)
            form_data.add_field('mode', 'image-to-image')  # Mode correct pour modification
            form_data.add_field('model', self.current_model)
            form_data.add_field('strength', '0.4')  # Force de modification optimale pour bulles
            form_data.add_field('cfg_scale', '8.0')  # Adhérence au prompt
            form_data.add_field('steps', '30')  # Qualité élevée
            form_data.add_field('output_format', 'png')
            
            # Appel asynchrone à l'API SD3 correcte
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.sd3_img2img_endpoint,
                    headers=headers,
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as response:
                    
                    print(f"         📡 SD3 Response Status: {response.status}")
                    
                    if response.status == 200:
                        # La réponse est directement l'image en binaire
                        image_data = await response.read()
                        
                        if image_data:
                            # Sauvegarder l'image résultante
                            output_path = image_path.parent / f"page_{page_number}_bubble_{bubble_number}_sd3.png"
                            with open(output_path, 'wb') as f:
                                f.write(image_data)
                            
                            print(f"         ✅ SD3 Image-to-Image réussi: {output_path.name}")
                            return output_path
                        else:
                            print(f"         ❌ SD3 - données image vides")
                            return None
                    else:
                        error_text = await response.text()
                        print(f"         ❌ SD3 erreur {response.status}: {error_text[:200]}")
                        return None
                        
        except Exception as e:
            print(f"         ❌ Exception SD3 Image-to-Image: {e}")
            return None
    
    async def _fallback_pil_bubble(self, image_path: Path, bubble_spec: Dict[str, Any], page_number: int, bubble_number: int) -> Path:
        """
        🛠️ FALLBACK PIL - Bulles basiques si SD3 échoue
        Crée une bulle simple avec PIL pour assurer la continuité
        """
        try:
            print(f"         🛠️ Fallback PIL pour bulle {bubble_number}")
            
            # Charger l'image
            with Image.open(image_path) as img:
                draw = ImageDraw.Draw(img)
                
                # Paramètres de la bulle
                text = bubble_spec["text"]
                area = bubble_spec["area"]
                
                # Calculer la position selon l'aire
                img_width, img_height = img.size
                positions = {
                    'upper_left': (img_width * 0.15, img_height * 0.15),
                    'upper_right': (img_width * 0.85, img_height * 0.15),
                    'upper_center': (img_width * 0.5, img_height * 0.15),
                    'lower_left': (img_width * 0.15, img_height * 0.75),
                    'lower_right': (img_width * 0.85, img_height * 0.75),
                    'lower_center': (img_width * 0.5, img_height * 0.75)
                }
                
                x, y = positions.get(area, (img_width * 0.5, img_height * 0.2))
                
                # Dessiner une bulle simple
                bubble_width = min(200, img_width * 0.3)
                bubble_height = min(80, img_height * 0.15)
                
                # Bulle (ellipse blanche avec contour noir)
                bubble_coords = [
                    x - bubble_width//2, y - bubble_height//2,
                    x + bubble_width//2, y + bubble_height//2
                ]
                
                draw.ellipse(bubble_coords, fill="white", outline="black", width=3)
                
                # Queue de la bulle (triangle simple)
                tail_points = [
                    (x - 10, y + bubble_height//2),
                    (x + 10, y + bubble_height//2),
                    (x, y + bubble_height//2 + 20)
                ]
                draw.polygon(tail_points, fill="white", outline="black")
                
                # Texte (simplifié)
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                except:
                    font = ImageFont.load_default()
                
                # Centrer le texte dans la bulle
                text_bbox = draw.textbbox((0, 0), text[:25], font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                text_x = x - text_width // 2
                text_y = y - text_height // 2
                
                draw.text((text_x, text_y), text[:25], fill="black", font=font)
                
                # Sauvegarder
                output_path = image_path.parent / f"page_{page_number}_bubble_{bubble_number}_fallback.png"
                img.save(output_path)
                
                print(f"         ✅ Fallback PIL sauvé: {output_path.name}")
                return output_path
                
        except Exception as e:
            print(f"         ❌ Erreur fallback PIL: {e}")
            return image_path  # Retourner l'image originale en cas d'échec total
    
    def _infer_positions_from_context(self, description: str) -> Dict[str, str]:
        """Inférence de positions depuis le contexte si aucune position explicite"""
        # Rechercher des indices contextuels
        context_positions = {}
        
        # Mots-clés indicateurs
        if "premiers" in description or "leader" in description:
            context_positions["character1"] = "left"
        if "suivant" in description or "second" in description:
            context_positions["character2"] = "right"
        if "groupe" in description or "ensemble" in description:
            context_positions["everyone"] = "center"
            
        return context_positions
    
    # === MÉTHODES D'ASSEMBLAGE ET EXPORT FINAL ===
    
    async def assemble_final_comic(self, processed_pages: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
        """
        📚 ASSEMBLAGE FINAL DE LA BD
        Crée les fichiers finaux prêts pour affichage/export
        """
        print("📚 Assemblage de la BD finale...")
        
        assembly_info = {
            "total_pages": len(processed_pages),
            "assembly_time": datetime.now().isoformat(),
            "pages": [],
            "export_formats": []
        }
        
        # Préparer chaque page
        for page in processed_pages:
            page_info = {
                "page_number": page.get("page_number"),
                "image_path": page.get("image_path"),
                "image_url": page.get("image_url"),
                "bubble_system": page.get("bubble_integration", "unknown"),
                "dialogues_count": len(page.get("dialogues", [])),
                "ready_for_display": Path(page.get("image_path", "")).exists()
            }
            assembly_info["pages"].append(page_info)
        
        # Créer un fichier JSON de métadonnées
        metadata_path = output_dir / "comic_final_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(assembly_info, f, indent=2, ensure_ascii=False)
        
        assembly_info["metadata_file"] = str(metadata_path)
        
        print(f"✅ BD assemblée: {len(processed_pages)} pages prêtes")
        return assembly_info
```
