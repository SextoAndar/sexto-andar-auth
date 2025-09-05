# app/dtos/account_dto.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union
from datetime import datetime
import uuid

class AccountResponse(BaseModel):
    """Account response DTO"""
    id: Union[str, uuid.UUID]
    username: str
    fullName: str
    email: str
    phoneNumber: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        """Override model_dump to convert UUID to string"""
        data = super().model_dump(**kwargs)
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        return data

class AccountListResponse(BaseModel):
    """Account list response DTO"""
    accounts: List[AccountResponse]
    total: int
    page: int
    size: int

class UpdateAccountRequest(BaseModel):
    """Update account request DTO"""
    fullName: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = Field(None, min_length=10, max_length=20)
    
class ChangePasswordRequest(BaseModel):
    """Change password request DTO"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
