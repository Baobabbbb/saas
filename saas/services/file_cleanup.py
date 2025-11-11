"""
Service de nettoyage automatique des fichiers locaux temporaires.
Supprime les fichiers de cache de plus de 24h pour économiser l'espace disque.
Les créations restent accessibles via Supabase Storage.
"""

import os
import time
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class FileCleanupService:
    """Service pour nettoyer automatiquement les fichiers temporaires locaux"""
    
    def __init__(self, max_age_hours: int = 24):
        """
        Args:
            max_age_hours: Âge maximum des fichiers en heures avant suppression (défaut: 24h)
        """
        self.max_age_seconds = max_age_hours * 3600
        
        # Dossiers à nettoyer (cache local uniquement)
        self.cache_directories = [
            "static/cache/coloring",
            "static/cache/comics",
            "static/cache/animations",
            "static/cache/audio",
            "static/coloring",
            "static/generated_comics"
        ]
    
    def get_file_age_seconds(self, file_path: Path) -> float:
        """Retourne l'âge du fichier en secondes"""
        try:
            return time.time() - file_path.stat().st_mtime
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'âge du fichier {file_path}: {e}")
            return 0
    
    def should_delete_file(self, file_path: Path) -> bool:
        """Détermine si un fichier doit être supprimé"""
        # Ne pas supprimer les fichiers système ou de configuration
        if file_path.name.startswith('.'):
            return False
        
        # Vérifier l'âge du fichier
        age_seconds = self.get_file_age_seconds(file_path)
        return age_seconds > self.max_age_seconds
    
    def clean_directory(self, directory: str) -> Dict[str, int]:
        """
        Nettoie un dossier en supprimant les fichiers expirés.
        
        Returns:
            Dict avec les statistiques de nettoyage
        """
        stats = {
            "files_deleted": 0,
            "space_freed_mb": 0,
            "errors": 0
        }
        
        dir_path = Path(directory)
        
        # Vérifier que le dossier existe
        if not dir_path.exists():
            logger.debug(f"Dossier inexistant ignoré: {directory}")
            return stats
        
        try:
            # Parcourir tous les fichiers du dossier
            for file_path in dir_path.rglob("*"):
                if not file_path.is_file():
                    continue
                
                try:
                    if self.should_delete_file(file_path):
                        # Obtenir la taille avant suppression
                        file_size_bytes = file_path.stat().st_size
                        
                        # Supprimer le fichier
                        file_path.unlink()
                        
                        stats["files_deleted"] += 1
                        stats["space_freed_mb"] += file_size_bytes / (1024 * 1024)
                        
                        logger.info(f"✅ Fichier supprimé: {file_path} (âge: {self.get_file_age_seconds(file_path) / 3600:.1f}h)")
                
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"❌ Erreur lors de la suppression de {file_path}: {e}")
            
            # Nettoyer les dossiers vides
            self._clean_empty_directories(dir_path)
        
        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage du dossier {directory}: {e}")
            stats["errors"] += 1
        
        return stats
    
    def _clean_empty_directories(self, base_path: Path):
        """Supprime récursivement les dossiers vides"""
        try:
            for dirpath in sorted(base_path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if dirpath.is_dir() and not any(dirpath.iterdir()):
                    try:
                        dirpath.rmdir()
                        logger.debug(f"Dossier vide supprimé: {dirpath}")
                    except Exception as e:
                        logger.debug(f"Impossible de supprimer le dossier vide {dirpath}: {e}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des dossiers vides: {e}")
    
    def run_cleanup(self) -> Dict[str, any]:
        """
        Exécute le nettoyage sur tous les dossiers configurés.
        
        Returns:
            Dict avec les statistiques globales de nettoyage
        """
        logger.info("🧹 Début du nettoyage automatique des fichiers locaux...")
        
        total_stats = {
            "files_deleted": 0,
            "space_freed_mb": 0,
            "errors": 0,
            "directories_cleaned": 0
        }
        
        for directory in self.cache_directories:
            logger.debug(f"Nettoyage du dossier: {directory}")
            stats = self.clean_directory(directory)
            
            total_stats["files_deleted"] += stats["files_deleted"]
            total_stats["space_freed_mb"] += stats["space_freed_mb"]
            total_stats["errors"] += stats["errors"]
            
            if stats["files_deleted"] > 0:
                total_stats["directories_cleaned"] += 1
        
        logger.info(
            f"✅ Nettoyage terminé: "
            f"{total_stats['files_deleted']} fichiers supprimés, "
            f"{total_stats['space_freed_mb']:.2f} MB libérés, "
            f"{total_stats['directories_cleaned']} dossiers nettoyés, "
            f"{total_stats['errors']} erreurs"
        )
        
        return total_stats


# Instance globale du service
cleanup_service = FileCleanupService(max_age_hours=24)


def run_scheduled_cleanup():
    """Fonction appelée par le scheduler pour exécuter le nettoyage"""
    try:
        cleanup_service.run_cleanup()
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage planifié: {e}")

