"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Version propre et fonctionnelle avec simulation intelligente
"""

import os
import time
from typing import Dict, Any
from datetime import datetime
import asyncio
import httpx

class RunwayGen4Service:
    """Service de génération vidéo Runway Gen-4 Turbo"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = os.getenv("RUNWAY_BASE_URL", "https://api.dev.runwayml.com")
        
        # Vérifier si on a une clé API valide
        if not self.api_key or self.api_key == "your-runway-api-key-here":
            print("❌ RUNWAY_API_KEY manquante - ERREUR FATALE")
            raise Exception("Clé API Runway manquante - impossible de continuer")
        else:
            print(f"🔑 Clé API Runway détectée: {self.api_key[:20]}...")
            print("🚀 MODE PRODUCTION RÉEL UNIQUEMENT - Aucune simulation autorisée")
            # SUPPRESSION TOTALE DU MODE SIMULATION
        
        # Styles supportés par Runway Gen-4 Turbo
        self.supported_styles = {
            "cartoon": "colorful cartoon animation style, vibrant colors, smooth animation",
            "fairy_tale": "magical fairy tale illustration style, dreamy and enchanting",
            "anime": "anime animation style, Japanese cartoon aesthetic",
            "realistic": "photorealistic style, natural lighting and movement",
            "paper_craft": "paper cut-out animation style, layered paper craft aesthetic",
            "watercolor": "watercolor painting style, soft brushstrokes, artistic flow"
        }
        
        print(f"🎬 Service Runway Gen-4 Turbo initialisé")
        print(f"📡 Base URL: {self.base_url}")
        print(f"🎨 Styles supportés: {list(self.supported_styles.keys())}")
        print(f"🚀 Mode: PRODUCTION RÉELLE UNIQUEMENT")

    def _create_optimized_prompt(self, style: str, theme: str, custom_prompt: str = "", orientation: str = "landscape") -> str:
        """Crée un prompt optimisé pour Runway Gen-4 Turbo et les enfants"""
        
        # Mapping des thèmes pour enfants
        theme_prompts = {
            "adventure": "exciting adventure with brave characters exploring magical places",
            "magic": "magical world with sparkles, fairy dust, and enchanted creatures", 
            "animals": "cute friendly animals playing together in a colorful environment",
            "friendship": "heartwarming friendship story with characters helping each other",
            "space": "space adventure with colorful planets, friendly aliens, and starships",
            "underwater": "underwater adventure with colorful fish, coral reefs, and sea creatures",
            "forest": "enchanted forest with magical creatures, talking trees, and fairy lights",
            "superhero": "child-friendly superhero saving the day with positive powers"
        }
        
        # Récupérer les prompts de style et thème
        style_prompt = self.supported_styles.get(style, self.supported_styles["cartoon"])
        theme_prompt = theme_prompts.get(theme, theme_prompts["adventure"])
        
        # Construire le prompt final
        prompt_parts = [style_prompt, theme_prompt]
        
        if custom_prompt and custom_prompt.strip():
            prompt_parts.append(custom_prompt.strip())
        
        # Ajouter des directives spécifiques pour les enfants et Runway
        final_prompt = ", ".join(prompt_parts)
        final_prompt += ", suitable for children, bright colors, positive atmosphere, high quality animation, smooth motion"
        
        return final_prompt
    
    def _generate_attractive_title(self, style: str, theme: str) -> str:
        """Génère un titre attractif pour l'animation"""
        
        title_templates = {
            "adventure": ["Les Explorateurs de", "L'Aventure de", "Le Voyage vers", "La Quête de"],
            "magic": ["Le Monde Magique de", "Les Sortilèges de", "La Magie de", "L'Enchantement de"],
            "animals": ["Les Amis de la", "L'Histoire de", "Les Aventures de", "Le Royaume de"],
            "friendship": ["Les Amis de", "L'Amitié de", "L'Histoire de", "Les Copains de"],
            "space": ["Les Explorateurs de l'", "L'Aventure Spatiale de", "Le Voyage vers", "Les Héros de l'"],
            "underwater": ["Les Secrets de l'", "L'Aventure Sous-Marine de", "Les Trésors de l'", "Le Monde de l'"],
            "forest": ["La Forêt Enchantée de", "Les Mystères de la", "L'Aventure dans la", "Les Amis de la"],
            "superhero": ["Les Super-Héros de", "L'Héro de", "Les Défenseurs de", "Les Gardiens de"]
        }
        
        locations = {
            "adventure": ["l'Inconnu", "la Montagne d'Or", "l'Île Mystérieuse", "la Cité Perdue"],
            "magic": ["Féerie", "l'Arc-en-Ciel", "la Lune", "l'Étoile Dorée"],
            "animals": ["Forêt", "Jungle", "Savane", "Océan"],
            "friendship": ["la Joie", "l'Amitié", "la Bonne Humeur", "l'Entraide"],
            "space": ["Espace", "Galaxie", "Étoiles", "Cosmos"],
            "underwater": ["Océan", "Mer Bleue", "Récif Coloré", "Abysses"],
            "forest": ["Forêt", "Bois Magique", "Clairière", "Arbres Anciens"],
            "superhero": ["la Ville", "l'Univers", "la Planète", "la Justice"]
        }
        
        import random
        template = random.choice(title_templates.get(theme, title_templates["adventure"]))
        location = random.choice(locations.get(theme, locations["adventure"]))
        
        return f"{template} {location}"

    async def generate_animation(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer un vrai dessin animé narratif avec Runway Gen-4 Turbo"""
        
        # Extraire les paramètres
        style = animation_data.get("style", "cartoon")
        theme = animation_data.get("theme", "adventure")
        orientation = animation_data.get("orientation", "landscape")
        custom_prompt = animation_data.get("prompt", "")
        title = animation_data.get("title", self._generate_attractive_title(style, theme))
        
        print(f"🎬 Génération DESSIN ANIMÉ NARRATIF - Style: {style}, Thème: {theme}, Orientation: {orientation}")
        print(f"📝 Prompt personnalisé: {custom_prompt}")
        
        # GÉNÉRATION D'UN VRAI DESSIN ANIMÉ AVEC HISTOIRE
        print("🚀 Création d'un dessin animé complet avec histoire...")
        
        try:
            # Étape 1: Créer le scénario de l'histoire
            story_scenes = await self._create_story_scenario(style, theme, custom_prompt)
            print(f"� Scénario créé avec {len(story_scenes)} scènes")
            
            # Étape 2: Générer les images et vidéos pour chaque scène
            scene_videos = []
            ratio_map = {
                "landscape": "1920:1080",
                "portrait": "1080:1920", 
                "square": "1080:1080"
            }
            ratio = ratio_map.get(orientation, "1920:1080")
            
            for i, scene in enumerate(story_scenes):
                print(f"🎨 Génération de la scène {i+1}/{len(story_scenes)}: {scene['title']}")
                
                # Générer l'image de la scène
                scene_image = await self._generate_image_from_text(scene['image_prompt'], ratio)
                print(f"✅ Image scène {i+1} générée: {scene_image}")
                
                # Générer la vidéo de la scène avec narration
                scene_video = await self._generate_video_from_image(
                    scene_image, 
                    scene['animation_prompt'], 
                    duration=8  # 8 secondes par scène
                )
                print(f"✅ Vidéo scène {i+1} générée: {scene_video}")
                
                scene_videos.append({
                    'title': scene['title'],
                    'image_url': scene_image,
                    'video_url': scene_video,
                    'narration': scene['narration']
                })
            
            # Pour l'instant, retourner la première scène comme résultat principal
            # (Dans une version future, on pourrait assembler toutes les scènes)
            main_scene = scene_videos[0]
            
            # Retourner le résultat final
            return {
                "id": f"runway_story_{int(time.time())}",
                "title": title,
                "description": f"Dessin animé {style} - {theme} avec histoire complète ({len(story_scenes)} scènes)",
                "video_url": main_scene['video_url'],
                "thumbnail_url": main_scene['image_url'],
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": len(story_scenes) * 8,  # Durée totale estimée
                "style": style,
                "theme": theme,
                "orientation": orientation,
                "prompt": custom_prompt,
                "story_scenes": scene_videos,  # Toutes les scènes générées
                "narrative_type": "full_story"  # Indique que c'est une histoire complète
            }
            
        except Exception as e:
            print(f"❌ Erreur critique lors de la génération du dessin animé: {e}")
            # AUCUNE SIMULATION - Si l'API échoue, on échoue
            raise Exception(f"Impossible de générer le dessin animé: {str(e)}")

    async def _create_story_scenario(self, style: str, theme: str, custom_prompt: str = "") -> list:
        """Crée un scénario complet pour le dessin animé avec plusieurs scènes"""
        
        # Histoires narratives par thème
        story_templates = {
            "space": [
                {
                    "title": "Décollage vers l'aventure",
                    "narration": "Notre héros embarque dans son vaisseau spatial pour une grande aventure",
                    "image_prompt": f"{style} style, young astronaut character in colorful spacesuit preparing for launch, friendly expression, bright spaceship interior",
                    "animation_prompt": "astronaut checking controls and preparing for takeoff, gentle movements, excitement in eyes"
                },
                {
                    "title": "Découverte d'une planète magique", 
                    "narration": "Il découvre une planète colorée pleine de créatures amicales",
                    "image_prompt": f"{style} style, beautiful alien planet with colorful landscapes, friendly alien creatures, rainbow skies, magical atmosphere",
                    "animation_prompt": "planet rotating slowly, creatures moving gently, sparkles and magical effects"
                },
                {
                    "title": "Nouvelle amitié",
                    "narration": "Il se lie d'amitié avec les habitants de la planète",
                    "image_prompt": f"{style} style, astronaut character meeting friendly colorful aliens, handshakes and smiles, peaceful interaction",
                    "animation_prompt": "characters waving hello, friendly gestures, warm interactions, happy expressions"
                }
            ],
            "adventure": [
                {
                    "title": "Le début de l'aventure",
                    "narration": "Notre aventurier découvre une carte mystérieuse",
                    "image_prompt": f"{style} style, brave young explorer character holding ancient treasure map, excited expression, adventure gear",
                    "animation_prompt": "character examining map carefully, wind blowing gently, anticipation in movements"
                },
                {
                    "title": "La forêt enchantée",
                    "narration": "Il traverse une forêt magique pleine de surprises",
                    "image_prompt": f"{style} style, magical forest with glowing trees, friendly forest animals, sparkling lights, enchanted atmosphere",
                    "animation_prompt": "trees swaying gently, magical sparkles floating, animals moving peacefully"
                },
                {
                    "title": "Le trésor découvert",
                    "narration": "Il trouve le trésor et partage sa joie avec ses nouveaux amis",
                    "image_prompt": f"{style} style, character finding colorful treasure chest, forest friends celebrating together, joy and friendship",
                    "animation_prompt": "treasure chest opening with sparkles, characters celebrating, happy dancing movements"
                }
            ],
            "animals": [
                {
                    "title": "Les amis de la forêt",
                    "narration": "Dans la forêt, tous les animaux vivent en harmonie",
                    "image_prompt": f"{style} style, various cute forest animals (rabbit, deer, squirrel, bird) playing together in sunny forest clearing",
                    "animation_prompt": "animals playing together, jumping and running playfully, peaceful nature movements"
                },
                {
                    "title": "Une mission d'entraide",
                    "narration": "Quand un petit oiseau perd son nid, tous s'unissent pour l'aider",
                    "image_prompt": f"{style} style, small sad bird character with forest friends gathering materials to build new nest, teamwork scene",
                    "animation_prompt": "animals working together, carrying twigs and leaves, cooperative movements"
                },
                {
                    "title": "La célébration de l'amitié",
                    "narration": "Le nouveau nid est construit et tous fêtent leur belle amitié",
                    "image_prompt": f"{style} style, happy bird in beautiful new nest with all forest friends celebrating around, party atmosphere",
                    "animation_prompt": "bird singing happily, friends dancing in circle, celebration movements"
                }
            ],
            "magic": [
                {
                    "title": "L'apprentie magicienne",
                    "narration": "Une jeune magicienne apprend ses premiers sorts",
                    "image_prompt": f"{style} style, young witch character with colorful hat and wand, practicing magic, sparkles around, friendly expression",
                    "animation_prompt": "character waving magic wand, colorful sparkles appearing, gentle magical movements"
                },
                {
                    "title": "Le sort qui fait des merveilles",
                    "narration": "Son sort transforme le jardin en paradis fleuri",
                    "image_prompt": f"{style} style, magical garden blooming with colorful flowers, butterflies, rainbow effects, enchanted atmosphere",
                    "animation_prompt": "flowers blooming rapidly, butterflies flying gracefully, magical transformation effects"
                },
                {
                    "title": "Le bonheur partagé",
                    "narration": "Elle partage sa magie avec tous ses amis du village",
                    "image_prompt": f"{style} style, young witch sharing magic with village children, everyone happy and amazed, magical sparkles everywhere",
                    "animation_prompt": "children laughing and clapping, magical effects spreading joy, warm community scene"
                }
            ]
        }
        
        # Récupérer le template d'histoire ou utiliser adventure par défaut
        scenes = story_templates.get(theme, story_templates["adventure"])
        
        # Personnaliser avec le prompt custom si fourni
        if custom_prompt and custom_prompt.strip():
            for scene in scenes:
                scene['image_prompt'] += f", {custom_prompt.strip()}"
        
        return scenes

    def validate_animation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les données d'animation"""
        errors = []
        
        if not data.get("style"):
            errors.append("Le style est requis")
        elif data["style"] not in self.supported_styles:
            errors.append(f"Style non supporté. Styles disponibles: {list(self.supported_styles.keys())}")
        
        if not data.get("theme"):
            errors.append("Le thème est requis")
        
        if data.get("prompt") and len(data["prompt"]) > 500:
            errors.append("La description ne peut pas dépasser 500 caractères")
        
        return {
            "isValid": len(errors) == 0,
            "errors": errors
        }

    def _get_headers(self) -> Dict[str, str]:
        """Headers pour l'authentification Runway selon la documentation officielle"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"  # Version couramment utilisée
        }

    async def _generate_image_from_text(self, prompt: str, ratio: str = "1920:1080") -> str:
        """Génère une image à partir d'un prompt avec l'API text_to_image de Runway"""
        
        print(f"🎨 Génération d'image avec l'API text_to_image de Runway...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        payload = {
            "model": "gen4_image",  # Modèle correct selon l'organisation
            "promptText": prompt,
            "ratio": ratio
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/text_to_image",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur text_to_image: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway text_to_image: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse text_to_image")
            
            print(f"⏳ Tâche image créée: {task_id}")
            
            # Attendre la génération de l'image
            image_url = await self._wait_for_task_completion(task_id, "image")
            return image_url

    async def _generate_video_from_image(self, image_url: str, prompt: str, duration: int = 10) -> str:
        """Génère une vidéo à partir d'une image avec l'API image_to_video de Runway"""
        
        print(f"🎬 Génération de vidéo avec l'API image_to_video de Runway...")
        print(f"🖼️ Image source: {image_url}")
        print(f"📝 Prompt vidéo: {prompt}")
        
        payload = {
            "model": "gen4_turbo",  # Modèle correct pour image_to_video
            "promptImage": image_url,
            "promptText": prompt,
            "duration": duration,
            "ratio": "1280:720"  # Ratio selon la documentation
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/image_to_video",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Erreur image_to_video: {response.status_code} - {error_detail}")
                raise Exception(f"Erreur API Runway image_to_video: {response.status_code} - {error_detail}")
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise Exception("ID de tâche manquant dans la réponse image_to_video")
            
            print(f"⏳ Tâche vidéo créée: {task_id}")
            
            # Attendre la génération de la vidéo
            video_url = await self._wait_for_task_completion(task_id, "video")
            return video_url

    async def _wait_for_task_completion(self, task_id: str, task_type: str = "task") -> str:
        """Attend la fin d'une tâche Runway et retourne l'URL du résultat"""
        
        max_attempts = 60  # 10 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/v1/tasks/{task_id}",
                        headers=self._get_headers()
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Erreur lors de la vérification du statut: {response.status_code}")
                        await asyncio.sleep(10)
                        attempt += 1
                        continue
                    
                    task_status = response.json()
                    status = task_status.get("status")
                    
                    print(f"📊 Statut {task_type}: {status} (tentative {attempt + 1}/{max_attempts})")
                    
                    if status in ["completed", "SUCCEEDED"]:
                        output = task_status.get("output")
                        if output and len(output) > 0:
                            result_url = output[0]
                            print(f"✅ {task_type.capitalize()} terminé: {result_url}")
                            return result_url
                        else:
                            raise Exception(f"Aucun output trouvé pour la tâche {task_id}")
                    
                    elif status in ["failed", "FAILED"]:
                        error = task_status.get("error", "Erreur inconnue")
                        raise Exception(f"Tâche {task_id} échouée: {error}")
                    
                    elif status in ["pending", "running", "PENDING", "RUNNING"]:
                        await asyncio.sleep(10)
                        attempt += 1
                    
                    else:
                        print(f"⚠️ Statut inattendu: {status}")
                        await asyncio.sleep(10)
                        attempt += 1
                        
            except Exception as e:
                print(f"❌ Erreur lors de la vérification: {e}")
                await asyncio.sleep(10)
                attempt += 1
        
        raise Exception(f"Timeout: La tâche {task_id} n'a pas terminé dans les temps")

# Instance globale du service
runway_gen4_service = RunwayGen4Service()
