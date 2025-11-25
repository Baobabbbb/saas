from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
from copy import deepcopy
import json
import os
import httpx
from datetime import datetime
from fastapi import status

# Fichier de stockage local pour les configurations
CONFIG_FILE = "features_config.json"

router = APIRouter(prefix="/api", tags=["admin"])

# ============================================
# FONCTIONS D'AUTHENTIFICATION ADMIN
# ============================================

# Import du client Supabase depuis l'environnement
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xfbmdeuzuyixpmouhqcv.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_AUTH_API_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

async def get_supabase_client():
    """Récupère le client Supabase"""
    if not SUPABASE_SERVICE_KEY:
        return None
    try:
        from supabase import create_client, Client
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except:
        return None

async def extract_user_id_from_jwt(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Valide le JWT via l'API Supabase et retourne l'identifiant utilisateur.
    Utilise l'endpoint /auth/v1/user pour garantir la vérification côté serveur.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    
    if not token or not SUPABASE_URL or not SUPABASE_AUTH_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_AUTH_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("id") or data.get("user", {}).get("id")

        print(f"[SECURITY] JWT invalide (status={response.status_code})")
    except httpx.HTTPError as exc:
        print(f"[SECURITY] Erreur lors de la validation JWT : {exc}")

    return None

async def verify_admin_for_features(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> str:
    """Vérifie que l'utilisateur est admin pour les routes features"""
    supabase_client = await get_supabase_client()
    
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Supabase non disponible"
        )
    
    # Récupérer le user_id depuis JWT uniquement
    user_id = await extract_user_id_from_jwt(authorization)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise. Fournissez un JWT dans le header Authorization."
        )
    
    # Vérifier le rôle admin
    try:
        response = supabase_client.table('profiles').select('role').eq('id', user_id).single().execute()
        
        if not response.data or response.data.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux administrateurs"
            )
        
        return user_id
    except HTTPException:
        raise
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )

# Modèles Pydantic
class FeatureUpdate(BaseModel):
    enabled: bool

class FeaturesResponse(BaseModel):
    features: Dict[str, Any]

# Configuration par défaut des fonctionnalités
DEFAULT_FEATURES = {
    "animation": {"enabled": True, "name": "Dessin animé", "icon": "🎬", "description": "Génération de dessins animés personnalisés avec IA"},
    "comic": {"enabled": True, "name": "Bande dessinée", "icon": "💬", "description": "Création de bandes dessinées avec bulles de dialogue"},
    "coloring": {"enabled": True, "name": "Coloriage", "icon": "🎨", "description": "Pages de coloriage à imprimer pour les enfants"},
    "histoire": {"enabled": True, "name": "Histoire", "icon": "📖", "description": "Histoires avec possibilité d'ajouter une narration audio"},
    "rhyme": {"enabled": True, "name": "Comptine", "icon": "🎵", "description": "Comptines musicales avec paroles et mélodies"}
}


