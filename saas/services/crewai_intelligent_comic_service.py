"""
Service hybride CrewAI + Stability AI pour génération intelligente de BD
Combine l'intelligence narrative de CrewAI avec l'ancien système de génération d'images
"""

import os
import json
import uuid
from typing import Dict, List, Any
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

from crewai import Agent, Task, Crew, LLM
# Import direct de l'API Stability AI pour plus de contrôle
import requests
import time


class CrewAIIntelligentComicService:
    """
    Service hybride orchestrant CrewAI pour l'intelligence narrative 
    et l'ancien système Stability AI pour la génération d'images réalistes
    """
    
    def __init__(self):
        """Initialise le service avec LLM GPT-4o-mini et configuration"""
        self.llm = LLM(model="gpt-4o-mini")
        self.base_seed = 12345
        self.output_dir = "static/comics"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configuration des agents CrewAI
        self._setup_agents()
        
    def _setup_agents(self):
        """Configure les 3 agents CrewAI spécialisés"""
        
        # Agent 1 : Scénariste BD Franco-Belge Expert
        self.scenario_agent = Agent(
            role="Scénariste BD Franco-Belge Expert",
            goal="Créer scénarios détaillés avec indications de composition visuelle",
            backstory="""Expert en BD style Tintin/Astérix qui comprend l'importance du placement des éléments.
            Tu maîtrises les codes narratifs franco-belges et sais structurer une histoire en cases avec 
            descriptions visuelles précises pour optimiser le placement des personnages et des bulles.""",
            llm=self.llm,
            verbose=True
        )
        
        # Agent 2 : Analyseur de Composition Visuelle BD
        self.composition_agent = Agent(
            role="Analyseur de Composition Visuelle BD",
            goal="Prédire la position des personnages dans les images générées par Stability AI",
            backstory="""Expert qui analyse les conventions visuelles et prédit où seront placés les personnages 
            selon le style et la description. Tu comprends comment Stability AI compose ses images et peux 
            anticiper la position des éléments visuels pour optimiser le placement des bulles.""",
            llm=self.llm,
            verbose=True
        )
        
        # Agent 3 : Compositeur Intelligent de Bulles BD
        self.bubble_agent = Agent(
            role="Compositeur Intelligent de Bulles BD",
            goal="Placer optimalement les bulles pour qu'elles pointent vers le bon personnage qui parle",
            backstory="""Expert en placement de bulles franco-belges qui comprend l'ordre de lecture et les 
            flèches directionnelles. Tu maîtrises les standards Tintin/Astérix : bulles ovales, contour noir,
            flèches pointues vers la bouche, respect de l'ordre de lecture occidental.""",
            llm=self.llm,
            verbose=True
        )

    def create_intelligent_comic(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Méthode principale orchestrant tout le processus de génération
        
        Args:
            spec: Spécifications de la BD (thème, nombre de pages, etc.)
            
        Returns:
            Dictionnaire avec les pages générées et métadonnées
        """
        try:
            print("🎭 Démarrage du service hybride CrewAI + Stability AI...")
            
            # Générer un ID unique pour cette BD
            comic_id = str(uuid.uuid4())[:8]
            
            # ÉTAPE 1: Génération du scénario avec CrewAI
            print("📝 Génération du scénario...")
            scenario_data = self._generate_scenario(spec)
            
            # ÉTAPE 2: Analyse de composition prédictive
            print("🎨 Analyse de composition prédictive...")
            composition_data = self._analyze_composition(scenario_data)
            
            # ÉTAPE 3: Composition intelligente des bulles
            print("💬 Composition intelligente des bulles...")
            bubble_specs = self._compose_bubbles(scenario_data, composition_data)
            
            # ÉTAPE 4: Génération des images avec Stability AI
            print("🖼️ Génération des images avec Stability AI...")
            generated_images = self._generate_images_with_stability_ai(scenario_data)
            
            # ÉTAPE 5: Application des bulles sur les images
            print("🎯 Application des bulles selon spécifications CrewAI...")
            final_pages = self._apply_intelligent_bubbles_composition(
                generated_images, bubble_specs, comic_id
            )
            
            result = {
                "id": comic_id,
                "method": "crewai_intelligent_hybrid",
                "real_stability_ai": True,
                "pages": final_pages,
                "scenario": scenario_data,
                "composition_analysis": composition_data,
                "bubble_specifications": bubble_specs,
                "total_pages": len(final_pages),
                "style": "franco-belge",
                "success": True
            }
            
            print(f"✅ BD générée avec succès ! ID: {comic_id}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": "crewai_intelligent_hybrid",
                "real_stability_ai": False
            }

    def _generate_scenario(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Génère le scénario avec positions estimées des personnages"""
        
        task = Task(
            description=f"""
            Créer un scénario détaillé pour une BD de {spec.get('pages', 4)} pages 
            sur le thème : {spec.get('theme', 'aventure')}.
            
            FORMAT DE SORTIE REQUIS (JSON strict):
            {{
                "pages": [
                    {{
                        "page_number": 1,
                        "scene_description": "Description visuelle détaillée de la scène",
                        "estimated_character_positions": [
                            {{
                                "character": "nom_personnage",
                                "x_percent": 30,
                                "y_percent": 40,
                                "role": "speaker|listener"
                            }}
                        ],
                        "dialogues": [
                            {{
                                "speaker": "nom_personnage",
                                "text": "texte du dialogue",
                                "type": "speech|thought|narration",
                                "emotion": "neutre|joyeux|colère|surprise",
                                "speaking_order": 1
                            }}
                        ]
                    }}
                ]
            }}
            
            CONSIGNES:
            - Style franco-belge (Tintin/Astérix)
            - Descriptions visuelles précises
            - Positions estimées en pourcentages (0-100)
            - Dialogues courts et percutants
            - Respect de l'ordre de lecture
            """,
            agent=self.scenario_agent,
            expected_output="JSON valide avec scénario complet structuré"
        )
        
        crew = Crew(
            agents=[self.scenario_agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        try:
            # Nettoyer et parser le JSON
            json_str = str(result).strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:-3]
            elif json_str.startswith('```'):
                json_str = json_str[3:-3]
                
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Erreur parsing JSON scénario: {e}")
            # Fallback avec structure minimale
            return {
                "pages": [
                    {
                        "page_number": 1,
                        "scene_description": f"Scène d'aventure sur le thème {spec.get('theme', 'aventure')}",
                        "estimated_character_positions": [
                            {"character": "héros", "x_percent": 30, "y_percent": 40, "role": "speaker"}
                        ],
                        "dialogues": [
                            {"speaker": "héros", "text": "Quelle aventure nous attend ?", "type": "speech", "emotion": "neutre", "speaking_order": 1}
                        ]
                    }
                ]
            }

    def _analyze_composition(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse prédictive de composition pour chaque page"""
        
        task = Task(
            description=f"""
            Analyser la composition visuelle prédite pour chaque page du scénario.
            Prévoir où Stability AI placera les personnages selon les descriptions.
            
            SCÉNARIO À ANALYSER:
            {json.dumps(scenario_data, indent=2)}
            
            FORMAT DE SORTIE REQUIS (JSON strict):
            {{
                "pages": [
                    {{
                        "page_number": 1,
                        "predicted_character_layout": [
                            {{
                                "character": "nom_personnage",
                                "head_position": {{"x_percent": 30, "y_percent": 25}},
                                "mouth_position": {{"x_percent": 32, "y_percent": 28}},
                                "body_bounds": {{"x1": 20, "y1": 25, "x2": 40, "y2": 70}},
                                "available_bubble_space": [
                                    {{"x1": 45, "y1": 10, "x2": 80, "y2": 35}}
                                ],
                                "optimal_bubble_zones": [
                                    {{"x_percent": 60, "y_percent": 20, "priority": 1}}
                                ]
                            }}
                        ]
                    }}
                ]
            }}
            
            CONSIGNES:
            - Prédire positions réalistes selon conventions BD
            - Identifier espaces libres pour bulles  
            - Éviter chevauchements personnages/bulles
            - Respecter ordre de lecture occidental
            """,
            agent=self.composition_agent,
            expected_output="JSON valide avec analyse de composition prédictive"
        )
        
        crew = Crew(
            agents=[self.composition_agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        try:
            json_str = str(result).strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:-3]
            elif json_str.startswith('```'):
                json_str = json_str[3:-3]
                
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Erreur parsing JSON composition: {e}")
            # Fallback structure
            return {
                "pages": [
                    {
                        "page_number": i+1,
                        "predicted_character_layout": [
                            {
                                "character": "héros",
                                "head_position": {"x_percent": 30, "y_percent": 25},
                                "mouth_position": {"x_percent": 32, "y_percent": 28},
                                "body_bounds": {"x1": 20, "y1": 25, "x2": 40, "y2": 70},
                                "available_bubble_space": [{"x1": 45, "y1": 10, "x2": 80, "y2": 35}],
                                "optimal_bubble_zones": [{"x_percent": 60, "y_percent": 20, "priority": 1}]
                            }
                        ]
                    }
                    for i in range(len(scenario_data.get('pages', [])))
                ]
            }

    def _compose_bubbles(self, scenario_data: Dict[str, Any], composition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Composition intelligente des bulles selon standards franco-belges"""
        
        task = Task(
            description=f"""
            Créer les spécifications détaillées pour le placement optimal des bulles
            selon les standards franco-belges (Tintin/Astérix).
            
            SCÉNARIO:
            {json.dumps(scenario_data, indent=2)}
            
            COMPOSITION PRÉDITE:
            {json.dumps(composition_data, indent=2)}
            
            FORMAT DE SORTIE REQUIS (JSON strict):
            {{
                "pages": [
                    {{
                        "page_number": 1,
                        "bubble_specs": [
                            {{
                                "dialogue_id": 1,
                                "speaker": "nom_personnage",
                                "position": {{"x_percent": 60, "y_percent": 20}},
                                "shape": "oval",
                                "style": "speech",
                                "width_percent": 25,
                                "height_percent": 15,
                                "arrow_specs": {{
                                    "start_point": {{"x_percent": 50, "y_percent": 30}},
                                    "end_point": {{"x_percent": 32, "y_percent": 28}},
                                    "type": "pointy"
                                }},
                                "text_layout": {{
                                    "lines": ["Texte", "multiligne"],
                                    "alignment": "center",
                                    "font_size": 16
                                }},
                                "reading_order": 1
                            }}
                        ]
                    }}
                ]
            }}
            
            STANDARDS FRANCO-BELGES OBLIGATOIRES:
            - Bulles ovales uniquement
            - Contour noir 3px
            - Fond blanc uni
            - Flèches pointues vers bouche du personnage
            - Ordre de lecture gauche→droite, haut→bas
            - Aucun chevauchement entre bulles et personnages
            - Texte centré dans la bulle
            """,
            agent=self.bubble_agent,
            expected_output="JSON valide avec spécifications complètes de bulles"
        )
        
        crew = Crew(
            agents=[self.bubble_agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        try:
            json_str = str(result).strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:-3]
            elif json_str.startswith('```'):
                json_str = json_str[3:-3]
                
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Erreur parsing JSON bulles: {e}")
            # Fallback structure
            return {
                "pages": [
                    {
                        "page_number": i+1,
                        "bubble_specs": [
                            {
                                "dialogue_id": 1,
                                "speaker": "héros",
                                "position": {"x_percent": 60, "y_percent": 20},
                                "shape": "oval",
                                "style": "speech",
                                "width_percent": 25,
                                "height_percent": 15,
                                "arrow_specs": {
                                    "start_point": {"x_percent": 50, "y_percent": 30},
                                    "end_point": {"x_percent": 32, "y_percent": 28},
                                    "type": "pointy"
                                },
                                "text_layout": {
                                    "lines": ["Dialogue par défaut"],
                                    "alignment": "center",
                                    "font_size": 16
                                },
                                "reading_order": 1
                            }
                        ]
                    }
                    for i in range(len(scenario_data.get('pages', [])))                ]
            }

    def _generate_images_with_stability_ai(self, scenario_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère les images avec l'API Stability AI directe"""
        
        generated_images = []
        
        # Configuration Stability AI
        STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
        ENGINE_ID = "stable-diffusion-xl-1024-v1-0"
        STABILITY_ENDPOINT = f"https://api.stability.ai/v1/generation/{ENGINE_ID}/text-to-image"
        
        if not STABILITY_API_KEY:
            raise ValueError("STABILITY_API_KEY non configurée dans .env")
        
        for i, page in enumerate(scenario_data.get('pages', [])):
            try:
                # Construire le prompt pour Stability AI
                prompt = f"""
                Comic book panel in Franco-Belgian style (Tintin/Asterix): {page['scene_description']}
                High quality, detailed illustration, professional comic art style,
                clear ligne claire technique, vibrant colors, detailed backgrounds,
                leave space for speech bubbles, comic book composition
                """
                
                # Utiliser seed cohérente
                seed = self.base_seed + i
                
                print(f"Génération image page {i+1} avec seed {seed}...")
                
                # Appel API Stability AI
                headers = {
                    "Authorization": f"Bearer {STABILITY_API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }

                body = {
                    "text_prompts": [
                        {"text": prompt, "weight": 1.0}
                    ],
                    "cfg_scale": 7.5,
                    "height": 1024,
                    "width": 1024,
                    "sampler": "K_DPMPP_2M",
                    "samples": 1,
                    "steps": 50,
                    "seed": seed,
                    "style_preset": "comic-book"
                }

                response = requests.post(
                    STABILITY_ENDPOINT,
                    headers=headers,
                    json=body,
                    timeout=90
                )
                
                response.raise_for_status()
                result = response.json()
                
                if "artifacts" in result and result["artifacts"]:
                    img_b64 = result["artifacts"][0]["base64"]
                    
                    generated_images.append({
                        "page_number": i + 1,
                        "image_data": img_b64,
                        "prompt": prompt,
                        "seed": seed
                    })
                    
                    print(f"✅ Image générée pour page {i+1}")
                else:
                    print(f"⚠️ Aucune image générée pour page {i+1}")
                    
            except Exception as e:
                print(f"❌ Erreur génération image page {i+1}: {str(e)}")
                continue
                
        return generated_images

    def _apply_intelligent_bubbles_composition(
        self, 
        generated_images: List[Dict[str, Any]], 
        bubble_specs: Dict[str, Any],
        comic_id: str
    ) -> List[Dict[str, Any]]:
        """Applique les bulles selon spécifications CrewAI"""
        
        final_pages = []
        
        for img_data in generated_images:
            try:
                page_num = img_data['page_number']
                
                # Trouver les specs de bulles pour cette page
                page_bubbles = None
                for page_spec in bubble_specs.get('pages', []):
                    if page_spec['page_number'] == page_num:
                        page_bubbles = page_spec['bubble_specs']
                        break
                
                if not page_bubbles:
                    print(f"⚠️ Aucune spec de bulle pour page {page_num}")
                    continue
                
                # Décoder l'image base64
                if isinstance(img_data['image_data'], str):
                    image_bytes = base64.b64decode(img_data['image_data'])
                else:
                    image_bytes = img_data['image_data']
                    
                image = Image.open(BytesIO(image_bytes))
                
                # Appliquer les bulles
                final_image = self._draw_bubbles_on_image(image, page_bubbles)
                
                # Sauvegarder l'image finale
                filename = f"comic_{comic_id}_page_{page_num}.png"
                filepath = os.path.join(self.output_dir, filename)
                final_image.save(filepath, "PNG")
                
                # Encoder en base64 pour le retour
                buffer = BytesIO()
                final_image.tobytes()
                final_image.save(buffer, format="PNG")
                final_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                final_pages.append({
                    "page_number": page_num,
                    "image_url": f"/static/comics/{filename}",
                    "image_data": final_base64,
                    "bubbles_applied": len(page_bubbles),
                    "original_seed": img_data.get('seed')
                })
                
                print(f"✅ Page {page_num} finalisée avec {len(page_bubbles)} bulles")
                
            except Exception as e:
                print(f"❌ Erreur application bulles page {img_data.get('page_number', '?')}: {str(e)}")
                continue
                
        return final_pages

    def _draw_bubbles_on_image(self, image: Image.Image, bubble_specs: List[Dict[str, Any]]) -> Image.Image:
        """Dessine les bulles sur l'image selon standards franco-belges"""
        
        # Créer une copie pour éviter de modifier l'original
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        width, height = img_copy.size
        
        # Trier par ordre de lecture
        sorted_bubbles = sorted(bubble_specs, key=lambda x: x.get('reading_order', 999))
        
        for bubble in sorted_bubbles:
            try:
                # Calculer position et taille
                x_center = int(bubble['position']['x_percent'] * width / 100)
                y_center = int(bubble['position']['y_percent'] * height / 100)
                bubble_width = int(bubble['width_percent'] * width / 100)
                bubble_height = int(bubble['height_percent'] * height / 100)
                
                # Coordonnées de la bulle ovale
                x1 = x_center - bubble_width // 2
                y1 = y_center - bubble_height // 2
                x2 = x_center + bubble_width // 2
                y2 = y_center + bubble_height // 2
                
                # Dessiner bulle ovale (fond blanc, contour noir 3px)
                draw.ellipse([x1, y1, x2, y2], fill="white", outline="black", width=3)
                
                # Dessiner la flèche pointue vers la bouche
                arrow_start_x = int(bubble['arrow_specs']['start_point']['x_percent'] * width / 100)
                arrow_start_y = int(bubble['arrow_specs']['start_point']['y_percent'] * height / 100)
                arrow_end_x = int(bubble['arrow_specs']['end_point']['x_percent'] * width / 100)
                arrow_end_y = int(bubble['arrow_specs']['end_point']['y_percent'] * height / 100)
                
                # Flèche triangulaire pointue
                self._draw_speech_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y)
                
                # Ajouter le texte centré
                self._draw_bubble_text(draw, bubble['text_layout'], x_center, y_center, bubble_width, bubble_height)
                
            except Exception as e:
                print(f"⚠️ Erreur dessin bulle: {str(e)}")
                continue
                
        return img_copy

    def _draw_speech_arrow(self, draw, start_x, start_y, end_x, end_y):
        """Dessine une flèche pointue style BD franco-belge"""
        
        # Calculer l'angle et la longueur
        import math
        
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
            
        # Normaliser
        dx /= length
        dy /= length
        
        # Taille de la pointe
        arrow_size = 8
        
        # Points du triangle de la flèche
        point1_x = end_x
        point1_y = end_y
        point2_x = end_x - arrow_size * dx + arrow_size * dy / 2
        point2_y = end_y - arrow_size * dy - arrow_size * dx / 2
        point3_x = end_x - arrow_size * dx - arrow_size * dy / 2
        point3_y = end_y - arrow_size * dy + arrow_size * dx / 2
        
        # Dessiner triangle plein
        draw.polygon([
            (point1_x, point1_y),
            (point2_x, point2_y),
            (point3_x, point3_y)
        ], fill="white", outline="black", width=2)

    def _draw_bubble_text(self, draw, text_layout, center_x, center_y, bubble_width, bubble_height):
        """Dessine le texte centré dans la bulle"""
        
        try:
            # Utiliser une police par défaut
            font_size = text_layout.get('font_size', 16)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            lines = text_layout.get('lines', [''])
            
            # Calculer la hauteur totale du texte
            line_height = font_size + 2
            total_text_height = len(lines) * line_height
            
            # Position de départ (centré verticalement)
            start_y = center_y - total_text_height // 2
            
            # Dessiner chaque ligne
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                    
                # Mesurer la largeur du texte
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                
                # Centrer horizontalement
                text_x = center_x - text_width // 2
                text_y = start_y + i * line_height
                
                # Vérifier que le texte reste dans la bulle
                if text_width < bubble_width - 10:  # Marge de 5px de chaque côté
                    draw.text((text_x, text_y), line, fill="black", font=font)
                    
        except Exception as e:
            print(f"⚠️ Erreur dessin texte: {str(e)}")
            # Fallback : texte simple
            draw.text((center_x - 30, center_y - 10), "...", fill="black")
