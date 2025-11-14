# app/dtos/admin_dto.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UpdateUserRequest(BaseModel):
    """Admin update user request DTO (US26, US29)"""
    fullName: Optional[str] = Field(None, min_length=2, max_length=100)
    phoneNumber: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, description="New password (no current password needed for admin)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fullName": "Updated Name",
                "phoneNumber": "+5511999998888",
                "email": "newemail@example.com",
                "password": "NewPassword123!"
            }
        }


class UserListItem(BaseModel):
    """User list item DTO"""
    id: UUID
    username: str
    fullName: str
    email: EmailStr
    phoneNumber: Optional[str] = None
    role: str
    createdAt: datetime
    isActive: bool = True

    class Config:
        from_attributes = True


class PaginatedUsersResponse(BaseModel):
    """Paginated users response DTO (US25, US28)"""
    items: List[UserListItem]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "johndoe",
                        "fullName": "John Doe",
                        "email": "john.doe@example.com",
                        "phoneNumber": "+5511999999999",
                        "role": "USER",
                        "createdAt": "2025-01-15T10:30:00Z",
                        "isActive": True
                    }
                ],
                "total": 50,
                "page": 1,
                "size": 10,
                "pages": 5
            }
        }


class SearchUsersResponse(BaseModel):
    """Search users response DTO (US33)"""
    users: List[UserListItem]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "johndoe",
                        "fullName": "John Doe",
                        "email": "john.doe@example.com",
                        "phoneNumber": "+5511999999999",
                        "role": "USER",
                        "createdAt": "2025-01-15T10:30:00Z",
                        "isActive": True
                    }
                ],
                "total": 1
            }
        }
