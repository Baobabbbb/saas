import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib

# Configuration JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Token court pour la sécurité
REFRESH_TOKEN_EXPIRE_DAYS = 30   # Token long pour le refresh

# Stockage des refresh tokens (en production, utiliser Redis ou base de données)
refresh_tokens = {}

class JWTAuth:
    def __init__(self):
        self.secret = JWT_SECRET
        self.algorithm = JWT_ALGORITHM
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Créer un access token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Créer un refresh token JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        
        # Stocker le refresh token (en production, utiliser Redis/DB)
        user_id = data.get("sub")
        if user_id:
            refresh_tokens[user_id] = encoded_jwt
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Vérifier un token JWT"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Rafraîchir un access token avec un refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=[self.algorithm])
            
            # Vérifier que c'est bien un refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide - type incorrect"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide - utilisateur manquant"
                )
            
            # Vérifier que le refresh token est stocké
            stored_token = refresh_tokens.get(user_id)
            if not stored_token or stored_token != refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token invalide"
                )
            
            # Créer un nouveau access token
            new_access_token = self.create_access_token(
                data={"sub": user_id, "email": payload.get("email")}
            )
            
            return {
                "access_token": new_access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except jwt.ExpiredSignatureError:
            # Supprimer le refresh token expiré
            if user_id in refresh_tokens:
                del refresh_tokens[user_id]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expiré"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalide"
            )
    
    def revoke_refresh_token(self, user_id: str) -> bool:
        """Révoquer un refresh token"""
        if user_id in refresh_tokens:
            del refresh_tokens[user_id]
            return True
        return False
    
    def create_tokens_for_user(self, user_id: str, email: str) -> Dict[str, str]:
        """Créer access et refresh tokens pour un utilisateur"""
        access_token = self.create_access_token(
            data={"sub": user_id, "email": email}
        )
        refresh_token = self.create_refresh_token(
            data={"sub": user_id, "email": email}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

# Instance globale
jwt_auth = JWTAuth()

# Middleware pour vérifier les tokens
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Schéma d'authentification invalide"
                )
            
            payload = jwt_auth.verify_token(credentials.credentials)
            
            # Vérifier que c'est un access token
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide - type incorrect"
                )
            
            request.state.user = payload
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token d'authentification invalide"
            )

# Fonction utilitaire pour obtenir l'utilisateur actuel
def get_current_user(request):
    """Obtenir l'utilisateur actuel depuis le request state"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié"
        )
    return request.state.user 