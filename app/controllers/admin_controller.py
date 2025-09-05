# app/controllers/admin_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.services.account_service import AccountService
from app.dtos.account_dto import AccountListResponse, AccountResponse, UpdateAccountRequest, ChangePasswordRequest
from app.auth.dependencies import get_current_admin_user
from app.models.account import Account

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=AccountListResponse)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users and property owners (admin only)
    
    Returns paginated list of non-admin accounts
    """
    account_service = AccountService(db)
    return account_service.get_all_non_admin_accounts(page, size)

@router.get("/users/{user_id}", response_model=AccountResponse)
async def get_user_by_id(
    user_id: str,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get user details by ID (admin only)
    """
    account_service = AccountService(db)
    return account_service.get_account_by_id(user_id)

@router.put("/users/{user_id}", response_model=AccountResponse)
async def update_user(
    user_id: str,
    update_data: UpdateAccountRequest,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user information (admin only)
    """
    account_service = AccountService(db)
    return account_service.update_account(user_id, update_data)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account (admin only)
    """
    account_service = AccountService(db)
    account_service.delete_account(user_id)
    return None

@router.put("/users/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
    user_id: str,
    password_data: ChangePasswordRequest,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Change user password (admin only)
    """
    account_service = AccountService(db)
    account_service.change_user_password(user_id, password_data)
    return None