def normalize_features_data(features: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliser la configuration (supprimer les doublons, forcer l'alias audio → histoire)."""
    if not isinstance(features, dict):
        return deepcopy(DEFAULT_FEATURES)

    normalized = deepcopy(features)

    # Fusionner l'ancienne clé "audio" avec "histoire" pour rétrocompatibilité
    if "audio" in normalized:
        audio_feature = normalized.pop("audio") or {}
        histoire_feature = normalized.get("histoire", {})

        # Prioriser les informations existantes sur "histoire" tout en complétant avec celles de "audio"
        merged_feature = {
            "enabled": histoire_feature.get("enabled", audio_feature.get("enabled", True)),
            "name": histoire_feature.get("name", audio_feature.get("name", "Histoire")),
            "icon": histoire_feature.get("icon", audio_feature.get("icon", "📖")),
            "description": histoire_feature.get(
                "description",
                audio_feature.get("description", "Histoires avec possibilité d'ajouter une narration audio")
            ),
            "updated_at": histoire_feature.get("updated_at", audio_feature.get("updated_at"))
        }

        normalized["histoire"] = merged_feature

    # S'assurer que la clé "histoire" existe avec les valeurs par défaut minimales
    if "histoire" not in normalized:
        normalized["histoire"] = DEFAULT_FEATURES["histoire"].copy()

    # Garantir les propriétés essentielles
    histoire_feature = normalized["histoire"]
    histoire_feature.setdefault("enabled", True)
    histoire_feature.setdefault("name", "Histoire")
    histoire_feature.setdefault("icon", "📖")
    histoire_feature.setdefault("description", "Histoires avec possibilité d'ajouter une narration audio")

    # Conserver un ordre déterministe des fonctionnalités principales
    ordered_keys = ["animation", "comic", "coloring", "histoire", "rhyme"]
    ordered_features = {key: normalized[key] for key in ordered_keys if key in normalized}

    # Ajouter toute autre fonctionnalité personnalisée à la fin pour compatibilité future
    for key, value in normalized.items():
        if key not in ordered_features:
            ordered_features[key] = value

    return ordered_features

def load_features_config():
    """Charger la configuration depuis le fichier JSON"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                raw_features = json.load(f)
                normalized_features = normalize_features_data(raw_features)

                # Si la normalisation a modifié les données, les persister immédiatement
                if normalized_features != raw_features:
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as nf:
                        json.dump(normalized_features, nf, indent=2, ensure_ascii=False)

                return normalized_features
        else:
            # Créer le fichier avec les valeurs par défaut
            save_features_config(DEFAULT_FEATURES)
            return DEFAULT_FEATURES
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        return DEFAULT_FEATURES

def save_features_config(features):
    """Sauvegarder la configuration dans le fichier JSON"""
    try:
        normalized_features = normalize_features_data(features)

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(normalized_features, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration: {e}")
        return False

@router.get("/features")
async def get_features():
    """Récupérer toutes les fonctionnalités"""
    try:
        features = load_features_config()
        return features
    except Exception as e:
        print(f"Erreur lors de la récupération des fonctionnalités: {e}")
        return DEFAULT_FEATURES

@router.put("/features/{feature_key}")
async def update_feature(
    feature_key: str, 
    feature_update: FeatureUpdate,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Mettre à jour une fonctionnalité spécifique (requiert admin)"""
    # Vérifier que l'utilisateur est admin
    await verify_admin_for_features(authorization=authorization, request=request)
    
    try:
        # Charger la configuration actuelle
        features = load_features_config()
        
        # Vérifier que la fonctionnalité existe
        if feature_key not in features:
            raise HTTPException(status_code=404, detail="Fonctionnalité non trouvée")
        
        # Mettre à jour la fonctionnalité
        features[feature_key]["enabled"] = feature_update.enabled
        features[feature_key]["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarder la configuration
        if save_features_config(features):
            return {"features": features}
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la fonctionnalité {feature_key}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/features/reset")
async def reset_features(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Réinitialiser toutes les fonctionnalités à leur état par défaut (requiert admin)"""
    # Vérifier que l'utilisateur est admin
    await verify_admin_for_features(authorization=authorization, request=request)
    
    try:
        # Réinitialiser toutes les fonctionnalités à True
        features = load_features_config()
        for feature_key in features:
            features[feature_key]["enabled"] = True
            features[feature_key]["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarder la configuration
        if save_features_config(features):
            return {"features": features}
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")
            
    except Exception as e:
        print(f"Erreur lors de la réinitialisation des fonctionnalités: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/features/{feature_key}")
async def get_feature(feature_key: str):
    """Récupérer une fonctionnalité spécifique"""
    try:
        features = load_features_config()
        
        if feature_key in features:
            return features[feature_key]
        else:
            raise HTTPException(status_code=404, detail="Fonctionnalité non trouvée")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la récupération de la fonctionnalité {feature_key}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# ============================================
# GESTION DES UTILISATEURS
# ============================================

@router.get("/users")
async def list_users(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Lister tous les utilisateurs (requiert admin)"""
    await verify_admin_for_features(authorization=authorization, request=request)
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configuration Supabase manquante"
        )
    
    try:
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/profiles",
                headers=headers,
                params={"select": "id,prenom,nom,email,role,created_at"}
            )
            
            response.raise_for_status()  # Lève une exception pour les codes 4xx/5xx
            users = response.json()
            users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return {"users": users}
    except httpx.HTTPStatusError as exc:
        print(f"[admin_users] Supabase status error: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Impossible de récupérer les utilisateurs ({exc.response.status_code})"
        )
    except Exception as exc:
        print(f"[admin_users] erreur inattendue lors de la liste des utilisateurs: {exc}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur lors de la récupération des utilisateurs"
        )

@router.delete("/users/{user_id}")
async def delete_user_and_creations(
    user_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Supprimer un utilisateur et toutes ses créations (requiert admin)"""
    await verify_admin_for_features(authorization=authorization, request=request)

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configuration Supabase manquante pour la suppression d'utilisateur"
        )

    try:
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            # 1. Supprimer les créations de l'utilisateur (non-bloquant)
            try:
                await client.delete(
                    f"{SUPABASE_URL}/rest/v1/creations",
                    headers=headers,
                    params={"user_id": f"eq.{user_id}"}
                ).raise_for_status()
                print(f"[admin_users] Créations de l'utilisateur {user_id} supprimées.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 404:
                    print(f"[admin_users] Avertissement: Erreur lors de la suppression des créations: {e.response.status_code}")
                else:
                    print(f"[admin_users] Aucune création trouvée pour l'utilisateur {user_id}.")

            # 2. Supprimer les abonnements de l'utilisateur (non-bloquant)
            try:
                await client.delete(
                    f"{SUPABASE_URL}/rest/v1/subscriptions",
                    headers=headers,
                    params={"user_id": f"eq.{user_id}"}
                ).raise_for_status()
                print(f"[admin_users] Abonnements de l'utilisateur {user_id} supprimés.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 404:
                    print(f"[admin_users] Avertissement: Erreur lors de la suppression des abonnements: {e.response.status_code}")
                else:
                    print(f"[admin_users] Aucun abonnement trouvé pour l'utilisateur {user_id}.")

            # 3. Supprimer les tokens de l'utilisateur (non-bloquant)
            try:
                await client.delete(
                    f"{SUPABASE_URL}/rest/v1/user_tokens",
                    headers=headers,
                    params={"user_id": f"eq.{user_id}"}
                ).raise_for_status()
                print(f"[admin_users] Tokens de l'utilisateur {user_id} supprimés.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 404:
                    print(f"[admin_users] Avertissement: Erreur lors de la suppression des tokens: {e.response.status_code}")
                else:
                    print(f"[admin_users] Aucun token trouvé pour l'utilisateur {user_id}.")

            # 4. Supprimer le profil de l'utilisateur (non-bloquant)
            try:
                await client.delete(
                    f"{SUPABASE_URL}/rest/v1/profiles",
                    headers=headers,
                    params={"id": f"eq.{user_id}"}
                ).raise_for_status()
                print(f"[admin_users] Profil de l'utilisateur {user_id} supprimé.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 404:
                    print(f"[admin_users] Avertissement: Erreur lors de la suppression du profil: {e.response.status_code}")
                else:
                    print(f"[admin_users] Aucun profil trouvé pour l'utilisateur {user_id}.")

            # 5. Supprimer l'utilisateur de Supabase Auth (nécessite l'API admin)
            auth_headers = {
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            try:
                auth_response = await client.delete(
                    f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                    headers=auth_headers
                )
                auth_response.raise_for_status()
                print(f"[admin_users] Utilisateur {user_id} supprimé de Supabase Auth.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    print(f"[admin_users] Avertissement: Utilisateur {user_id} non trouvé dans Supabase Auth (peut-être déjà supprimé).")
                else:
                    print(f"[admin_users] Erreur lors de la suppression de Supabase Auth: {e.response.status_code} - {e.response.text}")
                    raise  # Relever l'erreur pour Supabase Auth car c'est critique

        return {"message": f"Utilisateur {user_id} et toutes ses données supprimés avec succès."}

    except httpx.HTTPStatusError as exc:
        print(f"[admin_users] Erreur Supabase lors de la suppression: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Erreur lors de la suppression de l'utilisateur ({exc.response.status_code})"
        )
    except Exception as exc:
        print(f"[admin_users] Erreur inattendue lors de la suppression de l'utilisateur: {exc}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur lors de la suppression de l'utilisateur"
        )