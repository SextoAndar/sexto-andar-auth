# app/dtos/auth_dto.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union, Dict, Any
from datetime import datetime
import uuid

class LoginRequest(BaseModel):
    """Login request DTO"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    """Login response DTO"""
    access_token: str
    token_type: str = "bearer"
    user: dict

class RegisterUserRequest(BaseModel):
    """User registration request DTO"""
    username: str = Field(..., min_length=3, max_length=50)
    fullName: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phoneNumber: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)

class RegisterPropertyOwnerRequest(BaseModel):
    """Property owner registration request DTO"""
    username: str = Field(..., min_length=3, max_length=50)
    fullName: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phoneNumber: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)

class AuthUser(BaseModel):
    """Authenticated user DTO"""
    id: Union[str, uuid.UUID]
    username: str
    fullName: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        """Override model_dump to convert UUID to string"""
        data = super().model_dump(**kwargs)
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        return data

class IntrospectRequest(BaseModel):
    """Request DTO for token introspection"""
    token: str = Field(..., min_length=10)

class IntrospectResponse(BaseModel):
    """Response DTO for token introspection"""
    active: bool
    claims: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
