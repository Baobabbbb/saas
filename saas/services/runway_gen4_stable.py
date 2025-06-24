"""
Service Runway Gen-4 Turbo pour la génération de dessins animés
Version stable en mode simulation avec l'interface pour passer en production plus tard
"""

import os
import time
import asyncio
from typing import Dict, Any
from datetime import datetime

class RunwayGen4Service:
    """Service de génération vidéo Runway Gen-4 Turbo"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        
        # Pour le moment, forcer le mode simulation pour garantir la stabilité
        # TODO: Résoudre les problèmes d'API Runway et repasser en mode production
        print("⚠️ Mode simulation activé - Interface stable pendant le développement")
        self.simulation_mode = True
        
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
        print(f"🔑 Clé API disponible: {'Oui' if self.api_key else 'Non'}")
        print(f"🎨 Styles supportés: {list(self.supported_styles.keys())}")
        print(f"🚀 Mode: Simulation (interface stable)")
    
    def _create_optimized_prompt(self, style: str, theme: str, custom_prompt: str = "") -> str:
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
        """Générer une animation avec Runway Gen-4 Turbo"""
        
        # Extraire les paramètres
        style = animation_data.get("style", "cartoon")
        theme = animation_data.get("theme", "adventure")
        orientation = animation_data.get("orientation", "landscape")
        custom_prompt = animation_data.get("prompt", "")
        title = animation_data.get("title", self._generate_attractive_title(style, theme))
        
        print(f"🎬 Génération animation - Style: {style}, Thème: {theme}, Orientation: {orientation}")
        
        # Créer le prompt optimisé
        optimized_prompt = self._create_optimized_prompt(style, theme, custom_prompt)
        print(f"📝 Prompt optimisé: {optimized_prompt[:100]}...")
        
        # Mode simulation pour assurer la stabilité de l'interface
        print("🔄 Mode simulation - Génération instantanée")
        
        # Choisir une vidéo de démo en fonction du thème
        demo_videos = {
            "adventure": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "magic": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "animals": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "friendship": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "space": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "underwater": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "forest": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
            "superhero": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
        }
        
        video_url = demo_videos.get(theme, demo_videos["adventure"])
        
        return {
            "id": f"runway_sim_{int(time.time())}",
            "title": title,
            "description": f"Animation {style} - {theme} (Mode simulation - Interface fonctionnelle)",
            "video_url": video_url,
            "thumbnail_url": None,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration": 10,
            "style": style,
            "theme": theme,
            "orientation": orientation,
            "prompt": optimized_prompt
        }
    
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

# Instance globale du service
runway_gen4_service = RunwayGen4Service()
