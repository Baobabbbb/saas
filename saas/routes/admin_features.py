from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import os
from supabase import create_client, Client
from datetime import datetime

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Initialisation conditionnelle de Supabase
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("⚠️ Variables d'environnement Supabase non définies - mode fallback activé")

router = APIRouter(prefix="/api", tags=["admin"])

# Modèles Pydantic
class FeatureUpdate(BaseModel):
    enabled: bool

class FeatureResponse(BaseModel):
    feature_key: str
    enabled: bool
    name: str
    icon: str
    description: str

class FeaturesResponse(BaseModel):
    features: Dict[str, Any]

# Configuration par défaut des fonctionnalités
DEFAULT_FEATURES = {
    "animation": {"enabled": True, "name": "Dessin animé", "icon": "🎬"},
    "comic": {"enabled": True, "name": "Bande dessinée", "icon": "💬"},
    "coloring": {"enabled": True, "name": "Coloriage", "icon": "🎨"},
    "audio": {"enabled": True, "name": "Histoire", "icon": "📖"},
    "rhyme": {"enabled": True, "name": "Comptine", "icon": "🎵"}
}

@router.get("/features")
async def get_features():
    """Récupérer toutes les fonctionnalités depuis la base de données"""
    try:
        # Si Supabase n'est pas disponible, retourner les valeurs par défaut
        if not supabase:
            print("Supabase non disponible - retour des valeurs par défaut")
            return DEFAULT_FEATURES
            
        # Récupérer les fonctionnalités depuis Supabase
        response = supabase.table("feature_config").select("*").execute()
        
        if response.data:
            features = {}
            for feature in response.data:
                features[feature["feature_key"]] = {
                    "enabled": feature["enabled"],
                    "name": feature["name"],
                    "icon": feature["icon"],
                    "description": feature.get("description", "")
                }
            return features
        else:
            # Si aucune donnée, retourner les valeurs par défaut
            return DEFAULT_FEATURES
            
    except Exception as e:
        print(f"Erreur lors de la récupération des fonctionnalités: {e}")
        return DEFAULT_FEATURES

@router.put("/features/{feature_key}")
async def update_feature(feature_key: str, feature_update: FeatureUpdate):
    """Mettre à jour une fonctionnalité spécifique"""
    try:
        # Si Supabase n'est pas disponible, simuler la mise à jour
        if not supabase:
            print(f"Supabase non disponible - simulation de mise à jour pour {feature_key}")
            # Retourner les fonctionnalités par défaut avec la modification simulée
            features = DEFAULT_FEATURES.copy()
            if feature_key in features:
                features[feature_key]["enabled"] = feature_update.enabled
            return {"features": features}
            
        # Vérifier que la fonctionnalité existe
        response = supabase.table("feature_config").select("*").eq("feature_key", feature_key).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Fonctionnalité non trouvée")
        
        # Mettre à jour la fonctionnalité
        update_response = supabase.table("feature_config").update({
            "enabled": feature_update.enabled,
            "updated_at": datetime.now().isoformat()
        }).eq("feature_key", feature_key).execute()
        
        if update_response.data:
            # Récupérer toutes les fonctionnalités mises à jour
            all_features = await get_features()
            return {"features": all_features}
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la fonctionnalité {feature_key}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/features/reset")
async def reset_features():
    """Réinitialiser toutes les fonctionnalités à leur état par défaut"""
    try:
        # Réinitialiser toutes les fonctionnalités à True
        for feature_key in DEFAULT_FEATURES.keys():
            supabase.table("feature_config").update({
                "enabled": True,
                "updated_at": datetime.now().isoformat()
            }).eq("feature_key", feature_key).execute()
        
        # Récupérer toutes les fonctionnalités mises à jour
        all_features = await get_features()
        return {"features": all_features}
        
    except Exception as e:
        print(f"Erreur lors de la réinitialisation des fonctionnalités: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/features/{feature_key}")
async def get_feature(feature_key: str):
    """Récupérer une fonctionnalité spécifique"""
    try:
        response = supabase.table("feature_config").select("*").eq("feature_key", feature_key).execute()
        
        if response.data:
            feature = response.data[0]
            return {
                "feature_key": feature["feature_key"],
                "enabled": feature["enabled"],
                "name": feature["name"],
                "icon": feature["icon"],
                "description": feature.get("description", "")
            }
        else:
            raise HTTPException(status_code=404, detail="Fonctionnalité non trouvée")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la récupération de la fonctionnalité {feature_key}: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
