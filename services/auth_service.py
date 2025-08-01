import httpx
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from utils.jwt_auth import jwt_auth
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserProfile

# Configuration Supabase
SUPABASE_URL = "https://xfbmdeuzuyixpmouhqcv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhmYm1kZXV6dXlpeHBtb3VocWN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzMzE3ODQsImV4cCI6MjA2NDkwNzc4NH0.XzFIT3BwW9dKRrmFFbSAufCpC1SZuUI-VU2Uer5VoTw"

class AuthService:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.supabase_anon_key = SUPABASE_ANON_KEY
        self.headers = {
            "apikey": self.supabase_anon_key,
            "Content-Type": "application/json"
        }
    
    async def authenticate_user(self, login_data: LoginRequest) -> TokenResponse:
        """Authentifier un utilisateur avec Supabase et créer des JWT tokens"""
        try:
            async with httpx.AsyncClient() as client:
                # Authentification avec Supabase
                auth_response = await client.post(
                    f"{self.supabase_url}/auth/v1/token?grant_type=password",
                    headers=self.headers,
                    json={
                        "email": login_data.email,
                        "password": login_data.password
                    }
                )
                
                if auth_response.status_code != 200:
                    error_data = auth_response.json()
                    if "Invalid login credentials" in error_data.get("error_description", ""):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Identifiants invalides"
                        )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error_data.get("error_description", "Erreur d'authentification")
                        )
                
                auth_data = auth_response.json()
                user_id = auth_data.get("user", {}).get("id")
                email = auth_data.get("user", {}).get("email")
                
                if not user_id or not email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Données utilisateur manquantes"
                    )
                
                # Créer les JWT tokens
                tokens = jwt_auth.create_tokens_for_user(user_id, email)
                
                return TokenResponse(**tokens)
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erreur de connexion au service d'authentification"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )
    
    async def register_user(self, register_data: RegisterRequest) -> TokenResponse:
        """Inscrire un nouvel utilisateur avec Supabase et créer des JWT tokens"""
        try:
            async with httpx.AsyncClient() as client:
                # Inscription avec Supabase
                auth_response = await client.post(
                    f"{self.supabase_url}/auth/v1/signup",
                    headers=self.headers,
                    json={
                        "email": register_data.email,
                        "password": register_data.password
                    }
                )
                
                if auth_response.status_code != 200:
                    error_data = auth_response.json()
                    if "User already registered" in error_data.get("error_description", ""):
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Un utilisateur avec cet email existe déjà"
                        )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error_data.get("error_description", "Erreur d'inscription")
                        )
                
                auth_data = auth_response.json()
                user_id = auth_data.get("user", {}).get("id")
                email = auth_data.get("user", {}).get("email")
                
                if not user_id or not email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Données utilisateur manquantes"
                    )
                
                # Créer le profil utilisateur dans la table profiles
                profile_response = await client.post(
                    f"{self.supabase_url}/rest/v1/profiles",
                    headers=self.headers,
                    json={
                        "id": user_id,
                        "prenom": register_data.first_name,
                        "nom": register_data.last_name
                    }
                )
                
                # Créer les JWT tokens
                tokens = jwt_auth.create_tokens_for_user(user_id, email)
                
                return TokenResponse(**tokens)
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erreur de connexion au service d'authentification"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Récupérer le profil utilisateur depuis Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                # Récupérer le profil depuis la table profiles
                profile_response = await client.get(
                    f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}",
                    headers=self.headers
                )
                
                if profile_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Profil utilisateur non trouvé"
                    )
                
                profiles = profile_response.json()
                if not profiles:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Profil utilisateur non trouvé"
                    )
                
                profile = profiles[0]
                
                # Récupérer l'email depuis la table auth.users
                user_response = await client.get(
                    f"{self.supabase_url}/auth/v1/admin/users/{user_id}",
                    headers=self.headers
                )
                
                email = ""
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    email = user_data.get("email", "")
                
                return UserProfile(
                    id=user_id,
                    email=email,
                    first_name=profile.get("prenom", ""),
                    last_name=profile.get("nom", "")
                )
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erreur de connexion au service d'authentification"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """Mettre à jour le profil utilisateur"""
        try:
            async with httpx.AsyncClient() as client:
                # Mettre à jour le profil
                update_data = {}
                if "first_name" in profile_data:
                    update_data["prenom"] = profile_data["first_name"]
                if "last_name" in profile_data:
                    update_data["nom"] = profile_data["last_name"]
                
                if not update_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Aucune donnée à mettre à jour"
                    )
                
                profile_response = await client.patch(
                    f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}",
                    headers=self.headers,
                    json=update_data
                )
                
                if profile_response.status_code != 204:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Erreur lors de la mise à jour du profil"
                    )
                
                # Récupérer le profil mis à jour
                return await self.get_user_profile(user_id)
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erreur de connexion au service d'authentification"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )
    
    async def logout_user(self, user_id: str) -> bool:
        """Déconnecter un utilisateur en révoquant ses tokens"""
        return jwt_auth.revoke_refresh_token(user_id)
    
    async def reset_password(self, email: str) -> bool:
        """Demander une réinitialisation de mot de passe"""
        try:
            async with httpx.AsyncClient() as client:
                reset_response = await client.post(
                    f"{self.supabase_url}/auth/v1/recover",
                    headers=self.headers,
                    json={"email": email}
                )
                
                if reset_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Erreur lors de la demande de réinitialisation"
                    )
                
                return True
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erreur de connexion au service d'authentification"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur interne: {str(e)}"
            )

# Instance globale
auth_service = AuthService() 