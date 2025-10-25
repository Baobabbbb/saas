from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import json
import os
from datetime import datetime

# Fichier de stockage local pour les configurations
CONFIG_FILE = "features_config.json"

router = APIRouter(prefix="/api", tags=["admin"])

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

def load_features_config():
    """Charger la configuration depuis le fichier JSON"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
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
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(features, f, indent=2, ensure_ascii=False)
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
async def update_feature(feature_key: str, feature_update: FeatureUpdate):
    """Mettre à jour une fonctionnalité spécifique"""
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
async def reset_features():
    """Réinitialiser toutes les fonctionnalités à leur état par défaut"""
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