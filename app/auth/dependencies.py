# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Cookie
from typing import Optional
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.connection import get_db
from app.models.account import Account
from app.auth.jwt_handler import verify_token

security = HTTPBearer(auto_error=False)

async def get_current_user(
    header_credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    cookie_credentials: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> Account:
    """
    Get current authenticated user from JWT token.
    Prioritizes 'Authorization: Bearer' header, falls back to 'access_token' cookie.
    
    Args:
        header_credentials: HTTP Authorization credentials (Bearer token).
        cookie_credentials: JWT token from 'access_token' cookie.
        db: Database session.
        
    Returns:
        Current authenticated user.
        
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    access_token = None
    if header_credentials:
        access_token = header_credentials.credentials
    elif cookie_credentials:
        access_token = cookie_credentials

    if not access_token:
        raise credentials_exception

    # Verify token
    payload = verify_token(access_token)
    if not payload:
        raise credentials_exception
    
    # Get user ID from token
    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    # Get user from database
    user = db.query(Account).filter(Account.id == user_id).first()
    if not user:
        raise credentials_exception
    
    return user

async def get_current_admin_user(
    current_user: Account = Depends(get_current_user)
) -> Account:
    """
    Get current admin user (requires ADMIN role)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_active_user(
    current_user: Account = Depends(get_current_user)
) -> Account:
    """
    Get current active user (any authenticated user)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
    """
    return current_user
