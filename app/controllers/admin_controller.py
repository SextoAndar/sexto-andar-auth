# app/controllers/admin_controller.py
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
import logging
import math

from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.auth.dependencies import get_current_admin_user
from app.models.account import Account, RoleEnum
from app.repositories.account_repository import AccountRepository
from app.dtos.admin_dto import (
    UpdateUserRequest,
    UserListItem,
    PaginatedUsersResponse,
    SearchUsersResponse
)
from app.dtos.auth_dto import AuthUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/admin", tags=["admin"])


@router.get("/users", response_model=PaginatedUsersResponse, summary="List all users (US25)")
async def list_users(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Page size (max 100)"),
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all USER accounts with pagination (US25).
    
    **Admin only endpoint** - Requires ADMIN role.
    
    Features:
    - Paginated results (default: 10 per page)
    - Returns only accounts with role = USER
    - Excludes PROPERTY_OWNER and ADMIN accounts
    
    Returns:
    - List of users
    - Total count
    - Pagination metadata
    """
    logger.info(f"Admin '{current_admin.username}' listing users (page={page}, size={size})")
    
    account_repo = AccountRepository(db)
    users, total = account_repo.get_all_paginated(page=page, size=size, role_filter=RoleEnum.USER)
    
    pages = math.ceil(total / size) if total > 0 else 0
    
    return PaginatedUsersResponse(
        items=[UserListItem(
            id=user.id,
            username=user.username,
            fullName=user.fullName,
            email=user.email,
            phoneNumber=user.phoneNumber,
            role=user.role.value,
            createdAt=user.created_at,
            isActive=True
        ) for user in users],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/property-owners", response_model=PaginatedUsersResponse, summary="List all property owners (US28)")
async def list_property_owners(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Page size (max 100)"),
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all PROPERTY_OWNER accounts with pagination (US28).
    
    **Admin only endpoint** - Requires ADMIN role.
    
    Features:
    - Paginated results (default: 10 per page)
    - Returns only accounts with role = PROPERTY_OWNER
    - Excludes USER and ADMIN accounts
    
    Returns:
    - List of property owners
    - Total count
    - Pagination metadata
    """
    logger.info(f"Admin '{current_admin.username}' listing property owners (page={page}, size={size})")
    
    account_repo = AccountRepository(db)
    owners, total = account_repo.get_all_paginated(page=page, size=size, role_filter=RoleEnum.PROPERTY_OWNER)
    
    pages = math.ceil(total / size) if total > 0 else 0
    
    return PaginatedUsersResponse(
        items=[UserListItem(
            id=owner.id,
            username=owner.username,
            fullName=owner.fullName,
            email=owner.email,
            phoneNumber=owner.phoneNumber,
            role=owner.role.value,
            createdAt=owner.created_at,
            isActive=True
        ) for owner in owners],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.put("/users/{user_id}", response_model=AuthUser, summary="Update user (US26)")
async def update_user(
    user_id: str,
    update_data: UpdateUserRequest,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update any user's profile information (US26).
    
    **Admin only endpoint** - Requires ADMIN role.
    
    Features:
    - Admin can update any USER account
    - All fields are optional
    - No current password required (admin override)
    - Email uniqueness is validated
    - Password must be at least 8 characters
    - Cannot update ADMIN accounts (use admin-specific endpoints)
    
    Security:
    - Requires admin authentication
    - Logs all changes for audit trail
    - Prevents admin modification via this endpoint
    """
    auth_service = AuthService(db)
    updated_user = auth_service.admin_update_user(user_id, update_data, current_admin)
    return AuthUser.model_validate(updated_user)


@router.put("/property-owners/{owner_id}", response_model=AuthUser, summary="Update property owner (US29)")
async def update_property_owner(
    owner_id: str,
    update_data: UpdateUserRequest,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update any property owner's profile information (US29).
    
    **Admin only endpoint** - Requires ADMIN role.
    
    Features:
    - Admin can update any PROPERTY_OWNER account
    - All fields are optional
    - No current password required (admin override)
    - Email uniqueness is validated
    - Password must be at least 8 characters
    
    Security:
    - Requires admin authentication
    - Logs all changes for audit trail
    """
    auth_service = AuthService(db)
    updated_owner = auth_service.admin_update_user(owner_id, update_data, current_admin)
    return AuthUser.model_validate(updated_owner)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (US27)")
async def delete_user(
    user_id: str,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user account (US27).
    
    **Admin only endpoint** - Requires ADMIN role.
    
    Features:
    - Permanently deletes USER accounts
    - Cannot delete ADMIN accounts via this endpoint
    - Logs deletion for audit trail
    
    Security:
    - Requires admin authentication
    - Prevents deletion of admin accounts
    - Logs all deletions
    
    Returns 204 No Content on success.
    """
    auth_service = AuthService(db)
    await auth_service.admin_delete_user(user_id, current_admin)
    return None


@router.delete("/property-owners/{owner_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete property owner (US30)")
async def delete_property_owner(
    owner_id: str,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a property owner account (US30).
    
    **Admin only endpoint** - Requires ADMIN role.
    
    Features:
    - Permanently deletes PROPERTY_OWNER accounts
    - Cannot delete ADMIN accounts via this endpoint
    - Logs deletion for audit trail
    
    Security:
    - Requires admin authentication
    - Prevents deletion of admin accounts
    - Logs all deletions
    
    Returns 204 No Content on success.
    """
    auth_service = AuthService(db)
    await auth_service.admin_delete_user(owner_id, current_admin)
    return None


@router.get("/search", response_model=SearchUsersResponse, summary="Search users by email (US33)")
async def search_users_by_email(
    email: str = Query(..., min_length=1, description="Email to search (partial match)"),
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Search users and property owners by email (US33).
    
    **Admin only endpoint** - Requires ADMIN role.
    
    Features:
    - Case-insensitive partial email search
    - Searches across all roles (USER, PROPERTY_OWNER, ADMIN)
    - Returns all matching accounts
    
    Example:
    - Search "john" returns john@example.com, johnny@test.com, etc.
    
    Security:
    - Requires admin authentication
    - Logs all searches
    """
    logger.info(f"Admin '{current_admin.username}' searching users by email: '{email}'")
    
    account_repo = AccountRepository(db)
    users = account_repo.search_by_email(email)
    
    logger.info(f"Search returned {len(users)} results")
    
    return SearchUsersResponse(
        users=[UserListItem(
            id=user.id,
            username=user.username,
            fullName=user.fullName,
            email=user.email,
            phoneNumber=user.phoneNumber,
            role=user.role.value,
            createdAt=user.created_at,
            isActive=True
        ) for user in users],
        total=len(users)
    )
