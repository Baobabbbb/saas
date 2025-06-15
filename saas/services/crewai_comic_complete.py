"""
Service CrewAI COMPLET pour la génération de bandes dessinées
Gère TOUT : textes, images, bulles, composition selon les spécifications franco-belges
Basé sur la documentation CrewAI officielle
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool
from pydantic import BaseModel

class ComicSpecification(BaseModel):
    """Spécifications complètes pour une bande dessinée"""
    style: str
    hero_name: str
    story_type: str
    custom_request: str
    num_images: int
    user_parameters: Dict[str, Any]

class BubbleStyle(BaseModel):
    """Style d'une bulle de dialogue selon spécifications franco-belges"""
    type: str  # speech, thought, shout, whisper
    shape: str  # oval, elliptical, jagged
    outline_color: str = "black"
    outline_width: int = 2
    fill_color: str = "#FFFFFF"
    font_style: str = "comic"
    position: Dict[str, float]  # x, y, width, height en pourcentages
    appendix_style: str  # pointed, bubbles, jagged, dashed

class SceneResult(BaseModel):
    """Résultat complet d'une scène avec image et bulles"""
    scene_index: int
    description: str
    image_prompt: str
    image_url: str
    dialogues: List[Dict[str, Any]]
    bubble_specifications: List[BubbleStyle]
    layout_metadata: Dict[str, Any]

