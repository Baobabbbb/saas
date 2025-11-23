"""
Service Supabase Storage - Gestion centralisée du stockage des créations
Gère l'upload, le download, la suppression et la génération d'URLs signées
"""

import os
import uuid
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List
from supabase import Client
from datetime import timedelta

class SupabaseStorageService:
    """
    Service professionnel pour gérer le stockage des créations dans Supabase Storage
    
    Structure des chemins:
    - /{user_id}/comics/{comic_id}/page_{num}.png
    - /{user_id}/coloring/{coloring_id}.png
    - /{user_id}/animations/{animation_id}/{scene_id}.mp4
    - /{user_id}/audio/{audio_id}.mp3
    """
    
    # Mapping des types de créations vers leurs buckets publics
    CONTENT_TYPE_BUCKETS = {
        "comic": "comics",
        "bd": "comics",
        "coloring": "coloring",
        "coloriage": "coloring",
        "animation": "animations",
        "rhyme": "audio",
        "comptine": "audio",
        "audio": "audio",
        "story": "audio",  # Les histoires audio vont dans le bucket audio
        "histoire": "audio"  # Les histoires audio vont dans le bucket audio
    }
    
    # Mapping des types de créations vers leurs dossiers (pour organisation dans le bucket)
    CONTENT_TYPE_FOLDERS = {
        "comic": "comics",
        "bd": "comics",
        "coloring": "coloring",
        "coloriage": "coloring",
        "animation": "animations",
        "rhyme": "rhymes",
        "comptine": "rhymes",
        "audio": "stories",
        "story": "stories",
        "histoire": "stories"
    }
    
    def __init__(self, supabase_client: Client, supabase_url: str):
        """
        Initialise le service Storage
        
        Args:
            supabase_client: Client Supabase avec service_role
            supabase_url: URL du projet Supabase (pour construire les URLs publiques)
        """
        self.client = supabase_client
        self.supabase_url = supabase_url.rstrip('/')
        
        print(f"✅ SupabaseStorageService initialisé (buckets dynamiques: audio, coloring, comics, animations)")
    
    def _get_bucket_for_type(self, content_type: str) -> str:
        """Retourne le bucket correspondant au type de contenu"""
        return self.CONTENT_TYPE_BUCKETS.get(content_type, "audio")  # Par défaut: audio
    
    def _get_folder_for_type(self, content_type: str) -> str:
        """Retourne le dossier correspondant au type de contenu"""
        return self.CONTENT_TYPE_FOLDERS.get(content_type, "misc")
    
    def _generate_storage_path(
        self, 
        user_id: str, 
        content_type: str, 
        filename: str,
        creation_id: Optional[str] = None
    ) -> str:
        """
        Génère le chemin de stockage pour un fichier
        
        Args:
            user_id: ID de l'utilisateur
            content_type: Type de création (comic, coloring, etc.)
            filename: Nom du fichier
            creation_id: ID optionnel de la création (pour regrouper les fichiers)
        
        Returns:
            Chemin complet dans le bucket
        """
        folder = self._get_folder_for_type(content_type)
        
        if creation_id:
            # Regrouper par création (ex: BD avec plusieurs pages)
            return f"{user_id}/{folder}/{creation_id}/{filename}"
        else:
            # Fichier unique
            return f"{user_id}/{folder}/{filename}"
    
    async def upload_file(
        self,
        file_path: str,
        user_id: str,
        content_type: str,
        creation_id: Optional[str] = None,
        custom_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload un fichier vers Supabase Storage
        
        Args:
            file_path: Chemin local du fichier à uploader
            user_id: ID de l'utilisateur propriétaire
            content_type: Type de création
            creation_id: ID optionnel de la création
            custom_filename: Nom personnalisé (sinon utilise le nom du fichier)
        
        Returns:
            Dict avec 'success', 'storage_path', 'public_url', 'signed_url'
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Fichier non trouvé: {file_path}"
                }
            
            # Déterminer le nom du fichier
            if custom_filename:
                filename = custom_filename
            else:
                filename = Path(file_path).name
            
            # Générer le chemin de stockage
            storage_path = self._generate_storage_path(
                user_id, content_type, filename, creation_id
            )
            
            # Déterminer le MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # Fallback basé sur l'extension
                ext = Path(file_path).suffix.lower()
                mime_types_map = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.webp': 'image/webp',
                    '.mp4': 'video/mp4',
                    '.mp3': 'audio/mpeg',
                    '.wav': 'audio/wav'
                }
                mime_type = mime_types_map.get(ext, 'application/octet-stream')
            
            # Lire le fichier
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            file_size = len(file_data)
            
            # Déterminer le bucket selon le type de contenu
            bucket_name = self._get_bucket_for_type(content_type)
            bucket = self.client.storage.from_(bucket_name)
            
            print(f"📤 Upload vers Supabase Storage:")
            print(f"   - Bucket: {bucket_name}")
            print(f"   - Chemin: {storage_path}")
            print(f"   - Taille: {file_size / 1024:.2f} KB")
            print(f"   - Type MIME: {mime_type}")
            
            # Upload vers Supabase Storage
            response = bucket.upload(
                path=storage_path,
                file=file_data,
                file_options={
                    "content-type": mime_type,
                    "upsert": "true"  # Remplacer si existe déjà
                }
            )
            
            # Générer l'URL publique (bucket public)
            public_url = f"{self.supabase_url}/storage/v1/object/public/{bucket_name}/{storage_path}"
            
            # Générer une URL signée (valide 1 an) - utile pour les buckets privés
            signed_url_response = bucket.create_signed_url(
                path=storage_path,
                expires_in=31536000  # 1 an en secondes
            )
            
            signed_url = signed_url_response.get('signedURL') if signed_url_response else public_url
            
            print(f"✅ Upload réussi vers bucket '{bucket_name}': {storage_path}")
            
            return {
                "success": True,
                "storage_path": storage_path,
                "public_url": public_url,
                "signed_url": signed_url,
                "file_size": file_size,
                "mime_type": mime_type
            }
            
        except Exception as e:
            print(f"❌ Erreur upload Supabase Storage: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def upload_multiple_files(
        self,
        files: List[str],
        user_id: str,
        content_type: str,
        creation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload plusieurs fichiers d'une même création
        
        Args:
            files: Liste des chemins locaux des fichiers
            user_id: ID de l'utilisateur
            content_type: Type de création
            creation_id: ID de la création pour regroupement
        
        Returns:
            Dict avec 'success', 'uploaded_files', 'failed_files'
        """
        uploaded_files = []
        failed_files = []
        
        for file_path in files:
            result = await self.upload_file(
                file_path=file_path,
                user_id=user_id,
                content_type=content_type,
                creation_id=creation_id
            )
            
            if result["success"]:
                uploaded_files.append(result)
            else:
                failed_files.append({
                    "file_path": file_path,
                    "error": result.get("error")
                })
        
        return {
            "success": len(failed_files) == 0,
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "total": len(files),
            "uploaded": len(uploaded_files),
            "failed": len(failed_files)
        }
    
    def get_signed_url(
        self,
        storage_path: str,
        expires_in_seconds: int = 3600
    ) -> Optional[str]:
        """
        Génère une URL signée temporaire pour accéder à un fichier
        
        Args:
            storage_path: Chemin du fichier dans le bucket
            expires_in_seconds: Durée de validité en secondes (défaut: 1h)
        
        Returns:
            URL signée ou None si erreur
        """
        try:
            response = self.bucket.create_signed_url(
                path=storage_path,
                expires_in=expires_in_seconds
            )
            return response.get('signedURL') if response else None
        except Exception as e:
            print(f"❌ Erreur génération URL signée: {e}")
            return None
    
    def get_public_url(self, storage_path: str) -> str:
        """
        Retourne l'URL publique d'un fichier (nécessite bucket public ou URL signée)
        
        Args:
            storage_path: Chemin du fichier dans le bucket
        
        Returns:
            URL publique
        """
        return f"{self.supabase_url}/storage/v1/object/public/{self.BUCKET_NAME}/{storage_path}"
    
    async def delete_file(self, storage_path: str) -> Dict[str, Any]:
        """
        Supprime un fichier du Storage
        
        Args:
            storage_path: Chemin du fichier dans le bucket
        
        Returns:
            Dict avec 'success' et optionnellement 'error'
        """
        try:
            self.bucket.remove([storage_path])
            print(f"🗑️ Fichier supprimé: {storage_path}")
            return {"success": True}
        except Exception as e:
            print(f"❌ Erreur suppression fichier: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_folder(self, user_id: str, content_type: str, creation_id: str) -> Dict[str, Any]:
        """
        Supprime tous les fichiers d'une création (dossier complet)
        
        Args:
            user_id: ID de l'utilisateur
            content_type: Type de création
            creation_id: ID de la création
        
        Returns:
            Dict avec 'success', 'deleted_count'
        """
        try:
            folder = self._get_folder_for_type(content_type)
            folder_path = f"{user_id}/{folder}/{creation_id}"
            
            # Lister tous les fichiers du dossier
            files = self.bucket.list(path=folder_path)
            
            if files:
                # Supprimer tous les fichiers
                file_paths = [f"{folder_path}/{f['name']}" for f in files]
                self.bucket.remove(file_paths)
                
                print(f"🗑️ Dossier supprimé: {folder_path} ({len(files)} fichiers)")
                return {
                    "success": True,
                    "deleted_count": len(files)
                }
            else:
                return {
                    "success": True,
                    "deleted_count": 0
                }
                
        except Exception as e:
            print(f"❌ Erreur suppression dossier: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_user_files(
        self,
        user_id: str,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Liste tous les fichiers d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            content_type: Type de contenu optionnel pour filtrer
        
        Returns:
            Liste des fichiers avec métadonnées
        """
        try:
            if content_type:
                folder = self._get_folder_for_type(content_type)
                path = f"{user_id}/{folder}"
            else:
                path = user_id
            
            files = self.bucket.list(path=path)
            return files or []
            
        except Exception as e:
            print(f"❌ Erreur listage fichiers: {e}")
            return []


# Instance globale (sera initialisée dans main.py)
storage_service: Optional[SupabaseStorageService] = None

def get_storage_service() -> Optional[SupabaseStorageService]:
    """Retourne l'instance globale du service Storage"""
    return storage_service

def init_storage_service(supabase_client: Client, supabase_url: str):
    """Initialise le service Storage global"""
    global storage_service
    storage_service = SupabaseStorageService(supabase_client, supabase_url)
    return storage_service

