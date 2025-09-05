# app/repositories/account_repository.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.account import Account, RoleEnum

class AccountRepository:
    """Repository for Account operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_by_username(self, username: str) -> Optional[Account]:
        """Get account by username"""
        return self.db.query(Account).filter(Account.username == username.lower()).first()
    
    def get_by_email(self, email: str) -> Optional[Account]:
        """Get account by email"""
        return self.db.query(Account).filter(Account.email == email.lower()).first()
    
    def create(self, account: Account) -> Account:
        """Create new account"""
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def update(self, account: Account) -> Account:
        """Update existing account"""
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def delete(self, account: Account) -> None:
        """Delete account"""
        self.db.delete(account)
        self.db.commit()
    
    def get_all_paginated(self, page: int = 1, size: int = 10, role_filter: Optional[RoleEnum] = None) -> Tuple[List[Account], int]:
        """
        Get all accounts with pagination
        
        Args:
            page: Page number (1-based)
            size: Page size
            role_filter: Optional role filter
            
        Returns:
            Tuple of (accounts_list, total_count)
        """
        query = self.db.query(Account)
        
        if role_filter:
            query = query.filter(Account.role == role_filter)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        offset = (page - 1) * size
        accounts = query.offset(offset).limit(size).all()
        
        return accounts, total
    
    def get_non_admins_paginated(self, page: int = 1, size: int = 10) -> Tuple[List[Account], int]:
        """
        Get all non-admin accounts with pagination (USER and PROPERTY_OWNER only)
        
        Args:
            page: Page number (1-based)
            size: Page size
            
        Returns:
            Tuple of (accounts_list, total_count)
        """
        query = self.db.query(Account).filter(
            Account.role.in_([RoleEnum.USER, RoleEnum.PROPERTY_OWNER])
        )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        offset = (page - 1) * size
        accounts = query.offset(offset).limit(size).all()
        
        return accounts, total
    
    def username_exists(self, username: str, exclude_id: Optional[str] = None) -> bool:
        """Check if username exists (optionally excluding a specific account)"""
        query = self.db.query(Account).filter(Account.username == username.lower())
        if exclude_id:
            query = query.filter(Account.id != exclude_id)
        return query.first() is not None
    
    def email_exists(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """Check if email exists (optionally excluding a specific account)"""
        query = self.db.query(Account).filter(Account.email == email.lower())
        if exclude_id:
            query = query.filter(Account.id != exclude_id)
        return query.first() is not None
