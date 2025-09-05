# app/services/auth_service.py
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.account import Account, RoleEnum
from app.repositories.account_repository import AccountRepository
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.dtos.auth_dto import LoginRequest, RegisterUserRequest, RegisterPropertyOwnerRequest

class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
    
    def authenticate_user(self, login_data: LoginRequest) -> Optional[Account]:
        """
        Authenticate user with username/password
        
        Args:
            login_data: Login credentials
            
        Returns:
            Authenticated user or None
        """
        user = self.account_repo.get_by_username(login_data.username)
        
        if not user:
            return None
            
        if not verify_password(login_data.password, user.password):
            return None
            
        return user
    
    def create_user_token(self, user: Account) -> str:
        """
        Create JWT token for user
        
        Args:
            user: Authenticated user
            
        Returns:
            JWT token
        """
        token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
        return create_access_token(data=token_data)
    
    def register_user(self, register_data: RegisterUserRequest) -> Account:
        """
        Register a new USER
        
        Args:
            register_data: User registration data
            
        Returns:
            Created user account
            
        Raises:
            HTTPException: If username/email already exists
        """
        # Check if username exists
        if self.account_repo.username_exists(register_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email exists
        if self.account_repo.email_exists(register_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new user account
        hashed_password = hash_password(register_data.password)
        
        new_user = Account(
            username=register_data.username.lower(),
            fullName=register_data.fullName,
            email=register_data.email.lower(),
            phoneNumber=register_data.phoneNumber,
            password=hashed_password,
            role=RoleEnum.USER
        )
        
        return self.account_repo.create(new_user)
    
    def register_property_owner(self, register_data: RegisterPropertyOwnerRequest) -> Account:
        """
        Register a new PROPERTY_OWNER
        
        Args:
            register_data: Property owner registration data
            
        Returns:
            Created property owner account
            
        Raises:
            HTTPException: If username/email already exists
        """
        # Check if username exists
        if self.account_repo.username_exists(register_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email exists
        if self.account_repo.email_exists(register_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new property owner account
        hashed_password = hash_password(register_data.password)
        
        new_owner = Account(
            username=register_data.username.lower(),
            fullName=register_data.fullName,
            email=register_data.email.lower(),
            phoneNumber=register_data.phoneNumber,
            password=hashed_password,
            role=RoleEnum.PROPERTY_OWNER
        )
        
        return self.account_repo.create(new_owner)
