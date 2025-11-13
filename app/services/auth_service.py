# app/services/auth_service.py
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.account import Account, RoleEnum
from app.repositories.account_repository import AccountRepository
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.dtos.auth_dto import LoginRequest, RegisterUserRequest, RegisterPropertyOwnerRequest, RegisterAdminRequest

logger = logging.getLogger(__name__)

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
    
    def register_admin(self, register_data: RegisterAdminRequest, creator_admin: Account) -> Account:
        """
        Register a new ADMIN (only callable by existing admin)
        
        Args:
            register_data: Admin registration data
            creator_admin: The admin creating this new admin
            
        Returns:
            Created admin account
            
        Raises:
            HTTPException: If username/email already exists
        """
        # Log audit trail
        logger.info(
            f"Admin creation attempt by '{creator_admin.username}' "
            f"for new admin '{register_data.username}'"
        )
        
        # Check if username exists
        if self.account_repo.username_exists(register_data.username):
            logger.warning(
                f"Admin creation failed: username '{register_data.username}' already exists"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email exists
        if self.account_repo.email_exists(register_data.email):
            logger.warning(
                f"Admin creation failed: email '{register_data.email}' already exists"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new admin account
        hashed_password = hash_password(register_data.password)
        
        new_admin = Account(
            username=register_data.username.lower(),
            fullName=register_data.fullName,
            email=register_data.email.lower(),
            phoneNumber=register_data.phoneNumber,
            password=hashed_password,
            role=RoleEnum.ADMIN
        )
        
        created_admin = self.account_repo.create(new_admin)
        
        logger.info(
            f"Admin '{created_admin.username}' (ID: {created_admin.id}) "
            f"created successfully by '{creator_admin.username}' (ID: {creator_admin.id})"
        )
        
        return created_admin

    def get_user_by_id(self, user_id: str) -> Account:
        """
        Retrieve a user/account by UUID

        Args:
            user_id: UUID string of the user

        Returns:
            Account instance

        Raises:
            HTTPException: If user not found
        """
        user = self.account_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    def delete_admin(self, admin_id: str, deleter_admin: Account) -> None:
        """
        Delete an ADMIN account (only callable by existing admin)
        
        Args:
            admin_id: UUID of the admin to delete
            deleter_admin: The admin performing the deletion
            
        Raises:
            HTTPException: If validation fails (self-delete, last admin, not found, not an admin)
        """
        # Log audit trail
        logger.info(
            f"Admin deletion attempt by '{deleter_admin.username}' "
            f"for admin ID '{admin_id}'"
        )
        
        # Prevent self-deletion
        if str(deleter_admin.id) == admin_id:
            logger.warning(
                f"Admin '{deleter_admin.username}' attempted to delete themselves"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own admin account"
            )
        
        # Get the target admin
        target_admin = self.account_repo.get_by_id(admin_id)
        
        if not target_admin:
            logger.warning(f"Admin deletion failed: account ID '{admin_id}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin account not found"
            )
        
        # Verify target is actually an admin
        if not target_admin.is_admin():
            logger.warning(
                f"Admin deletion failed: account '{target_admin.username}' "
                f"is not an admin (role: {target_admin.role.value})"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target account is not an admin"
            )
        
        # Prevent deletion of last admin
        total_admins = self.account_repo.count_admins()
        if total_admins <= 1:
            logger.warning(
                f"Admin deletion failed: cannot delete last admin in the system"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin account in the system"
            )
        
        # Delete the admin
        self.account_repo.delete(target_admin)
        
        logger.info(
            f"Admin '{target_admin.username}' (ID: {target_admin.id}) "
            f"deleted successfully by '{deleter_admin.username}' (ID: {deleter_admin.id})"
        )

