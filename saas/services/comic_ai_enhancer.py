"""
Module d'amélioration IA pour les bulles de bande dessinée
Utilise GPT-4o pour l'analyse d'images et GPT-4o-mini pour les dialogues
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import openai
import base64
import json
import os
import math
import asyncio
from typing import Dict, List, Tuple, Any
from pathlib import Path
from dotenv import load_dotenv


class ComicAIEnhancer:
    def __init__(self):
        """Initialise le module IA pour l'amélioration des BD"""
        load_dotenv()
        
        # Configuration OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-test-"):
            print("⚠️ Clé API OpenAI manquante ou factice - Mode test activé")
            self.openai_client = None
            self.test_mode = True
        else:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=api_key)
            self.test_mode = False
        
        # Configuration des modèles
        self.vision_model = os.getenv("COMIC_VISION_MODEL", "gpt-4o")
        self.text_model = os.getenv("COMIC_TEXT_MODEL", "gpt-4o-mini")
        self.enabled = os.getenv("ENABLE_AI_BUBBLES", "true").lower() == "true"
        
    async def enhance_comic_page(self, 
                                image_path: str, 
                                story_context: Dict[str, Any],
                                comic_dir: Path,
                                page_number: int) -> Path:
        """
        Analyse l'image et génère des bulles cohérentes avec IA
        Retourne le chemin de l'image améliorée
        """
        if not self.enabled:
            # Si l'IA est désactivée, retourner l'image originale
            print("⚠️ IA désactivée - retour image originale")
            final_path = comic_dir / f"page_{page_number}_final.png"
            img = Image.open(image_path)
            img.save(final_path, 'PNG')
            return final_path
        
        try:
            print(f"🤖 Amélioration IA de la page {page_number}...")
            
            # 1. Analyser l'image pour détecter les personnages
            character_positions = await self._detect_characters(image_path)
            
            # 2. Générer des dialogues cohérents avec l'histoire
            characters = [story_context.get("hero_name", "Héros")]
            dialogues = await self._generate_contextual_dialogues(
                story_context, page_number, characters, character_positions
            )
            
            # 3. Optimiser le placement des bulles
            optimized_bubbles = self._optimize_bubble_placement(
                dialogues, character_positions
            )
            
            # 4. Appliquer les bulles sur l'image et sauvegarder
            final_path = await self._apply_ai_bubbles(
                image_path, optimized_bubbles, comic_dir, page_number
            )
            
            print(f"✅ Page {page_number} améliorée avec {len(dialogues)} bulles")
            
            return final_path
            
        except Exception as e:
            print(f"⚠️ Erreur lors de l'amélioration IA de la page {page_number}: {e}")
            # Fallback : retourner l'image originale
            final_path = comic_dir / f"page_{page_number}_final.png"
            img = Image.open(image_path)
            img.save(final_path, 'PNG')
            return final_path
    
    async def _detect_characters(self, image_path: str) -> Dict[str, Any]:
        """
        Utilise GPT-4o pour analyser l'image en profondeur et détecter personnages et composition
        """
        if self.test_mode:
            print("🧪 Mode test: génération de données factices pour la détection de personnages")
            return {
                "characters": [
                    {
                        "name": "Héros principal",
                        "position": {"x": 0.3, "y": 0.6},
                        "face_direction": "right",
                        "mouth_position": {"x": 0.32, "y": 0.58},
                        "expression": "excited",
                        "description": "Personnage principal au centre de l'image"
                    }
                ],
                "free_zones": [
                    {"x": 0.1, "y": 0.1, "width": 0.25, "height": 0.15, "quality": "excellent"},
                    {"x": 0.65, "y": 0.05, "width": 0.3, "height": 0.2, "quality": "good"}
                ],
                "image_analysis": {
                    "dominant_colors": ["blue", "green"],
                    "style": "cartoon",
                    "busy_areas": [{"x": 0.4, "y": 0.7, "width": 0.3, "height": 0.2}]
                }
            }

        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = await self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Tu es un expert en bande dessinée professionnelle. Analyse minutieusement cette image pour créer des bulles de dialogue ULTRA-RÉALISTES.

ANALYSE REQUISE :
1. **Personnages** - Position précise, direction du regard, position de la bouche, expression
2. **Zones libres** - Espaces optimaux pour bulles (éviter éléments importants)
3. **Composition** - Style artistique, couleurs dominantes, zones chargées à éviter
4. **Perspectives** - Profondeur, premier/arrière-plan

ATTENTION : Les bulles doivent être comme dans une vraie BD professionnelle :
- Queues pointant PRÉCISÉMENT vers la bouche du personnage
- Formes organiques qui s'adaptent au contenu
- Placement intelligent qui respecte la composition
- Éviter les zones détaillées/importantes de l'image

