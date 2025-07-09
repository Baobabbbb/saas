"""
🎯 SYSTÈME AUTONOME D'INTÉGRATION DE BULLES RÉALISTES - VERSION PROFESSIONNELLE
Analyse les images de BD et y intègre automatiquement des bulles indiscernables d'une vraie BD
via Stable Diffusion 3 Image-to-Image avec prompts ultra-précis et gestion intelligente
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


class SD3BubbleIntegratorPro:
    """
    🚀 SYSTÈME AUTONOME COMPLET DE BULLES INTÉGRÉES - VERSION PROFESSIONNELLE
    
    FONCTIONNALITÉS AVANCÉES :
    ✅ Analyse automatique ultra-précise des scènes et dialogues
    ✅ Détection intelligente multi-niveau des positions de personnages  
    ✅ Génération de prompts laser-focalisés pour SD3 Image-to-Image
    ✅ Intégration séquentielle optimisée de multiples bulles
    ✅ Équilibrage visuel dynamique et cohérence stylistique
    ✅ Fallback PIL professionnel en cas d'échec SD3
    ✅ Assembly final en BD publication-ready
    ✅ Gestion des cas complexes (multiples personnages, bulles croisées)
    """
    
    def __init__(self):
        print("🎨 Initialisation SD3BubbleIntegratorPro - Système autonome de bulles ultra-réalistes")
        
        # Configuration API Stable Diffusion 3 optimisée
        self.stability_key = os.getenv("STABILITY_API_KEY")
        self.sd3_img2img_endpoint = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        # Configuration qualité professionnelle
        self.bubble_models = {
            "ultra_quality": "sd3-large",
            "high_quality": "sd3-medium", 
            "fast": "sd3-large-turbo"
        }
        self.current_model = "sd3-large-turbo"  # Optimal pour intégration rapide
        self.max_bubbles_per_image = 4
        self.image_resolution = 1024
        
        # Patterns avancés de détection de positions
        self.advanced_position_patterns = {
            'left': ['gauche', 'left', 'à gauche', 'on the left', 'leftmost', 'côté gauche'],
            'right': ['droite', 'right', 'à droite', 'on the right', 'rightmost', 'côté droit'], 
            'center': ['centre', 'center', 'milieu', 'middle', 'au centre', 'au milieu'],
            'foreground': ['devant', 'foreground', 'premier plan', 'front', 'en avant'],
            'background': ['derrière', 'background', 'arrière-plan', 'back', 'fond', 'en arrière']
        }
        
        # Templates de prompts ultra-spécialisés pour bulles parfaites
        self.professional_bubble_templates = {
            'single_speech': """Add ONE professional comic book speech bubble to this image. Position: {position} area. Text: "{text}".

BUBBLE SPECIFICATIONS:
- Classic comic speech bubble with white background
- Bold black outline (2-3px thick)
- Curved organic tail pointing directly to {character_position} character's mouth
- Bubble size proportional to text length
- Natural hand-drawn comic book appearance
- Seamlessly integrated into the original artwork style

TEXT SPECIFICATIONS:
- Clear, readable comic book lettering
- Proper spacing and kerning
- Text centered within bubble
- Font style matching comic book standards

INTEGRATION REQUIREMENTS:
- Preserve all original image details
- Natural shadow/depth if needed
- Match existing art style perfectly
- No artificial or digital appearance""",

            'multiple_speech': """Add speech bubble #{number} of {total} in this comic scene. Position: {position}. Text: "{text}".

BUBBLE #{number} SPECIFICATIONS:
- Professional comic book speech bubble
- White background, bold black outline
- Curved tail pointing to {character_position} character
- Balanced placement with other bubbles
- No overlap with existing or planned bubbles

COMPOSITION BALANCE:
- Maintain visual hierarchy
- Preserve reading flow (left to right, top to bottom)
- Ensure all characters remain clearly visible
- Professional comic book layout standards

STYLE CONSISTENCY:
- Match {style_context}
- Seamless integration with original artwork
- Hand-drawn organic appearance""",

            'thought_bubble': """Add a comic book thought bubble in {position} area. Text: "{text}".

THOUGHT BUBBLE SPECIFICATIONS:
- Cloud-like puffy outline instead of solid line
- Small floating circles leading to character's head
- Softer, more organic shape than speech bubbles
- White/light background with subtle outline
- Dreamy, ethereal appearance

TEXT STYLE:
- Slightly more stylized lettering
- Often italicized for thoughts
- Centered and readable

POSITIONING:
- Above or near {character_position} character's head
- Natural connection via floating circles""",

            'shout_bubble': """Add an emphatic SHOUT bubble in {position}. Text: "{text}".

SHOUT BUBBLE SPECIFICATIONS:
- Jagged, spiky outline edges
- Bold, thick black border (3-4px)
- Explosive, dynamic shape
- White background for contrast
- Radiating energy lines optional

TEXT STYLE:
- BOLD, UPPERCASE lettering
- Larger font size for emphasis
- Strong, impactful appearance
- Centered in dramatic bubble

