# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Cookie
from typing import Optional, Annotated
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.account import Account, RoleEnum
from app.auth.jwt_handler import verify_token

async def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    db: Session = Depends(get_db)
) -> Account:
    """
    Get current authenticated user from JWT cookie
    
    Args:
        access_token: JWT token from cookie
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
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
