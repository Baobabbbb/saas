"""
Service de gestion de l'unicité des contenus générés
Garantit que les utilisateurs ne reçoivent jamais de doublons

Architecture:
- Non-invasif: fonctionne en wrapper autour des générations existantes
- Non-bloquant: si le service échoue, la génération continue normalement
- Optionnel: peut être désactivé via variable d'environnement
"""

import hashlib
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Feature flag pour activer/désactiver le service
ENABLE_UNIQUENESS = os.getenv("ENABLE_UNIQUENESS_CHECK", "true").lower() == "true"


class UniquenessService:
    """Service centralisé pour garantir l'unicité des contenus"""
    
    def __init__(self):
        self.enabled = ENABLE_UNIQUENESS
        logger.info(f"UniquenessService initialisé (enabled={self.enabled})")
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """
        Calcule un hash SHA256 du contenu
        
        Args:
            content: Texte dont on veut calculer le hash
            
        Returns:
            Hash SHA256 en hexadécimal
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_summary(content: str, content_type: str, max_length: int = 150) -> str:
        """
        Génère un résumé court du contenu
        
        Args:
            content: Contenu à résumer
            content_type: Type de contenu (histoire, coloriage, etc.)
            max_length: Longueur maximale du résumé
            
        Returns:
            Résumé court
        """
        # Résumé simple: premiers mots du contenu
        words = content.split()[:30]
        summary = ' '.join(words)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    @staticmethod
    def extract_variation_tags(
        content: str, 
        content_type: str,
        theme: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extrait des tags de variation selon le type de contenu
        
        Args:
            content: Contenu généré
            content_type: Type (histoire, coloriage, bd, comptine, animation)
            theme: Thème choisi par l'utilisateur
            custom_data: Données supplémentaires spécifiques au type
            
        Returns:
            Dictionnaire de tags de variation
        """
        tags = {
            "content_type": content_type,
            "theme": theme,
            "generated_at": datetime.now().isoformat()
        }
        
        # Ajouter des tags spécifiques selon le type
        if custom_data:
            tags.update(custom_data)
        
        return tags
    
    async def check_for_duplicates(
        self,
        supabase_client,
        user_id: str,
        content_type: str,
        content_hash: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Vérifie si un contenu est un doublon exact
        
        Args:
            supabase_client: Client Supabase
            user_id: ID de l'utilisateur
            content_type: Type de contenu
            content_hash: Hash du contenu généré
            limit: Nombre max de créations à vérifier
            
        Returns:
            {
                "is_duplicate": bool,
                "existing_creation_id": int or None
            }
        """
        try:
            # Rechercher dans l'historique de l'utilisateur
            response = supabase_client.table('creations').select('id, content_hash').eq(
                'user_id', user_id
            ).eq(
                'type', content_type
            ).eq(
                'content_hash', content_hash
            ).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                return {
                    "is_duplicate": True,
                    "existing_creation_id": response.data[0]['id']
                }
            
            return {"is_duplicate": False, "existing_creation_id": None}
            
        except Exception as e:
            logger.error(f"Erreur vérification doublon: {e}")
            # En cas d'erreur, on considère que ce n'est pas un doublon
            return {"is_duplicate": False, "existing_creation_id": None}
    
    async def get_user_history(
        self,
        supabase_client,
        user_id: str,
        content_type: str,
        theme: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Récupère l'historique récent de l'utilisateur
        
        Args:
            supabase_client: Client Supabase
            user_id: ID de l'utilisateur
            content_type: Type de contenu
            theme: Filtrer par thème (optionnel)
            limit: Nombre max de créations à récupérer
            
        Returns:
            Liste des créations récentes avec leurs métadonnées
        """
        try:
            query = supabase_client.table('creations').select(
                'id, title, summary, data, created_at'
            ).eq(
                'user_id', user_id
            ).eq(
                'type', content_type
            ).order(
                'created_at', desc=True
            ).limit(limit)
            
            response = query.execute()
            
            history = []
            for item in response.data:
                # Extraire les variation_tags du champ data (jsonb)
                data = item.get('data', {}) or {}
                variation_tags = data.get('variation_tags', {})
                
                # Filtrer par thème si spécifié
                if theme and variation_tags.get('theme') != theme:
                    continue
                
                history.append({
                    "id": item['id'],
                    "title": item.get('title', ''),
                    "summary": item.get('summary', ''),
                    "variation_tags": variation_tags,
                    "created_at": item.get('created_at')
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return []
    
    def enrich_prompt_with_history(
        self,
        base_prompt: str,
        history: List[Dict[str, Any]],
        content_type: str
    ) -> str:
        """
        Enrichit le prompt avec l'historique pour éviter les doublons
        
        Args:
            base_prompt: Prompt de base
            history: Historique des créations de l'utilisateur
            content_type: Type de contenu
            
        Returns:
            Prompt enrichi
        """
        if not history:
            return base_prompt
        
        # Construire le contexte d'historique
        history_context = "\n\nIMPORTANT - ÉVITER LES DOUBLONS:\n"
        history_context += f"L'utilisateur a déjà reçu {len(history)} {content_type}(s) similaire(s):\n"
        
        for idx, item in enumerate(history[:3], 1):  # Max 3 pour ne pas surcharger
            title = item.get('title', 'Sans titre')
            summary = item.get('summary', '')
            tags = item.get('variation_tags', {})
            
            history_context += f"\n{idx}. {title}"
            if summary:
                history_context += f" - {summary[:100]}"
            if tags:
                # Afficher quelques tags pertinents
                relevant_tags = [f"{k}: {v}" for k, v in tags.items() 
                               if k not in ['content_type', 'generated_at', 'theme']]
                if relevant_tags:
                    history_context += f" (Tags: {', '.join(relevant_tags[:3])})"
        
        history_context += "\n\nCrée un contenu COMPLÈTEMENT DIFFÉRENT en évitant ces éléments déjà utilisés. "
        history_context += "Explore de nouvelles variations, personnages, décors, ou approches narratives.\n"
        
        return base_prompt + history_context
    
    async def ensure_unique_content(
        self,
        supabase_client,
        user_id: Optional[str],
        content_type: str,
        theme: Optional[str],
        generated_content: str,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Point d'entrée principal: vérifie et garantit l'unicité du contenu
        
        Args:
            supabase_client: Client Supabase
            user_id: ID de l'utilisateur (peut être None pour utilisateurs non connectés)
            content_type: Type de contenu
            theme: Thème choisi
            generated_content: Contenu généré à vérifier
            custom_data: Données supplémentaires pour les tags
            
        Returns:
            {
                "is_duplicate": bool,
                "should_regenerate": bool,
                "content_hash": str,
                "summary": str,
                "variation_tags": dict,
                "history": list (pour enrichir le prompt si régénération)
            }
        """
        try:
            # Si le service est désactivé, retourner immédiatement
            if not self.enabled:
                return {
                    "is_duplicate": False,
                    "should_regenerate": False,
                    "content_hash": None,
                    "summary": None,
                    "variation_tags": {},
                    "history": []
                }
            
            # Si pas d'user_id, on ne peut pas vérifier (utilisateur non connecté)
            if not user_id:
                # Générer quand même les métadonnées pour stockage
                content_hash = self.compute_content_hash(generated_content)
                summary = self.generate_summary(generated_content, content_type)
                variation_tags = self.extract_variation_tags(
                    generated_content, content_type, theme, custom_data
                )
                
                return {
                    "is_duplicate": False,
                    "should_regenerate": False,
                    "content_hash": content_hash,
                    "summary": summary,
                    "variation_tags": variation_tags,
                    "history": []
                }
            
            # Calculer le hash du contenu
            content_hash = self.compute_content_hash(generated_content)
            
            # Vérifier si c'est un doublon exact
            duplicate_check = await self.check_for_duplicates(
                supabase_client, user_id, content_type, content_hash
            )
            
            # Récupérer l'historique pour enrichir les prompts futurs
            history = await self.get_user_history(
                supabase_client, user_id, content_type, theme
            )
            
            # Générer les métadonnées
            summary = self.generate_summary(generated_content, content_type)
            variation_tags = self.extract_variation_tags(
                generated_content, content_type, theme, custom_data
            )
            
            return {
                "is_duplicate": duplicate_check["is_duplicate"],
                "should_regenerate": duplicate_check["is_duplicate"],
                "content_hash": content_hash,
                "summary": summary,
                "variation_tags": variation_tags,
                "history": history,
                "existing_creation_id": duplicate_check.get("existing_creation_id")
            }
            
        except Exception as e:
            logger.error(f"Erreur dans ensure_unique_content: {e}")
            # En cas d'erreur, retourner des valeurs par défaut sûres
            return {
                "is_duplicate": False,
                "should_regenerate": False,
                "content_hash": None,
                "summary": None,
                "variation_tags": {},
                "history": []
            }


# Instance globale du service
uniqueness_service = UniquenessService()

