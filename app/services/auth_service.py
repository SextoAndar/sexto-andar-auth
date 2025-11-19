# app/services/auth_service.py
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.account import Account, RoleEnum
from app.repositories.account_repository import AccountRepository
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.dtos.auth_dto import (
    LoginRequest, 
    RegisterUserRequest, 
    RegisterPropertyOwnerRequest, 
    RegisterAdminRequest,
    UpdateProfileRequest
)
from app.dtos.admin_dto import UpdateUserRequest

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

    def update_profile(self, current_user: Account, update_data: UpdateProfileRequest) -> Account:
        """
        Update user profile (name, phone, email, password)
        
        Args:
            current_user: The authenticated user
            update_data: Profile update data
            
        Returns:
            Updated account
            
        Raises:
            HTTPException: If validation fails
        """
        logger.info(f"Profile update attempt for user '{current_user.username}' (ID: {current_user.id})")
        
        # Check if there's anything to update
        if not any([
            update_data.fullName,
            update_data.phoneNumber,
            update_data.email,
            update_data.newPassword
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # If changing email or password, current password is required
        if (update_data.email or update_data.newPassword) and not update_data.currentPassword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to change email or password"
            )
        
        # Verify current password if provided
        if update_data.currentPassword:
            if not verify_password(update_data.currentPassword, current_user.password):
                logger.warning(f"Profile update failed: incorrect password for user '{current_user.username}'")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )
        
        # Update full name
        if update_data.fullName:
            current_user.fullName = update_data.fullName
            logger.info(f"Updated fullName for user '{current_user.username}'")
        
        # Update phone number
        if update_data.phoneNumber:
            current_user.phoneNumber = update_data.phoneNumber
            logger.info(f"Updated phoneNumber for user '{current_user.username}'")
        
        # Update email (check uniqueness)
        if update_data.email:
            email_lower = update_data.email.lower()
            if email_lower != current_user.email.lower():
                # Check if new email already exists
                existing_user = self.account_repo.get_by_email(email_lower)
                if existing_user and existing_user.id != current_user.id:
                    logger.warning(f"Profile update failed: email '{email_lower}' already exists")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
                current_user.email = email_lower
                logger.info(f"Updated email for user '{current_user.username}'")
        
        # Update password
        if update_data.newPassword:
            current_user.password = hash_password(update_data.newPassword)
            logger.info(f"Updated password for user '{current_user.username}'")
        
        # Save changes
        updated_user = self.account_repo.update(current_user)
        
        logger.info(f"Profile updated successfully for user '{current_user.username}' (ID: {current_user.id})")
        
        return updated_user
    
    def admin_update_user(self, user_id: str, update_data: UpdateUserRequest, admin: Account) -> Account:
        """
        Admin updates any user's profile (US26, US29)
        
        Args:
            user_id: Target user ID
            update_data: Profile update data
            admin: The admin performing the update
            
        Returns:
            Updated account
            
        Raises:
            HTTPException: If validation fails
        """
        logger.info(f"Admin '{admin.username}' updating user ID '{user_id}'")
        
        # Get target user
        target_user = self.account_repo.get_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if there's anything to update
        if not any([
            update_data.fullName,
            update_data.phoneNumber,
            update_data.email,
            update_data.password
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update full name
        if update_data.fullName:
            target_user.fullName = update_data.fullName
            logger.info(f"Updated fullName for user '{target_user.username}'")
        
        # Update phone number
        if update_data.phoneNumber:
            target_user.phoneNumber = update_data.phoneNumber
            logger.info(f"Updated phoneNumber for user '{target_user.username}'")
        
        # Update email (check uniqueness)
        if update_data.email:
            email_lower = update_data.email.lower()
            if email_lower != target_user.email.lower():
                if self.account_repo.email_exists(email_lower, exclude_id=str(target_user.id)):
                    logger.warning(f"Admin update failed: email '{email_lower}' already exists")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
                target_user.email = email_lower
                logger.info(f"Updated email for user '{target_user.username}'")
        
        # Update password (admin doesn't need current password)
        if update_data.password:
            target_user.password = hash_password(update_data.password)
            logger.info(f"Updated password for user '{target_user.username}'")
        
        # Save changes
        updated_user = self.account_repo.update(target_user)
        
        logger.info(
            f"User '{target_user.username}' (ID: {target_user.id}) updated successfully "
            f"by admin '{admin.username}' (ID: {admin.id})"
        )
        
        return updated_user
    
    def admin_delete_user(self, user_id: str, admin: Account) -> None:
        """
        Admin deletes a user account (US27, US30)
        
        Args:
            user_id: Target user ID
            admin: The admin performing the deletion
            
        Raises:
            HTTPException: If validation fails
        """
        logger.info(f"Admin '{admin.username}' attempting to delete user ID '{user_id}'")
        
        # Get target user
        target_user = self.account_repo.get_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deletion of admins (use dedicated admin deletion endpoint)
        if target_user.is_admin():
            logger.warning(
                f"Admin '{admin.username}' attempted to delete admin user '{target_user.username}' "
                f"via user deletion endpoint"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete admin users via this endpoint. Use admin deletion endpoint instead."
            )
        
        # Delete the user
        self.account_repo.delete(target_user)
        
        logger.info(
            f"User '{target_user.username}' (ID: {target_user.id}, Role: {target_user.role.value}) "
            f"deleted successfully by admin '{admin.username}' (ID: {admin.id})"
        )
    
    def upload_profile_picture(
        self, 
        user: Account, 
        image_data: bytes, 
        content_type: str
    ) -> Account:
        """
        Upload or update user profile picture
        
        Args:
            user: The account to update
            image_data: Binary image data
            content_type: MIME type of the image (e.g., 'image/jpeg')
            
        Returns:
            Updated account
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate image size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if len(image_data) > max_size:
            logger.warning(f"Profile picture upload failed for user '{user.username}': image too large ({len(image_data)} bytes)")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image size exceeds maximum allowed size of {max_size // (1024 * 1024)}MB"
            )
        
        # Validate content type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if content_type.lower() not in allowed_types:
            logger.warning(f"Profile picture upload failed for user '{user.username}': invalid content type '{content_type}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Update user profile picture
        user.profile_picture = image_data
        user.profile_picture_content_type = content_type
        
        updated_user = self.account_repo.update(user)
        
        logger.info(
            f"Profile picture uploaded successfully for user '{user.username}' "
            f"(ID: {user.id}, Size: {len(image_data)} bytes, Type: {content_type})"
        )
        
        return updated_user
    
    def get_profile_picture(self, user_id: str) -> tuple[bytes, str]:
        """
        Get user profile picture
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Tuple of (image_data, content_type)
            
        Raises:
            HTTPException: If user not found or no profile picture
        """
        user = self.account_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.profile_picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has no profile picture"
            )
        
        return (user.profile_picture, user.profile_picture_content_type or 'image/jpeg')
    
    def delete_profile_picture(self, user: Account) -> Account:
        """
        Delete user profile picture
        
        Args:
            user: The account to update
            
        Returns:
            Updated account
        """
        user.profile_picture = None
        user.profile_picture_content_type = None
        
        updated_user = self.account_repo.update(user)
        
        logger.info(f"Profile picture deleted for user '{user.username}' (ID: {user.id})")
        
        return updated_user






