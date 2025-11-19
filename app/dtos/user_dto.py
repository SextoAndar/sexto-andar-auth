from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserInfoResponse(BaseModel):
    id: UUID
    username: str
    fullName: str
    email: EmailStr
    phoneNumber: Optional[str] = None
    role: str
    createdAt: datetime
    isActive: bool = True
    hasProfilePicture: bool = False

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "fullName": "John Doe",
                "email": "john.doe@example.com",
                "phoneNumber": "+5511999999999",
                "role": "USER",
                "createdAt": "2025-01-15T10:30:00Z",
                "isActive": True
            }
        }

    @classmethod
    def from_account(cls, account):
        return cls(
            id=account.id,
            username=account.username,
            fullName=account.fullName,
            email=account.email,
            phoneNumber=account.phoneNumber,
            role=account.role.value if hasattr(account.role, 'value') else account.role,
            createdAt=account.created_at,
            isActive=True,
            hasProfilePicture=account.profile_picture is not None
        )
