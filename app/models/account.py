# app/models/account.py
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy_utils import EmailType, PhoneNumberType
from datetime import datetime, timezone
import uuid
import re
import enum

from app.database.connection import BaseModel

class RoleEnum(enum.Enum):
    """Enum for system roles"""
    USER = "user"
    PROPERTY_OWNER = "property_owner"

class Account(BaseModel):
    """
    Account class for system users
    Role defines whether it's a regular user or property owner
    """
    __tablename__ = "accounts"
    
    # Attributes
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )
    
    username = Column(
        String(50), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    fullName = Column(
        String(100), 
        nullable=False
    )
    
    phoneNumber = Column(
        String(20),
        nullable=False
    )
    
    email = Column(
        EmailType, 
        unique=True, 
        nullable=False,
        index=True
    )
    
    password = Column(
        String(255), 
        nullable=False
    )
    
    # Role field to distinguish user and property owner
    role = Column(
        Enum(RoleEnum), 
        nullable=False,
        index=True
    )
    
    # Timestamps
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Validations
    @validates('email')
    def validate_email(self, key, email):
        """Additional email validation (EmailType already validates format)"""
        if not email:
            raise ValueError("Email is required")
        
        # EmailType already validates format automatically
        # Here we can add business-specific validations
        return email.lower() if isinstance(email, str) else email
    
    @validates('username')
    def validate_username(self, key, username):
        """Username validation"""
        if not username:
            raise ValueError("Username is required")
        
        if len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        
        # Only letters, numbers and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("Username must contain only letters, numbers and underscore")
        
        return username.lower()
    
    @validates('phoneNumber')
    def validate_phone(self, key, phone):
        """Phone number validation"""
        if not phone:
            raise ValueError("Phone number is required")
        
        # Remove non-numeric characters for validation
        clean_phone = re.sub(r'\D', '', phone)
        if len(clean_phone) < 10 or len(clean_phone) > 15:
            raise ValueError("Phone number must have between 10 and 15 digits")
        
        return phone
    
    @validates('password')
    def validate_password(self, key, password):
        """Password validation"""
        if not password:
            raise ValueError("Password is required")
        
        if len(password) < 8:
            raise ValueError("Password must have at least 8 characters")
        
        return password
    
    @validates('role')
    def validate_role(self, key, role):
        """Role validation"""
        if not role:
            raise ValueError("Role is required")
        
        if isinstance(role, str):
            # Convert string to enum
            try:
                return RoleEnum(role)
            except ValueError:
                raise ValueError(f"Role must be '{RoleEnum.USER.value}' or '{RoleEnum.PROPERTY_OWNER.value}'")
        
        return role
    
    # Convenience methods to check role
    def is_user(self) -> bool:
        """Check if it's a regular user"""
        return self.role == RoleEnum.USER
    
    def is_property_owner(self) -> bool:
        """Check if it's a property owner"""
        return self.role == RoleEnum.PROPERTY_OWNER
    
    def get_role_display(self) -> str:
        """Returns the role name for display"""
        role_names = {
            RoleEnum.USER: "User",
            RoleEnum.PROPERTY_OWNER: "Property Owner"
        }
        return role_names.get(self.role, "Unknown")
    
    def __repr__(self):
        return f"<Account(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    def __str__(self):
        return f"{self.fullName} ({self.username}) - {self.get_role_display()}"