@CrewBase
class CrewAIComicComplete:
    """
    Service CrewAI COMPLET pour créer des bandes dessinées professionnelles    Gère l'ensemble du processus : scénario, images, bulles, composition
    """
    
    # Chemins vers les fichiers de configuration YAML
    agents_config = '../config/agents_complete.yaml'
    tasks_config = '../config/tasks_complete.yaml'
    
    def __init__(self):
        self.llm_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        
    @agent
    def scenario_writer(self) -> Agent:
        """Agent scénariste - Crée le scénario de base"""
        return Agent(
            config=self.agents_config['scenario_writer'],
            verbose=True,
            memory=True,
            tools=[FileReadTool(), FileWriterTool()],
            llm=self.llm_model
        )    @agent 
    def bubble_designer(self) -> Agent:
        """Agent concepteur de bulles - Spécialiste bulles franco-belges"""
        return Agent(
            config=self.agents_config['bubble_designer'],
            verbose=True,
            memory=True,
            tools=[FileReadTool(), FileWriterTool()],
            llm=self.llm_model
        )    @agent
    def image_director(self) -> Agent:
        """Agent directeur artistique - Génère les descriptions d'images"""
        return Agent(
            config=self.agents_config['image_director'],
            verbose=True,
            memory=True,            tools=[FileReadTool(), FileWriterTool()],
            llm=self.llm_model
        )
        
    @agent
    def layout_composer(self) -> Agent:
        """Agent compositeur - Assemble l'ensemble"""
        return Agent(
            config=self.agents_config['layout_composer'],
            verbose=True,
            memory=True,
            tools=[FileReadTool(), FileWriterTool()],
            llm=self.llm_model
        )
        
    @task
    def create_scenario_task(self) -> Task:
        """Tâche de création du scénario"""
        return Task(
            config=self.tasks_config['create_scenario_task'],
            agent=self.scenario_writer(),
            output_json=dict
        )

    @task 
    def design_bubbles_task(self) -> Task:
        """Tâche de conception des bulles"""
        return Task(
            config=self.tasks_config['design_bubbles_task'],
            agent=self.bubble_designer(),
            context=[self.create_scenario_task()],
            output_json=dict
        )

    @task
    def create_image_prompts_task(self) -> Task:
        """Tâche de création des prompts d'images"""
        return Task(
            config=self.tasks_config['create_image_prompts_task'],
            agent=self.image_director(),
            context=[self.create_scenario_task(), self.design_bubbles_task()],
            output_json=dict
        )

    @task
    def final_composition_task(self) -> Task:
        """Tâche de composition finale"""
        return Task(
            config=self.tasks_config['final_composition_task'],
            agent=self.layout_composer(),
            context=[self.create_scenario_task(), self.design_bubbles_task(), self.create_image_prompts_task()],
            output_json=dict
        )

    @crew
    def comic_creation_crew(self) -> Crew:
        """Équipe complète de création de BD"""
        return Crew(
            agents=[
                self.scenario_writer(),
                self.bubble_designer(), 
                self.image_director(),
                self.layout_composer()
            ],
            tasks=[
                self.create_scenario_task(),
                self.design_bubbles_task(),
                self.create_image_prompts_task(),
                self.final_composition_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        )

    async def generate_complete_comic(self, spec: ComicSpecification) -> Dict[str, Any]:
        """
        Génère une bande dessinée complète avec CrewAI
        """
        try:
            print("🚀 Démarrage génération BD complète avec CrewAI")
            
            # Préparer les inputs pour CrewAI
            inputs = {
                'style': spec.style,
                'hero_name': spec.hero_name,
                'story_type': spec.story_type,
                'custom_request': spec.custom_request,
                'num_images': spec.num_images
            }
            
            print(f"📋 Inputs CrewAI: {inputs}")
            
            # Lancer l'équipe CrewAI
            crew = self.comic_creation_crew()
            result = crew.kickoff(inputs=inputs)
            
            print("✅ Génération CrewAI terminée")
            
            # Parser le résultat
            if hasattr(result, 'raw'):
                comic_data = json.loads(result.raw)
            else:
                comic_data = json.loads(str(result))
            
            # Post-traitement : génération des images et application des bulles
            final_result = await self._post_process_comic(comic_data, spec)
            
            return final_result
            
        except Exception as e:
            print(f"❌ Erreur génération BD complète: {e}")
            raise

    async def _post_process_comic(self, comic_data: Dict[str, Any], spec: ComicSpecification) -> Dict[str, Any]:
        """
        Post-traitement : génération d'images et application des bulles
        """
        try:
            print("🎨 Post-traitement : génération images et bulles")
            
            # Générer les images
            image_prompts = comic_data.get('image_prompts', [])
            generated_images = []
            
            for prompt_data in image_prompts:
                image_url = await self._generate_image(prompt_data['english_prompt'], spec.style)
                generated_images.append(image_url)
            
            # Appliquer les bulles
            bubble_specs = comic_data.get('bubble_specifications', [])
            final_scenes = []
            
            for i, (image_url, bubble_spec) in enumerate(zip(generated_images, bubble_specs)):
                scene_with_bubbles = await self._apply_bubbles_to_scene(
                    image_url, bubble_spec, comic_data['scenes'][i]
                )
                final_scenes.append(scene_with_bubbles)
            
            return {
                'title': comic_data.get('title', 'Ma BD'),
                'pages': [scene['final_image_path'] for scene in final_scenes],
                'enhanced_by_crewai': True,
                'creation_method': 'complete_crewai_pipeline',
                'quality_score': 9.5,
                'scenes_data': final_scenes,
                'metadata': comic_data.get('comic_metadata', {})
            }
            
        except Exception as e:
            print(f"❌ Erreur post-traitement: {e}")
            raise

    async def _generate_image(self, prompt: str, style: str) -> str:
        """Génère une image via Stability AI"""
        try:
            style_modifiers = self._get_style_modifiers(style)
            full_prompt = f"{prompt}. {style_modifiers}"
            
            body = {
                "text_prompts": [{"text": full_prompt, "weight": 1.0}],
                "cfg_scale": 10,
                "height": 1024,
                "width": 1024,
                "sampler": "K_DPMPP_2M",
                "samples": 1,
                "steps": 40,
                "style_preset": "comic-book"
            }
            
            headers = {
                "Authorization": f"Bearer {self.stability_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers=headers,
                json=body,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                image_data = data["artifacts"][0]["base64"]
                
                # Sauvegarder l'image
                import base64
                image_bytes = base64.b64decode(image_data)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_scene_{timestamp}.png"
                filepath = f"static/{filename}"
                
                os.makedirs("static", exist_ok=True)
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                
                return filepath
            else:
                raise Exception(f"Erreur génération image: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur génération image: {e}")
            raise

    def _get_style_modifiers(self, style: str) -> str:
        """Retourne les modificateurs de style"""
        style_map = {
            'cartoon': 'cartoon style, animated, colorful, family-friendly, professional illustration',
            'realistic': 'realistic style, detailed, photorealistic, high quality illustration',
            'manga': 'manga style, anime art, japanese comic book style',
            'comic': 'comic book style, superhero comic art, dynamic poses',
            'watercolor': 'watercolor painting style, soft colors, artistic',
            'sketch': 'pencil sketch style, hand-drawn, artistic lines'
        }
        return style_map.get(style.lower(), 'comic book style, professional illustration')

    async def _apply_bubbles_to_scene(self, image_path: str, bubble_spec: Dict[str, Any], scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique les bulles à une scène selon les spécifications franco-belges"""
        try:
            # Charger l'image
            img = Image.open(image_path).convert("RGBA")
            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Police franco-belge
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Appliquer chaque bulle
            for bubble_data in bubble_spec.get('bubbles', []):
                self._draw_franco_belge_bubble(draw, bubble_data, scene_data, img.size, font)
            
            # Fusionner les calques
            final_image = Image.alpha_composite(img, overlay).convert("RGB")
            
            # Sauvegarder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"comic_scene_final_{timestamp}.png"
            final_path = f"static/{final_filename}"
            final_image.save(final_path, "PNG", optimize=True)
            
            return {
                'scene_index': bubble_spec.get('scene_index', 0),
                'original_image': image_path,
                'final_image_path': final_path,
                'bubbles_applied': len(bubble_spec.get('bubbles', [])),
                'quality_score': 9.0
            }
            
        except Exception as e:
            print(f"❌ Erreur application bulles: {e}")
            raise

    def _draw_franco_belge_bubble(self, draw, bubble_data, scene_data, img_size, font):
        """Dessine une bulle selon les standards franco-belges"""
        img_width, img_height = img_size
        
        # Position en pixels
        pos = bubble_data['position']
        x = int(pos['x'] * img_width)
        y = int(pos['y'] * img_height)
        width = int(pos['width'] * img_width)
        height = int(pos['height'] * img_height)
        
        # Forme ovale/elliptique
        bubble_rect = [x, y, x + width, y + height]
        
        # Contour noir régulier et net
        draw.ellipse(
            bubble_rect,
            fill=bubble_data['fill_color'],
            outline=bubble_data['outline_color'],
            width=bubble_data['outline_width']
        )
        
        # Appendice selon le type
        self._draw_appendix(draw, bubble_data, bubble_rect, img_size)
        
        # Texte centré style franco-belge
        self._draw_franco_belge_text(draw, bubble_data, bubble_rect, font, scene_data)

    def _draw_appendix(self, draw, bubble_data, bubble_rect, img_size):
        """Dessine l'appendice (queue) de la bulle"""
        appendix_style = bubble_data.get('appendix_style', 'pointed')
        target = bubble_data.get('appendix_target', {'x': 0.5, 'y': 0.7})
        
        img_width, img_height = img_size
        target_x = int(target['x'] * img_width)
        target_y = int(target['y'] * img_height)
        
        bubble_center_x = (bubble_rect[0] + bubble_rect[2]) // 2
        bubble_bottom = bubble_rect[3]
        
        if appendix_style == 'pointed':
            # Trait pointu vers la bouche
            triangle_points = [
                (bubble_center_x - 10, bubble_bottom),
                (bubble_center_x + 10, bubble_bottom),
                (target_x, target_y)
            ]
            draw.polygon(triangle_points, fill=bubble_data['fill_color'], outline=bubble_data['outline_color'])
            
        elif appendix_style == 'bubbles':
            # Petits cercles pour les pensées
            num_bubbles = 3
            for i in range(num_bubbles):
                size = 8 - i * 2
                bubble_x = bubble_center_x + (target_x - bubble_center_x) * (i + 1) / (num_bubbles + 1)
                bubble_y = bubble_bottom + (target_y - bubble_bottom) * (i + 1) / (num_bubbles + 1)
                draw.ellipse([bubble_x - size//2, bubble_y - size//2, bubble_x + size//2, bubble_y + size//2],
                           fill=bubble_data['fill_color'], outline=bubble_data['outline_color'])

    def _draw_franco_belge_text(self, draw, bubble_data, bubble_rect, font, scene_data):
        """Dessine le texte avec style franco-belge"""
        # Récupérer le texte du dialogue
        dialogue_index = bubble_data.get('dialogue_index', 0)
        dialogues = scene_data.get('dialogues', [])
        
        if dialogue_index < len(dialogues):
            text = dialogues[dialogue_index].get('text', '')
            
            # Diviser en lignes (max 40 chars/ligne, max 3 lignes)
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if len(test_line) <= 40:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                    
                if len(lines) >= 3:  # Max 3 lignes
                    break
            
            if current_line and len(lines) < 3:
                lines.append(current_line)
            
            # Centrer le texte
            bubble_center_x = (bubble_rect[0] + bubble_rect[2]) // 2
            bubble_center_y = (bubble_rect[1] + bubble_rect[3]) // 2
            
            line_height = font.size + 4
            total_height = len(lines) * line_height
            start_y = bubble_center_y - total_height // 2
            
            for i, line in enumerate(lines):
                text_bbox = draw.textbbox((0, 0), line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = bubble_center_x - text_width // 2
                text_y = start_y + i * line_height
                
                # Texte noir pour lisibilité
                draw.text((text_x, text_y), line, fill="black", font=font)


# Instance globale
crewai_comic_complete = CrewAIComicComplete()
