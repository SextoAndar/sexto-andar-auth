# app/auth/jwt_handler.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from jwt import InvalidTokenError

from app.settings import settings

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except InvalidTokenError:
        return None

def get_token_expiry() -> timedelta:
    """
    Get the default token expiration time
    
    Returns:
        Token expiration timedelta
    """
    return timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
