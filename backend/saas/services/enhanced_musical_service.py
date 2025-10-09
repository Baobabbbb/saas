"""
Version améliorée du service de comptines musicales avec gestion d'erreurs
"""

from .musical_nursery_rhyme_service import MusicalNurseryRhymeService
import asyncio

class EnhancedMusicalNurseryRhymeService(MusicalNurseryRhymeService):
    """Service amélioré avec gestion d'erreurs et mode démo"""
    
    async def generate_complete_rhyme(
        self,
        rhyme_type: str,
        custom_request: str = None,
        custom_style: str = None,
        generate_music: bool = True,
        language: str = "fr"
    ):
        """
        Version améliorée avec gestion d'erreurs et messages informatifs
        """
        try:
            # Appeler la méthode parent
            result = await super().generate_complete_rhyme(
                rhyme_type, custom_request, custom_style, generate_music, language
            )
            
            # Si la génération musicale a échoué, ajouter un message informatif
            if generate_music and result.get("music_status") == "failed":
                if "demo_message" not in result:
                    result["demo_message"] = (
                        "🎵 Mode démonstration activé ! "
                        "La génération musicale nécessite une connexion à une API externe "
                        "qui semble actuellement indisponible. "
                        "Vos paroles de comptine ont été générées avec succès et vous pouvez "
                        "les utiliser avec n'importe quel logiciel de musique pour créer votre mélodie !"
                    )
                    
                # Ajouter des suggestions
                result["suggestions"] = [
                    "🎹 Utilisez un piano ou un clavier pour créer la mélodie",
                    "🎤 Chantez les paroles sur une mélodie simple",
                    "📱 Utilisez une app de création musicale comme GarageBand",
                    "🎵 Partagez les paroles avec un musicien pour créer la musique"
                ]
            
            return result
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "demo_message": "Une erreur s'est produite lors de la génération. Veuillez réessayer."
            }