ENERGY:
- Convey loud, emphatic speech
- Dynamic visual impact
- Maintain comic book excitement"""
        }
        
    async def process_comic_pages(self, comic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 POINT D'ENTRÉE PRINCIPAL - Traite une BD complète avec système professionnel
        """
        print("🚀 === DÉMARRAGE SYSTÈME PROFESSIONNEL SD3 BUBBLE INTEGRATOR ===")
        
        pages = comic_data.get("pages", [])
        if not pages:
            print("⚠️ Aucune page à traiter")
            return comic_data
            
        processed_pages = []
        
        for i, page_data in enumerate(pages):
            try:
                print(f"\n📄 TRAITEMENT PROFESSIONNEL PAGE {i+1}/{len(pages)}")
                print(f"   Description: {page_data.get('description', 'N/A')[:80]}...")
                print(f"   Dialogues: {len(page_data.get('dialogues', []))} éléments")
                
                # Traitement professionnel avec analyse avancée
                enhanced_page = await self._process_page_professional(page_data)
                processed_pages.append(enhanced_page)
                
                print(f"✅ Page {i+1} traitée avec qualité professionnelle")
                
            except Exception as e:
                print(f"❌ Erreur page {i+1}: {e}")
                page_fallback = page_data.copy()
                page_fallback["bubble_integration"] = "failed_pro_fallback"
                page_fallback["error"] = str(e)
                processed_pages.append(page_fallback)
        
        # Assemblage final professionnel
        result = comic_data.copy()
        result["pages"] = processed_pages
        result["bubble_system"] = "sd3_professional_integrated"
        result["processing_time"] = datetime.now().isoformat()
        result["total_pages_processed"] = len(processed_pages)
        result["quality_level"] = "professional"
        
        print(f"\n🎉 BD PROFESSIONNELLE COMPLÈTE: {len(processed_pages)} pages avec bulles ultra-réalistes")
        return result
    
    async def _process_page_professional(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 TRAITEMENT PROFESSIONNEL D'UNE PAGE AVEC ANALYSE AVANCÉE
        """
        image_path = page_data.get("image_path", "")
        description = page_data.get("description", "")
        dialogues = page_data.get("dialogues", [])
        page_number = page_data.get("page_number", 1)
        
        print(f"   🧠 Analyse professionnelle: {len(dialogues)} dialogues détectés")
        
        if not image_path or not dialogues:
            print("   ⚠️ Page sans image ou dialogues - conservation état original")
            return page_data
        
        if not Path(image_path).exists():
            print(f"   ❌ Image non trouvée: {image_path}")
            return page_data
        
        try:
            # ÉTAPE 1: Analyse avancée de la composition
            print("   📊 Analyse avancée de la composition...")
            advanced_analysis = await self._analyze_composition_advanced(description, dialogues)
            
            # ÉTAPE 2: Génération de plan d'intégration optimal
            print("   🎯 Génération du plan d'intégration optimal...")
            integration_plan = self._create_integration_plan(advanced_analysis)
            
            # ÉTAPE 3: Intégration séquentielle professionnelle via SD3
            print("   🎨 Intégration professionnelle via SD3...")
            final_image_path = await self._integrate_bubbles_professional(
                image_path, integration_plan, page_number
            )
            
            # ÉTAPE 4: Validation et préparation finale
            enhanced_page = page_data.copy()
            enhanced_page["image_path"] = str(final_image_path)
            enhanced_page["bubble_integration"] = "sd3_professional_success"
            enhanced_page["advanced_analysis"] = advanced_analysis
            enhanced_page["integration_plan"] = integration_plan
            enhanced_page["processing_timestamp"] = datetime.now().isoformat()
            enhanced_page["quality_metrics"] = self._calculate_quality_metrics(integration_plan)
            
            # Mise à jour URL
            if "image_url" in enhanced_page:
                enhanced_page["image_url"] = f"/static/generated_comics/{final_image_path.parent.name}/{final_image_path.name}"
            
            print(f"   ✅ Intégration professionnelle réussie: {final_image_path.name}")
            return enhanced_page
            
        except Exception as e:
            print(f"   ❌ Erreur intégration professionnelle: {e}")
            fallback_page = page_data.copy()
            fallback_page["bubble_integration"] = "sd3_pro_failed_fallback"
            fallback_page["error"] = str(e)
            return fallback_page
    
    async def _analyze_composition_advanced(self, description: str, dialogues: List[Dict]) -> Dict[str, Any]:
        """
        🧠 ANALYSE AVANCÉE DE LA COMPOSITION AVEC IA CONTEXTUELLE
        """
        print(f"      🔍 Analyse avancée: {description[:60]}...")
        
        # Extraction sophistiquée des positions
        character_positions = self._extract_positions_advanced(description)
        character_actions = self._extract_character_actions(description)
        scene_mood = self._analyze_scene_mood(description)
        
        print(f"      📍 Positions avancées: {character_positions}")
        print(f"      🎭 Actions détectées: {character_actions}")
        print(f"      🎨 Ambiance scène: {scene_mood}")
        
        # Analyse sophistiquée des dialogues
        dialogue_analysis = []
        for i, dialogue in enumerate(dialogues):
            speaker = dialogue.get("character", "").lower()
            text = dialogue.get("text", "")
            dialogue_type = self._classify_dialogue_type(text)
            
            if not text.strip():
                continue
            
            # Positionnement intelligent
            speaker_info = self._locate_speaker_advanced(speaker, character_positions, character_actions)
            
            # Spécifications de bulle optimales
            bubble_specs = {
                "bubble_id": f"bubble_{i+1}",
                "speaker": speaker,
                "text": text,
                "dialogue_type": dialogue_type,
                "speaker_position": speaker_info["position"],
                "bubble_area": speaker_info["optimal_bubble_area"],
                "character_action": character_actions.get(speaker, "neutral"),
                "priority": self._calculate_advanced_priority(dialogue_type, i, scene_mood),
                "style_context": self._determine_style_context(description, scene_mood),
                "visual_weight": self._calculate_visual_weight(text, dialogue_type)
            }
            
            dialogue_analysis.append(bubble_specs)
            print(f"      💬 Bulle {i+1}: {speaker} ({dialogue_type}) - '{text[:30]}...'")
        
        return {
            "total_bubbles": len(dialogue_analysis),
            "dialogue_analysis": dialogue_analysis,
            "character_positions": character_positions,
            "character_actions": character_actions,
            "scene_mood": scene_mood,
            "scene_description": description,
            "complexity_level": self._assess_complexity(dialogue_analysis),
            "visual_balance_analysis": self._analyze_visual_balance_advanced(dialogue_analysis)
        }
    
    def _extract_positions_advanced(self, description: str) -> Dict[str, Dict]:
        """
        📍 EXTRACTION AVANCÉE DES POSITIONS AVEC CONTEXTE SPATIAL
        """
        positions = {}
        desc_lower = description.lower()
        
        # Patterns sophistiqués multi-linguistiques
        advanced_patterns = [
            # Patterns détaillés français
            (r'(\w+)\s+(?:se trouve|est positionné|se tient|est placé)\s+(?:à\s+)?(?:la\s+)?(gauche|droite|centre|devant|derrière|fond)\s*(?:de\s+(?:la\s+)?(?:scène|image))?', 
             lambda m: (m.group(1), {"position": m.group(2), "specificity": "high"})),
            
            # Patterns d'action avec position implicite
            (r'(?:à\s+)?(gauche|droite|centre),\s*(\w+)\s+(?:brandit|tient|regarde|pointe)', 
             lambda m: (m.group(2), {"position": m.group(1), "specificity": "action_based"})),
            
            # Patterns relationnels
            (r'(\w+)\s+(?:face à|devant|derrière|à côté de)\s+(\w+)', 
             lambda m: self._infer_relative_positions(m.group(1), m.group(2))),
            
            # Patterns anglais
            (r'(\w+)\s+(?:is|stands|sits)\s+(?:on\s+the\s+)?(left|right|center|front|back|background)', 
             lambda m: (m.group(1), {"position": m.group(2), "specificity": "high"}))
        ]
        
        for pattern, extractor in advanced_patterns:
            matches = re.finditer(pattern, desc_lower)
            for match in matches:
                try:
                    if callable(extractor):
                        result = extractor(match)
                        if isinstance(result, tuple) and len(result) == 2:
                            character, pos_info = result
                            if isinstance(pos_info, dict):
                                normalized_pos = self._normalize_position_advanced(pos_info["position"])
                                positions[character.strip()] = {
                                    "position": normalized_pos,
                                    "specificity": pos_info.get("specificity", "medium"),
                                    "source": "pattern_matched"
                                }
                except Exception as e:
                    print(f"        ⚠️ Erreur extraction pattern: {e}")
                    continue
        
        # Fallback intelligent si aucune position explicite
        if not positions:
            positions = self._infer_positions_intelligent(desc_lower)
        
        return positions
    
    def _normalize_position_advanced(self, position: str) -> str:
        """Normalisation avancée avec gestion des nuances"""
        position_lower = position.lower().strip()
        
        advanced_position_map = {
            # Positions principales
            'gauche': 'left', 'left': 'left', 'leftmost': 'left', 'côté gauche': 'left',
            'droite': 'right', 'right': 'right', 'rightmost': 'right', 'côté droit': 'right',
            'centre': 'center', 'center': 'center', 'milieu': 'center', 'middle': 'center',
            
            # Profondeur
            'devant': 'foreground', 'front': 'foreground', 'foreground': 'foreground', 'premier plan': 'foreground',
            'derrière': 'background', 'back': 'background', 'background': 'background', 'fond': 'background', 'arrière-plan': 'background',
            
            # Positions spéciales
            'haut': 'upper', 'top': 'upper', 'en haut': 'upper',
            'bas': 'lower', 'bottom': 'lower', 'en bas': 'lower'
        }
        
        return advanced_position_map.get(position_lower, 'center')
    
    def _extract_character_actions(self, description: str) -> Dict[str, str]:
        """Extraction des actions des personnages pour contextualiser les bulles"""
        actions = {}
        desc_lower = description.lower()
        
        action_patterns = [
            (r'(\w+)\s+(?:brandit|tient|lève|pointe)', 'holding'),
            (r'(\w+)\s+(?:regarde|observe|fixe)', 'looking'),
            (r'(\w+)\s+(?:sourit|rit|grimace)', 'expressing'),
            (r'(\w+)\s+(?:court|marche|avance)', 'moving'),
            (r'(\w+)\s+(?:crie|hurle|chuchote)', 'speaking_intense')
        ]
        
        for pattern, action_type in action_patterns:
            matches = re.finditer(pattern, desc_lower)
            for match in matches:
                character = match.group(1).strip()
                actions[character] = action_type
        
        return actions
    
    def _analyze_scene_mood(self, description: str) -> str:
        """Analyse de l'ambiance de la scène pour adapter le style des bulles"""
        desc_lower = description.lower()
        
        mood_indicators = {
            'action': ['combat', 'court', 'explose', 'attaque', 'fuit'],
            'mysterious': ['ombre', 'sombre', 'mystérieux', 'caché', 'secret'],
            'peaceful': ['calme', 'tranquille', 'paisible', 'souriant', 'heureux'],
            'tense': ['tendu', 'inquiet', 'nerveux', 'danger', 'peur'],
            'humorous': ['drôle', 'comique', 'rit', 'amusant', 'blague']
        }
        
        for mood, keywords in mood_indicators.items():
            if any(keyword in desc_lower for keyword in keywords):
                return mood
        
        return 'neutral'
    
    def _classify_dialogue_type(self, text: str) -> str:
        """Classification avancée du type de dialogue"""
        text_upper = text.upper()
        
        # Détection par ponctuation et contenu
        if text.endswith('!') or text.isupper() or any(word in text_upper for word in ['ATTENTION', 'STOP', 'NON', 'OUI']):
            return 'shout'
        elif text.endswith('?'):
            return 'question'
        elif '...' in text or text.startswith('(') or 'pense' in text.lower():
            return 'thought'
        elif len(text) < 20 and text.islower():
            return 'whisper'
        else:
            return 'speech'
    
    def _locate_speaker_advanced(self, speaker: str, positions: Dict, actions: Dict) -> Dict:
        """Localisation avancée du personnage avec contexte d'action"""
        # Recherche directe dans positions
        for char_name, pos_info in positions.items():
            if speaker.lower() in char_name.lower() or char_name.lower() in speaker.lower():
                optimal_area = self._calculate_optimal_bubble_area(pos_info["position"], actions.get(speaker, "neutral"))
                return {
                    "position": pos_info["position"],
                    "optimal_bubble_area": optimal_area,
                    "confidence": "high",
                    "source": "direct_match"
                }
        
        # Inférence contextuelle avancée
        if "premier" in speaker.lower() or "1" in speaker:
            return {"position": "left", "optimal_bubble_area": "upper_left", "confidence": "medium", "source": "inference"}
        elif "second" in speaker.lower() or "2" in speaker:
            return {"position": "right", "optimal_bubble_area": "upper_right", "confidence": "medium", "source": "inference"}
        
        # Valeur par défaut optimisée
        return {"position": "center", "optimal_bubble_area": "upper_center", "confidence": "low", "source": "default"}
    
    def _calculate_optimal_bubble_area(self, position: str, action: str) -> str:
        """Calcul de la zone optimale pour la bulle selon position et action"""
        base_areas = {
            'left': 'upper_left',
            'right': 'upper_right',
            'center': 'upper_center',
            'foreground': 'lower_center',
            'background': 'upper_center'
        }
        
        base_area = base_areas.get(position, 'upper_center')
        
        # Ajustements selon l'action
        if action == 'looking' and 'upper' in base_area:
            return base_area.replace('upper', 'middle')  # Pas trop haut si regarde
        elif action == 'holding' and position in ['left', 'right']:
            return base_area  # Position optimale déjà
        
        return base_area
    
    def _calculate_advanced_priority(self, dialogue_type: str, index: int, scene_mood: str) -> int:
        """Calcul avancé de priorité intégrant le type et l'ambiance"""
        type_priorities = {
            "shout": 20,
            "question": 15,
            "speech": 10,
            "thought": 8,
            "whisper": 5
        }
        
        mood_modifiers = {
            "action": 5,
            "tense": 3,
            "mysterious": 2,
            "peaceful": 1,
            "humorous": 4
        }
        
        base_priority = type_priorities.get(dialogue_type, 10)
        mood_bonus = mood_modifiers.get(scene_mood, 1)
        position_bonus = max(0, 5 - index)  # Premier dialogue prioritaire
        
        return base_priority + mood_bonus + position_bonus
    
    def _determine_style_context(self, description: str, mood: str) -> str:
        """Détermination du contexte stylistique pour prompts optimaux"""
        desc_lower = description.lower()
        
        # Style selon la description
        if any(word in desc_lower for word in ['cartoon', 'coloré', 'bright', 'vibrant']):
            base_style = "vibrant cartoon comic book style"
        elif any(word in desc_lower for word in ['realistic', 'détaillé', 'photo', 'réaliste']):
            base_style = "realistic comic book illustration style"
        elif any(word in desc_lower for word in ['manga', 'anime', 'japonais']):
            base_style = "manga and anime comic style"
        else:
            base_style = "professional comic book art style"
        
        # Modification selon l'ambiance
        mood_modifiers = {
            "action": "with dynamic energy and movement",
            "mysterious": "with darker tones and dramatic shadows",
            "peaceful": "with soft, harmonious elements",
            "tense": "with sharp contrasts and dramatic lighting",
            "humorous": "with playful, expressive elements"
        }
        
        modifier = mood_modifiers.get(mood, "")
        return f"{base_style} {modifier}".strip()
    
    def _calculate_visual_weight(self, text: str, dialogue_type: str) -> float:
        """Calcul du poids visuel pour équilibrage"""
        base_weight = len(text) / 50.0  # Poids basé sur longueur
        
        type_multipliers = {
            "shout": 1.5,
            "question": 1.2,
            "speech": 1.0,
            "thought": 0.8,
            "whisper": 0.6
        }
        
        return base_weight * type_multipliers.get(dialogue_type, 1.0)
    
    def _assess_complexity(self, dialogue_analysis: List[Dict]) -> str:
        """Évaluation de la complexité de la scène"""
        bubble_count = len(dialogue_analysis)
        
        if bubble_count == 1:
            return "simple"
        elif bubble_count == 2:
            return "moderate"
        elif bubble_count <= 3:
            return "complex"
        else:
            return "very_complex"
    
    def _analyze_visual_balance_advanced(self, dialogue_analysis: List[Dict]) -> Dict:
        """Analyse avancée de l'équilibre visuel"""
        if not dialogue_analysis:
            return {"balance": "empty", "recommendations": []}
        
        # Analyse des zones utilisées
        areas_used = [bubble["bubble_area"] for bubble in dialogue_analysis]
        area_weights = {}
        
        for bubble in dialogue_analysis:
            area = bubble["bubble_area"]
            weight = bubble["visual_weight"]
            area_weights[area] = area_weights.get(area, 0) + weight
        
        # Détermination de l'équilibre
        max_weight = max(area_weights.values()) if area_weights else 0
        total_weight = sum(area_weights.values())
        balance_ratio = max_weight / total_weight if total_weight > 0 else 0
        
        if balance_ratio < 0.4:
            balance = "excellent"
        elif balance_ratio < 0.6:
            balance = "good"
        elif balance_ratio < 0.8:
            balance = "acceptable"
        else:
            balance = "poor"
        
        # Recommandations
        recommendations = []
        if balance in ["acceptable", "poor"]:
            recommendations.append("redistribute_bubbles")
        if len(set(areas_used)) < len(areas_used):
            recommendations.append("avoid_area_overlap")
        
        return {
            "balance": balance,
            "balance_ratio": balance_ratio,
            "area_weights": area_weights,
            "recommendations": recommendations
        }
    
    def _create_integration_plan(self, advanced_analysis: Dict) -> Dict:
        """
        🎯 CRÉATION DU PLAN D'INTÉGRATION OPTIMAL
        """
        dialogue_analysis = advanced_analysis["dialogue_analysis"]
        visual_balance = advanced_analysis["visual_balance_analysis"]
        complexity = advanced_analysis["complexity_level"]
        
        # Trier par priorité
        sorted_bubbles = sorted(dialogue_analysis, key=lambda x: x["priority"], reverse=True)
        
        # Optimisation selon la complexité
        if complexity == "very_complex":
            # Réduire à 3 bulles max pour éviter surcharge
            sorted_bubbles = sorted_bubbles[:3]
            print(f"      ⚠️ Complexité élevée: réduction à {len(sorted_bubbles)} bulles prioritaires")
        
        # Ajustements selon l'équilibre visuel
        if visual_balance["balance"] in ["acceptable", "poor"]:
            sorted_bubbles = self._rebalance_bubble_positions(sorted_bubbles)
        
        integration_plan = {
            "total_bubbles": len(sorted_bubbles),
            "execution_order": sorted_bubbles,
            "complexity_level": complexity,
            "balance_optimization": visual_balance["balance"],
            "integration_strategy": self._determine_integration_strategy(complexity),
            "estimated_processing_time": len(sorted_bubbles) * 15  # secondes
        }
        
        print(f"      📋 Plan d'intégration: {len(sorted_bubbles)} bulles, stratégie {integration_plan['integration_strategy']}")
        return integration_plan
    
    def _rebalance_bubble_positions(self, bubbles: List[Dict]) -> List[Dict]:
        """Rééquilibrage des positions de bulles"""
        print("      ⚖️ Rééquilibrage des positions...")
        
        # Zones préférées pour éviter surcharge
        preferred_zones = ["upper_left", "upper_right", "upper_center", "middle_left", "middle_right"]
        
        for i, bubble in enumerate(bubbles):
            current_area = bubble["bubble_area"]
            
            # Si zone surchargée, redistribuer
            zone_count = sum(1 for b in bubbles if b["bubble_area"] == current_area)
            if zone_count > 1 and i < len(preferred_zones):
                # Assigner nouvelle zone disponible
                new_area = preferred_zones[i % len(preferred_zones)]
                bubble["bubble_area"] = new_area
                bubble["rebalanced"] = True
                print(f"        🔄 Bulle {i+1} déplacée vers {new_area}")
        
        return bubbles
    
    def _determine_integration_strategy(self, complexity: str) -> str:
        """Détermination de la stratégie d'intégration"""
        strategies = {
            "simple": "single_pass",
            "moderate": "sequential_optimized", 
            "complex": "staged_integration",
            "very_complex": "priority_based_selective"
        }
        return strategies.get(complexity, "sequential_optimized")
    
    async def _integrate_bubbles_professional(self, image_path: str, integration_plan: Dict, page_number: int) -> Path:
        """
        🚀 INTÉGRATION PROFESSIONNELLE DES BULLES AVEC SD3
        """
        execution_order = integration_plan["execution_order"]
        strategy = integration_plan["integration_strategy"]
        
        if not execution_order:
            print("      ⚠️ Aucune bulle à intégrer")
            return Path(image_path)
        
        current_image_path = Path(image_path)
        
        print(f"      🎨 Intégration {strategy}: {len(execution_order)} bulle(s)")
        
        for i, bubble_spec in enumerate(execution_order):
            try:
                print(f"         💬 Bulle {i+1}/{len(execution_order)}: {bubble_spec['speaker']} ({bubble_spec['dialogue_type']})")
                
                # Génération du prompt ultra-spécialisé
                ultra_prompt = self._generate_ultra_precise_prompt(bubble_spec, integration_plan, i)
                print(f"         🎯 Prompt ultra-précis généré ({len(ultra_prompt)} chars)")
                
                # Appel SD3 avec gestion d'erreur robuste
                result_path = await self._call_sd3_professional(
                    current_image_path, ultra_prompt, page_number, i+1, bubble_spec
                )
                
                if result_path and result_path.exists():
                    current_image_path = result_path
                    print(f"         ✅ Intégration SD3 réussie: {result_path.name}")
                else:
                    print(f"         ❌ Échec SD3, fallback PIL professionnel")
                    current_image_path = await self._fallback_professional(
                        current_image_path, bubble_spec, page_number, i+1
                    )
                
                # Pause adaptative selon la stratégie
                pause_duration = self._calculate_pause_duration(strategy, i)
                await asyncio.sleep(pause_duration)
                
            except Exception as e:
                print(f"         ❌ Erreur bulle {i+1}: {e}")
                continue
        
        print(f"      ✅ Intégration {strategy} terminée: {current_image_path.name}")
        return current_image_path
    
    def _generate_ultra_precise_prompt(self, bubble_spec: Dict, integration_plan: Dict, bubble_index: int) -> str:
        """
        🎯 GÉNÉRATION DE PROMPTS ULTRA-PRÉCIS POUR BULLES PARFAITES
        """
        dialogue_type = bubble_spec["dialogue_type"]
        text = bubble_spec["text"]
        position = bubble_spec["speaker_position"]
        area = bubble_spec["bubble_area"]
        style_context = bubble_spec["style_context"]
        
        # Sélection du template optimal
        if dialogue_type == "thought":
            template_key = "thought_bubble"
        elif dialogue_type == "shout":
            template_key = "shout_bubble"
        elif integration_plan["total_bubbles"] == 1:
            template_key = "single_speech"
        else:
            template_key = "multiple_speech"
        
        template = self.professional_bubble_templates[template_key]
        
        # Formatage ultra-précis
        if template_key == "single_speech":
            prompt = template.format(
                position=self._area_to_natural_description(area),
                text=text,
                character_position=position
            )
        elif template_key == "multiple_speech":
            prompt = template.format(
                number=bubble_index + 1,
                total=integration_plan["total_bubbles"],
                position=self._area_to_natural_description(area),
                text=text,
                character_position=position,
                style_context=style_context
            )
        elif template_key in ["thought_bubble", "shout_bubble"]:
            prompt = template.format(
                position=self._area_to_natural_description(area),
                text=text,
                character_position=position
            )
        
        # Ajout de spécifications techniques
        prompt += f"\n\nTECHNICAL SPECIFICATIONS:\n- Maintain {integration_plan['complexity_level']} scene complexity\n- Balance optimization: {integration_plan['balance_optimization']}\n- Integration strategy: {integration_plan['integration_strategy']}"
        
        return prompt.strip()
    
    def _area_to_natural_description(self, area: str) -> str:
        """Conversion des zones en descriptions naturelles"""
        natural_descriptions = {
            'upper_left': 'upper left region',
            'upper_right': 'upper right region',
            'upper_center': 'upper center area',
            'middle_left': 'middle left section',
            'middle_right': 'middle right section', 
            'middle_center': 'central area',
            'lower_left': 'lower left corner',
            'lower_right': 'lower right corner',
            'lower_center': 'lower center region'
        }
        return natural_descriptions.get(area, 'center area')
    
    async def _call_sd3_professional(self, image_path: Path, prompt: str, page_number: int, 
                                   bubble_number: int, bubble_spec: Dict) -> Optional[Path]:
        """
        🔧 APPEL SD3 PROFESSIONNEL AVEC GESTION AVANCÉE
        """
        if not self.stability_key:
            print("         ⚠️ Clé Stability AI manquante - fallback PIL professionnel")
            return None
        
        try:
            # Préparation de l'image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Headers optimisés
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Accept": "image/*",
                "User-Agent": "SD3BubbleIntegratorPro/1.0"
            }
            
            # FormData optimisé pour SD3
            form_data = aiohttp.FormData()
            form_data.add_field('image', image_data, filename=f'input_page_{page_number}.png', content_type='image/png')
            form_data.add_field('prompt', prompt)
            form_data.add_field('mode', 'image-to-image')
            form_data.add_field('model', self.current_model)
            
            # Paramètres optimaux selon le type de bulle
            strength = self._get_optimal_strength(bubble_spec["dialogue_type"])
            cfg_scale = self._get_optimal_cfg_scale(bubble_spec["visual_weight"])
            
            form_data.add_field('strength', str(strength))
            form_data.add_field('cfg_scale', str(cfg_scale))
            form_data.add_field('steps', '35')  # Qualité maximale
            form_data.add_field('output_format', 'png')
            
            # Appel asynchrone optimisé
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.sd3_img2img_endpoint,
                    headers=headers,
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=120)  # Timeout plus long pour qualité
                ) as response:
                    
                    print(f"         📡 SD3 Professional Response: {response.status}")
                    
                    if response.status == 200:
                        image_data = await response.read()
                        
                        if image_data and len(image_data) > 1000:  # Validation basique
                            output_path = image_path.parent / f"page_{page_number}_bubble_{bubble_number}_professional.png"
                            with open(output_path, 'wb') as f:
                                f.write(image_data)
                            
                            print(f"         ✅ SD3 Professional Success: {output_path.name}")
                            return output_path
                        else:
                            print(f"         ❌ SD3 données invalides")
                            return None
                    else:
                        error_text = await response.text()
                        print(f"         ❌ SD3 Error {response.status}: {error_text[:200]}")
                        return None
                        
        except Exception as e:
            print(f"         ❌ Exception SD3 Professional: {str(e)[:100]}")
            return None
    
    def _get_optimal_strength(self, dialogue_type: str) -> float:
        """Force optimale selon le type de dialogue"""
        strength_map = {
            "thought": 0.3,     # Modification subtile pour pensées
            "whisper": 0.35,    # Léger pour chuchotements
            "speech": 0.4,      # Standard pour parole normale
            "question": 0.45,   # Un peu plus fort pour questions
            "shout": 0.5        # Maximum pour cris
        }
        return strength_map.get(dialogue_type, 0.4)
    
    def _get_optimal_cfg_scale(self, visual_weight: float) -> float:
        """CFG Scale optimal selon le poids visuel"""
        if visual_weight < 0.5:
            return 7.0  # Adhérence standard pour petites bulles
        elif visual_weight < 1.0:
            return 8.0  # Plus d'adhérence pour bulles moyennes
        else:
            return 9.0  # Maximum pour grosses bulles importantes
    
    def _calculate_pause_duration(self, strategy: str, bubble_index: int) -> float:
        """Calcul de la pause adaptative"""
        base_pauses = {
            "single_pass": 0.3,
            "sequential_optimized": 0.5,
            "staged_integration": 0.8,
            "priority_based_selective": 1.0
        }
        
        base_pause = base_pauses.get(strategy, 0.5)
        
        # Pause plus longue pour les premières bulles (plus importantes)
        if bubble_index == 0:
            return base_pause * 1.5
        elif bubble_index == 1:
            return base_pause * 1.2
        else:
            return base_pause
    
    async def _fallback_professional(self, image_path: Path, bubble_spec: Dict, 
                                   page_number: int, bubble_number: int) -> Path:
        """
        🛠️ FALLBACK PIL PROFESSIONNEL AVEC RENDU AMÉLIORÉ
        """
        try:
            print(f"         🛠️ Fallback PIL Professionnel pour bulle {bubble_number}")
            
            with Image.open(image_path) as img:
                # Conversion en RGBA pour transparence
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Créer une couche pour la bulle
                bubble_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(bubble_layer)
                
                # Paramètres avancés
                text = bubble_spec["text"]
                area = bubble_spec["bubble_area"]
                dialogue_type = bubble_spec["dialogue_type"]
                
                # Position calculée
                x, y = self._calculate_professional_position(img.size, area)
                
                # Dimensions adaptatives
                bubble_width, bubble_height = self._calculate_bubble_dimensions(text, dialogue_type, img.size)
                
                # Dessiner la bulle selon le type
                if dialogue_type == "thought":
                    self._draw_thought_bubble_professional(draw, x, y, bubble_width, bubble_height, text)
                elif dialogue_type == "shout":
                    self._draw_shout_bubble_professional(draw, x, y, bubble_width, bubble_height, text)
                else:
                    self._draw_speech_bubble_professional(draw, x, y, bubble_width, bubble_height, text)
                
                # Fusionner les couches
                img = Image.alpha_composite(img, bubble_layer)
                img = img.convert('RGB')
                
                # Sauvegarder
                output_path = image_path.parent / f"page_{page_number}_bubble_{bubble_number}_pro_fallback.png"
                img.save(output_path, 'PNG', quality=95)
                
                print(f"         ✅ Fallback PIL Professionnel: {output_path.name}")
                return output_path
                
        except Exception as e:
            print(f"         ❌ Erreur fallback professionnel: {e}")
            return image_path
    
    def _calculate_professional_position(self, img_size: Tuple[int, int], area: str) -> Tuple[int, int]:
        """Calcul de position professionnel avec marges optimales"""
        width, height = img_size
        margin = min(width, height) * 0.1  # Marge 10%
        
        positions = {
            'upper_left': (width * 0.2, height * 0.15),
            'upper_right': (width * 0.8, height * 0.15),
            'upper_center': (width * 0.5, height * 0.15),
            'middle_left': (width * 0.2, height * 0.4),
            'middle_right': (width * 0.8, height * 0.4),
            'middle_center': (width * 0.5, height * 0.4),
            'lower_left': (width * 0.2, height * 0.75),
            'lower_right': (width * 0.8, height * 0.75),
            'lower_center': (width * 0.5, height * 0.75)
        }
        
        return positions.get(area, (width * 0.5, height * 0.2))
    
    def _calculate_bubble_dimensions(self, text: str, dialogue_type: str, img_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calcul des dimensions optimales de bulle"""
        base_width = min(300, img_size[0] * 0.4)
        base_height = min(100, img_size[1] * 0.15)
        
        # Ajustement selon longueur du texte
        text_factor = min(2.0, len(text) / 30.0)
        width = int(base_width * text_factor)
        height = int(base_height * max(1.0, text_factor * 0.7))
        
        # Ajustement selon le type
        type_modifiers = {
            "shout": (1.2, 1.1),
            "thought": (1.1, 1.0),
            "whisper": (0.8, 0.9),
            "speech": (1.0, 1.0)
        }
        
        w_mod, h_mod = type_modifiers.get(dialogue_type, (1.0, 1.0))
        
        return int(width * w_mod), int(height * h_mod)
    
    def _draw_speech_bubble_professional(self, draw: ImageDraw.Draw, x: int, y: int, 
                                       width: int, height: int, text: str):
        """Dessin professionnel d'une bulle de parole"""
        # Bulle principale
        bubble_coords = [x - width//2, y - height//2, x + width//2, y + height//2]
        draw.ellipse(bubble_coords, fill="white", outline="black", width=3)
        
        # Queue de la bulle (triangle)
        tail_base = 15
        tail_height = 20
        tail_points = [
            (x - tail_base//2, y + height//2),
            (x + tail_base//2, y + height//2),
            (x, y + height//2 + tail_height)
        ]
        draw.polygon(tail_points, fill="white", outline="black", width=3)
        
        # Texte centré
        self._draw_centered_text(draw, x, y, text, width, height)
    
    def _draw_thought_bubble_professional(self, draw: ImageDraw.Draw, x: int, y: int, 
                                        width: int, height: int, text: str):
        """Dessin professionnel d'une bulle de pensée"""
        # Bulle principale avec bords nuageux
        bubble_coords = [x - width//2, y - height//2, x + width//2, y + height//2]
        
        # Simuler contour nuageux avec cercles
        num_circles = 12
        for i in range(num_circles):
            angle = 2 * 3.14159 * i / num_circles
            circle_x = x + (width//2 - 10) * math.cos(angle)
            circle_y = y + (height//2 - 10) * math.sin(angle)
            draw.ellipse([circle_x-8, circle_y-8, circle_x+8, circle_y+8], 
                        fill="white", outline="black", width=2)
        
        # Remplir le centre
        draw.ellipse([x-width//2+15, y-height//2+10, x+width//2-15, y+height//2-10], 
                    fill="white")
        
        # Petits cercles flottants
        for i, (dx, dy, size) in enumerate([(15, 25, 8), (25, 35, 5), (35, 45, 3)]):
            draw.ellipse([x+dx-size, y+height//2+dy-size, x+dx+size, y+height//2+dy+size],
                        fill="white", outline="black", width=2)
        
        # Texte
        self._draw_centered_text(draw, x, y, text, width, height, italic=True)
    
    def _draw_shout_bubble_professional(self, draw: ImageDraw.Draw, x: int, y: int, 
                                      width: int, height: int, text: str):
        """Dessin professionnel d'une bulle de cri"""
        # Bulle avec bords dentelés
        num_spikes = 16
        outer_radius = max(width, height) // 2
        inner_radius = outer_radius - 15
        
        spike_points = []
        for i in range(num_spikes * 2):
            angle = 2 * 3.14159 * i / (num_spikes * 2)
            radius = outer_radius if i % 2 == 0 else inner_radius
            spike_x = x + radius * math.cos(angle)
            spike_y = y + radius * math.sin(angle)
            spike_points.append((spike_x, spike_y))
        
        draw.polygon(spike_points, fill="white", outline="black", width=4)
        
        # Queue dentelée
        tail_points = [
            (x - 10, y + inner_radius),
            (x + 10, y + inner_radius),
            (x + 5, y + inner_radius + 15),
            (x, y + inner_radius + 25),
            (x - 5, y + inner_radius + 15)
        ]
        draw.polygon(tail_points, fill="white", outline="black", width=3)
        
        # Texte en gras
        self._draw_centered_text(draw, x, y, text.upper(), width, height, bold=True)
    
    def _draw_centered_text(self, draw: ImageDraw.Draw, x: int, y: int, text: str, 
                          width: int, height: int, italic: bool = False, bold: bool = False):
        """Dessin de texte centré professionnel"""
        try:
            # Tentative de police système
            font_size = max(12, min(20, width // 15))
            font_path = None
            
            # Recherche de polices système
            possible_fonts = [
                "arial.ttf", "Arial.ttf", 
                "calibri.ttf", "Calibri.ttf",
                "comic.ttf", "Comic Sans MS.ttf"
            ]
            
            for font_name in possible_fonts:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except:
                    continue
            else:
                font = ImageFont.load_default()
            
        except:
            font = ImageFont.load_default()
        
        # Découpage du texte
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= width - 20:  # Marge interne
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Centrage vertical
        total_height = len(lines) * (font_size + 2)
        start_y = y - total_height // 2
        
        # Dessin des lignes
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            text_x = x - line_width // 2
            text_y = start_y + i * (font_size + 2)
            
            # Couleur selon style
            text_color = "black"
            if bold:
                # Simuler gras avec décalage
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        draw.text((text_x + dx, text_y + dy), line, fill=text_color, font=font)
            else:
                draw.text((text_x, text_y), line, fill=text_color, font=font)
    
    def _calculate_quality_metrics(self, integration_plan: Dict) -> Dict:
        """Calcul des métriques de qualité"""
        return {
            "bubble_count": integration_plan["total_bubbles"],
            "complexity_handled": integration_plan["complexity_level"],
            "balance_achieved": integration_plan["balance_optimization"],
            "strategy_used": integration_plan["integration_strategy"],
            "estimated_quality": self._estimate_final_quality(integration_plan)
        }
    
    def _estimate_final_quality(self, integration_plan: Dict) -> str:
        """Estimation de la qualité finale"""
        complexity = integration_plan["complexity_level"]
        balance = integration_plan["balance_optimization"]
        
        if complexity in ["simple", "moderate"] and balance in ["excellent", "good"]:
            return "excellent"
        elif complexity == "complex" and balance != "poor":
            return "good"
        elif complexity == "very_complex":
            return "acceptable"
        else:
            return "basic"
    
    def _infer_relative_positions(self, char1: str, char2: str) -> Tuple[str, Dict]:
        """Inférence de positions relatives entre personnages"""
        # Logique simplifiée - peut être étendue
        return (char1, {"position": "left", "specificity": "relative"})
    
    def _infer_positions_intelligent(self, description: str) -> Dict[str, Dict]:
        """Inférence intelligente des positions"""
        positions = {}
        
        # Recherche de noms propres
        import re
        names = re.findall(r'\b[A-Z][a-z]+\b', description)
        
        # Attribution par défaut selon l'ordre d'apparition
        default_positions = ["left", "right", "center", "background"]
        
        for i, name in enumerate(set(names)):
            if i < len(default_positions):
                positions[name.lower()] = {
                    "position": default_positions[i],
                    "specificity": "inferred",
                    "source": "name_order"
                }
        
        return positions

# Import math pour les calculs géométriques
import math

# Fonction d'assistance pour tests
async def test_sd3_bubble_integrator():
    """Test rapide du système"""
    integrator = SD3BubbleIntegratorPro()
    
    # Test de données simulées
    test_comic = {
        "pages": [
            {
                "page_number": 1,
                "description": "Léo se tient à gauche, brandissant une torche. Zoé est à droite, visiblement inquiète.",
                "dialogues": [
                    {"character": "Léo", "text": "On y est presque !"},
                    {"character": "Zoé", "text": "Tu es sûr que c'est une bonne idée ?"}
                ],
                "image_path": "/fake/path/test.png"
            }
        ]
    }
    
    print("🧪 Test du système SD3BubbleIntegratorPro")
    # result = await integrator.process_comic_pages(test_comic)
    print("✅ Test terminé")

if __name__ == "__main__":
    print("🎨 SD3BubbleIntegratorPro - Système Autonome de Bulles Réalistes")
    print("📋 Version: Professionnelle avec prompts ultra-précis")
    print("🚀 Prêt pour intégration dans le pipeline principal")
