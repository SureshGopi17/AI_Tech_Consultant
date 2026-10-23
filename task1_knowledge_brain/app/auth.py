"""
JWT Authentication Module for Task 1: The Knowledge Brain.
Provides:
- Cryptographic JSON Web Token (JWT) generation with HS256 algorithm
- Token verification and payload extraction
- FastAPI dependency for Bearer token extraction and authentication
- Claims: sub, email, name, role, active_dashboard_id, exp, iat
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.models import UserSession

# HTTP Bearer scheme with auto_error=False to allow flexible handling
bearer_scheme = HTTPBearer(auto_error=False)

def create_access_token(user: UserSession, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a cryptographically signed JWT access token (HS256)
    with standard and custom claims.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "active_dashboard_id": user.active_dashboard_id,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "ai-tech-consultant",
        "aud": "knowledge-brain-users"
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT access token.
    Raises HTTPException(401) on expiration or signature errors.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience="knowledge-brain-users"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token has expired. Please authenticate again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate JWT credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> Optional[UserSession]:
    """
    Extracts authenticated UserSession if Bearer token is provided.
    Returns None if no token is passed.
    """
    if not credentials or not credentials.credentials:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)
    
    from app.kb_manager import kb_manager
    user = kb_manager.get_user_by_email(payload.get("email", ""))
    if user:
        return user

    # Fallback to session constructed from JWT claims
    return UserSession(
        id=payload.get("sub", "user-jwt"),
        name=payload.get("name", "Authenticated User"),
        email=payload.get("email", "user@example.com"),
        role=payload.get("role", "AI Consultant"),
        active_dashboard_id=payload.get("active_dashboard_id", "dash-bd-prod-01"),
        created_at=datetime.fromtimestamp(payload.get("iat", time.time()), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )

def require_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> UserSession:
    """
    Strict FastAPI dependency for endpoints requiring verified JWT authentication.
    Raises 401 Unauthorized if token is missing or invalid.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Expected 'Authorization: Bearer <JWT_TOKEN>'",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return get_current_user_optional(credentials)