Réponds UNIQUEMENT en JSON valide :
{
    "characters": [
        {
            "position": {"x": 0.3, "y": 0.6},
            "face_direction": "left/right/front/back",
            "mouth_position": {"x": 0.32, "y": 0.58},
            "expression": "happy/sad/angry/surprised/excited/neutral/worried",
            "size": {"width": 0.2, "height": 0.4},
            "speaking_likely": true,
            "thought_likely": false
        }
    ],
    "optimal_bubble_zones": [
        {
            "x": 0.1, "y": 0.1, 
            "width": 0.3, "height": 0.2, 
            "quality": "excellent/good/poor",
            "reason": "espace libre au-dessus du personnage"
        }
    ],
    "avoid_zones": [
        {
            "x": 0.4, "y": 0.7, 
            "width": 0.3, "height": 0.2,
            "reason": "zone détaillée importante"
        }
    ],
    "image_style": {
        "art_style": "cartoon/manga/realistic",
        "color_scheme": "bright/dark/pastel",
        "bubble_style_recommendation": "round/spiky/cloud/rectangular"
    }
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"🔍 Analyse GPT-4o terminée: {len(result.get('characters', []))} personnages détectés")
            return result
            
        except Exception as e:
            print(f"⚠️ Erreur détection personnages: {e}")
            # Fallback basique
            return {
                "characters": [
                    {
                        "position": {"x": 0.5, "y": 0.6},
                        "face_direction": "front",
                        "mouth_position": {"x": 0.5, "y": 0.58},
                        "expression": "neutral",
                        "size": {"width": 0.2, "height": 0.3},
                        "speaking_likely": True,
                        "thought_likely": False
                    }
                ],
                "optimal_bubble_zones": [
                    {"x": 0.1, "y": 0.1, "width": 0.3, "height": 0.2, "quality": "good"},
                    {"x": 0.6, "y": 0.1, "width": 0.3, "height": 0.2, "quality": "good"}
                ],
                "avoid_zones": [],
                "image_style": {
                    "art_style": "cartoon",
                    "color_scheme": "bright",
                    "bubble_style_recommendation": "round"
                }
            }
    
    async def _generate_contextual_dialogues(self, 
                                           story_context: Dict,
                                           page_number: int,
                                           characters: List[str],
                                           character_analysis: Dict) -> List[Dict[str, Any]]:
        """
        Génère des dialogues ultra-contextuels avec GPT-4o-mini basés sur l'analyse d'image
        """
        if self.test_mode:
            print("🧪 Mode test: génération de dialogues factices")
            return [
                {
                    "text": "Quelle aventure nous attend ?",
                    "character_index": 0,
                    "type": "speech",
                    "emotion": "curious",
                    "priority": "high"
                }
            ]

        try:
            detected_chars = character_analysis.get("characters", [])
            image_style = character_analysis.get("image_style", {})
            
            # Limiter à 1-2 bulles maximum pour éviter la surcharge
            max_dialogues = min(len(detected_chars), 2)
            
            if max_dialogues == 0:
                return []

            # Analyser les expressions et probabilités de parole
            speaking_chars = []
            for i, char in enumerate(detected_chars[:max_dialogues]):
                if char.get("speaking_likely", True):
                    speaking_chars.append({
                        "index": i,
                        "expression": char.get("expression", "neutral"),
                        "face_direction": char.get("face_direction", "front")
                    })

            if not speaking_chars:
                speaking_chars = [{"index": 0, "expression": "neutral", "face_direction": "front"}]

            # Extraire le nom du héros principal
            hero_name = story_context.get("hero_name", "Héros")
            story_type = story_context.get("story_type", "adventure")
            style = story_context.get("style", "cartoon")

            prompt = f"""Tu es un scénariste BD professionnel. Crée des dialogues COURTS et IMPACTANTS pour cette page {page_number}.

CONTEXTE HISTOIRE :
- Héros: {hero_name}
- Type: {story_type}
- Style: {style}
- Page: {page_number}

ANALYSE VISUELLE :
- Personnages détectés: {len(detected_chars)}
- Expressions: {[char.get('expression') for char in detected_chars]}
- Style artistique: {image_style.get('art_style', 'cartoon')}

RÈGLES STRICTES :
1. Maximum {max_dialogues} dialogues courts (3-8 mots MAX)
2. Adapter au style et à l'expression détectée
3. Cohérence avec l'histoire et la page
4. Types selon l'expression :
   - "speech" : dialogue normal (expression neutre/happy)
   - "thought" : pensée interne (expression concentrée/worried)
   - "shout" : exclamation (expression excited/surprised)
   - "whisper" : chuchotement (expression mystérieuse)

EXPRESSIONS DÉTECTÉES :
{[f"Personnage {i}: {char.get('expression', 'neutral')}" for i, char in enumerate(detected_chars)]}

Réponds en JSON valide avec dialogues adaptés aux expressions :
{{
    "dialogues": [
        {{
            "character_index": 0,
            "text": "Dialogue court adapté",
            "type": "speech/thought/shout/whisper",
            "emotion": "expression_detectee",
            "priority": "high/medium"
        }}
    ]
}}"""
            
            response = await self.openai_client.chat.completions.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            dialogues = result.get("dialogues", [])
            
            print(f"💬 Dialogues générés: {len(dialogues)} bulles contextuelles")
            return dialogues[:max_dialogues]  # Sécurité
            
        except Exception as e:
            print(f"⚠️ Erreur génération dialogues: {e}")
            # Fallback avec dialogue adapté au contexte
            hero_name = story_context.get("hero_name", "Héros") if isinstance(story_context, dict) else "Héros"
            return [
                {
                    "character_index": 0,
                    "text": f"En avant {hero_name} !",
                    "type": "speech",
                    "emotion": "excited",
                    "priority": "medium"
                }
            ]
    
    def _optimize_bubble_placement(self, 
                                 dialogues: List[Dict],
                                 character_analysis: Dict) -> List[Dict[str, Any]]:
        """
        Placement intelligent des bulles basé sur l'analyse GPT-4o de l'image
        """
        bubbles = []
        characters = character_analysis.get("characters", [])
        optimal_zones = character_analysis.get("optimal_bubble_zones", [])
        avoid_zones = character_analysis.get("avoid_zones", [])
        image_style = character_analysis.get("image_style", {})
        
        for dialogue in dialogues:
            char_index = dialogue.get("character_index", 0)
            
            if char_index >= len(characters):
                char_index = 0
            
            character = characters[char_index]
            
            # Calculer la taille de bulle basée sur le texte
            text = dialogue.get("text", "")
            bubble_size = self._calculate_realistic_bubble_size(text, dialogue.get("type", "speech"))
            
            # Trouver la meilleure zone pour la bulle
            bubble_position = self._find_optimal_bubble_position(
                character, bubble_size, optimal_zones, avoid_zones, bubbles
            )
            
            # Calculer la queue pointant vers la bouche du personnage
            tail_info = self._calculate_precise_tail(character, bubble_position, dialogue.get("type", "speech"))
            
            # Déterminer le style de bulle selon le type et l'analyse d'image
            bubble_style = self._determine_bubble_style(
                dialogue.get("type", "speech"), 
                image_style.get("bubble_style_recommendation", "round")
            )
            
            bubble_data = {
                "text": text,
                "type": dialogue.get("type", "speech"),
                "position": bubble_position,
                "size": bubble_size,
                "tail": tail_info,
                "style": bubble_style,
                "character_index": char_index,
                "priority": dialogue.get("priority", "medium")
            }
            
            bubbles.append(bubble_data)
        
        # Réorganiser les bulles pour éviter les chevauchements
        bubbles = self._resolve_bubble_overlaps(bubbles)
        
        print(f"🎯 Placement optimisé: {len(bubbles)} bulles positionnées intelligemment")
        return bubbles
    
    def _calculate_realistic_bubble_size(self, text: str, bubble_type: str) -> Dict[str, float]:
        """Calcule une taille de bulle réaliste basée sur le contenu"""
        # Compter les caractères et mots
        char_count = len(text)
        word_count = len(text.split())
        
        # Taille de base selon le type
        base_multipliers = {
            "speech": 1.0,
            "thought": 1.2,  # Les bulles de pensée sont souvent plus grandes
            "shout": 0.9,    # Les cris sont souvent compacts
            "whisper": 0.8   # Les chuchotements sont plus petits
        }
        
        multiplier = base_multipliers.get(bubble_type, 1.0)
        
        # Calcul intelligent de la taille
        base_width = max(0.15, min(0.4, char_count * 0.008 + 0.1)) * multiplier
        base_height = max(0.08, min(0.25, word_count * 0.02 + 0.06)) * multiplier
        
        return {
            "width": base_width,
            "height": base_height
        }
    
    def _find_optimal_bubble_position(self, character: Dict, bubble_size: Dict, 
                                    optimal_zones: List[Dict], avoid_zones: List[Dict],
                                    existing_bubbles: List[Dict]) -> Dict[str, float]:
        """Trouve la position optimale pour une bulle en évitant les obstacles"""
        
        char_pos = character.get("position", {"x": 0.5, "y": 0.6})
        mouth_pos = character.get("mouth_position", char_pos)
        
        # Positions préférées par ordre de priorité
        preferred_positions = [
            # Au-dessus du personnage
            {
                "x": mouth_pos["x"] - bubble_size["width"] / 2,
                "y": mouth_pos["y"] - bubble_size["height"] - 0.1,
                "priority": 10
            },
            # À côté du personnage (selon sa direction)
            {
                "x": char_pos["x"] + (0.15 if character.get("face_direction") == "left" else -bubble_size["width"] - 0.15),
                "y": mouth_pos["y"] - bubble_size["height"] / 2,
                "priority": 8
            },
            # Au-dessus à droite
            {
                "x": mouth_pos["x"] + 0.05,
                "y": mouth_pos["y"] - bubble_size["height"] - 0.08,
                "priority": 7
            },
            # Au-dessus à gauche
            {
                "x": mouth_pos["x"] - bubble_size["width"] - 0.05,
                "y": mouth_pos["y"] - bubble_size["height"] - 0.08,
                "priority": 7
            }
        ]
        
        # Évaluer chaque position
        best_position = None
        best_score = -1
        
        for pos in preferred_positions:
            score = pos["priority"]
            
            # Vérifier si dans les limites de l'image
            if (pos["x"] < 0.05 or pos["x"] + bubble_size["width"] > 0.95 or
                pos["y"] < 0.05 or pos["y"] + bubble_size["height"] > 0.95):
                score -= 5
            
            # Vérifier si dans une zone optimale
            in_optimal_zone = False
            for zone in optimal_zones:
                if (pos["x"] >= zone["x"] and pos["x"] + bubble_size["width"] <= zone["x"] + zone["width"] and
                    pos["y"] >= zone["y"] and pos["y"] + bubble_size["height"] <= zone["y"] + zone["height"]):
                    if zone.get("quality") == "excellent":
                        score += 5
                    elif zone.get("quality") == "good":
                        score += 3
                    in_optimal_zone = True
                    break
            
            # Pénalité si dans une zone à éviter
            for zone in avoid_zones:
                if (pos["x"] < zone["x"] + zone["width"] and pos["x"] + bubble_size["width"] > zone["x"] and
                    pos["y"] < zone["y"] + zone["height"] and pos["y"] + bubble_size["height"] > zone["y"]):
                    score -= 8
            
            # Vérifier les chevauchements avec les bulles existantes
            for existing in existing_bubbles:
                existing_pos = existing.get("position", {})
                existing_size = existing.get("size", {})
                if (pos["x"] < existing_pos.get("x", 0) + existing_size.get("width", 0) and
                    pos["x"] + bubble_size["width"] > existing_pos.get("x", 0) and
                    pos["y"] < existing_pos.get("y", 0) + existing_size.get("height", 0) and
                    pos["y"] + bubble_size["height"] > existing_pos.get("y", 0)):
                    score -= 10
            
            if score > best_score:
                best_score = score
                best_position = pos
        
        # Ajuster la position si nécessaire pour rester dans l'image
        if best_position:
            best_position["x"] = max(0.05, min(0.95 - bubble_size["width"], best_position["x"]))
            best_position["y"] = max(0.05, min(0.95 - bubble_size["height"], best_position["y"]))
        else:
            # Position de fallback
            best_position = {
                "x": max(0.05, min(0.95 - bubble_size["width"], char_pos["x"] - bubble_size["width"] / 2)),
                "y": max(0.05, char_pos["y"] - bubble_size["height"] - 0.1)
            }
        
        return best_position
    
    def _calculate_precise_tail(self, character: Dict, bubble_position: Dict, bubble_type: str) -> Dict[str, Any]:
        """Calcule une queue précise pointant vers la bouche du personnage"""
        
        mouth_pos = character.get("mouth_position", character.get("position", {"x": 0.5, "y": 0.6}))
        
        bubble_center_x = bubble_position["x"] + bubble_position.get("width", 0.2) / 2
        bubble_center_y = bubble_position["y"] + bubble_position.get("height", 0.1) / 2
        
        # Point de départ sur le bord de la bulle le plus proche de la bouche
        dx = mouth_pos["x"] - bubble_center_x
        dy = mouth_pos["y"] - bubble_center_y
        
        # Normaliser et trouver le point d'intersection avec le bord de la bulle
        distance = math.sqrt(dx*dx + dy*dy)
        if distance == 0:
            distance = 0.01
        
        # Point sur le bord de la bulle
        edge_ratio = 0.8  # 80% du rayon pour un aspect naturel
        tail_start_x = bubble_center_x + (dx / distance) * (bubble_position.get("width", 0.2) / 2) * edge_ratio
        tail_start_y = bubble_center_y + (dy / distance) * (bubble_position.get("height", 0.1) / 2) * edge_ratio
        
        # Style de queue selon le type de bulle
        if bubble_type == "thought":
            # Petites bulles pour les pensées
            return {
                "type": "thought_bubbles",
                "bubbles": [
                    {"x": tail_start_x, "y": tail_start_y + 0.02, "radius": 0.008},
                    {"x": mouth_pos["x"] - 0.01, "y": mouth_pos["y"] - 0.01, "radius": 0.006},
                    {"x": mouth_pos["x"], "y": mouth_pos["y"], "radius": 0.004}
                ]
            }
        else:
            # Queue classique pour parole, cri, chuchotement
            return {
                "type": "classic_tail",
                "start": {"x": tail_start_x, "y": tail_start_y},
                "end": {"x": mouth_pos["x"], "y": mouth_pos["y"]},
                "style": bubble_type  # Pour adapter l'épaisseur/style
            }
    
    def _determine_bubble_style(self, bubble_type: str, recommended_style: str) -> Dict[str, Any]:
        """Détermine le style visuel de la bulle"""
        
        base_styles = {
            "speech": {
                "border_style": "solid",
                "border_width": 2,
                "fill_color": (255, 255, 255, 240),
                "border_color": (0, 0, 0, 255),
                "shape": "rounded_rectangle"
            },
            "thought": {
                "border_style": "dashed",
                "border_width": 2,
                "fill_color": (248, 248, 255, 230),
                "border_color": (100, 100, 100, 255),
                "shape": "cloud"
            },
            "shout": {
                "border_style": "bold",
                "border_width": 3,
                "fill_color": (255, 255, 240, 250),
                "border_color": (0, 0, 0, 255),
                "shape": "spiky"
            },
            "whisper": {
                "border_style": "dotted",
                "border_width": 1,
                "fill_color": (250, 250, 250, 200),
                "border_color": (128, 128, 128, 200),
                "shape": "small_round"
            }
        }
        
        style = base_styles.get(bubble_type, base_styles["speech"]).copy()
        
        # Adapter selon la recommandation de style d'image
        if recommended_style == "spiky" and bubble_type == "speech":
            style["shape"] = "spiky"
        elif recommended_style == "cloud":
            style["shape"] = "cloud"
        
        return style
    
    def _resolve_bubble_overlaps(self, bubbles: List[Dict]) -> List[Dict]:
        """Résout les chevauchements entre bulles en les déplaçant légèrement"""
        
        for i, bubble1 in enumerate(bubbles):
            for j, bubble2 in enumerate(bubbles[i+1:], i+1):
                pos1 = bubble1.get("position", {})
                size1 = bubble1.get("size", {})
                pos2 = bubble2.get("position", {})
                size2 = bubble2.get("size", {})
                
                # Vérifier le chevauchement
                if (pos1.get("x", 0) < pos2.get("x", 0) + size2.get("width", 0) and
                    pos1.get("x", 0) + size1.get("width", 0) > pos2.get("x", 0) and
                    pos1.get("y", 0) < pos2.get("y", 0) + size2.get("height", 0) and
                    pos1.get("y", 0) + size1.get("height", 0) > pos2.get("y", 0)):
                    
                    # Déplacer la bulle de priorité plus faible
                    priority1 = {"high": 3, "medium": 2, "low": 1}.get(bubble1.get("priority", "medium"), 2)
                    priority2 = {"high": 3, "medium": 2, "low": 1}.get(bubble2.get("priority", "medium"), 2)
                    
                    if priority1 >= priority2:
                        # Déplacer bubble2
                        bubble2["position"]["y"] = pos1.get("y", 0) + size1.get("height", 0) + 0.02
                    else:
                        # Déplacer bubble1
                        bubble1["position"]["y"] = pos2.get("y", 0) + size2.get("height", 0) + 0.02
        
        return bubbles
        detected_chars = character_positions.get("characters", [])
        free_zones = character_positions.get("free_zones", [])
        
        for dialogue in dialogues:
            char_idx = dialogue.get("character_index", 0)
            
            if char_idx < len(detected_chars):
                char_pos = detected_chars[char_idx]
                
                # Calculer position optimale de la bulle
                bubble_pos = self._calculate_optimal_bubble_position(
                    char_pos, dialogue["text"], dialogue["type"], free_zones
                )
                
                # Calculer la queue pointant vers le personnage
                tail_pos = self._calculate_tail_position(char_pos, bubble_pos)
                
                bubbles.append({
                    "dialogue": dialogue,
                    "character_position": char_pos,
                    "bubble_position": bubble_pos,
                    "tail_position": tail_pos
                })
        
        return bubbles
    
    def _calculate_optimal_bubble_position(self, 
                                         char_pos: Dict,
                                         text: str,
                                         bubble_type: str,
                                         free_zones: List[Dict]) -> Dict[str, float]:
        """
        Calcule la position optimale de la bulle
        """
        # Taille basée sur le texte
        text_length = len(text)
        bubble_width = min(0.35, 0.15 + text_length * 0.008)
        bubble_height = 0.08 + (text_length // 25) * 0.02
        
        char_x = char_pos["position"]["x"]
        char_y = char_pos["position"]["y"]
        
        # Essayer de placer la bulle au-dessus du personnage
        bubble_x = char_x - bubble_width / 2
        bubble_y = char_y - bubble_height - 0.15
        
        # Ajuster si la bulle sort de l'image
        bubble_x = max(0.05, min(0.95 - bubble_width, bubble_x))
        bubble_y = max(0.05, bubble_y)
        
        # Si la bulle est trop basse, essayer à côté
        if bubble_y > 0.7:
            if char_x < 0.5:
                # Personnage à gauche, bulle à droite
                bubble_x = min(0.95 - bubble_width, char_x + 0.1)
            else:
                # Personnage à droite, bulle à gauche
                bubble_x = max(0.05, char_x - bubble_width - 0.1)
            bubble_y = char_y - bubble_height / 2
        
        return {
            "x": bubble_x,
            "y": bubble_y,
            "width": bubble_width,
            "height": bubble_height
        }
    
    def _calculate_tail_position(self, 
                               char_pos: Dict,
                               bubble_pos: Dict) -> Dict[str, Any]:
        """
        Calcule la position de la queue pour pointer vers le personnage
        """
        char_x = char_pos["position"]["x"]
        char_y = char_pos["position"]["y"]
        
        bubble_center_x = bubble_pos["x"] + bubble_pos["width"] / 2
        bubble_center_y = bubble_pos["y"] + bubble_pos["height"] / 2
        
        # Point de départ sur le bord de la bulle le plus proche du personnage
        if char_y > bubble_center_y:
            # Personnage en bas, queue part du bas de la bulle
            tail_start_x = bubble_center_x
            tail_start_y = bubble_pos["y"] + bubble_pos["height"]
        else:
            # Personnage en haut, queue part du haut de la bulle
            tail_start_x = bubble_center_x
            tail_start_y = bubble_pos["y"]
        
        # Point d'arrivée vers le personnage (légèrement au-dessus)
        tail_end_x = char_x
        tail_end_y = char_y - 0.05
        
        return {
            "start": {"x": tail_start_x, "y": tail_start_y},
            "end": {"x": tail_end_x, "y": tail_end_y}
        }
    
    async def _apply_ai_bubbles(self, 
                              image_path: str,
                              bubbles: List[Dict],
                              comic_dir: Path,
                              page_number: int) -> Path:
        """
        Applique des bulles ULTRA-RÉALISTES sur l'image avec rendu professionnel
        """
        try:
            # Charger l'image
            image = Image.open(image_path).convert("RGBA")
            overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Charger des polices de qualité
            font_sizes = self._get_optimal_font_sizes(image.size)
            fonts = self._load_quality_fonts(font_sizes)
            
            img_width, img_height = image.size
            
            for bubble_data in bubbles:
                # Extraire les données de la bulle
                text = bubble_data.get("text", "")
                bubble_type = bubble_data.get("type", "speech")
                position = bubble_data.get("position", {})
                size = bubble_data.get("size", {})
                tail = bubble_data.get("tail", {})
                style = bubble_data.get("style", {})
                
                # Convertir les coordonnées relatives en pixels
                bubble_x = int(position.get("x", 0.1) * img_width)
                bubble_y = int(position.get("y", 0.1) * img_height)
                bubble_w = int(size.get("width", 0.2) * img_width)
                bubble_h = int(size.get("height", 0.1) * img_height)
                
                # 1. Dessiner la queue en premier (pour qu'elle soit sous la bulle)
                self._draw_realistic_tail(draw, tail, img_width, img_height, style)
                
                # 2. Dessiner la bulle selon son style
                self._draw_realistic_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h, style, bubble_type)
                
                # 3. Ajouter le texte avec rendu professionnel
                self._draw_professional_text(draw, text, bubble_x, bubble_y, bubble_w, bubble_h, fonts, bubble_type)
            
            # Fusionner avec l'image originale avec antialiasing
            final_image = Image.alpha_composite(image, overlay)
            final_image = final_image.convert("RGB")
            
            # Sauvegarder l'image finale
            final_path = comic_dir / f"page_{page_number}_final.png"
            final_image.save(final_path, 'PNG', quality=95, optimize=True)
            
            print(f"✅ Bulles ultra-réalistes appliquées: {final_path}")
            return final_path
            
        except Exception as e:
            print(f"❌ Erreur application bulles: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback : copier l'image originale
            final_path = comic_dir / f"page_{page_number}_final.png"
            image = Image.open(image_path)
            image.save(final_path, 'PNG')
            return final_path
    
    def _get_optimal_font_sizes(self, image_size: Tuple[int, int]) -> Dict[str, int]:
        """Calcule les tailles de police optimales selon la résolution"""
        width, height = image_size
        base_size = max(14, int(min(width, height) / 40))  # Adaptation dynamique
        
        return {
            "normal": base_size,
            "small": max(10, base_size - 2),
            "large": base_size + 2,
            "title": base_size + 4
        }
    
    def _load_quality_fonts(self, sizes: Dict[str, int]) -> Dict[str, Any]:
        """Charge des polices de qualité avec fallback"""
        fonts = {}
        
        # Polices à essayer par ordre de préférence
        font_paths = [
            "arial.ttf", "Arial.ttf", "calibri.ttf", "Calibri.ttf",
            "comic.ttf", "comics.ttf", "DejaVuSans.ttf"
        ]
        
        for size_name, size in sizes.items():
            fonts[size_name] = None
            
            # Essayer de charger une police système
            for font_path in font_paths:
                try:
                    fonts[size_name] = ImageFont.truetype(font_path, size)
                    break
                except (OSError, IOError):
                    continue
            
            # Fallback vers la police par défaut
            if fonts[size_name] is None:
                try:
                    fonts[size_name] = ImageFont.load_default()
                except:
                    fonts[size_name] = None
        
        return fonts
    
    def _draw_realistic_tail(self, draw: ImageDraw.Draw, tail: Dict, img_width: int, img_height: int, style: Dict):
        """Dessine une queue de bulle ultra-réaliste"""
        tail_type = tail.get("type", "classic_tail")
        
        if tail_type == "thought_bubbles":
            # Petites bulles pour les pensées
            bubbles = tail.get("bubbles", [])
            fill_color = style.get("fill_color", (255, 255, 255, 240))
            border_color = style.get("border_color", (0, 0, 0, 255))
            
            for bubble in bubbles:
                x = int(bubble.get("x", 0.5) * img_width)
                y = int(bubble.get("y", 0.5) * img_height)
                radius = int(bubble.get("radius", 0.01) * min(img_width, img_height))
                
                # Bulle circulaire avec bord
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           fill=fill_color, outline=border_color, width=1)
        
        elif tail_type == "classic_tail":
            # Queue classique pointant vers la bouche
            start = tail.get("start", {})
            end = tail.get("end", {})
            tail_style = tail.get("style", "speech")
            
            start_x = int(start.get("x", 0.5) * img_width)
            start_y = int(start.get("y", 0.5) * img_height)
            end_x = int(end.get("x", 0.5) * img_width)
            end_y = int(end.get("y", 0.5) * img_height)
            
            # Déterminer l'épaisseur selon le type
            width = {"whisper": 1, "speech": 2, "shout": 3}.get(tail_style, 2)
            color = style.get("border_color", (0, 0, 0, 255))
            
            # Créer une queue en forme de triangle
            self._draw_triangle_tail(draw, start_x, start_y, end_x, end_y, width, color, style)
    
    def _draw_triangle_tail(self, draw: ImageDraw.Draw, start_x: int, start_y: int, 
                          end_x: int, end_y: int, width: int, color: Tuple, style: Dict):
        """Dessine une queue triangulaire réaliste"""
        # Calculer la direction perpendiculaire pour l'épaisseur
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            # Vecteur perpendiculaire normalisé
            perp_x = -dy / length * width
            perp_y = dx / length * width
            
            # Points du triangle
            points = [
                (start_x + perp_x, start_y + perp_y),
                (start_x - perp_x, start_y - perp_y),
                (end_x, end_y)
            ]
            
            # Remplir d'abord avec la couleur de fond
            fill_color = style.get("fill_color", (255, 255, 255, 240))
            draw.polygon(points, fill=fill_color)
            
            # Puis dessiner le contour
            draw.polygon(points, outline=color, width=1)
    
    def _draw_realistic_bubble(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, 
                             style: Dict, bubble_type: str):
        """Dessine une bulle avec un style ultra-réaliste"""
        
        shape = style.get("shape", "rounded_rectangle")
        fill_color = style.get("fill_color", (255, 255, 255, 240))
        border_color = style.get("border_color", (0, 0, 0, 255))
        border_width = style.get("border_width", 2)
        
        if shape == "cloud":
            self._draw_cloud_bubble(draw, x, y, w, h, fill_color, border_color, border_width)
        elif shape == "spiky":
            self._draw_spiky_bubble(draw, x, y, w, h, fill_color, border_color, border_width)
        elif shape == "small_round":
            self._draw_small_round_bubble(draw, x, y, w, h, fill_color, border_color, border_width)
        else:
            self._draw_round_bubble(draw, x, y, w, h, fill_color, border_color, border_width)
    
    def _draw_cloud_bubble(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int,
                         fill_color: Tuple, border_color: Tuple, border_width: int):
        """Dessine une bulle en forme de nuage pour les pensées"""
        # Créer plusieurs cercles qui se chevauchent pour former un nuage
        circles = [
            (x + w*0.2, y + h*0.3, w*0.25),
            (x + w*0.5, y + h*0.2, w*0.3),
            (x + w*0.8, y + h*0.3, w*0.25),
            (x + w*0.15, y + h*0.7, w*0.3),
            (x + w*0.5, y + h*0.8, w*0.25),
            (x + w*0.85, y + h*0.7, w*0.3),
            (x + w*0.5, y + h*0.5, w*0.4)  # Centre
        ]
        
        # Dessiner chaque cercle
        for cx, cy, radius in circles:
            left = int(cx - radius)
            top = int(cy - radius)
            right = int(cx + radius)
            bottom = int(cy + radius)
            
            draw.ellipse([left, top, right, bottom], fill=fill_color, outline=border_color, width=border_width)
    
    def _draw_spiky_bubble(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int,
                         fill_color: Tuple, border_color: Tuple, border_width: int):
        """Dessine une bulle explosive pour les cris"""
        # Points de base du rectangle
        points = []
        num_spikes = 8
        
        # Créer des points avec des épines
        for i in range(num_spikes * 4):
            angle = i * 2 * math.pi / (num_spikes * 4)
            
            if i % 2 == 0:
                # Point normal
                radius_x = w * 0.4
                radius_y = h * 0.4
            else:
                # Point d'épine
                radius_x = w * 0.5
                radius_y = h * 0.5
            
            px = x + w/2 + radius_x * math.cos(angle)
            py = y + h/2 + radius_y * math.sin(angle)
            points.append((px, py))
        
        draw.polygon(points, fill=fill_color, outline=border_color, width=border_width)
    
    def _draw_small_round_bubble(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int,
                               fill_color: Tuple, border_color: Tuple, border_width: int):
        """Dessine une petite bulle ronde pour les chuchotements"""
        draw.ellipse([x, y, x + w, y + h], fill=fill_color, outline=border_color, width=border_width)
    
    def _draw_round_bubble(self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int,
                         fill_color: Tuple, border_color: Tuple, border_width: int):
        """Dessine une bulle ronde classique avec coins arrondis"""
        # Utiliser un rectangle avec coins arrondis
        radius = min(w, h) // 8
        
        # Dessiner le rectangle principal
        draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, 
                             fill=fill_color, outline=border_color, width=border_width)
    
    def _draw_professional_text(self, draw: ImageDraw.Draw, text: str, 
                              bubble_x: int, bubble_y: int, bubble_w: int, bubble_h: int,
                              fonts: Dict, bubble_type: str):
        """Dessine le texte avec un rendu professionnel"""
        
        if not text or not fonts.get("normal"):
            return
        
        # Choisir la police selon le type de bulle
        font = fonts.get("normal")
        if bubble_type == "shout":
            font = fonts.get("large", font)
        elif bubble_type == "whisper":
            font = fonts.get("small", font)
        
        # Calculer la position centree
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Position centrée dans la bulle avec marges
        margin_x = bubble_w * 0.1
        margin_y = bubble_h * 0.15
        
        text_x = bubble_x + (bubble_w - text_width) // 2
        text_y = bubble_y + (bubble_h - text_height) // 2
        
        # S'assurer que le texte reste dans la bulle
        text_x = max(bubble_x + margin_x, min(bubble_x + bubble_w - text_width - margin_x, text_x))
        text_y = max(bubble_y + margin_y, min(bubble_y + bubble_h - text_height - margin_y, text_y))
        
        # Couleur du texte selon le type
        text_color = (0, 0, 0, 255)  # Noir par défaut
        if bubble_type == "shout":
            text_color = (0, 0, 0, 255)  # Noir bold
        elif bubble_type == "whisper":
            text_color = (64, 64, 64, 200)  # Gris léger
        
        # Dessiner le texte
        draw.text((text_x, text_y), text, fill=text_color, font=font)
