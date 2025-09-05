# app/services/account_service.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.account import Account, RoleEnum
from app.repositories.account_repository import AccountRepository
from app.auth.password_handler import hash_password, verify_password
from app.dtos.account_dto import UpdateAccountRequest, ChangePasswordRequest, AccountListResponse, AccountResponse

class AccountService:
    """Service for account management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
    
    def get_all_non_admin_accounts(self, page: int = 1, size: int = 10) -> AccountListResponse:
        """
        Get all non-admin accounts (USER and PROPERTY_OWNER only) with pagination
        
        Args:
            page: Page number (1-based)
            size: Page size
            
        Returns:
            Paginated account list
        """
        accounts, total = self.account_repo.get_non_admins_paginated(page, size)
        
        account_responses = [AccountResponse.model_validate(account) for account in accounts]
        
        return AccountListResponse(
            accounts=account_responses,
            total=total,
            page=page,
            size=size
        )
    
    def get_account_by_id(self, account_id: str) -> AccountResponse:
        """
        Get account by ID
        
        Args:
            account_id: Account ID
            
        Returns:
            Account details
            
        Raises:
            HTTPException: If account not found or is admin
        """
        account = self.account_repo.get_by_id(account_id)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Don't allow access to admin accounts
        if account.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access admin accounts"
            )
        
        return AccountResponse.model_validate(account)
    
    def update_account(self, account_id: str, update_data: UpdateAccountRequest) -> AccountResponse:
        """
        Update account information
        
        Args:
            account_id: Account ID
            update_data: Updated account data
            
        Returns:
            Updated account
            
        Raises:
            HTTPException: If account not found, is admin, or validation fails
        """
        account = self.account_repo.get_by_id(account_id)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Don't allow updating admin accounts
        if account.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update admin accounts"
            )
        
        # Update fields if provided
        if update_data.fullName is not None:
            account.fullName = update_data.fullName
        
        if update_data.email is not None:
            # Check if email already exists for another user
            if self.account_repo.email_exists(update_data.email, exclude_id=str(account.id)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            account.email = update_data.email.lower()
        
        if update_data.phoneNumber is not None:
            account.phoneNumber = update_data.phoneNumber
        
        updated_account = self.account_repo.update(account)
        return AccountResponse.model_validate(updated_account)
    
    def delete_account(self, account_id: str) -> None:
        """
        Delete account
        
        Args:
            account_id: Account ID
            
        Raises:
            HTTPException: If account not found or is admin
        """
        account = self.account_repo.get_by_id(account_id)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Don't allow deleting admin accounts
        if account.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete admin accounts"
            )
        
        self.account_repo.delete(account)
    
    def change_user_password(self, account_id: str, password_data: ChangePasswordRequest) -> None:
        """
        Change user password
        
        Args:
            account_id: Account ID
            password_data: Password change data
            
        Raises:
            HTTPException: If account not found, is admin, or current password is wrong
        """
        account = self.account_repo.get_by_id(account_id)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Don't allow changing admin passwords
        if account.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change admin passwords"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, account.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        account.password = hash_password(password_data.new_password)
        self.account_repo.update(account)
